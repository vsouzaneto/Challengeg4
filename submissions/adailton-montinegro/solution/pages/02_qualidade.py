import pandas as pd
import plotly.express as px
import streamlit as st

from ui import as_bool, footer, fmt_int, fmt_pct, load_context, load_table, page_header, stop_callout


page_header(
    "01 · ANTES DE CONFIAR",
    "Qualidade dos dados e o gate de decisão",
    "A integridade referencial é boa; a integridade temporal e semântica não é. Aqui, cada descarte permanece "
    "rastreável e nenhuma correção inventa um fato de negócio.",
)

quality = load_table("quality_summary")
issues = load_table("quality_issues")
scope = load_table("analysis_scope")
accounts = load_table("account_snapshot")
context = load_context()

scope_labels = {
    "accounts_snapshot": "Cadastro de contas disponível",
    "subscriptions_observed": "Assinaturas registradas",
    "usage_temporal": "Registros confiáveis da base de uso (features)",
    "support_temporal": "Registros confiáveis da base de tickets (suporte)",
    "churn_event_ledger": "Histórico de ocorrências de churn",
    "account_revenue_proxy": "Estimativa condicionada de receita por conta",
    "account_triage": "Contas disponíveis para triagem demonstrativa",
}
confidence_labels = {
    "Observed": "Disponível como registrado",
    "Derived": "Confiável após tratamento",
    "Conditional": "Usável com restrições",
    "Unavailable": "Não calculável",
}
table_labels = {
    "accounts": "Contas",
    "subscriptions": "Assinaturas",
    "feature_usage": "Uso de funcionalidades",
    "support_tickets": "Tickets de suporte",
    "churn_events": "Ocorrências de churn",
}
rule_labels = {
    "churn_missing_feedback": "Ocorrência sem comentário do cliente",
    "churn_snapshot_disagreement": "Ocorrência diverge do status no cadastro",
    "churn_unknown_reason": "Motivo de churn não informado",
    "usage_after_subscription": "Uso registrado após término da assinatura",
    "usage_before_signup": "Uso registrado antes do cadastro da conta",
    "usage_before_subscription": "Uso registrado antes do início da assinatura",
    "usage_duplicate_id_conflict": "Mesmo ID de uso com conteúdo conflitante",
    "usage_duplicate_surplus": "Registro excedente de uso duplicado",
    "subscription_account_plan_mismatch": "Plano da assinatura diverge do plano da conta",
    "subscription_overlap_unresolved": "Assinaturas simultâneas sem identificação do contrato",
    "support_before_signup": "Ticket aberto antes do cadastro da conta",
    "support_missing_csat": "Ticket sem avaliação de satisfação",
}

raw_rows = int(context["kpis"]["raw_total_rows"])
affected = int(issues["issue_id"].nunique())
snapshot_flag = as_bool(accounts["snapshot_churn_flag"])
ledger_event = as_bool(accounts["has_valid_churn_event"])
agreement = (snapshot_flag == ledger_event).mean() * 100
ambiguous_revenue = (accounts["revenue_confidence"].astype(str).str.lower() != "high").mean() * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("Linhas raw", fmt_int(raw_rows))
c2.metric("Ocorrências de qualidade", fmt_int(affected))
c3.metric("Coincidência snapshot × ledger", fmt_pct(agreement))
c4.metric("Contas com receita ambígua", fmt_pct(ambiguous_revenue))

st.subheader("Quanto dos dados pode ser usado em cada leitura")
chart_scope = scope[scope["raw_rows"] > 0].copy()
chart_scope["eligible_pct"] = 100 * chart_scope["eligible_rows"] / chart_scope["raw_rows"]
chart_scope["business_label"] = chart_scope["scope_id"].map(scope_labels).fillna(chart_scope["scope_label"])
chart_scope["confidence_label"] = chart_scope["confidence_state"].map(confidence_labels)
fig_scope = px.bar(
    chart_scope.sort_values("eligible_pct"),
    x="eligible_pct",
    y="business_label",
    orientation="h",
    color="confidence_label",
    text="eligible_pct",
    labels={"eligible_pct": "% aproveitável", "business_label": "Finalidade da análise", "confidence_label": "Como interpretar"},
    color_discrete_map={
        "Disponível como registrado": "#177a5b",
        "Confiável após tratamento": "#0f6cbd",
        "Usável com restrições": "#d97706",
        "Não calculável": "#b42318",
    },
)
fig_scope.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
fig_scope.update_layout(height=max(420, 34 * len(chart_scope)), margin=dict(l=10, r=50, t=20, b=10))
st.plotly_chart(fig_scope, use_container_width=True)
legend_cols = st.columns(3)
legend_cols[0].success("**Disponível como registrado:** existe na fonte, mas ainda pode conter contradições de negócio.")
legend_cols[1].info("**Confiável após tratamento:** passou pelas regras temporais e de deduplicação definidas.")
legend_cols[2].warning("**Usável com restrições:** serve apenas como proxy ou triagem, com premissas visíveis.")
st.caption("Importante: 100% disponível não significa 100% correto. Assinaturas, por exemplo, estão presentes, mas quase todas se sobrepõem.")

left, right = st.columns([1.15, 1])
with left:
    st.subheader("Onde a base falha — percentual afetado por fonte")
    failed_quality = quality[quality["failed_rows"] > 0].copy()
    failed_quality["Regra de negócio"] = failed_quality["rule_id"].map(rule_labels).fillna(failed_quality["rule_id"])
    failed_quality["Fonte"] = failed_quality["table_name"].map(table_labels).fillna(failed_quality["table_name"])
    pivot = failed_quality.pivot_table(
        index="Regra de negócio", columns="Fonte", values="failure_pct", aggfunc="max", fill_value=0
    )
    fig_heat = px.imshow(
        pivot,
        text_auto=".1f",
        aspect="auto",
        color_continuous_scale=[[0, "#eef4f9"], [0.35, "#f6c56f"], [1, "#a61b1b"]],
        labels={"color": "% dos registros afetados", "x": "Fonte de dados", "y": "Falha encontrada"},
    )
    fig_heat.update_layout(height=470, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_heat, use_container_width=True)
    st.caption("Cada célula mostra a parcela da fonte que viola a regra indicada. Quanto mais escura, maior o impacto na análise.")

with right:
    st.subheader("Análise de churn divergente entre contas e histórico")
    matrix = pd.crosstab(
        snapshot_flag.map({True: "Flag = churn", False: "Sem flag de churn"}),
        ledger_event.map({True: "Tem evento", False: "Sem evento"}),
    )
    fig_matrix = px.imshow(
        matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="Blues",
        labels={"x": "Histórico", "y": "Snapshot", "color": "Contas"},
    )
    fig_matrix.update_layout(height=330, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_matrix, use_container_width=True)
    st.warning(
        "`accounts.churn_flag` descreve um snapshot declarado; `churn_events` descreve histórico. "
        "Nenhuma das duas fontes será usada silenciosamente para corrigir a outra."
    )

with st.expander("Ver catálogo detalhado das falhas e amostra das evidências na base"):
    quality_display = quality.copy()
    quality_display["Falha encontrada"] = quality_display["rule_id"].map(rule_labels).fillna(quality_display["rule_id"])
    quality_display["Fonte"] = quality_display["table_name"].map(table_labels).fillna(quality_display["table_name"])
    st.dataframe(
        quality_display.rename(columns={
            "failed_rows": "Registros afetados",
            "failure_pct": "% da fonte afetada",
            "severity": "Severidade",
            "metric_state": "Condição de uso",
        })[["Fonte", "Falha encontrada", "Registros afetados", "% da fonte afetada", "Severidade", "Condição de uso"]]
        .sort_values(["Severidade", "% da fonte afetada"], ascending=[True, False]),
        use_container_width=True,
        hide_index=True,
    )
    st.dataframe(issues.head(500), use_container_width=True, hide_index=True)

stop_callout()
footer()
