"""Rascunho e dossiê: LLM (cadeia) → guardrail → template. Nada chega ao agente sem passar pelo guardrail."""

from __future__ import annotations

from dataclasses import dataclass, field

from . import base_conhecimento as kb
from . import guardrails, llm, prompts, regras
from .decisao import Decisao
from .logs import registrar


@dataclass
class Texto:
    texto: str
    origem: str               # llm | template | indisponivel
    provedor: str
    modelo: str
    bloqueios: list = field(default_factory=list)
    latencia_ms: float = 0.0
    aviso: str = ""


def _aviso(r: llm.Resposta) -> str:
    erros = [t for t in r.tentativas if t["status"] == "erro"]
    if not erros:
        return ""
    return "fallback: " + " → ".join(f"{t['provedor']} ({t['categoria']})" for t in erros) + f" → {r.provedor}"


def _bloquear(bloqueios: list[str], r: llm.Resposta, d: Decisao) -> None:
    for regra in bloqueios:
        registrar("WARNING", "guardrail", "guardrail_reprovou", regra=regra, provedor=r.provedor, trace_id=d.trace_id)


def rascunho(d: Decisao, texto_ticket: str, sessao=None, cadeia=None) -> Texto:
    if not d.permite_rascunho:
        raise PermissionError(d.motivo_permissao)
    nome = kb.artigo_para(regras.sinais_d1(texto_ticket))
    art = kb.carregar(nome) if nome else None
    if art is None:
        registrar("WARNING", "assistente", "kb_ausente", artigo=nome, trace_id=d.trace_id)
        return Texto("", "indisponivel", "", "", [], 0.0, "rascunho indisponível: sem artigo na base; responder manualmente")
    ja = kb.tentativas(texto_ticket)
    tpl = lambda: kb.rascunho_template(art, ja)  # noqa: E731
    r = llm.gerar("rascunho", prompts.mensagens_rascunho(texto_ticket, art, ja), template=tpl,
                  trace_id=d.trace_id, sessao=sessao, cadeia=cadeia)
    if r.texto is None:
        return Texto("", "indisponivel", "nenhum", "", [], 0.0, "nenhum provedor respondeu: responder manualmente")
    if r.provedor == "template":
        return Texto(r.texto, "template", "template", "kb", [], r.latencia_ms, _aviso(r))
    bloqueios = guardrails.checar_rascunho(r.texto, d, texto_ticket)
    if bloqueios:
        _bloquear(bloqueios, r, d)
        return Texto(tpl(), "template", "template", "kb", bloqueios, r.latencia_ms,
                     f"texto de {r.provedor} bloqueado ({', '.join(bloqueios)}): mostrando o template")
    return Texto(r.texto, "llm", r.provedor, r.modelo, [], r.latencia_ms, _aviso(r))


def dossie(d: Decisao, texto_ticket: str, sessao=None, cadeia=None) -> Texto:
    if not d.permite_dossie:
        raise PermissionError(d.motivo_permissao)
    tpl = lambda: kb.dossie_template(d, texto_ticket)  # noqa: E731
    r = llm.gerar("dossie", prompts.mensagens_dossie(d, texto_ticket), template=tpl, trace_id=d.trace_id,
                  sessao=sessao, cadeia=cadeia)
    if r.texto is None:
        return Texto(tpl(), "template", "template", "kb", [], 0.0, "nenhum provedor respondeu: dossiê por regra")
    if r.provedor == "template":
        return Texto(r.texto, "template", "template", "kb", [], r.latencia_ms, _aviso(r))
    bloqueios = guardrails.checar_dossie(r.texto)
    if bloqueios:
        _bloquear(bloqueios, r, d)
        return Texto(tpl(), "template", "template", "kb", bloqueios, r.latencia_ms,
                     f"dossiê de {r.provedor} bloqueado ({', '.join(bloqueios)}): mostrando o dossiê por regra")
    return Texto(r.texto, "llm", r.provedor, r.modelo, [], r.latencia_ms, _aviso(r))
