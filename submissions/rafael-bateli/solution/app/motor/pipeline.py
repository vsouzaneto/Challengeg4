"""Triagem ponta a ponta de um ticket. Sem LLM: rota e prioridade saem em milissegundos."""

from __future__ import annotations

import math
import time

from . import config, guardrails, qualidade, regras
from .decisao import Decisao

MOTIVO_SEM_DUPLICATA_D1 = "não aplicável: falta customer_id no D1 (P8); e-mail repetido é de pessoas diferentes"


def _texto(v) -> str:
    return "" if v is None or (isinstance(v, float) and math.isnan(v)) else str(v)


def triar_d1(ticket: dict) -> Decisao:
    d = Decisao("d1", str(ticket.get("Ticket ID", "novo")))
    desc = _texto(ticket.get("Ticket Description"))
    d.prioridade_declarada = ticket.get("Ticket Priority")

    t0 = time.perf_counter()
    q = qualidade.avaliar_texto(desc)
    d.marcacoes += q.marcacoes
    d.registrar("qualidade", "ok" if q.ok else q.motivo, ", ".join(q.marcacoes) or "texto utilizável", t0)

    t0 = time.perf_counter()
    d.registrar("duplicata", "não aplicável", MOTIVO_SEM_DUPLICATA_D1, t0)

    t0 = time.perf_counter()
    if not q.ok:
        d.rota, d.motivo = "3", q.motivo
    elif "idioma_nao_suportado" in q.marcacoes:
        d.rota, d.motivo = "1B", "idioma_nao_suportado"   # falha de entendimento → humano
    else:
        f = regras.sinais_d1(desc)
        d.gatilhos = [k for k in regras.RISCO if f[k]]
        d.rota, d.motivo = regras.rota_d1(f)
        d.marcacoes += [k for k in ("ja_tentou_o_basico", "incidente") if f[k]]
        if f["urgencia"]:
            d.marcacoes.append("urgente")
    d.rota_rotulo = regras.ROTULO_D1_CURTO[d.rota]
    d.registrar("risco e rota", d.rota_rotulo, d.motivo, t0)

    t0 = time.perf_counter()
    d.prioridade, motivos_p = regras.prioridade_d1(desc)
    d.sla_horas = config.SLA_HORAS[d.prioridade]
    d.registrar("prioridade e SLA", f"{d.prioridade} · SLA {d.sla_horas:g} h",
                ", ".join(motivos_p) or "nenhum sinal de severidade ou urgência", t0)

    t0 = time.perf_counter()
    if ticket.get("Ticket Channel") == "Social media":
        d.marcacoes.append("canal_publico")
    guardrails.aplicar_permissoes(d)
    d.registrar("permissões da IA", f"rascunho: {'sim' if d.permite_rascunho else 'não'} · dossiê: "
                f"{'sim' if d.permite_dossie else 'não'}", d.motivo_permissao, t0)
    return d
