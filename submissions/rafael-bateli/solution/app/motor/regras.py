"""Regras determinísticas. As do D1 são IMPORTADAS da Entrega 2 (automacao.py) e da
Entrega 1 (triagem_ia.py): uma fonte da verdade. Aqui entram só as novidades da
Entrega 3: divisão 1A/1B, rótulos de tela e os gatilhos do D2."""

from __future__ import annotations

import re

from . import config  # noqa: F401  (coloca automacao/ e diagnostico/solucao/ no sys.path)
from automacao import (GENERICO, PROBLEMAS, RISCO, ROTA_AUTO, ROTA_COPILOTO, ROTA_HUMANO, SINAIS,
                       TECNICO)
from triagem_ia import RECONTATO, URGENCIA
from triagem_ia import SINAIS as SINAIS_PRIORIDADE

TODOS_SINAIS = list(PROBLEMAS) + list(SINAIS) + ["generico"]
_RX = {k: re.compile(p, re.IGNORECASE) for k, p in {**PROBLEMAS, **SINAIS}.items()}
_GENERICO = re.compile(GENERICO)  # sem IGNORECASE, como em automacao.parte_a
RISCO_SO_NA_DECISAO = {"hardware", "reparo_troca", "recontato"}  # rota 1A (harness A10)

ROTULO_D1 = {"1A": ROTA_HUMANO, "1B": ROTA_HUMANO, "2": ROTA_COPILOTO, "3": ROTA_AUTO}
ROTULO_D1_CURTO = {"1A": "Rota 1A · humano decide, IA rascunha", "1B": "Rota 1B · humano decide e escreve",
                   "2": "Rota 2 · IA sugere, humano aprova", "3": "Rota 3 · coleta automática"}
ROTULO_D2 = {"auto": "Roteado automático para a fila da classe", "triagem": "Triagem humana (3 sugestões)",
             "sensivel": "Humano aprova a ação", "detalhes": "Pedir detalhes (coleta)"}
ORDEM_PRIORIDADE = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Sem sinal": 4}


def sinais_d1(desc: str | None) -> dict[str, bool]:
    """Mesmo pré-processamento de automacao.parte_a: NaN → '' e quebra de linha → espaço."""
    t = (desc or "").replace("\n", " ")
    f = {k: bool(rx.search(t)) for k, rx in _RX.items()}
    f["generico"] = bool(_GENERICO.search(t)) and not any(f[k] for k in PROBLEMAS)
    return f


def rota_d1(f: dict[str, bool]) -> tuple[str, str]:
    """Espelho de automacao.parte_a.rota, com a rota 1 dividida em 1A/1B."""
    risco = [k for k in RISCO if f[k]]
    if risco:
        return ("1A" if set(risco) <= RISCO_SO_NA_DECISAO else "1B"), ", ".join(risco)
    extra = [k for k in ("ja_tentou_o_basico", "incidente") if f[k]]
    tec = [k for k in TECNICO if f[k]]
    if tec:
        return "2", ", ".join(tec + extra)
    base = "sem problema descrito" if f["generico"] else "sem sinal de risco"
    return "3", ", ".join([base] + extra)


_RXP = {k: (re.compile(p, re.IGNORECASE), w) for k, (p, w) in SINAIS_PRIORIDADE.items()}
_URG = re.compile(URGENCIA, re.IGNORECASE)
_REC = re.compile(RECONTATO, re.IGNORECASE)


def prioridade_d1(desc: str | None) -> tuple[str, list[str]]:
    """Espelho de triagem_ia.parte_c.sugerir, sobre o texto cru (sem trocar quebras de linha)."""
    t = desc or ""
    hits = [k for k, (rx, _) in _RXP.items() if rx.search(t)]
    sev = max([_RXP[k][1] for k in hits], default=0)
    urg, rec = bool(_URG.search(t)), bool(_REC.search(t))
    motivos = hits + (["urgencia"] if urg else []) + (["recontato"] if rec else [])
    if sev == 0 and not urg:
        return "Sem sinal", motivos
    pontos = sev + 2 * urg + rec
    p = "Critical" if pontos >= 5 else "High" if pontos >= 3 else "Medium" if pontos >= 2 else "Low"
    return p, motivos


# D2 — gatilhos que SÓ tiram da automação (Entrega 2, seção 2).
# Permissão de admin: protege-se a AÇÃO (conceder acesso exige aprovação humana no sistema de
# identidade), não o rótulo. Uma regex de texto ("permission|administrator") foi medida na
# Entrega 3: tirava 725 tickets bons da automação para salvar 3 — removida (Entrega 2, B4).
RH_SENSIVEL = re.compile(r"\b(?:salary|payroll|termination|resign|sick|maternity)", re.IGNORECASE)
ALERTA = re.compile(r"critical alert", re.IGNORECASE)


def gatilhos_d2(texto: str, classe: str | None) -> list[str]:
    g = []
    if classe == "Administrative rights":
        g.append("permissao_admin")
    if classe == "HR Support" and RH_SENSIVEL.search(texto):
        g.append("rh_sensivel")
    if ALERTA.search(texto):
        g.append("alerta_maquina")
    return g
