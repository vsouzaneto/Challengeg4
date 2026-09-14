from datetime import datetime

import streamlit as st

from ui import as_bool, footer, hero, load_context, load_table, metric_note


hero(
    "Verdade antes do churn",
    "Uma auditoria executiva da RavenStack que separa fatos observáveis, sinais demonstrativos e métricas "
    "que os dados não permitem calcular. A pergunta inicial não é quem está causando o churn, mas se o "
    "sistema consegue medi-lo sem contradizer a si próprio.",
)

context = load_context()
kpis = context["kpis"]
data_period = kpis["data_period"]
period_start, period_end = data_period.split(" to ")
formatted_period = (
    f'{datetime.strptime(period_start, "%Y-%m-%d").strftime("%d/%m/%Y")} até '
    f'{datetime.strptime(period_end, "%Y-%m-%d").strftime("%d/%m/%Y")}'
)
total_accounts = int(kpis["total_accounts"])
source_table_count = int(kpis["source_table_count"])
valid_churn_events = int(kpis["valid_churn_events"])
accounts = load_table("account_snapshot")
scope = {row["scope_id"]: row for row in context["analysis_scope"]}
usage_scope = scope["usage_temporal"]
support_scope = scope["support_temporal"]
snapshot_flag = as_bool(accounts["snapshot_churn_flag"])
ledger_event = as_bool(accounts["has_valid_churn_event"])
agreement = 100 * (snapshot_flag == ledger_event).mean()

cols = st.columns(4)
raw_total = int(kpis["raw_total_rows"])
with cols[0]:
    st.metric("Registros auditados", f"{raw_total:,.0f}".replace(",", "."))
    metric_note("Observado", f"{source_table_count} fontes cruzadas")
with cols[1]:
    st.metric("Uso confiável", f'{int(usage_scope["eligible_rows"]):,}'.replace(",", "."))
    metric_note("Derivado", f'{usage_scope["coverage_pct"]:.1f}% dos registros de uso')
with cols[2]:
    st.metric("Tickets confiáveis", f'{int(support_scope["eligible_rows"]):,}'.replace(",", "."))
    metric_note("Derivado", f'{support_scope["coverage_pct"]:.1f}% dos tickets')
with cols[3]:
    st.metric("Coerência entre fontes de churn", f"{agreement:.1f}%".replace(".", ","))
    metric_note("Derivado", "cadastro × histórico")

st.caption(
    f"Escopo auditado: {total_accounts} contas · período dos registros: {formatted_period} · "
    "as chaves conectam as cinco fontes, mas isso não garante coerência temporal ou de negócio."
)

st.subheader("A leitura executiva em três níveis")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        f'<div class="truth-card"><h3>O que sabemos</h3><p>Chaves conectam, fórmulas de linha fecham e existem '
        f'{valid_churn_events} eventos históricos válidos. A qualidade temporal, porém, varia radicalmente por fonte.</p></div>',
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        '<div class="truth-card" style="border-top-color:#d97706"><h3>O que podemos investigar</h3><p>Associações '
        'por segmento, motivos declarados e sinais de uso/suporte na parcela temporalmente elegível.</p></div>',
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        '<div class="truth-card" style="border-top-color:#b42318"><h3>O que não podemos afirmar</h3><p>Causa '
        'raiz causal, churn mensal reconciliado, MRR perdido real, ROI ou probabilidade individual.</p></div>',
        unsafe_allow_html=True,
    )

st.subheader("Índice da entrega")
index_rows = [
    ("01", "Qualidade e gate", "Onde a base quebra e qual decisão profissional isso exige."),
    ("02", "One-page executivo", "Os números centrais da parcela recuperável, sem esconder cobertura."),
    ("03", "Diagnóstico", "Eventos, segmentos, quadrantes e limites das hipóteses."),
    ("04", "Triagem de risco", "Contas específicas por atenção, impacto e confiança."),
    ("05", "Plano de ação", "Instrumentação, pesquisa independente, shadow mode e experimentos."),
]
for number, title, description in index_rows:
    st.markdown(f"**{number} · {title}** — {description}")

st.info(
    "Crédito da fonte: RavenStack Synthetic SaaS Dataset, criado por River @ Rivalytics e disponibilizado no Kaggle."
)
footer()
