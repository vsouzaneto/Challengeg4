"""O que a IA pode fazer em cada rota (regra em código, não no prompt) e checagem do texto gerado."""

from __future__ import annotations

import re

from . import config
from .base_conhecimento import tentativas
from .decisao import Decisao
from .qualidade import idioma


def aplicar_permissoes(d: Decisao) -> None:
    if d.operacao == "d2":
        d.permite_rascunho, d.permite_dossie = False, False
        d.motivo_permissao = "service desk: a IA classifica e roteia; a proposta não prevê rascunho aqui"
    elif "canal_publico" in d.marcacoes:
        d.permite_rascunho, d.permite_dossie = False, d.rota in ("1A", "1B")
        d.motivo_permissao = "canal público: só o template aprovado, que leva a conversa para o privado"
    elif d.rota == "1B":
        d.permite_rascunho, d.permite_dossie = False, True
        d.motivo_permissao = "risco no texto (perda de dados, segurança, dinheiro ou idioma): IA só monta o dossiê"
    elif d.rota == "1A":
        d.permite_rascunho, d.permite_dossie = True, True
        d.motivo_permissao = "risco na decisão (hardware, reparo, recontato): IA rascunha, humano decide"
    elif d.rota == "2":
        d.permite_rascunho, d.permite_dossie = True, False
        d.motivo_permissao = "IA rascunha a partir da base de conhecimento; agente aprova, edita ou descarta"
    else:
        d.permite_rascunho, d.permite_dossie = False, False
        d.motivo_permissao = "coleta por template fixo; o ticket volta à triagem quando o cliente responder"


REGRAS = ["perda_de_dados_sem_reset", "sem_promessa_financeira", "sem_liberar_acesso", "nao_repetir_basico",
          "sem_seguir_injecao", "formato"]

_NEGACAO = re.compile(r"\b(?:never|not|cannot|don't|do not|won't|não|nunca)\b|n't", re.IGNORECASE)
_RESET = re.compile(r"\b(?:factory reset|reset (?:it|the device|your device) to (?:its )?factory|reinstall\w*|"
                    r"format(?:ting)? (?:the|your) (?:drive|disk|device|storage)|wipe)", re.IGNORECASE)
_FINANCEIRO = re.compile(
    r"\b(?:we|i)(?:'ll| will| can| are going to| am going to)\b[^.!?\n]{0,60}"
    r"\b(?:refund|reimburs\w*|credit|compensat\w*|replace|replacement|repair|cancel)\b"
    r"|\b(?:refund|reimbursement|credit|replacement|repair)\b[^.!?\n]{0,30}\b(?:has been|is|was) "
    r"(?:approved|processed|issued|scheduled|confirmed)"
    r"|\byou will (?:receive|get) (?:a |an |your )?(?:full )?(?:refund|replacement|credit|new unit)"
    r"|\baprova\w* (?:o )?(?:seu )?reembolso|\breembolso\b[^.!?\n]{0,30}\baprovado", re.IGNORECASE)
_ACESSO = re.compile(
    r"\b(?:unlocked|reactivated|re-enabled)\b"
    r"|\b(?:account|access)\b[^.!?\n]{0,30}\b(?:has been|is now|was) (?:unlocked|restored|reactivated|re-enabled)"
    r"|\b(?:send|share|provide|tell|give|reply with)\b[^.!?\n]{0,30}"
    r"\b(?:password|passcode|pin|verification code|2fa code|otp)\b", re.IGNORECASE)
_BASICO = {
    "factory_reset": r"factory reset|reset (?:it|the device|your device) to (?:its )?factory",
    "updates": r"(?:check|checking|look) for (?:any )?(?:software |firmware )?updates|update (?:the|your) (?:software|firmware)",
    "settings": r"(?:check|review|adjust|try) (?:the |your )?(?:device )?settings|different settings",
    "cables": r"(?:different|another) cable",
    "manual": r"user manual",
    "cache": r"clear(?:ing)? (?:the |your )?(?:app )?cache",
    "tutorials": r"online tutorials?",
    "support_site": r"official support website",
}
_RECONHECE = re.compile(r"already|you(?:'ve| have) (?:tried|done|performed|checked)|since you", re.IGNORECASE)
_INJECAO = re.compile(r"\b(?:i|we) (?:have |'ve )?(?:approved|processed|authorized)\b"
                      r"|\bignor(?:e|ed|ing) (?:all |the |previous |prior |usual )*(?:instructions|rules)"
                      r"|system prompt|\bas an ai\b", re.IGNORECASE)


def _frases(t: str) -> list[str]:
    return [f for f in re.split(r"(?<=[.!?])\s+|\n+", t) if f.strip()]


def _afirmativas(t: str) -> list[str]:
    return [f for f in _frases(t) if not _NEGACAO.search(f)]


def checar_rascunho(rascunho: str, d: Decisao, texto_ticket: str) -> list[str]:
    t = rascunho or ""
    violadas = []
    if "perda_de_dados" in d.gatilhos and any(_RESET.search(f) for f in _afirmativas(t)):
        violadas.append("perda_de_dados_sem_reset")
    if any(_FINANCEIRO.search(f) for f in _afirmativas(t)):
        violadas.append("sem_promessa_financeira")
    if any(_ACESSO.search(f) for f in _afirmativas(t)):
        violadas.append("sem_liberar_acesso")
    if "ja_tentou_o_basico" in d.marcacoes:
        ja = tentativas(texto_ticket)
        instrucoes = [f for f in _frases(t) if not _RECONHECE.search(f)]
        if any(re.search(_BASICO[k], f, re.IGNORECASE) for k in ja for f in instrucoes):
            violadas.append("nao_repetir_basico")
    if _INJECAO.search(t):
        violadas.append("sem_seguir_injecao")
    if not t.strip() or len(t) > config.RASCUNHO_MAX_CHARS or idioma(t) != idioma(texto_ticket):
        violadas.append("formato")
    return violadas


def checar_dossie(texto: str) -> list[str]:
    t = texto or ""
    violadas = []
    if _INJECAO.search(t):
        violadas.append("sem_seguir_injecao")
    if not t.strip() or len(t) > config.RASCUNHO_MAX_CHARS:
        violadas.append("formato")
    return violadas
