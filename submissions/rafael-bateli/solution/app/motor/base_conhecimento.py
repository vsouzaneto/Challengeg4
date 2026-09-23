"""Base de conhecimento curada (o campo Resolution do D1 é texto sem sentido: Entrega 1)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import config
from .decisao import Decisao

# Alternativas de SINAIS["ja_tentou_o_basico"] (automacao.py), separadas por passo.
TENTATIVAS = {
    "factory_reset": r"factory reset",
    "updates": r"checked for (?:any available )?software updates",
    "settings": r"tried different settings|checked the device settings",
    "cables": r"different cables",
    "manual": r"user manual",
    "cache": r"clearing the cache",
    "tutorials": r"online tutorials",
    "support_site": r"official support website",
}
NOMES = {"factory_reset": "a factory reset", "updates": "checking for software updates",
         "settings": "adjusting the device settings", "cables": "different cables", "manual": "the user manual",
         "cache": "clearing the cache", "tutorials": "online tutorials", "support_site": "the official support website"}
ORDEM_ARTIGO = ["perda_de_dados", "conta_bloqueada", "credencial_invalida", "senha_reset_quebrado", "rede",
                "software_bug", "hardware"]
_PASSO = re.compile(r"^\d+\.\s+(.*)$")
_TAG = re.compile(r"\s*\[ja:([a-z_]+)\]\s*$")


@dataclass
class Passo:
    texto: str
    chave: str | None


@dataclass
class Artigo:
    nome: str
    titulo: str
    passos: list = field(default_factory=list)
    corpo: str = ""


def carregar(nome: str) -> Artigo | None:
    caminho = config.KB / f"{nome}.md"
    if not nome or not caminho.exists():
        return None
    linhas = caminho.read_text(encoding="utf-8").splitlines()
    titulo = linhas[0].lstrip("# ").strip() if linhas else nome
    passos = []
    for linha in linhas[1:]:
        m = _PASSO.match(linha.strip())
        if m:
            tag = _TAG.search(m.group(1))
            passos.append(Passo(_TAG.sub("", m.group(1)).strip(), tag.group(1) if tag else None))
    return Artigo(nome, titulo, passos, "\n".join(linhas[1:]).strip())


def artigo_para(sinais: dict) -> str | None:
    for k in ORDEM_ARTIGO:
        if sinais.get(k):
            return k
    if sinais.get("reparo_troca"):
        return "hardware"
    if sinais.get("recontato"):
        return "recontato"
    return None


def tentativas(texto: str) -> list[str]:
    return [k for k, p in TENTATIVAS.items() if re.search(p, texto or "", re.IGNORECASE)]


def rascunho_template(artigo: Artigo, ja: list[str]) -> str:
    passos = [p.texto for p in artigo.passos if p.chave not in ja]
    partes = ["Hello,", "", "Thank you for contacting us about this."]
    if ja:
        partes.append("Since you have already tried " + ", ".join(NOMES[k] for k in ja) +
                      ", we will skip those steps.")
    cabecalho = "Here is what happens next:" if artigo.nome == "recontato" else "Please try the following:"
    partes += ["", cabecalho] + [f"{i}. {p}" for i, p in enumerate(passos, 1)]
    partes += ["", "Best regards,", "Support team"]
    return "\n".join(partes)


def dossie_template(d: Decisao, texto: str) -> str:
    ja = tentativas(texto)
    cuidados = []
    if "perda_de_dados" in d.gatilhos:
        cuidados.append("não sugerir reset, reinstalação ou formatação (pode destruir dado recuperável)")
    if "dinheiro" in d.gatilhos:
        cuidados.append("reembolso/cobrança: elegibilidade por regra (data de compra + política); aprovação humana")
    if {"seguranca", "conta_bloqueada"} & set(d.gatilhos):
        cuidados.append("liberar acesso só após verificação de identidade pelo processo padrão")
    if "recontato" in d.gatilhos:
        cuidados.append("cliente já contatou várias vezes: assumir o caso e não pedir o que ele já informou")
    linhas = [
        f"Resumo: ticket com gatilho(s) {', '.join(d.gatilhos) or 'nenhum'}; prioridade {d.prioridade}.",
        f"O cliente já tentou: {', '.join(NOMES[k] for k in ja) if ja else 'nada informado'}.",
        f"Cuidados: {'; '.join(cuidados) if cuidados else 'nenhum específico'}.",
        f"Trecho do ticket: {texto[:200]}",
    ]
    return "\n".join(linhas)
