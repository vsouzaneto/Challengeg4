"""Tela 1: a fila do agente, já triada. O agente trabalha pela ordem do risco real."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from motor import assistente, regras
from motor import base_conhecimento as kb
from telas import comum

STATUS = ["Open", "Pending Customer Response", "Closed"]
OPERACOES = ["Suporte ao cliente (D1)", "Service desk (D2)"]


def render() -> None:
    st.title("Fila do agente")
    comum.checar_dados()
    op = st.radio("Operação", OPERACOES, horizontal=True, key="op_fila")
    if op == OPERACOES[0]:
        _fila_d1()
    else:
        _fila_d2()


def _fila_d1() -> None:
    df, decs = comum.d1(), comum.fila_d1()
    st.caption("Dataset 1: 8.469 tickets reais. Rota e prioridade saem do motor em milissegundos, sem LLM; "
               "o rascunho só é gerado quando você pede.")
    c1, c2 = st.columns(2)
    status = c1.multiselect("Status", STATUS, default=["Open"], key="f_status")
    rotas = c2.multiselect("Rota", list(regras.ROTULO_D1_CURTO), default=list(regras.ROTULO_D1_CURTO), key="f_rota")
    idx = [i for i, d in enumerate(decs) if df.at[i, "Ticket Status"] in status and d.rota in rotas]
    idx.sort(key=lambda i: (regras.ORDEM_PRIORIDADE[decs[i].prioridade], decs[i].sla_horas, int(decs[i].ticket_id)))
    n = len(idx) or 1
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tickets na fila", comum.num(len(idx)))
    m2.metric("Não precisa abrir (rota 3)", comum.pct(sum(decs[i].rota == "3" for i in idx) / n, 0))
    m3.metric("Humano decide (rota 1)", comum.pct(sum(decs[i].rota in ("1A", "1B") for i in idx) / n, 0))
    m4.metric("Risco que estava como Low/Medium", comum.num(sum(
        decs[i].prioridade in ("Critical", "High") and df.at[i, "Ticket Priority"] in ("Low", "Medium") for i in idx)))
    topo = idx[:200]
    st.dataframe(pd.DataFrame([{
        "ID": decs[i].ticket_id, "Prioridade (declarada → sugerida)": f"{df.at[i, 'Ticket Priority']} → {decs[i].prioridade}",
        "SLA (h)": decs[i].sla_horas, "Rota": decs[i].rota, "Motivo": decs[i].motivo,
        "Marcações": ", ".join(decs[i].marcacoes), "Canal": df.at[i, "Ticket Channel"]} for i in topo]),
        hide_index=True, width="stretch", height=280)
    st.caption(f"Mostrando os {len(topo)} primeiros de {comum.num(len(idx))}, na ordem de prioridade sugerida e SLA.")
    if not topo:
        return
    escolhido = st.selectbox("Abrir ticket", [decs[i].ticket_id for i in topo], key="ticket_d1")
    i = next(i for i in topo if decs[i].ticket_id == escolhido)
    _card_d1(decs[i], df.iloc[i])


def _card_d1(d, row) -> None:
    st.divider()
    st.subheader(f"#{d.ticket_id} · {row['Ticket Subject']}")
    a, b, c, e = st.columns(4)
    a.metric("Prioridade sugerida", d.prioridade, f"declarada: {row['Ticket Priority']}", delta_color="off")
    b.metric("SLA", f"{d.sla_horas:g} h")
    c.metric("Rota", d.rota)
    e.metric("Canal", row["Ticket Channel"])
    st.markdown(f"**{d.rota_rotulo}** · motivo: `{d.motivo}`")
    if d.marcacoes:
        st.caption("Marcações: " + " · ".join(d.marcacoes))
    if d.rota in ("1A", "1B"):
        st.warning(f"A IA não decide este ticket ({d.motivo}). {d.motivo_permissao}.")
    texto = str(row["Ticket Description"])
    st.text_area("Texto do cliente", texto, height=120, disabled=True, key=f"txt_{d.ticket_id}")
    with st.expander("Rastro da decisão (cada etapa, motivo e tempo)"):
        st.dataframe(comum.rastro_df(d), hide_index=True, width="stretch")
    st.markdown("#### O que a IA prepara")
    st.caption(d.motivo_permissao)
    if "canal_publico" in d.marcacoes:
        st.info(kb.carregar("rede_social").corpo)
    if d.rota == "3":
        st.info(kb.carregar("coleta").corpo)
        st.caption("Enviado automaticamente. Lembretes em D+2 e D+5; fecha em D+7 com reabertura em 1 clique.")
    if d.permite_dossie and st.button("Gerar dossiê", key=f"dos_{d.ticket_id}"):
        st.session_state[f"dossie_{d.ticket_id}"] = assistente.dossie(d, texto)
    if d.permite_rascunho and st.button("Gerar rascunho", key=f"ras_{d.ticket_id}"):
        st.session_state[f"rascunho_{d.ticket_id}"] = assistente.rascunho(d, texto)
    if st.session_state.get(f"dossie_{d.ticket_id}"):
        mostrar_texto("Dossiê", st.session_state[f"dossie_{d.ticket_id}"])
    if st.session_state.get(f"rascunho_{d.ticket_id}"):
        _revisar(d, st.session_state[f"rascunho_{d.ticket_id}"])
    with st.expander("Alterar prioridade (vira rótulo para o modelo futuro)"):
        opcoes = list(regras.ORDEM_PRIORIDADE)
        nova = st.selectbox("Nova prioridade", opcoes, index=opcoes.index(d.prioridade), key=f"np_{d.ticket_id}")
        if st.button("Salvar prioridade", key=f"sp_{d.ticket_id}") and nova != d.prioridade:
            comum.gravar("prioridade_alterada", ticket_id=d.ticket_id, de=d.prioridade, para=nova)


def _origem(t) -> str:
    modelo = f" · {t.modelo}" if t.modelo and t.modelo != "kb" else ""
    return f"gerado por `{t.provedor or '—'}{modelo}` · {t.latencia_ms:.0f} ms"


def mostrar_texto(titulo: str, t) -> None:
    st.markdown(f"**{titulo}** · {_origem(t)}")
    if t.bloqueios:
        st.warning("Guardrail bloqueou o texto da LLM: " + ", ".join(t.bloqueios))
    if t.origem == "indisponivel":
        st.error(t.aviso)
        return
    if t.aviso:
        st.caption(t.aviso)
    st.text(t.texto)


def _revisar(d, t) -> None:
    if t.origem == "indisponivel":
        st.error(t.aviso)
        return
    st.markdown(f"**Rascunho** · {_origem(t)}")
    if t.bloqueios:
        st.warning("Guardrail bloqueou o texto da LLM: " + ", ".join(t.bloqueios))
    if t.aviso:
        st.caption(t.aviso)
    editado = st.text_area("Rascunho (edite se precisar)", t.texto, height=220, key=f"ed_{d.ticket_id}")
    base = {"ticket_id": d.ticket_id, "rota": d.rota, "origem": t.origem, "provedor": t.provedor, "modelo": t.modelo}
    c1, c2 = st.columns(2)
    if c1.button("Aprovar e enviar", key=f"ap_{d.ticket_id}"):
        comum.gravar("aprovar" if editado.strip() == t.texto.strip() else "editar", **base)
    if c2.button("Descartar", key=f"dc_{d.ticket_id}"):
        comum.gravar("descartar", **base)


def _fila_d2() -> None:
    decs = comum.fila_d2()
    m, _ = comum.modelo()
    st.caption("Dataset 2: 9.568 tickets de teste que o modelo nunca viu no treino. Acima do limiar de confiança o "
               "ticket é roteado sozinho; abaixo, vai para triagem humana com 3 sugestões.")
    cols = st.columns(4)
    for col, r in zip(cols, ["auto", "triagem", "sensivel", "detalhes"]):
        col.metric(regras.ROTULO_D2[r], comum.pct(sum(d.rota == r for d in decs) / len(decs)))
    rotas = st.multiselect("Rota", list(regras.ROTULO_D2), default=["sensivel", "triagem", "detalhes"],
                           format_func=regras.ROTULO_D2.get, key="f_rota_d2")
    gabarito = st.toggle("Mostrar o rótulo real do dataset (gabarito)", key="gabarito")
    idx = [i for i, d in enumerate(decs) if d.rota in rotas]
    idx.sort(key=lambda i: (comum.ORDEM_ROTA_D2[decs[i].rota], decs[i].confianca or 0))
    topo = idx[:200]
    linhas = []
    for i in topo:
        d = decs[i]
        linha = {"ID": d.ticket_id, "Rota": d.rota, "Classe prevista": d.classe,
                 "Confiança": None if d.confianca is None else round(d.confianca, 2), "Motivo": d.motivo}
        if gabarito:
            linha["Rótulo real"] = m.y_te[i]
        linhas.append(linha)
    st.dataframe(pd.DataFrame(linhas), hide_index=True, width="stretch", height=280)
    if not topo:
        return
    escolhido = st.selectbox("Abrir ticket", [decs[i].ticket_id for i in topo], key="ticket_d2")
    i = next(i for i in topo if decs[i].ticket_id == escolhido)
    _card_d2(decs[i], m.X_te[i], m.y_te[i] if gabarito else None, m)


def _card_d2(d, texto, real, m) -> None:
    st.divider()
    st.subheader(f"{d.ticket_id} · {d.rota_rotulo}")
    st.markdown(f"Motivo: `{d.motivo}`")
    if d.gatilhos:
        st.warning(f"Gatilho sensível ({', '.join(d.gatilhos)}): a IA roteia, mas a ação (conceder acesso, "
                   "responder sobre dado pessoal, declarar incidente) é humana.")
    st.text_area("Texto do ticket", texto, height=110, disabled=True, key=f"t2_{d.ticket_id}")
    if d.top3:
        st.markdown(f"**3 classes mais prováveis** (limiar de confiança: {m.limiar:.2f})")
        st.bar_chart(pd.DataFrame(d.top3, columns=["classe", "probabilidade"]).set_index("classe"))
    if real is not None:
        st.caption(f"Rótulo real do dataset: {real}")
    if d.similares:
        st.markdown("**Tickets parecidos no histórico**")
        st.dataframe(pd.DataFrame(d.similares), hide_index=True, width="stretch")
    with st.expander("Rastro da decisão"):
        st.dataframe(comum.rastro_df(d), hide_index=True, width="stretch")
    c1, c2 = st.columns([2, 1])
    correta = c1.selectbox("Fila errada? Escolha a classe correta", list(m.classes), key=f"cc_{d.ticket_id}")
    if c2.button("Devolver para a fila certa", key=f"fe_{d.ticket_id}"):
        comum.gravar("fila_errada", ticket_id=d.ticket_id, classe_prevista=d.classe, classe_correta=correta,
                     confianca=d.confianca)
