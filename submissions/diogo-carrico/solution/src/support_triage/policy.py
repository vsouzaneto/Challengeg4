"""Never-automate policy: tickets that always go to a person, whatever the model says.

Checked on the raw text, in Portuguese and English, before the classifier runs.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    name: str
    goes_to: str
    why: str
    patterns: tuple[str, ...]


# Up to three words may sit between the two halves of a phrase: "bateria está inchada".
GAP = r"\W+(?:\w+\W+){0,3}"

# Order matters: the first rule that matches names the reason, so the gravest checks come first.
RULES: tuple[Rule, ...] = (
    Rule(
        "Tentativa de manipular a IA",
        "Atendente",
        "A mensagem é tratada como texto do cliente, nunca como instrução",
        (
            r"ignor\w*" + GAP + r"(instru|regras)",
            r"ignore" + GAP + r"(previous|prior|above) instructions",
            r"system prompt",
        ),
    ),
    Rule(
        "Risco físico",
        "Atendente, com prioridade",
        "Orientar a desligar o aparelho e não carregar",
        (
            r"bateria" + GAP + r"inchad",
            r"fuma[cç]a",
            r"superaquec",
            r"esquentando",
            r"cheiro de queimado",
            r"pegou fogo",
            r"battery" + GAP + r"swollen",
            r"swollen battery",
            r"\bsmok(e|ing)\b",
            r"overheat",
            r"caught fire",
        ),
    ),
    Rule(
        "Dinheiro: reembolso, estorno ou devolução",
        "Equipe financeira",
        "Envolve dinheiro e direito do consumidor",
        (
            r"reembols",
            r"estorn",
            r"devolu[cç]",
            r"dinheiro de volta",
            r"\brefund",
            r"money back",
            r"chargeback",
        ),
    ),
    Rule(
        "Cancelamento",
        "Atendente",
        "Pode envolver contrato e multa",
        (r"cancel",),
    ),
    Rule(
        "Cobrança indevida ou em duplicidade",
        "Equipe financeira",
        "Pode ser fraude",
        (
            r"cobran[cç]a (indevida|duplicada|em duplicidade)",
            r"cobrad[oa] (duas vezes|em dobro)",
            r"double charge",
            r"charged twice",
            r"unauthori[sz]ed charge",
        ),
    ),
    Rule(
        "Risco jurídico ou de reputação",
        "Supervisor",
        "Exige julgamento e autonomia para resolver",
        (
            r"procon",
            r"advogad",
            r"processo judicial",
            r"vou (te |os |lhes )?processar",
            r"entrar na justi[cç]a",
            r"reclame aqui",
            r"\blawyer",
            r"lawsuit",
            r"\bsue\b",
        ),
    ),
    Rule(
        "Segurança da conta",
        "Equipe de segurança",
        "Risco para o cliente",
        (
            r"invadi",
            r"hackead",
            r"acesso indevido",
            r"n[aã]o fui eu",
            r"\bhacked",
            r"unauthori[sz]ed access",
            r"compromised",
        ),
    ),
    Rule(
        "Dados pessoais (LGPD)",
        "Encarregado de dados",
        "Obrigação legal",
        (
            r"\blgpd\b",
            r"(apag|exclu|delet)\w* (os )?meus dados",
            r"meus dados pessoais",
            r"delete my (data|account)",
            r"\bgdpr\b",
        ),
    ),
)

# Classes the classifier may predict but that are never routed automatically.
NEVER_AUTOMATED_CLASSES = {
    "Administrative rights": "Concessão de privilégio: a decisão final é humana (hipótese 3.1 do Diogo) e a classe não alcança 95% de precisão com confiança",
}


def _fold(text: str) -> str:
    return unicodedata.normalize("NFC", str(text)).lower()


def matching_rule(text: str) -> Rule | None:
    """The first never-automate rule the text triggers, or None."""
    folded = _fold(text)
    for rule in RULES:
        if any(re.search(p, folded) for p in rule.patterns):
            return rule
    return None
