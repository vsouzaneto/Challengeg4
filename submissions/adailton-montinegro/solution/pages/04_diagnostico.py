import plotly.express as px
import streamlit as st

from ui import demonstrative_banner, footer, load_table, page_header


page_header(
    "03 · DIAGNÓSTICO ANALÍTICO",
    "Sinais, segmentos e turning points sem atalhos causais",
    "A página explora padrões possíveis, preservando os furos da base e mostrando o universo de cada comparação.",
)
demonstrative_banner()

triage = load_table("account_triage")
segments = load_table("segment_snapshot")
monthly = load_table("monthly_events")
reasons = load_table("churn_reasons")
pre_event = load_table("pre_event_signals")
tests = load_table("statistical_tests")

st.subheader("O diagnóstico que os dados permitem")
c1, c2, c3 = st.columns(3)
c1.success("**Sabemos:** há conflitos sistêmicos; motivos e volumes de eventos são observáveis.")
c2.warning("**Suspeitamos:** alguns segmentos e sinais merecem investigação humana.")
c3.error("**Não sabemos:** causa raiz causal, MRR perdido e probabilidade individual.")

st.subheader("Quadrante exploratório por conta")
numeric_options = {
    "Recência de uso válido (dias)": "usage_recency_days",
    "Tendência de uso válido (%)": "usage_trend_pct",
    "Taxa de erro (%)": "error_rate_pct",
    "Tickets válidos": "total_tickets",
    "Taxa de escalação (%)": "escalation_rate_pct",
    "CSAT médio respondido": "avg_csat",
    "Exposição proxy conservadora (US$)": "mrr_proxy_conservative",
    "Exposição proxy aditiva (US$)": "mrr_proxy_additive",
    "Índice de triagem": "triage_score",
}
q1, q2 = st.columns(2)
x_label = q1.selectbox("Eixo X", list(numeric_options), index=0)
y_label = q2.selectbox("Eixo Y", list(numeric_options), index=3)

plot_df = triage.dropna(subset=[numeric_options[x_label], numeric_options[y_label]]).copy()
fig_quad = px.scatter(
    plot_df,
    x=numeric_options[x_label],
    y=numeric_options[y_label],
    color="evidence_confidence",
    size="mrr_proxy_conservative",
    hover_name="account_name",
    hover_data=["account_id", "plan_tier", "industry", "triage_band", "signal_1", "signal_2"],
    color_discrete_map={"High": "#177a5b", "Medium": "#d97706", "Low": "#b42318"},
    labels={numeric_options[x_label]: x_label, numeric_options[y_label]: y_label, "evidence_confidence": "Confiança"},
)
fig_quad.update_layout(height=520, margin=dict(l=10, r=10, t=20, b=10))
st.plotly_chart(fig_quad, use_container_width=True)
st.caption("O tamanho usa a proxy conservadora. O gráfico serve para investigação, não para provar causalidade.")

left, right = st.columns(2)
with left:
    st.subheader("Segmentos do snapshot")
    segment_dimension = st.selectbox(
        "Dimensão",
        sorted(segments["dimension_name"].dropna().unique()),
        key="diagnostic_segment_dimension",
    )
    segment_view = segments[segments["dimension_name"] == segment_dimension].sort_values(
        "snapshot_churn_rate_pct"
    )
    fig_segment = px.scatter(
        segment_view,
        x="snapshot_churn_rate_pct",
        y="segment_value",
        size="total_accounts",
        error_x=segment_view["wilson_ci_high_pct"] - segment_view["snapshot_churn_rate_pct"],
        error_x_minus=segment_view["snapshot_churn_rate_pct"] - segment_view["wilson_ci_low_pct"],
        labels={
            "snapshot_churn_rate_pct": "Prevalência da flag (%)",
            "segment_value": "Segmento",
            "total_accounts": "n",
        },
        hover_data=["total_accounts", "wilson_ci_low_pct", "wilson_ci_high_pct", "global_p_value"],
    )
    fig_segment.update_traces(marker_color="#0f6cbd")
    fig_segment.update_layout(height=390, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_segment, use_container_width=True)
    if not segment_view.empty:
        p_value = float(segment_view["global_p_value"].iloc[0])
        st.caption(
            f"Teste global da dimensão: p={p_value:.3f}. Intervalos de Wilson mostram a incerteza por segmento; "
            "a comparação é transversal e não causal."
        )

with right:
    st.subheader("Evolução do volume de eventos")
    fig_turn = px.line(
        monthly,
        x="month_start",
        y="valid_churn_events",
        markers=True,
        labels={"month_start": "Mês", "valid_churn_events": "Eventos válidos"},
    )
    fig_turn.update_traces(line_color="#b42318", line_width=3)
    fig_turn.update_layout(height=390, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_turn, use_container_width=True)
    st.caption("Sem população exposta reconciliada, a curva descreve volume registrado, não churn rate.")

st.subheader("Motivos declarados: hipótese para pesquisa, não sentença")
reason_columns = {
    "reason_code": "Motivo declarado",
    "valid_churn_events": "Ocorrências válidas",
    "distinct_accounts": "Contas distintas",
    "refund_amount_usd": "Reembolsos registrados (US$)",
    "event_share_pct": "Participação nas ocorrências (%)",
    "coverage_pct": "Cobertura da classificação (%)",
}
st.dataframe(
    reasons.sort_values("valid_churn_events", ascending=False).rename(columns=reason_columns),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Sinais antes do próximo evento registrado")
st.caption(
    "Cada uso ou ticket elegível é associado apenas ao próximo churn futuro da conta. Isso evita a multiplicação "
    "do protótipo, mas ainda não cria grupo causal nem independência entre observações."
)
pre_event = pre_event.sort_values("window_order")
pre_event["usage_per_record"] = pre_event["usage_count"] / pre_event["usage_events"].replace(0, float("nan"))
e1, e2 = st.columns(2)
with e1:
    fig_usage = px.line(
        pre_event,
        x="window_label",
        y="usage_per_record",
        markers=True,
        labels={"window_label": "Dias antes do próximo evento", "usage_per_record": "Uso médio por registro elegível"},
    )
    fig_usage.update_traces(line_color="#0f6cbd", line_width=3)
    usage_max = float(pre_event["usage_per_record"].max())
    fig_usage.update_yaxes(range=[0, usage_max * 1.12])
    fig_usage.update_layout(height=360, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_usage, use_container_width=True)
    st.caption("A intensidade permanece praticamente plana entre as janelas.")
with e2:
    fig_support = px.bar(
        pre_event,
        x="window_label",
        y="escalation_rate_pct",
        text="support_tickets",
        labels={"window_label": "Dias antes do próximo evento", "escalation_rate_pct": "Escalação (%)", "support_tickets": "n tickets"},
        color_discrete_sequence=["#d97706"],
    )
    fig_support.update_traces(texttemplate="n=%{text}", textposition="outside")
    fig_support.update_layout(height=360, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_support, use_container_width=True)
    escalation_test = tests[tests["test_id"] == "pre_event_escalation_0_14"]
    if not escalation_test.empty:
        near = pre_event[pre_event["window_label"] == "0-14"].iloc[0]
        reference = pre_event[pre_event["window_label"].isin(["15-30", "31-60"])]
        ref_escalated = int(reference["escalated_tickets"].sum())
        ref_tickets = int(reference["support_tickets"].sum())
        st.caption(
            f"Leitura de negócio: {int(near['escalated_tickets'])} de {int(near['support_tickets'])} tickets "
            f"foram escalados nos 14 dias anteriores ({near['escalation_rate_pct']:.1f}%), contra "
            f"{ref_escalated} de {ref_tickets} entre 15 e 60 dias. É um sinal para investigação, não prova de causa."
        )

with st.expander("Ver testes estatísticos e limites"):
    test_view = tests[["analysis", "universe", "test_name", "n", "p_value", "effect_name", "effect_value", "interpretation", "notes"]].copy()
    analysis_labels = {
        "Declared reason versus feedback text": "Motivo declarado × comentário do cliente",
        "Escalations in the 0-14 day pre-event window": "Escalações nos 14 dias anteriores à ocorrência",
        "Snapshot churn by country": "Flag de churn por país",
        "Snapshot churn by industry": "Flag de churn por indústria",
        "Snapshot churn by plan_tier": "Flag de churn por plano",
        "Snapshot churn by referral_source": "Flag de churn por canal de aquisição",
        "Agreement between churn universes": "Coerência entre cadastro e histórico de churn",
        "Valid support csat by snapshot state": "Satisfação no suporte por estado do cadastro",
        "Valid support escalation by snapshot state": "Escalação no suporte por estado do cadastro",
        "Valid support first_response by snapshot state": "Primeira resposta do suporte por estado do cadastro",
    }
    universe_labels = {
        "Valid historical churn events": "Ocorrências históricas de churn consideradas válidas",
        "Eligible tickets linked to their next future valid churn event": "Tickets confiáveis ligados à próxima ocorrência de churn",
        "Eligible account snapshot": "Cadastro de contas",
        "Eligible accounts and valid churn-event ledger": "Cadastro de contas e histórico válido de churn",
        "Eligible support tickets": "Tickets de suporte confiáveis",
    }
    note_labels = {
        "Synthetic low-cardinality text; no semantic causal interpretation.": "Texto sintético e pouco variado; não permite interpretação causal.",
        "Exploratory: 6/40 escalations in the 0-14 day window.": "Sinal exploratório: 6 escalações em 40 tickets na janela de 0 a 14 dias.",
        "Cross-sectional association; not a causal estimate.": "Associação transversal; não estima efeito causal.",
        "Historical events do not automatically represent current state.": "Ocorrências históricas não representam automaticamente o status atual.",
        "Ticket-level association; repeated accounts are not independent.": "Associação no nível do ticket; contas repetidas não são observações independentes.",
    }
    test_view["analysis"] = test_view["analysis"].replace(analysis_labels)
    test_view["universe"] = test_view["universe"].replace(universe_labels)
    test_view["test_name"] = test_view["test_name"].replace({"Chi-square": "Qui-quadrado", "Fisher exact": "Exato de Fisher", "Mann-Whitney U": "Mann-Whitney U"})
    test_view["interpretation"] = test_view["interpretation"].replace({
        "No statistical evidence of association": "Sem evidência estatística de associação",
        "Evidence of association": "Há evidência estatística de associação",
    })
    test_view["notes"] = test_view["notes"].replace(note_labels)
    st.dataframe(
        test_view.rename(columns={
            "analysis": "Análise", "universe": "Universo analisado", "test_name": "Método",
            "n": "Observações", "p_value": "Nível de evidência (p)", "effect_name": "Medida de efeito",
            "effect_value": "Magnitude", "interpretation": "Leitura", "notes": "Limitações",
        }),
        use_container_width=True,
        hide_index=True,
    )
footer()
