"""Tela 4: qualidade da IA para o supervisor — acerto por classe, auditoria, eventos, medição da LLM e saúde."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from motor import config, eventos, logs
from telas import comum


def render() -> None:
    st.title("Qualidade da IA")
    comum.checar_dados()
    _por_classe()
    _auditoria()
    _eventos()
    _medicao()
    _saude()


def _por_classe() -> None:
    st.subheader("Acerto no teste inteiro do D2 (9.568 tickets nunca vistos)")
    m, _ = comum.modelo()
    av = comum.avaliacao_d2()
    c = st.columns(4)
    c[0].metric("Decididos sozinhos", comum.pct(av["cobertura"]))
    c[1].metric("Acerto nesses", comum.pct(av["acerto"]))
    c[2].metric("Acerto abaixo do limiar", comum.pct(av["acerto_abaixo_do_limiar"]), "vão para humano", delta_color="off", delta_arrow="off")
    c[3].metric("Limiar", f"{m.limiar:.2f}")
    df = pd.DataFrame({"real": m.y_te, "prev": av["prev"], "auto": av["conf"] >= m.limiar})
    df["certo"] = df["real"] == df["prev"]
    linhas = [{"classe": k, "tickets": len(g), "% automático": round(g["auto"].mean(), 3),
               "acerto no automático": round(g.loc[g["auto"], "certo"].mean(), 3)} for k, g in df.groupby("real")]
    st.dataframe(pd.DataFrame(linhas).sort_values("% automático"), hide_index=True, width="stretch")
    erros = df[df["auto"] & ~df["certo"]].groupby(["real", "prev"]).size().sort_values(ascending=False).head(6)
    st.markdown("**Para onde vão os erros acima do limiar**")
    st.dataframe(erros.rename("erros").reset_index(), hide_index=True)
    st.caption("Com os gatilhos sensíveis (admin, RH com dado pessoal, alerta de máquina), a fatia roteada sozinha "
               "na fila cai abaixo da cobertura do modelo: gatilho só tira da automação.")


def _auditoria() -> None:
    st.subheader("Auditoria sorteada: 10% das decisões automáticas")
    m, _ = comum.modelo()
    decs = comum.fila_d2()
    autos = [i for i, d in enumerate(decs) if d.rota == "auto"]
    amostra = sorted(np.random.default_rng(2026).choice(autos, max(1, len(autos) // 10), replace=False).tolist())
    st.caption(f"{comum.num(len(amostra))} de {comum.num(len(autos))} decisões automáticas, sorteadas com semente fixa. "
               "Com 10%, uma queda de acerto de 95% para 90% aparece no mês (Entrega 2, B5).")
    pos = int(st.number_input("Item da amostra", 1, len(amostra), 1, key="aud_pos")) - 1
    i = amostra[pos]
    d = decs[i]
    st.text_area("Ticket", m.X_te[i], disabled=True, height=90, key=f"aud_t_{i}")
    st.markdown(f"A IA decidiu: **{d.classe}** ({comum.pct(d.confianca, 0)})")
    c1, c2 = st.columns(2)
    if c1.button("Certo", key=f"aud_ok_{i}"):
        comum.gravar("auditoria_certo", ticket_id=d.ticket_id, classe=d.classe)
    if c2.button("Errado", key=f"aud_er_{i}"):
        comum.gravar("auditoria_errado", ticket_id=d.ticket_id, classe=d.classe)


def _eventos() -> None:
    st.subheader("O que os agentes fizeram (registro de eventos)")
    mt = eventos.metricas(comum.registro().ler())
    c = st.columns(4)
    c[0].metric("Rascunhos revisados", mt["revisados"])
    c[1].metric("Aprovados sem edição (LLM)", "—" if mt["aprovacao_sem_edicao_llm"] is None
                else comum.pct(mt["aprovacao_sem_edicao_llm"], 0), f"{mt['revisados_llm']} da LLM", delta_color="off", delta_arrow="off")
    c[2].metric("Prioridades alteradas", mt["prioridades_alteradas"])
    c[3].metric("Auditoria: acerto", "—" if mt["auditoria_acerto"] is None else comum.pct(mt["auditoria_acerto"], 0),
                f"{mt['auditoria_n']} conferidos", delta_color="off", delta_arrow="off")
    if mt["devolucoes_por_classe"]:
        st.markdown("**Devoluções \"fila errada\" por classe prevista** (o monitor de categoria nova olha isto)")
        st.bar_chart(pd.Series(mt["devolucoes_por_classe"], name="devoluções"))
    st.caption("Promoção do copiloto para envio automático exige ≥ 90% de aprovação sem edição em 200 casos (Entrega 2, 3.4).")


def _medicao() -> None:
    st.subheader("Medição da LLM (M1–M4, critérios pré-registrados)")
    res = comum.ler_json(str(config.OUT_APP / "medicao_llm.json"))
    if not res:
        st.info("Ainda não medido. Rode `python medir_llm.py` com as chaves no .env.")
        return
    for k in ("M1", "M2", "M3", "M4"):
        if k not in res:
            continue
        st.markdown(f"**{k}** · critério: {res['criterios'][k]}")
        st.dataframe(pd.DataFrame(res[k]["por_modelo"]).T.astype(str), width="stretch")
    st.caption(f"Executado em {res.get('data', '—')}. Cada número é de um modelo só; provedores nunca misturados.")


def _saude() -> None:
    st.subheader("Saúde do sistema (logs)")
    s = logs.saude(logs.ler())
    c = st.columns(4)
    c[0].metric("Chamadas OK por provedor", ", ".join(f"{k}: {v}" for k, v in s["chamadas_ok_por_provedor"].items()) or "—")
    c[1].metric("Taxa de fallback", comum.pct(s["taxa_fallback"], 0))
    c[2].metric("Latência p50 / p95", "—" if s["latencia_p50_ms"] is None
                else f"{s['latencia_p50_ms']:.0f} / {s['latencia_p95_ms']:.0f} ms")
    c[3].metric("Bloqueios de guardrail", sum(s["bloqueios_guardrail"].values()))
    if s["erros_por_categoria"]:
        st.bar_chart(pd.Series(s["erros_por_categoria"], name="ocorrências"))
    if s["ultimas_falhas"]:
        st.markdown("**Últimas falhas**")
        st.dataframe(pd.DataFrame(s["ultimas_falhas"]).astype(str), hide_index=True, width="stretch")
    st.caption(f"Arquivo: {logs.caminho_log()} (JSON por linha, rotação 5 MB × 3, sem chave e sem texto de ticket).")
