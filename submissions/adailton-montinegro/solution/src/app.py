import os
import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da Página
st.set_page_config(
    page_title="RavenStack SaaS Churn Intelligence",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = "submissions/adailton-montinegro/solution/data/ravenstack.duckdb"

@st.cache_resource
def get_db_connection():
    if not os.path.exists(DB_PATH):
        st.error(f"Banco DuckDB não encontrado em {DB_PATH}. Execute `python src/pipeline.py` primeiro.")
        st.stop()
    return duckdb.connect(DB_PATH, read_only=True)

con = get_db_connection()

# Sidebar de Navegação
st.sidebar.title("🦅 RavenStack Analytics")
st.sidebar.caption("SaaS Retention & Churn Intelligence Engine")

pages = [
    "1. Visão Executiva & MRR Bridge",
    "2. Retenção & Matriz de Coortes",
    "3. Diagnóstico de Produto & Suporte",
    "4. Alerta de Risco & Simulador"
]

selected_page = st.sidebar.radio("Navegação:", pages)
st.sidebar.markdown("---")
st.sidebar.markdown("**Engine:** DuckDB Gold Layer")
st.sidebar.markdown("**Snapshot:** Janeiro / 2026")
st.sidebar.markdown("**Status:** Produção")

# ==============================================================================
# PÁGINA 1: VISÃO EXECUTIVA & MRR BRIDGE
# ==============================================================================
if selected_page == "1. Visão Executiva & MRR Bridge":
    st.title("📊 Visão Executiva: Receita e MRR Bridge")
    st.markdown("Decomposição contábil canônica do crescimento de receita, perdas por churn e eficiência SaaS.")
    
    # Busca dados mais recentes do MRR Bridge
    df_bridge = con.execute("SELECT * FROM gold.agg_mrr_bridge ORDER BY month_date ASC").df()
    latest = df_bridge.iloc[-1]
    prev_year = df_bridge[df_bridge['year_month'] == '2025-01'].iloc[0] if len(df_bridge[df_bridge['year_month'] == '2025-01']) > 0 else df_bridge.iloc[-12]
    
    # Linha de KPIs de Alto Nível
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("MRR Atual (Jan/2026)", f"${latest['ending_mrr']:,.2f}", f"+${latest['ending_mrr'] - prev_year['ending_mrr']:,.2f} YoY")
    with col2:
        st.metric("ARR Estimado", f"${latest['ending_mrr'] * 12:,.2f}", "+21.5% YoY")
    with col3:
        st.metric("Contas Ativas", f"{int(latest['active_accounts'])}", "+75 contas YoY")
    with col4:
        st.metric("Revenue Churn Rate", f"{latest['gross_revenue_churn_rate_pct']:.2f}%", "-0.77% vs Méd.")
    with col5:
        quick_ratio_val = f"{latest['saas_quick_ratio']:.2f}" if pd.notnull(latest['saas_quick_ratio']) else "N/A"
        st.metric("SaaS Quick Ratio", quick_ratio_val, "Alerta (<2.0)")

    st.markdown("---")
    
    # Gráfico 1: Evolução Histórica do MRR e Decomposição
    st.subheader("Evolução Histórica do MRR e Decomposição Líquida")
    
    fig_bridge = go.Figure()
    fig_bridge.add_trace(go.Bar(
        x=df_bridge['year_month'], y=df_bridge['new_mrr'],
        name='New MRR', marker_color='#2ca02c'
    ))
    fig_bridge.add_trace(go.Bar(
        x=df_bridge['year_month'], y=df_bridge['expansion_mrr'],
        name='Expansion MRR', marker_color='#1f77b4'
    ))
    fig_bridge.add_trace(go.Bar(
        x=df_bridge['year_month'], y=df_bridge['reactivation_mrr'],
        name='Reactivation MRR', marker_color='#17becf'
    ))
    fig_bridge.add_trace(go.Bar(
        x=df_bridge['year_month'], y=-df_bridge['contraction_mrr'],
        name='Contraction MRR', marker_color='#ff7f0e'
    ))
    fig_bridge.add_trace(go.Bar(
        x=df_bridge['year_month'], y=-df_bridge['churned_mrr'],
        name='Churned MRR', marker_color='#d62728'
    ))
    fig_bridge.add_trace(go.Scatter(
        x=df_bridge['year_month'], y=df_bridge['ending_mrr'],
        name='Ending MRR', mode='lines+markers', line=dict(color='#333333', width=3)
    ))
    fig_bridge.update_layout(
        barmode='relative',
        title="MRR Bridge Mensal (2021 a 2026) - Receita em USD",
        xaxis_title="Mês",
        yaxis_title="USD",
        hovermode="x unified",
        height=480
    )
    st.plotly_chart(fig_bridge, use_container_width=True)
    
    # Tabela de Fechamento Anual
    st.subheader("Resumo Anual Consolidado do MRR Bridge")
    df_annual = con.execute("""
        SELECT 
            year(month_date) AS ano,
            round(sum(new_mrr), 2) AS new_mrr,
            round(sum(expansion_mrr), 2) AS expansion_mrr,
            round(sum(reactivation_mrr), 2) AS reactivation_mrr,
            round(sum(contraction_mrr), 2) AS contraction_mrr,
            round(sum(churned_mrr), 2) AS churned_mrr,
            round(arg_max(ending_mrr, month_date), 2) AS ending_mrr,
            round(avg(saas_quick_ratio), 2) AS quick_ratio_medio
        FROM gold.agg_mrr_bridge
        GROUP BY year(month_date)
        ORDER BY ano ASC
    """).df()
    st.dataframe(df_annual.style.format({
        'new_mrr': '${:,.2f}',
        'expansion_mrr': '${:,.2f}',
        'reactivation_mrr': '${:,.2f}',
        'contraction_mrr': '${:,.2f}',
        'churned_mrr': '${:,.2f}',
        'ending_mrr': '${:,.2f}',
        'quick_ratio_medio': '{:.2f}'
    }), use_container_width=True)

# ==============================================================================
# PÁGINA 2: RETENÇÃO & MATRIZ DE COORTES
# ==============================================================================
elif selected_page == "2. Retenção & Matriz de Coortes":
    st.title("🎯 Retenção e Dinâmica de Coortes")
    st.markdown("Acompanhamento das safras de clientes: Retenção de Logos e Net Revenue Retention (NRR).")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Logo Retention por Safra Anual (%)")
        df_cohort_annual = con.execute("SELECT * FROM gold.agg_cohort_annual_summary ORDER BY cohort_year ASC").df()
        
        fig_cohort_logo = px.bar(
            df_cohort_annual,
            x='cohort_year',
            y=['logo_ret_m3_pct', 'logo_ret_m6_pct', 'logo_ret_m12_pct'],
            barmode='group',
            labels={'value': 'Retenção (%)', 'cohort_year': 'Safra', 'variable': 'Janela'},
            title="Retenção de Clientes (M3, M6 e M12 por Safra)",
            color_discrete_sequence=['#6baed6', '#3182bd', '#08519c']
        )
        fig_cohort_logo.update_layout(height=400)
        st.plotly_chart(fig_cohort_logo, use_container_width=True)
        
    with col_b:
        st.subheader("Net Revenue Retention M12 por Safra (%)")
        fig_cohort_nrr = px.line(
            df_cohort_annual,
            x='cohort_year',
            y='revenue_ret_m12_nrr_pct',
            markers=True,
            title="Evolução do NRR aos 12 Meses (Queda Crítica em 2025)",
            labels={'revenue_ret_m12_nrr_pct': 'NRR M12 (%)', 'cohort_year': 'Safra'}
        )
        fig_cohort_nrr.add_hline(y=100, line_dash="dash", line_color="green", annotation_text="Break-even (100%)")
        fig_cohort_nrr.update_layout(height=400)
        st.plotly_chart(fig_cohort_nrr, use_container_width=True)
        
    st.markdown("---")
    st.subheader("Tabela Completa de Coortes Anuais")
    st.dataframe(df_cohort_annual.style.format({
        'total_initial_mrr': '${:,.2f}',
        'logo_ret_m3_pct': '{:.1f}%',
        'logo_ret_m6_pct': '{:.1f}%',
        'logo_ret_m12_pct': '{:.1f}%',
        'revenue_ret_m12_nrr_pct': '{:.1f}%'
    }), use_container_width=True)
    
    st.info("💡 **Alerta Executivo:** A safra de 2025 despencou para 41,7% de retenção de clientes e 68,3% de NRR após 12 meses, contrastando com safras pré-2025 que mantinham >83% de retenção e >118% de NRR.")

# ==============================================================================
# PÁGINA 3: DIAGNÓSTICO DE PRODUTO & SUPORTE
# ==============================================================================
elif selected_page == "3. Diagnóstico de Produto & Suporte":
    st.title("🔍 Diagnóstico de Atrito: Produto & Atendimento")
    st.markdown("Cruzamento das causas que explicam o paradoxo do CEO: estabilidade de produto vs experiência de suporte.")
    
    tab1, tab2 = st.tabs(["Falhas de Produto & Features", "Gargalos de Suporte"])
    
    with tab1:
        st.subheader("Ranking de Erros por Funcionalidade")
        df_features = con.execute("""
            SELECT 
                feature_name,
                is_beta_feature,
                sum(usage_count) as total_usage,
                sum(error_count) as total_errors,
                round(sum(error_count) * 100.0 / nullif(sum(usage_count), 0), 2) as error_rate_pct,
                round(avg(usage_duration_secs), 1) as avg_duration_secs
            FROM gold.fato_eventos_uso
            GROUP BY feature_name, is_beta_feature
            ORDER BY total_errors DESC
            LIMIT 15
        """).df()
        
        fig_err = px.bar(
            df_features,
            x='feature_name',
            y='total_errors',
            color='is_beta_feature',
            labels={'total_errors': 'Total de Erros', 'feature_name': 'Funcionalidade', 'is_beta_feature': 'Feature Beta'},
            title="Top 15 Features com Maior Volume de Erros",
            color_discrete_map={True: '#d62728', False: '#1f77b4'}
        )
        st.plotly_chart(fig_err, use_container_width=True)
        st.dataframe(df_features, use_container_width=True)
        
    with tab2:
        st.subheader("Métricas de Atendimento por Tier de Plano")
        df_tickets = con.execute("""
            SELECT 
                plan_tier,
                count(*) as total_tickets,
                round(avg(resolution_time_hours), 1) as avg_resolution_hours,
                round(avg(first_response_time_minutes), 1) as avg_first_resp_min,
                round(avg(satisfaction_score), 2) as avg_csat,
                count(CASE WHEN escalation_flag THEN 1 END) as escalated_tickets
            FROM gold.fato_atendimento
            GROUP BY plan_tier
            ORDER BY total_tickets DESC
        """).df()
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.dataframe(df_tickets, use_container_width=True)
        with col_t2:
            fig_csat = px.pie(
                con.execute("SELECT csat_tier, count(*) as cnt FROM gold.fato_atendimento GROUP BY csat_tier").df(),
                values='cnt', names='csat_tier',
                title="Distribuição de Avaliações CSAT",
                color_discrete_sequence=['#2ca02c', '#1f77b4', '#d62728', '#7f7f7f']
            )
            st.plotly_chart(fig_csat, use_container_width=True)

# ==============================================================================
# PÁGINA 4: ALERTA DE RISCO & SIMULADOR
# ==============================================================================
elif selected_page == "4. Alerta de Risco & Simulador":
    st.title("🚨 Radar de Risco de Churn & Simulador de Impacto")
    st.markdown("Identificação nominal de contas em risco e simulação financeira de retenção para tomada de decisão.")
    
    # Resumo das Contas em Risco
    df_health = con.execute("SELECT * FROM gold.agg_account_health_score WHERE is_currently_active = true").df()
    
    c1, c2, c3 = st.columns(3)
    red_count = len(df_health[df_health['risk_tier'].str.contains('Vermelho')])
    red_arr = df_health[df_health['risk_tier'].str.contains('Vermelho')]['arr_at_risk'].sum()
    yellow_count = len(df_health[df_health['risk_tier'].str.contains('Amarelo')])
    green_count = len(df_health[df_health['risk_tier'].str.contains('Verde')])
    
    with c1:
        st.error(f"🔴 **Crítico (Risco Imediato):** {red_count} contas\n\n**ARR em Risco:** ${red_arr:,.2f}")
    with c2:
        st.warning(f"🟡 **Atenção:** {yellow_count} contas\n\nMonitoramento ativo")
    with c3:
        st.success(f"🟢 **Saudável:** {green_count} contas\n\nOperação normal")
        
    st.markdown("---")
    
    # Simulador de Retenção
    st.subheader("Simulador de Retenção de Receita (ARR)")
    reduction_pct = st.slider("Se reduzirmos o churn atual em (%):", min_value=5, max_value=50, value=20, step=5)
    
    mrr_lost_recent_annual = 60490.00 * 12 # Projeção de perdas anuais com base em 2025
    arr_saved = (red_arr * (reduction_pct / 100.0))
    
    st.metric(
        f"ARR Preservado com Redução de {reduction_pct}% no Churn",
        f"${arr_saved:,.2f}",
        f"+{reduction_pct}% Eficiência de Retenção"
    )
    
    # Filtro e Tabela Nominal das Contas
    st.subheader("Contas em Monitoramento Ativo")
    filter_plan = st.multiselect("Filtrar por Plano:", options=['Enterprise', 'Pro', 'Basic'], default=['Enterprise', 'Pro'])
    filter_tier = st.multiselect("Filtrar por Nível de Risco:", options=list(df_health['risk_tier'].unique()), default=['Vermelho (Crítico / Risco Alto)'])
    
    filtered_df = df_health[
        (df_health['plan_tier'].isin(filter_plan)) &
        (df_health['risk_tier'].isin(filter_tier))
    ][['account_name', 'plan_tier', 'industry', 'country', 'mrr_amount', 'health_score', 'total_errors', 'low_csat_tickets', 'escalated_tickets', 'risk_tier']]
    
    st.dataframe(filtered_df.style.format({
        'mrr_amount': '${:,.2f}'
    }), use_container_width=True)
