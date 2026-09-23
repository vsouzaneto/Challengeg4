"""Triagem ponta a ponta de um ticket. Sem LLM: rota e prioridade saem em milissegundos."""

from __future__ import annotations

import math
import time

from . import classificador, config, guardrails, qualidade, regras, similares
from .decisao import Decisao
from .logs import registrar

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


def triar_d2(texto: str, m, ticket_id: str = "novo") -> Decisao:
    return triar_d2_lote([texto], m, [ticket_id])[0]


def triar_d2_lote(textos, m, ids=None) -> list[Decisao]:
    textos = [_texto(t) for t in textos]
    ids = ids or [str(i) for i in range(len(textos))]
    qs = [qualidade.avaliar_texto(t) for t in textos]
    validos = [i for i, q in enumerate(qs) if q.ok]
    prevs, vizs, falha = {}, {}, None
    t0 = time.perf_counter()
    if validos:
        entrada = [qs[i].texto for i in validos]
        try:
            prevs = dict(zip(validos, classificador.prever(m, entrada)))
        except Exception as e:
            falha = "falha_classificador"
            registrar("ERROR", "classificador", "falha_classificador", motivo=type(e).__name__, tickets=len(validos))
        try:
            vizs = dict(zip(validos, similares.vizinhos_lote(m, entrada)))
        except Exception as e:  # sem similares o ticket ainda é roteado; só perde o contexto
            registrar("ERROR", "similares", "falha_classificador", motivo=type(e).__name__)
    ms = (time.perf_counter() - t0) * 1000 / max(len(validos), 1)
    return [_montar_d2(textos[i], ids[i], qs[i], prevs.get(i), vizs.get(i, []), ms, falha, m)
            for i in range(len(textos))]


def _montar_d2(texto, tid, q, prev, viz, ms, falha, m) -> Decisao:
    d = Decisao("d2", str(tid))
    d.marcacoes += q.marcacoes
    d.etapa("qualidade", "ok" if q.ok else q.motivo, ", ".join(q.marcacoes) or "texto utilizável", 0.0)
    if not q.ok:
        d.rota, d.motivo = "detalhes", q.motivo
    else:
        d.similares = viz
        dup = viz[0] if viz and viz[0]["duplicata"] else None
        if dup:
            d.marcacoes.append("quase_duplicata")
        d.etapa("duplicata", f"vínculo com ticket parecido (cosseno {dup['similaridade']:.2f})" if dup else "nenhuma",
                f"classe do ticket anterior: {dup['classe']}" if dup else "nenhum ticket com cosseno ≥ 0,9", 0.0)
        if falha or prev is None:
            d.rota, d.motivo = "triagem", "falha_classificador"
            d.etapa("classificação", "falhou", "ticket vai para humano (toda falha vai para humano)", ms)
        else:
            d.classe, d.confianca, d.top3 = prev.classe, prev.confianca, prev.top3
            d.etapa("classificação", f"{prev.classe} ({prev.confianca:.0%})",
                    "top-3: " + ", ".join(f"{c} {p:.0%}" for c, p in prev.top3), ms)
            d.gatilhos = regras.gatilhos_d2(texto, prev.classe)
            if d.gatilhos:
                d.rota, d.motivo = "sensivel", ", ".join(d.gatilhos)
            elif "idioma_nao_suportado" in q.marcacoes:
                d.rota, d.motivo = "triagem", "idioma_nao_suportado"
            elif prev.confianca >= m.limiar:
                d.rota, d.motivo = "auto", f"confiança {prev.confianca:.2f} ≥ limiar {m.limiar:.2f}"
            else:
                d.rota, d.motivo = "triagem", f"confiança {prev.confianca:.2f} < limiar {m.limiar:.2f}"
    d.rota_rotulo = regras.ROTULO_D2[d.rota]
    d.etapa("gatilho e rota", d.rota_rotulo, d.motivo, 0.0)
    guardrails.aplicar_permissoes(d)
    d.etapa("permissões da IA", "rascunho: não", d.motivo_permissao, 0.0)
    return d
