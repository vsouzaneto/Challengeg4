import plotly.express as px
import streamlit as st

from ui import as_bool, demonstrative_banner, footer, fmt_int, fmt_money, load_table, metric_note, page_header


page_header(
    "04 · TRIAGEM DE RISCO",
    "Quem merece atenção — e com qual confiança",
    "O índice abaixo ordena investigação. Não é probabilidade de churn, não foi treinado no target e não deve "
    "acionar comunicação automática com clientes.",
)
demonstrative_banner()

triage = load_table("account_triage")
candidates = triage[~as_bool(triage["snapshot_churn_flag"])].copy()

bands = list(candidates["triage_band"].dropna().unique())
confidence = list(candidates["evidence_confidence"].dropna().unique())
f1, f2, f3 = st.columns(3)
selected_bands = f1.multiselect("Faixa de triagem", bands, default=bands)
selected_conf = f2.multiselect("Confiança", confidence, default=confidence)
selected_plan = f3.multiselect("Plano", sorted(candidates["plan_tier"].dropna().unique()), default=sorted(candidates["plan_tier"].dropna().unique()))

view = candidates[
    candidates["triage_band"].isin(selected_bands)
    & candidates["evidence_confidence"].isin(selected_conf)
    & candidates["plan_tier"].isin(selected_plan)
].copy()

high_mask = view["triage_band"].astype(str).str.lower().str.contains("high|alto|critical|crítico")
low_conf = view["evidence_confidence"].astype(str).str.lower().eq("low")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Contas candidatas", fmt_int(len(view)))
    metric_note("Observado", "sem flag de churn; atividade não reconciliada")
with c2:
    st.metric("Atenção alta", fmt_int(high_mask.sum()))
    metric_note("Derivado", "não probabilístico")
with c3:
    st.metric("Baixa confiança", fmt_int(low_conf.sum()))
    metric_note("Derivado", "cobertura insuficiente; não automatizar")
with c4:
    st.metric("Exposição conservadora", fmt_money(view["mrr_proxy_conservative"].sum(min_count=1), True))
    metric_note("Condicional", "proxy; cobertura exibida por conta")

fig = px.scatter(
    view,
    x="triage_score",
    y="mrr_proxy_conservative",
    color="triage_band",
    symbol="evidence_confidence",
    size="mrr_proxy_additive",
    hover_name="account_name",
    hover_data=["account_id", "plan_tier", "industry", "signal_1", "signal_2", "signal_3"],
    labels={
        "triage_score": "Intensidade dos sinais (0–100)",
        "mrr_proxy_conservative": "Exposição mensal conservadora (US$)",
        "triage_band": "Faixa de triagem",
        "evidence_confidence": "Confiança da evidência",
    },
)
score_threshold = 50
revenue_threshold = float(view["mrr_proxy_conservative"].median()) if not view.empty else 0
fig.add_vline(x=score_threshold, line_dash="dash", line_color="#64748b")
fig.add_hline(y=revenue_threshold, line_dash="dash", line_color="#64748b")
fig.add_annotation(xref="paper", yref="paper", x=0.78, y=0.97, text="Validar primeiro", showarrow=False, bgcolor="#fff3da")
fig.add_annotation(xref="paper", yref="paper", x=0.22, y=0.97, text="Proteger valor", showarrow=False, bgcolor="#e8f1fb")
fig.add_annotation(xref="paper", yref="paper", x=0.78, y=0.05, text="Investigar em lote", showarrow=False, bgcolor="#feeceb")
fig.add_annotation(xref="paper", yref="paper", x=0.22, y=0.05, text="Monitorar", showarrow=False, bgcolor="#e8f5ef")
fig.update_layout(height=500, margin=dict(l=10, r=10, t=20, b=10))
st.plotly_chart(fig, use_container_width=True)
st.caption(
    f"Cortes dos quadrantes: intensidade dos sinais = {score_threshold}; exposição mensal = mediana das contas filtradas "
    f"({fmt_money(revenue_threshold)}). Os cortes organizam a fila e não representam probabilidade de churn."
)

quadrants = st.columns(4)
quadrant_text = [
    ("Proteger valor", "Baixos sinais e alta exposição. Confirmar status e preservar relacionamento; não criar contato alarmista."),
    ("Validar primeiro", "Sinais e exposição altos. Revisão humana prioritária de telemetria, contrato e contexto de CS."),
    ("Monitorar", "Baixos sinais e baixa exposição. Acompanhar sem intervenção automática."),
    ("Investigar em lote", "Sinais altos e menor exposição. Buscar causa comum antes de agir conta a conta."),
]
for column, (title, description) in zip(quadrants, quadrant_text):
    column.markdown(f'<div class="quadrant-card"><strong>{title}</strong>{description}</div>', unsafe_allow_html=True)

display_cols = [
    "account_name", "account_id", "triage_score", "triage_band", "evidence_confidence",
    "evidence_coverage_pct", "mrr_proxy_conservative", "mrr_proxy_additive", "signal_1", "signal_2", "signal_3",
]
column_labels = {
    "account_name": "Conta", "account_id": "ID da conta", "triage_score": "Intensidade dos sinais",
    "triage_band": "Faixa de triagem", "evidence_confidence": "Confiança da evidência",
    "evidence_coverage_pct": "Cobertura das evidências (%)",
    "mrr_proxy_conservative": "Exposição mensal conservadora (US$)",
    "mrr_proxy_additive": "Exposição mensal aditiva (US$)",
    "signal_1": "Principal sinal", "signal_2": "Segundo sinal", "signal_3": "Terceiro sinal",
}
display_view = view.sort_values(["triage_score", "mrr_proxy_conservative"], ascending=False)[display_cols].rename(columns=column_labels)
st.dataframe(
    display_view,
    use_container_width=True,
    hide_index=True,
)
st.download_button(
    "Exportar fila para validação humana",
    display_view.to_csv(index=False).encode("utf-8"),
    file_name="ravenstack_triagem_shadow_mode.csv",
    mime="text/csv",
)

with st.expander("Como interpretar o índice"):
    st.markdown(
        "O índice combina recência e tendência de uso válido, erros, carga/escalonamento de suporte e sinais "
        "contratuais observáveis. Receita afeta prioridade, não risco. A confiança mede cobertura e ambiguidades. "
        "Nenhum componente utiliza `churn_flag` para formar o score."
    )
footer()
