"""Log de erros e de chamadas: JSON por linha, rotação 5 MB × 3, sem segredo e sem texto de ticket."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from collections import Counter
from logging.handlers import RotatingFileHandler
from pathlib import Path

import numpy as np

from . import config

CATEGORIAS = {None, "sem_chave", "rate_limit", "timeout", "http_5xx", "rede", "resposta_invalida",
              "guardrail_reprovou", "dataset_ausente", "modelo_invalido", "falha_classificador",
              "falha_eventos", "kb_ausente"}
_PROIBIDOS = {"chave", "api_key", "authorization", "texto", "prompt", "mensagens"}
_estado: dict = {"logger": None, "caminho": None}


def caminho_log() -> Path:
    return config.local_dir() / "logs" / "app.log"


def _segredos() -> list[str]:
    return [v for k, v in os.environ.items() if k.endswith("_API_KEY") and v]


class _Json(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        linha = json.dumps(record.msg, ensure_ascii=False, default=str)
        for s in _segredos():
            linha = linha.replace(s, "***")
        return linha


def _logger() -> logging.Logger:
    caminho = caminho_log()
    if _estado["logger"] is None or _estado["caminho"] != caminho:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        lg = logging.getLogger("prototipo")
        lg.setLevel(logging.INFO)
        lg.propagate = False
        for h in list(lg.handlers):
            lg.removeHandler(h)
            h.close()
        h = RotatingFileHandler(caminho, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
        h.setFormatter(_Json())
        lg.addHandler(h)
        _estado.update(logger=lg, caminho=caminho)
    return _estado["logger"]


def registrar(nivel: str, etapa: str, categoria: str | None = None, **campos) -> None:
    if categoria not in CATEGORIAS:
        raise ValueError(f"categoria fora da lista fechada: {categoria}")
    reg = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "nivel": nivel, "etapa": etapa, "categoria": categoria}
    reg.update({k: v for k, v in campos.items() if k not in _PROIBIDOS})
    _logger().log(getattr(logging, nivel), reg)


def ticket_ref(ticket_id, texto: str | None) -> str:
    t = texto or ""
    return f"{ticket_id}:{hashlib.sha1(t.encode('utf-8')).hexdigest()[:10]}:{t[:80]}"


def ler(n: int = 5000) -> list[dict]:
    caminho = caminho_log()
    if not caminho.exists():
        return []
    saida = []
    for linha in caminho.read_text(encoding="utf-8").splitlines()[-n:]:
        try:
            saida.append(json.loads(linha))
        except json.JSONDecodeError:
            continue
    return saida


def saude(regs: list[dict]) -> dict:
    llm_ok = [r for r in regs if r.get("etapa") == "llm" and r.get("status") == "ok"]
    finais = [r for r in regs if r.get("etapa") == "llm_final"]
    lat = [r["latencia_ms"] for r in llm_ok if r.get("latencia_ms") is not None]
    return {
        "chamadas_ok_por_provedor": dict(Counter(r.get("provedor") for r in llm_ok)),
        "taxa_fallback": round(float(np.mean([bool(r.get("fallback")) for r in finais])), 4) if finais else 0.0,
        "latencia_p50_ms": round(float(np.percentile(lat, 50)), 1) if lat else None,
        "latencia_p95_ms": round(float(np.percentile(lat, 95)), 1) if lat else None,
        "erros_por_categoria": dict(Counter(r["categoria"] for r in regs if r.get("categoria"))),
        "bloqueios_guardrail": dict(Counter(r.get("regra") for r in regs if r.get("categoria") == "guardrail_reprovou")),
        "ultimas_falhas": [r for r in regs if r.get("nivel") in ("WARNING", "ERROR")][-20:],
    }
