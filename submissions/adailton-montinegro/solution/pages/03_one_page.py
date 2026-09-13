import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ui import as_bool, demonstrative_banner, footer, fmt_int, fmt_money, fmt_pct, load_table, metric_note, page_header


page_header(
    "02 · ONE-PAGE EXECUTIVO",
    "O que resta quando a precisão aparente é removida",
    "Visão central da operação com as fontes deliberadamente separadas. Eventos não são tratados como logos "
    "perdidos e proxies financeiros não são chamados de receita reconciliada.",
)
demonstrative_banner()

accounts = load_table("account_snapshot")
monthly = load_table("monthly_events")
segments = load_table("segment_snapshot")
reasons = load_table("churn_reasons")
scope = load_table("analysis_scope")

total = len(accounts)
snapshot_flag = as_bool(accounts["snapshot_churn_flag"])
ledger_event = as_bool(accounts["has_valid_churn_event"])
snapshot_churned = int(snapshot_flag.sum())
event_accounts = int(ledger_event.sum())
overlap = (snapshot_flag == ledger_event).mean() * 100
overlap_accounts = int((snapshot_flag == ledger_event).sum())
candidate = accounts[~snapshot_flag]
lower = candidate["mrr_proxy_conservative"].sum(min_count=1)
upper = candidate["mrr_proxy_additive"].sum(min_count=1)
financial_coverage = 100 * candidate["mrr_proxy_conservative"].notna().mean()

cols = st.columns(4)
with cols[0]:
    st.metric("Contas avaliadas", fmt_int(total))
    metric_note("Observado", "cadastro de contas")
with cols[1]:
    st.metric("Marcadas como churn no cadastro", fmt_int(snapshot_churned))
    metric_note("Derivado", f"{fmt_pct(100 * snapshot_churned / total)} das contas")
with cols[2]:
    st.metric("Com alguma ocorrência de churn", fmt_int(event_accounts))
    metric_note("Derivado", "histórico; não representa status atual")
with cols[3]:
    st.metric("Contas coerentes nas duas fontes", fmt_int(overlap_accounts))
    metric_note("Derivado", f"{fmt_pct(overlap)} de coincidência; não valida status")

st.markdown("##### Exposição mensal das contas sem flag de churn no cadastro")
financial_cols = st.columns(2)
with financial_cols[0]:
    st.metric("Cenário conservador", fmt_money(lower, True))
    metric_note("Condicional", f"maior assinatura por conta · cobertura {financial_coverage:.1f}%")
with financial_cols[1]:
    st.metric("Cenário aditivo", fmt_money(upper, True))
    metric_note("Condicional", "soma das assinaturas simultâneas; pode superestimar")

st.markdown("**Parcela considerada nesta continuação demonstrativa**")
scope_focus = scope[scope["scope_id"].isin(["usage_temporal", "support_temporal"])]
scope_name = {
    "usage_temporal": "Registros confiáveis da base de uso (features)",
    "support_temporal": "Registros confiáveis da base de tickets (suporte)",
}
scope_cols = st.columns(len(scope_focus))
for container, (_, row) in zip(scope_cols, scope_focus.iterrows()):
    with container:
        discarded_pct = 100 - float(row["coverage_pct"])
        st.metric(
            scope_name[row["scope_id"]],
            f'{int(row["eligible_rows"]):,}/{int(row["raw_rows"]):,}'.replace(",", "."),
            delta=f"{discarded_pct:.1f}% desconsiderado".replace(".", ","),
            delta_color="inverse",
        )
        st.caption(row["notes"])

st.subheader("Entradas e eventos de churn por mês — séries separadas")
fig = go.Figure()
fig.add_bar(
    x=monthly["month_start"], y=monthly["new_accounts"], name="Novas contas",
    marker_color="#0f6cbd", text=monthly["new_accounts"], textposition="outside",
)
fig.add_scatter(
    x=monthly["month_start"], y=monthly["valid_churn_events"], name="Ocorrências de churn",
    mode="lines+markers+text", text=monthly["valid_churn_events"], textposition="top center",
    line=dict(color="#b42318", width=3), cliponaxis=False,
)
fig.update_layout(
    barmode="group", height=390, yaxis_title="Volume observado", xaxis_title="Mês",
    legend=dict(orientation="h", y=1.12), margin=dict(l=10, r=10, t=20, b=10),
)
st.plotly_chart(fig, use_container_width=True)
st.caption("Não é possível calcular o saldo de clientes nem o churn rate a partir das fontes.")

left, right = st.columns(2)
with left:
    dimensions = sorted(segments["dimension_name"].dropna().unique())
    dimension_names = {"plan_tier": "Plano", "industry": "Indústria", "referral_source": "Canal de aquisição", "country": "País"}
    dimension = st.selectbox(
        "% Churn na perspectiva do snapshot",
        dimensions,
        index=dimensions.index("plan_tier") if "plan_tier" in dimensions else 0,
        format_func=lambda value: dimension_names.get(value, value),
    )
    seg = segments[segments["dimension_name"] == dimension].sort_values("snapshot_churn_rate_pct")
    fig_seg = px.bar(
        seg,
        x="snapshot_churn_rate_pct",
        y="segment_value",
        orientation="h",
        text="snapshot_churn_rate_pct",
        color="snapshot_churn_rate_pct",
        color_continuous_scale="Blues",
        hover_data=["total_accounts", "wilson_ci_low_pct", "wilson_ci_high_pct", "global_p_value"],
        labels={"snapshot_churn_rate_pct": "Contas com flag de churn (%)", "segment_value": "Segmento", "total_accounts": "n"},
    )
    fig_seg.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_seg.update_layout(height=390, margin=dict(l=10, r=50, t=20, b=10), coloraxis_showscale=False)
    st.plotly_chart(fig_seg, use_container_width=True)
    st.caption("Associação transversal com a flag do snapshot; não é taxa mensal nem evidência causal.")

with right:
    st.markdown("#### % Churn na perspectiva de ocorrências")
    reason_plot = reasons.sort_values("valid_churn_events")
    fig_reason = px.bar(
        reason_plot,
        x="valid_churn_events",
        y="reason_code",
        orientation="h",
        text="event_share_pct",
        color="event_share_pct",
        color_continuous_scale="Tealgrn",
        labels={"valid_churn_events": "Eventos", "reason_code": "Motivo declarado"},
    )
    fig_reason.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_reason.update_layout(height=390, margin=dict(l=10, r=50, t=20, b=10))
    fig_reason.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_reason, use_container_width=True)
    st.caption("Motivos declarados no grão de evento; uma conta pode aparecer mais de uma vez.")

st.info(
    "Leitura central: a alta de eventos é observável, mas o denominador de clientes expostos e a receita perdida "
    "não são reconciliáveis. O próximo passo é testar associações na parcela elegível, não escolher um culpado."
)
footer()
