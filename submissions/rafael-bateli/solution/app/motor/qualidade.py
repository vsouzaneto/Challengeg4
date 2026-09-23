"""Quality Gate por ticket (Entrega 1 avaliava o export inteiro; aqui, um ticket por vez)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import config

PLACEHOLDER = re.compile(r"\{[a-z_]+\}")
PALAVRA = re.compile(r"[A-Za-zÀ-ÿ]{2,}")
_PT = re.compile(r"\b(?:de|do|da|dos|das|que|não|nao|para|com|uma|um|por|você|voce|seu|sua|meu|meus|minha|"
                 r"está|esta|isso|preciso|consigo|todos|obrigado)\b", re.IGNORECASE)
_EN = re.compile(r"\b(?:the|and|to|of|you|your|is|for|with|please|we|this|that|it|my|have|not|can)\b",
                 re.IGNORECASE)


@dataclass
class Qualidade:
    ok: bool
    motivo: str | None
    marcacoes: list = field(default_factory=list)
    texto: str = ""


def idioma(texto: str) -> str:
    pt, en = len(_PT.findall(texto or "")), len(_EN.findall(texto or ""))
    return "pt" if pt >= 2 and pt > en else "en"


def avaliar_texto(texto: str | None) -> Qualidade:
    t = (texto or "").strip() if isinstance(texto, str) or texto is None else ""
    if not t:
        return Qualidade(False, "texto_vazio", [], "")
    marc = ["template_quebrado"] if PLACEHOLDER.search(t) else []
    if len(PALAVRA.findall(PLACEHOLDER.sub(" ", t))) < config.MIN_PALAVRAS:
        return Qualidade(False, "sem_problema_descrito", marc, t)
    if idioma(t) != "en":
        marc.append("idioma_nao_suportado")
    if len(t) > config.LIMITE_TEXTO:
        marc.append("texto_truncado")
        t = t[:config.LIMITE_TEXTO]
    return Qualidade(True, None, marc, t)
