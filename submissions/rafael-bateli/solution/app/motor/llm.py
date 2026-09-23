"""Cadeia de provedores: Groq → Gemini → template. Pula para o próximo por falta de chave,
429, 5xx, timeout, erro de rede ou resposta inválida. Cada tentativa vira uma linha de log."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Callable

import requests

from . import config
from .logs import registrar

PROVEDORES = {
    "groq": {"url": "https://api.groq.com/openai/v1/chat/completions", "chave": ["GROQ_API_KEY"],
             "env_modelo": "GROQ_MODELO", "modelo": "openai/gpt-oss-120b", "extra": {"reasoning_effort": "low"}},
    # o Google usa os dois nomes na documentação; aceitamos ambos
    "gemini": {"url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
               "chave": ["GEMINI_API_KEY", "GOOGLE_API_KEY"], "env_modelo": "GEMINI_MODELO",
               "modelo": "gemini-2.5-flash", "extra": {"reasoning_effort": "low"}},
}


def _chave(prov: str) -> str | None:
    return next((os.environ[n] for n in PROVEDORES[prov]["chave"] if os.environ.get(n)), None)


class ErroLLM(Exception):
    def __init__(self, categoria: str, detalhe: str = "", retry_after: float = 0.0):
        super().__init__(f"{categoria}: {detalhe}")
        self.categoria, self.detalhe, self.retry_after = categoria, detalhe, retry_after


@dataclass
class Resposta:
    texto: str | None
    provedor: str
    modelo: str
    latencia_ms: float
    tokens: int | None = None
    tentativas: list = field(default_factory=list)


def cadeia_padrao() -> list[str]:
    return [p.strip() for p in os.environ.get("LLM_CADEIA", "groq,gemini,template").split(",") if p.strip()]


def modelo_de(prov: str) -> str:
    c = PROVEDORES[prov]
    return os.environ.get(c["env_modelo"]) or c["modelo"]


def chaves_presentes() -> dict[str, bool]:
    return {p: bool(_chave(p)) for p in PROVEDORES}


def chamar(prov: str, mensagens: list[dict], *, temperatura: float = 0.3, max_tokens: int = 1500,
           sessao=None) -> tuple[str, int | None]:
    c = PROVEDORES[prov]
    chave = _chave(prov)
    if not chave:
        raise ErroLLM("sem_chave", " ou ".join(c["chave"]))
    corpo = {"model": modelo_de(prov), "messages": mensagens, "temperature": temperatura,
             "max_tokens": max_tokens, **c["extra"]}
    http = sessao or requests
    try:
        r = http.post(c["url"], headers={"Authorization": f"Bearer {chave}", "Content-Type": "application/json"},
                      json=corpo, timeout=config.LLM_TIMEOUT_S)
    except requests.Timeout as e:
        raise ErroLLM("timeout", type(e).__name__)
    except requests.RequestException as e:
        raise ErroLLM("rede", type(e).__name__)
    if r.status_code == 429:
        try:
            espera = float(r.headers.get("retry-after", 0) or 0)
        except ValueError:
            espera = 0.0
        raise ErroLLM("rate_limit", "HTTP 429", espera)
    if r.status_code in (401, 403):
        raise ErroLLM("sem_chave", f"HTTP {r.status_code}")
    if r.status_code >= 500:
        raise ErroLLM("http_5xx", f"HTTP {r.status_code}")
    if r.status_code >= 400:
        raise ErroLLM("resposta_invalida", f"HTTP {r.status_code}")
    try:
        dados = r.json()
        texto = dados["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as e:
        raise ErroLLM("resposta_invalida", type(e).__name__)
    if not texto or not str(texto).strip():
        raise ErroLLM("resposta_invalida", "resposta vazia")
    return str(texto).strip(), (dados.get("usage") or {}).get("total_tokens")


def _final(resp: Resposta, tarefa: str, trace_id: str, primeiro: str | None) -> Resposta:
    registrar("INFO", "llm_final", provedor=resp.provedor, fallback=resp.provedor != primeiro,
              tentativas=len(resp.tentativas), tarefa=tarefa, trace_id=trace_id)
    return resp


def gerar(tarefa: str, mensagens: list[dict], *, template: Callable[[], str] | None = None,
          temperatura: float = 0.3, max_tokens: int = 1500, cadeia: list[str] | None = None,
          validar: Callable[[str], bool] | None = None, trace_id: str = "", sessao=None,
          dormir: Callable[[float], None] = time.sleep) -> Resposta:
    cadeia = cadeia or cadeia_padrao()
    primeiro = cadeia[0] if cadeia else None
    tentativas: list[dict] = []
    for prov in cadeia:
        if prov == "template":
            if template is None:
                continue
            t0 = time.perf_counter()
            texto = template()
            return _final(Resposta(texto, "template", "kb", (time.perf_counter() - t0) * 1000, None, tentativas),
                          tarefa, trace_id, primeiro)
        if prov not in PROVEDORES:
            registrar("WARNING", "llm", "resposta_invalida", provedor=prov, detalhe="provedor desconhecido",
                      trace_id=trace_id)
            continue
        for n in (1, 2):
            t0 = time.perf_counter()
            try:
                texto, tokens = chamar(prov, mensagens, temperatura=temperatura, max_tokens=max_tokens, sessao=sessao)
                if validar is not None and not validar(texto):
                    raise ErroLLM("resposta_invalida", "falhou na validação")
                ms = (time.perf_counter() - t0) * 1000
                tentativas.append({"provedor": prov, "status": "ok"})
                registrar("INFO", "llm", provedor=prov, modelo=modelo_de(prov), status="ok", latencia_ms=round(ms, 1),
                          tokens=tokens, tarefa=tarefa, trace_id=trace_id)
                return _final(Resposta(texto, prov, modelo_de(prov), ms, tokens, tentativas), tarefa, trace_id, primeiro)
            except ErroLLM as e:
                ms = (time.perf_counter() - t0) * 1000
                espera = e.categoria == "rate_limit" and n == 1 and 0 < e.retry_after <= config.RETRY_AFTER_MAX_S
                tentativas.append({"provedor": prov, "status": "erro", "categoria": e.categoria})
                registrar("WARNING", "llm", e.categoria, provedor=prov, modelo=modelo_de(prov), status="erro",
                          latencia_ms=round(ms, 1), detalhe=e.detalhe, tarefa=tarefa, trace_id=trace_id,
                          proximo_passo="esperar e tentar de novo" if espera else "próximo provedor")
                if espera:
                    dormir(e.retry_after)
                    continue
                break
    return _final(Resposta(None, "nenhum", "", 0.0, None, tentativas), tarefa, trace_id, primeiro)
