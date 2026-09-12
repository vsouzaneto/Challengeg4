import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import os

st.set_page_config(
    page_title="RavenStack — Diagnóstico Executivo de Churn",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Caminhos dos dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "..", "artifacts")
DATA_DIR = os.path.join(BASE_DIR, "..", "..", "..", "data", "churn")

@st.cache_data
def load_data():
    scores_path = os.path.join(ARTIFACTS_DIR, "ravenstack_account_risk_scores.csv")
    accounts_path = os.path.join(DATA_DIR, "ravenstack_accounts.csv")
    subs_path = os.path.join(DATA_DIR, "ravenstack_subscriptions.csv")
    churn_path = os.path.join(DATA_DIR, "ravenstack_churn_events.csv")
    tickets_path = os.path.join(DATA_DIR, "ravenstack_support_tickets.csv")
    usage_path = os.path.join(DATA_DIR, "ravenstack_feature_usage.csv")

    df_scores = pd.read_csv(scores_path)
    df_accounts = pd.read_csv(accounts_path)
    df_subs = pd.read_csv(subs_path)
    df_churn = pd.read_csv(churn_path)
    df_tickets = pd.read_csv(tickets_path)
    df_usage = pd.read_csv(usage_path)

    df_churn['churn_date'] = pd.to_datetime(df_churn['churn_date'])
    df_churn['quarter'] = df_churn['churn_date'].dt.to_period('Q').astype(str)

    df_usage['usage_date'] = pd.to_datetime(df_usage['usage_date'])
    df_usage['quarter'] = df_usage['usage_date'].dt.to_period('Q').astype(str)

    return df_scores, df_accounts, df_subs, df_churn, df_tickets, df_usage

df_scores, df_accounts, df_subs, df_churn, df_tickets, df_usage = load_data()

# Header Executivo
st.title("🦅 RavenStack — Diagnóstico de Churn & Cockpit Prescritivo")
st.caption("AI Master Squad — Consultoria Montinegro | Análise Causal, Sobrevivência e Retenção de MRR")

# KPI Cards
col1, col2, col3, col4, col5 = st.columns(5)
total_accs = len(df_accounts)
churned_accs = df_accounts['churn_flag'].sum()
active_accs = total_accs - churned_accs
lost_mrr = df_scores[df_scores['churn_flag']]['latest_mrr'].sum()
active_mrr = df_scores[~df_scores['churn_flag']]['latest_mrr'].sum()

with col1:
    st.metric("Total de Contas", f"{total_accs}", delta="100% Auditado")
with col2:
    st.metric("Contas Ativas", f"{active_accs}", delta=f"{active_accs/total_accs:.1%}")
with col3:
    st.metric("Logo Churn Total", f"{churned_accs}", delta=f"-{churned_accs/total_accs:.1%}", delta_color="inverse")
with col4:
    st.metric("MRR Ativo", f"${active_mrr:,.0f}/mês")
with col5:
    st.metric("MRR Perdido (Churn)", f"${lost_mrr:,.0f}/mês", delta=f"-${lost_mrr*12:,.0f} ARR", delta_color="inverse")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Visão Executiva (CEO): O Paradoxo Explicado",
    "🎯 Cockpit Prescritivo de CS",
    "💡 Simulador de ROI de Retenção",
    "🔍 Auditoria de Dados & Integridade"
])

# ==============================================================================
# TAB 1: VISÃO EXECUTIVA (CEO)
# ==============================================================================
with tab1:
    st.subheader("1. Desmistificando o Paradoxo: Por que o Churn Explodiu se 'Uso Cresceu' e 'CSAT está OK'?")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**Evolução Trimestral: Eventos de Churn vs Uso Agregado**")
        df_q_churn = df_churn.groupby('quarter').size().reset_index(name='churn_events')
        df_q_usage = df_usage.groupby('quarter')['usage_count'].sum().reset_index(name='total_usage')
        df_merged_q = pd.merge(df_q_churn, df_q_usage, on='quarter', how='outer').fillna(0)
        
        base = alt.Chart(df_merged_q).encode(x=alt.X('quarter:N', title='Trimestre'))
        bar_churn = base.mark_bar(color='#E44057', opacity=0.85).encode(
            y=alt.Y('churn_events:Q', title='Eventos de Churn (Barras Vermelhas)'),
            tooltip=['quarter', 'churn_events', 'total_usage']
        )
        line_usage = base.mark_line(color='#51A3D3', strokeWidth=3, point=True).encode(
            y=alt.Y('total_usage:Q', title='Uso Agregado (Linha Azul)', axis=alt.Axis(orient='right'))
        )
        chart_paradox = alt.layer(bar_churn, line_usage).resolve_scale(y='independent')
        st.altair_chart(chart_paradox, use_container_width=True)
        st.info("💡 **A Ilusão Volumétrica:** O uso atinge a máxima em 2024-Q4 (32.227) impulsionado pelo fluxo acelerado de novas contas com alta atividade de onboarding. No mesmo período, o churn atinge 251 eventos (41.8% do histórico da empresa).")

    with col_b:
        st.markdown("**O Viés do Suporte: CSAT Aparente vs Escalações Críticas Pré-Churn**")
        df_pre_churn_esc = pd.DataFrame({
            'Janela': ['60+ dias antes', '31-60 dias antes', '15-30 dias antes', '0-14 dias antes (Gatilho)'],
            'Taxa de Escalação (%)': [5.0, 4.1, 4.5, 14.6],
            'CSAT Reportado': [3.98, 4.03, 4.00, 4.03]
        })
        chart_esc = alt.Chart(df_pre_churn_esc).mark_bar(color='#E47C40').encode(
            x=alt.X('Janela:N', sort=None, title='Tempo Pré-Cancelamento'),
            y=alt.Y('Taxa de Escalação (%):Q', title='Taxa de Escalação (%)'),
            tooltip=['Janela', 'Taxa de Escalação (%)', 'CSAT Reportado']
        )
        st.altair_chart(chart_esc, use_container_width=True)
        st.warning("⚠️ **O Viés do Sobrevivente:** 41.2% dos tickets sequer foram avaliados no CSAT. Nos últimos 14 dias antes do churn, a taxa de escalação salta para **14.6%** (3x a média), revelando falha terminal no suporte em incidentes de crise.")

    st.markdown("---")
    
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("**Taxa de Churn por Vertical de Indústria**")
        df_ind_churn = df_accounts.groupby('industry')['churn_flag'].agg(['count', 'mean']).reset_index()
        df_ind_churn['churn_pct'] = df_ind_churn['mean'] * 100
        chart_ind = alt.Chart(df_ind_churn).mark_bar().encode(
            x=alt.X('churn_pct:Q', title='Taxa de Churn (%)'),
            y=alt.Y('industry:N', sort='-x', title='Vertical'),
            color=alt.condition(
                alt.datum.churn_pct > 25,
                alt.value('#E44057'),
                alt.value('#51A3D3')
            ),
            tooltip=['industry', 'count', alt.Tooltip('churn_pct:Q', format='.1f')]
        )
        st.altair_chart(chart_ind, use_container_width=True)
        st.caption("DevTools lidera com 31.0% de cancelamentos — sensibilidade extrema a erros de produto.")

    with col_d:
        st.markdown("**Taxa de Churn por Canal de Aquisição**")
        df_ref_churn = df_accounts.groupby('referral_source')['churn_flag'].agg(['count', 'mean']).reset_index()
        df_ref_churn['churn_pct'] = df_ref_churn['mean'] * 100
        chart_ref = alt.Chart(df_ref_churn).mark_bar().encode(
            x=alt.X('churn_pct:Q', title='Taxa de Churn (%)'),
            y=alt.Y('referral_source:N', sort='-x', title='Canal de Aquisição'),
            color=alt.condition(
                alt.datum.churn_pct > 25,
                alt.value('#E44057'),
                alt.value('#A8E440')
            ),
            tooltip=['referral_source', 'count', alt.Tooltip('churn_pct:Q', format='.1f')]
        )
        st.altair_chart(chart_ref, use_container_width=True)
        st.caption("Eventos (30.2%) e Ads (23.5%) trazem contas de menor aderência; Parceiros (14.6%) é o canal mais resiliente.")

# ==============================================================================
# TAB 2: COCKPIT PRESCRITIVO DE CS
# ==============================================================================
with tab2:
    st.subheader("2. Matriz Prescritiva de Retenção — Priorização de Ações por Conta")
    st.markdown("Identificação preditiva de contas at-risk com plano de ação determinístico antes do cancelamento formal.")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        selected_risk = st.multiselect("Nível de Risco:", options=df_scores['risk_tier'].unique(), default=['Crítico (Alto Risco)', 'Atenção (Médio Risco)'])
    with col_f2:
        selected_plan = st.multiselect("Plano:", options=df_scores['plan_tier'].unique(), default=df_scores['plan_tier'].unique())
    with col_f3:
        filter_status = st.selectbox("Status da Conta:", ["Apenas Contas Ativas (Foco Retenção)", "Todas as Contas", "Apenas Já Churneadas"])
    
    filtered_df = df_scores.copy()
    if selected_risk:
        filtered_df = filtered_df[filtered_df['risk_tier'].isin(selected_risk)]
    if selected_plan:
        filtered_df = filtered_df[filtered_df['plan_tier'].isin(selected_plan)]
    if filter_status == "Apenas Contas Ativas (Foco Retenção)":
        filtered_df = filtered_df[~filtered_df['churn_flag']]
    elif filter_status == "Apenas Já Churneadas":
        filtered_df = filtered_df[filtered_df['churn_flag']]
        
    mrr_at_risk = filtered_df['latest_mrr'].sum()
    st.markdown(f"**Contas no Filtro:** `{len(filtered_df)}` | **MRR em Monitoramento:** `${mrr_at_risk:,.2f}/mês` (`${mrr_at_risk*12:,.2f} ARR`)")
    
    # Exibição estilizada da tabela
    st.dataframe(
        filtered_df[['account_id', 'account_name', 'industry', 'plan_tier', 'seats', 
                     'latest_mrr', 'churn_risk_score', 'risk_tier', 'recommended_action',
                     'error_rate_pct', 'total_escalations', 'avg_frt_minutes']],
        use_container_width=True,
        column_config={
            "latest_mrr": st.column_config.NumberColumn("MRR ($)", format="$%.2f"),
            "churn_risk_score": st.column_config.ProgressColumn("Score de Risco", min_value=0, max_value=1, format="%.2f"),
            "error_rate_pct": st.column_config.NumberColumn("Taxa Erro (%)", format="%.2f%%"),
            "avg_frt_minutes": st.column_config.NumberColumn("FRT (min)", format="%.0f min")
        },
        hide_index=True
    )

# ==============================================================================
# TAB 3: SIMULADOR DE ROI DE RETENÇÃO
# ==============================================================================
with tab3:
    st.subheader("3. Simulador de Impacto Financeiro (ROI de Retenção)")
    st.markdown("Estime quanto ARR a RavenStack preservará implementando as medidas prescritivas da squad.")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("**Parâmetros de Intervenção:**")
        pct_ent = st.slider("Redução no Churn Enterprise (%)", min_value=0, max_value=80, value=35, step=5)
        pct_pro = st.slider("Redução no Churn Pro (%)", min_value=0, max_value=80, value=25, step=5)
        cost_cs = st.number_input("Investimento Anual em CS / Engenharia de Resiliência ($)", value=120000, step=10000)
    
    ent_lost_mrr = df_scores[(df_scores['churn_flag']) & (df_scores['plan_tier'] == 'Enterprise')]['latest_mrr'].sum()
    pro_lost_mrr = df_scores[(df_scores['churn_flag']) & (df_scores['plan_tier'] == 'Pro')]['latest_mrr'].sum()
    
    saved_mrr_ent = ent_lost_mrr * (pct_ent / 100.0)
    saved_mrr_pro = pro_lost_mrr * (pct_pro / 100.0)
    total_saved_mrr = saved_mrr_ent + saved_mrr_pro
    total_saved_arr = total_saved_mrr * 12
    net_roi = total_saved_arr - cost_cs
    roi_pct = (net_roi / cost_cs) * 100 if cost_cs > 0 else 0
    
    with col_s2:
        st.markdown("**Resultado Projetado:**")
        st.metric("MRR Preservado", f"${total_saved_mrr:,.2f}/mês")
        st.metric("ARR Preservado Anualmente", f"${total_saved_arr:,.2f}")
        st.metric("Retorno Líquido (ARR - Custo)", f"${net_roi:,.2f}", delta=f"{roi_pct:.0f}% ROI")
        st.success(f"Preservar apenas {pct_ent}% das contas Enterprise que cancelariam paga o investimento com um payback de {cost_cs / total_saved_mrr:.1f} meses.")

# ==============================================================================
# TAB 4: AUDITORIA DE INTEGRIDADE
# ==============================================================================
with tab4:
    st.subheader("4. Auditoria Determinística de Dados (DuckDB)")
    st.markdown("Verificação de integridade referencial, conciliações financeiras e mapeamento de chaves.")
    
    audit_data = [
        {"Tabela": "accounts", "Linhas": 500, "Chave Primária": "account_id (100% único)", "Órfãos": 0, "Nulos Críticos": "0%"},
        {"Tabela": "subscriptions", "Linhas": 5000, "Chave Primária": "subscription_id (100% único)", "Órfãos": 0, "Nulos Críticos": "end_date: 90.3% ativos"},
        {"Tabela": "feature_usage", "Linhas": 25000, "Chave Primária": "usage_id", "Órfãos": 0, "Nulos Críticos": "0%"},
        {"Tabela": "support_tickets", "Linhas": 2000, "Chave Primária": "ticket_id (100% único)", "Órfãos": 0, "Nulos Críticos": "satisfaction_score: 41.2%"},
        {"Tabela": "churn_events", "Linhas": 600, "Chave Primária": "churn_event_id (100% único)", "Órfãos": 0, "Nulos Críticos": "feedback_text: 24.7%"}
    ]
    st.table(pd.DataFrame(audit_data))
    st.info("Conciliação de Faturamento: 100% das 5.000 assinaturas obedecem à regra estrita `ARR == MRR * 12` (0 discrepâncias).")

