"""Réplica vetorizada da política de roteamento de app/lib/classifier.ts (decideRoute).

Existe só para SELECIONAR limiares na validação sem sair do Python. Os números publicados de
roteamento vêm da função TypeScript real (app/scripts/evaluate-routing.ts), que também exige
concordância de 100% com as rotas calculadas aqui.
"""

from __future__ import annotations

import json
import re

import numpy as np
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from common import HERE

RULES_PATH = HERE.parent / "app" / "lib" / "policy-rules.json"
TOKEN_RE = re.compile(r"\b[a-z]{2,}\b")


def load_rules() -> dict:
    return json.loads(RULES_PATH.read_text(encoding="utf-8"))


def tokens_of(normalized: str) -> list[str]:
    return TOKEN_RE.findall(normalized)


def known_share(token_lists: list[list[str]], vocab: set[str]) -> np.ndarray:
    """Fração das palavras de conteúdo (sem stopwords) conhecidas pelo modelo."""
    out = np.zeros(len(token_lists))
    for i, toks in enumerate(token_lists):
        content = [t for t in toks if t not in ENGLISH_STOP_WORDS]
        out[i] = sum(t in vocab for t in content) / len(content) if content else 0.0
    return out


def escalation_hits(token_lists: list[list[str]], rules: dict) -> np.ndarray:
    terms = set(rules["escalationTerms"])
    return np.array([bool(terms.intersection(toks)) for toks in token_lists])


def decide_routes(*, pred: np.ndarray, conf: np.ndarray, p_admin: np.ndarray, known: np.ndarray,
                  escalate: np.ndarray, confidence: float, ood: float, admin_rights: float | None,
                  rules: dict) -> tuple[np.ndarray, np.ndarray]:
    """Mesma ordem de decideRoute: escalação → guarda → confiança → sempre-humano → risco de privilégio → auto."""
    always_human = np.isin(pred, [r["category"] for r in rules["alwaysHuman"]])
    admin_risk = (p_admin >= admin_rights) if admin_rights is not None else np.zeros(len(pred), bool)
    reason = np.select(
        [escalate, known < ood, conf < confidence, always_human, admin_risk],
        ["escalation_terms", "out_of_domain", "low_confidence", "always_human", "admin_rights_risk"],
        default="auto",
    )
    route = np.select([reason == "escalation_terms", reason == "auto"], ["escalar", "auto"], default="revisao_humana")
    return route, reason
