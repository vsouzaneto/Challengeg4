"""Tela 2: painel do Diretor. Cruza os gargalos do D1, o acerto medido no D2 e o ROI da Entrega 2."""

from __future__ import annotations

import time
from collections import Counter

import pandas as pd
import streamlit as st

from motor import config, pipeline
from telas import comum


def horas_ano(auto: dict) -> int:
    return int(sum(x["horas_ano"] or 0 for x in auto.get("D_impacto_esforco", {}).get("itens", [])))


def render() -> None:
    st.title("Painel do Diretor")
    comum.checar_dados()
    diag = comum.ler_json(str(config.OUT_DIAG / "resultados.json")) or {}
    auto = comum.ler_json(str(config.OUT_AUTOMACAO / "automacao.json")) or {}
    _gargalos(diag)
    _replay(auto)
    _roi(auto, diag)
    _onde_para()


def _gargalos(diag: dict) -> None:
    st.subheader("Onde perdemos tempo hoje (Dataset 1)")
    if not diag:
        st.info("Rode diagnostico/diagnostico.py para gerar resultados.json.")
        return
    i0, g = diag["etapa0_integridade"], diag["etapa1_gargalos"]
    pri = g["por_dimensao"]["Ticket Priority"]["pct_open_sem_1a_resposta"]
    c = st.columns(4)
    c[0].metric("Tickets sem 1ª resposta", comum.pct(g["status_pct"]["Open"], 0))
    c[1].metric("Triagem que acerta o assunto", comum.pct(i0["assunto_bate_descricao"]),
                f"acaso: {comum.pct(i0['assunto_bate_descricao_acaso'])}", delta_color="off")
    c[2].metric("Critical sem resposta", comum.pct(pri["Critical"]), f"Low: {comum.pct(pri['Low'])}", delta_color="off")
    c[3].metric("Fechados antes da 1ª resposta", comum.pct(i0["pct_resolucao_antes_da_1a_resposta"], 0))


def _zerar() -> dict:
    return {"i": 0, "rodando": False, "passo": 200, "rotas": Counter(), "riscos": Counter(), "subpriorizados": 0,
            "ms": 0.0}


def _replay(auto: dict) -> None:
    st.subheader("Replay: os 8.469 tickets passando pelo motor")
    st.caption("Cada atualização tria um lote de tickets reais com o mesmo motor da fila (regras + prioridade + SLA).")
    ss = st.session_state
    if "replay" not in ss:
        ss.replay = _zerar()
    c1, c2, c3, c4 = st.columns([1, 1, 1, 3])
    if c1.button("▶ Iniciar", key="rp_play"):
        ss.replay["rodando"] = True
    if c2.button("⏸ Pausar", key="rp_pause"):
        ss.replay["rodando"] = False
    if c3.button("↺ Zerar", key="rp_reset"):
        ss.replay = _zerar()
    ss.replay["passo"] = c4.slider("Tickets por atualização", 50, 1000, ss.replay["passo"], 50, key="rp_passo")
    total_h = horas_ano(auto)

    @st.fragment(run_every=0.7 if ss.replay["rodando"] else None)
    def _passo() -> None:
        r, df = st.session_state.replay, comum.d1()
        total = len(df)
        if r["rodando"] and r["i"] < total:
            t0 = time.perf_counter()
            for t in df.iloc[r["i"]: r["i"] + r["passo"]].to_dict("records"):
                d = pipeline.triar_d1(t)
                r["rotas"][d.rota] += 1
                r["riscos"].update(d.gatilhos)
                if d.prioridade in ("Critical", "High") and t["Ticket Priority"] in ("Low", "Medium"):
                    r["subpriorizados"] += 1
            r["ms"] += (time.perf_counter() - t0) * 1000
            r["i"] = min(total, r["i"] + r["passo"])
            if r["i"] >= total:
                r["rodando"] = False
                st.rerun()
        feitos = r["i"]
        st.progress(feitos / total, text=f"{comum.num(feitos)} de {comum.num(total)} tickets · "
                                         f"{r['ms'] / max(feitos, 1):.2f} ms por ticket")
        a, b, c, e = st.columns(4)
        a.metric("Humano decide (rota 1)", comum.num(r["rotas"]["1A"] + r["rotas"]["1B"]))
        b.metric("IA sugere, humano aprova (rota 2)", comum.num(r["rotas"]["2"]))
        c.metric("Coleta automática (rota 3)", comum.num(r["rotas"]["3"]))
        e.metric("Risco que estava como Low/Medium", comum.num(r["subpriorizados"]))
        if r["riscos"]:
            st.bar_chart(pd.Series(dict(r["riscos"]), name="tickets").sort_values(ascending=False))
        st.metric("Horas/ano devolvidas (proporcional ao que já passou)", comum.num(round(total_h * feitos / total)),
                  f"de {comum.num(total_h)} h/ano no total", delta_color="off")

    _passo()


def _roi(auto: dict, diag: dict) -> None:
    st.subheader("Quanto a proposta devolve (Entrega 2)")
    itens = auto.get("D_impacto_esforco", {}).get("itens", [])
    if not itens:
        st.info("Rode automacao/automacao.py para gerar automacao.json.")
        return
    st.dataframe(pd.DataFrame([{
        "Automação": x["automacao"], "Técnica": x["tipo"], "h/ano": x["horas_ano"],
        "h/mês": round(x["horas_ano"] / 12) if x["horas_ano"] else None, "R$/ano": x["rs_ano"],
        "Semanas": x["esforco_semanas"]} for x in itens]), hide_index=True, width="stretch")
    total = horas_ano(auto)
    av = comum.avaliacao_d2()
    c = st.columns(3)
    c[0].metric("Total", f"{comum.num(total)} h/ano", f"≈ {comum.num(round(total / 12))} h/mês", delta_color="off")
    c[1].metric("Classificação medida (D2)", f"{comum.pct(av['cobertura'])} decididos",
                f"com {comum.pct(av['acerto'])} de acerto", delta_color="off")
    if diag:
        c[2].metric("Triagem de hoje (D1)", comum.pct(diag["etapa0_integridade"]["assunto_bate_descricao"]),
                    "igual ao acaso", delta_color="off")
    st.caption("Horas: premissas e fórmulas da Entrega 2 (automacao.json), sem recalcular. Só o ganho da "
               "classificação é medido; os demais usam o cenário base da Entrega 1.")


def _onde_para() -> None:
    st.subheader("Onde a IA para")
    decs = comum.fila_d1()
    rota1 = [d for d in decs if d.rota in ("1A", "1B")]
    c = st.columns(3)
    c[0].metric("Vão direto para humano", comum.pct(len(rota1) / len(decs)), f"{comum.num(len(rota1))} tickets",
                delta_color="off")
    c[1].metric("1A · IA rascunha, humano decide", comum.num(sum(d.rota == "1A" for d in rota1)))
    c[2].metric("1B · humano decide e escreve", comum.num(sum(d.rota == "1B" for d in rota1)))
    st.bar_chart(pd.Series(dict(Counter(g for d in rota1 for g in d.gatilhos)), name="tickets").sort_values(ascending=False))
    st.caption("Um ticket pode ter mais de um gatilho. Gatilho de risco só tira da automação, nunca coloca.")
    d2 = comum.fila_d2()
    st.caption(f"No service desk (D2), {comum.pct(sum(d.rota == 'sensivel' for d in d2) / len(d2))} dos tickets têm "
               "gatilho sensível (permissão de admin, RH com dado pessoal, alerta de máquina): a IA roteia, humano age.")
