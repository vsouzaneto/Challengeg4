import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import json
import os

st.set_page_config(
    page_title="RavenStack — Diagnóstico de Churn & Cockpit Prescritivo",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Resolução dinâmica de caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "artifacts"))

CANDIDATE_DATA_DIRS = [
    os.path.abspath(os.path.join(BASE_DIR, "..", "..", "..", "..", "data", "churn")),
    os.path.abspath(os.path.join(BASE_DIR, "..", "..", "..", "data", "churn")),
    os.path.abspath(os.path.join(BASE_DIR, "..", "data", "churn")),
    "/Users/montinegro/G4 AI Master/data/churn",
    "/Users/montinegro/G4 AI Master/repo/data/churn"
]
DATA_DIR = next((d for d in CANDIDATE_DATA_DIRS if os.path.exists(d) and os.path.exists(os.path.join(d, "ravenstack_accounts.csv"))), CANDIDATE_DATA_DIRS[0])

@st.cache_data
def load_all_data():
    scores_path = os.path.join(ARTIFACTS_DIR, "ravenstack_account_risk_scores.csv")
    analytics_json_path = os.path.join(ARTIFACTS_DIR, "advanced_analytics.json")
    accounts_path = os.path.join(DATA_DIR, "ravenstack_accounts.csv")
    
    df_scores = pd.read_csv(scores_path)
    if os.path.exists(accounts_path):
        df_acc = pd.read_csv(accounts_path)
        if 'referral_source' in df_acc.columns and 'referral_source' not in df_scores.columns:
            df_scores = df_scores.merge(df_acc[['account_id', 'referral_source']], on='account_id', how='left')
            
    with open(analytics_json_path, 'r', encoding='utf-8') as f:
        analytics = json.load(f)
        
    df_monthly = pd.DataFrame(analytics['monthly_timeline'])
    df_quadrants = pd.DataFrame(analytics['quadrants_summary'])
    df_reasons = pd.DataFrame(analytics['churn_reasons'])
    df_feedback = pd.DataFrame(analytics['feedback_frequencies'])
    df_contracts = pd.DataFrame(analytics['contracts_breakdown'])
    df_benchmark = pd.DataFrame(analytics['retention_benchmark'])
    
    return df_scores, df_monthly, df_quadrants, df_reasons, df_feedback, df_contracts, df_benchmark

df_scores, df_monthly, df_quadrants, df_reasons, df_feedback, df_contracts, df_benchmark = load_all_data()

# ------------------------------------------------------------------------------
# SIDEBAR: CONFIGURAÇÕES & LOCALIZAÇÃO
# ------------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=64)
    st.markdown("### **Configurações Globais**")
    
    currency_mode = st.radio(
        "Moeda de Exibição:",
        ["Dólar Americano (USD $)", "Real Brasileiro (BRL R$)"],
        help="A base de dados oficial RavenStack foi gerada em USD. O modo BRL utiliza taxa de câmbio referencial PTAX de R$ 5,50."
    )
    cambio = 5.50 if "BRL" in currency_mode else 1.0
    simbolo = "R$ " if "BRL" in currency_mode else "$ "
    
    st.markdown("---")
    st.markdown("### **Metadados do Projeto**")
    st.caption("**Squad:** Montinegro Consultoria")
    st.caption("**Arquiteto Líder:** Altman (Codex CLI)")
    st.caption("**Orquestrador:** Japax (Antigravity)")
    st.caption("**Repositório:** `branch: submission/adailton-montinegro`")
    st.caption("**Governança:** Taiga ID 3 (Épico 03)")
    st.info("💡 **Nota de Formatação:** Todos os separadores decimais e numéricos seguem a convenção executiva brasileira.")

def fmt_money(val):
    val_conv = val * cambio
    return f"{simbolo}{val_conv:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_num(val):
    return f"{val:,.0f}".replace(",", ".")

# ------------------------------------------------------------------------------
# HEADER EXECUTIVO & KPI CARDS (SEMÁFORO RIGOROSO)
# ------------------------------------------------------------------------------
st.title("🦅 RavenStack — Diagnóstico Causal de Churn & Cockpit Prescritivo")
st.markdown(f"**Visão Executiva C-Level** | Análise Factual de 24 Meses, Desmistificação de Vieses e Matriz de Quadrantes | Valores expressos em **{currency_mode}**")

total_accs = len(df_scores)
churned_accs = int(df_scores['churn_flag'].sum())
active_accs = total_accs - churned_accs
active_mrr = float(df_scores[~df_scores['churn_flag']]['latest_mrr'].sum())
lost_mrr = float(df_scores[df_scores['churn_flag']]['latest_mrr'].sum())

kpi_html = f"""
<div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin-bottom: 24px;">
    <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 16px;">
        <div style="font-size: 12px; color: #94a3b8; font-weight: 600; text-transform: uppercase;">Total de Contas</div>
        <div style="font-size: 26px; font-weight: 700; color: #f8fafc; margin-top: 4px;">{fmt_num(total_accs)}</div>
        <div style="font-size: 12px; color: #38bdf8; margin-top: 4px;">Base 100% Auditada</div>
    </div>
    <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 16px;">
        <div style="font-size: 12px; color: #94a3b8; font-weight: 600; text-transform: uppercase;">Contas Ativas</div>
        <div style="font-size: 26px; font-weight: 700; color: #f8fafc; margin-top: 4px;">{fmt_num(active_accs)}</div>
        <div style="font-size: 12px; color: #34d399; font-weight: 600; margin-top: 4px;">▲ {active_accs/total_accs:.1%} da base</div>
    </div>
    <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 16px;">
        <div style="font-size: 12px; color: #94a3b8; font-weight: 600; text-transform: uppercase;">Logo Churn Acumulado</div>
        <div style="font-size: 26px; font-weight: 700; color: #f43f5e; margin-top: 4px;">{fmt_num(churned_accs)}</div>
        <div style="font-size: 12px; color: #f43f5e; font-weight: 600; margin-top: 4px;">▼ {churned_accs/total_accs:.1%} de perda</div>
    </div>
    <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 16px;">
        <div style="font-size: 12px; color: #94a3b8; font-weight: 600; text-transform: uppercase;">MRR Ativo Mensal</div>
        <div style="font-size: 26px; font-weight: 700; color: #f8fafc; margin-top: 4px;">{fmt_money(active_mrr)}</div>
        <div style="font-size: 12px; color: #34d399; font-weight: 600; margin-top: 4px;">▲ {fmt_money(active_mrr*12)} ARR</div>
    </div>
    <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 16px;">
        <div style="font-size: 12px; color: #94a3b8; font-weight: 600; text-transform: uppercase;">MRR Perdido (Churn)</div>
        <div style="font-size: 26px; font-weight: 700; color: #f43f5e; margin-top: 4px;">{fmt_money(lost_mrr)}</div>
        <div style="font-size: 12px; color: #f43f5e; font-weight: 600; margin-top: 4px;">▼ -{fmt_money(lost_mrr*12)} ARR</div>
    </div>
</div>
"""
st.markdown(kpi_html, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# NAVEGAÇÃO EM ABAS
# ------------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 1. Visão Executiva & Desmistificação Causal",
    "🎯 2. Matriz Cartesiana de Quadrantes",
    "💬 3. Motivos de Churn & Feedbacks",
    "🛡️ 4. Benchmark de Clientes Retidos (ICP)",
    "📋 5. Cockpit Prescritivo de CS",
    "💡 6. Simulador Financeiro & Metodologia"
])

# ==============================================================================
# TAB 1: VISÃO EXECUTIVA & DESMISTIFICAÇÃO CAUSAL
# ==============================================================================
with tab1:
    st.subheader("1. Desmistificando os Paradoxos do CEO")
    
    col1a, col1b = st.columns(2)
    
    with col1a:
        st.markdown("#### **Paradoxo do Produto: O Uso Realmente Cresceu?**")
        st.caption("Evolução Mensal Contínua (24 Meses) de Eventos de Churn vs Uso Médio por Conta Ativa")
        
        base_m = alt.Chart(df_monthly).encode(x=alt.X('year_month:N', title='Mês (2023-01 a 2024-12)', axis=alt.Axis(labelAngle=-45)))
        
        bar_churn_m = base_m.mark_bar(color='#f43f5e', opacity=0.85).encode(
            y=alt.Y('churn_events:Q', title='Eventos de Churn (Barras Vermelhas)'),
            tooltip=['year_month', 'churn_events', 'usage_per_active_account', 'total_usage']
        )
        
        line_usage_m = base_m.mark_line(color='#38bdf8', strokeWidth=3, point=alt.OverlayMarkDef(color='#38bdf8', size=40)).encode(
            y=alt.Y('usage_per_active_account:Q', title='Uso Médio por Conta Ativa (Linha Azul)', scale=alt.Scale(domain=[0, 35]), axis=alt.Axis(orient='right')),
            tooltip=['year_month', 'usage_per_active_account']
        )
        
        chart_trend = alt.layer(bar_churn_m, line_usage_m).resolve_scale(y='independent')
        st.altair_chart(chart_trend, use_container_width=True)
        
        st.info("""
        🔬 **Evidência Factual Inegável:**
        - **O uso não despencou e não cresceu:** O uso médio por conta ativa foi matematicamente **estável entre 23,0 e 26,7 usos/mês** durante os 24 meses inteiros.
        - **A ilusão da diretoria de produto:** A sensação de crescimento decorreu de oscilações nominais de final de ano (+2,6%), mas a média per capita é constante.
        - **Aceleração exponencial de churn:** Os cancelamentos saíram de **1 em Jan/2023** para **117 em Dez/2024**. O churn é **descolado do volume de uso**.
        """)

    with col1b:
        st.markdown("#### **Paradoxo do Suporte: O CSAT Está Realmente Saudável?**")
        st.caption("Taxa de Escalação de Chamados e Nota de Satisfação na Janela Pré-Cancelamento")
        
        df_esc_view = pd.DataFrame({
            'Janela': ['60+ dias antes (Normal)', '31-60 dias antes', '15-30 dias antes', '0-14 dias antes (Gatilho Fatal)'],
            'Taxa de Escalação (%)': [5.0, 4.1, 4.5, 14.6],
            'Nota Média Satisfação (1-5)': [3.98, 4.03, 4.00, 4.03]
        })
        
        chart_esc_v = alt.Chart(df_esc_view).mark_bar().encode(
            x=alt.X('Janela:N', sort=None, title='Janela Temporal Retrospectiva até o Cancelamento', axis=alt.Axis(labelAngle=-15)),
            y=alt.Y('Taxa de Escalação (%):Q', title='Taxa de Chamados Escalados (%)'),
            color=alt.condition(
                alt.datum['Taxa de Escalação (%)'] > 10,
                alt.value('#f43f5e'),
                alt.value('#38bdf8')
            ),
            tooltip=['Janela', 'Taxa de Escalação (%)', 'Nota Média Satisfação (1-5)']
        )
        st.altair_chart(chart_esc_v, use_container_width=True)
        
        st.warning("""
        ⚠️ **O Viés do Sobrevivente no Suporte:**
        - **41,2% dos chamados não possuem nota (825 de 2.000 tickets):** Clientes severamente frustrados simplesmente não avaliam o suporte.
        - **O sinal fatal:** Nas duas semanas imediatamente anteriores ao cancelamento (0 a 14 dias), a taxa de escalação de chamados **salta de 4,5% para 14,6% (mais que o triplo)**.
        - **Causa Raiz Operacional:** Incidentes graves não resolvidos na primeira linha foram o gatilho final que culminou no cancelamento.
        """)

    st.markdown("---")
    
    col1c, col1d = st.columns(2)
    with col1c:
        st.markdown("#### **Taxa de Churn por Vertical de Indústria**")
        df_ind_c = df_scores.groupby('industry')['churn_flag'].agg(contas='count', churn_rate='mean').reset_index()
        df_ind_c['churn_pct'] = df_ind_c['churn_rate'] * 100
        
        c_ind = alt.Chart(df_ind_c).mark_bar().encode(
            x=alt.X('churn_pct:Q', title='Taxa de Churn (%)'),
            y=alt.Y('industry:N', sort='-x', title='Vertical'),
            color=alt.condition(alt.datum.churn_pct > 25, alt.value('#f43f5e'), alt.value('#38bdf8')),
            tooltip=['industry', 'contas', alt.Tooltip('churn_pct:Q', format='.1f')]
        )
        st.altair_chart(c_ind, use_container_width=True)
        st.caption("DevTools lidera com 31,0% de cancelamentos devido à alta intolerância técnica a instabilidades e features beta com erro.")
        
    with col1d:
        st.markdown("#### **Taxa de Churn por Canal de Aquisição**")
        df_ref_c = df_scores.groupby('referral_source')['churn_flag'].agg(contas='count', churn_rate='mean').reset_index()
        df_ref_c['churn_pct'] = df_ref_c['churn_rate'] * 100
        
        c_ref = alt.Chart(df_ref_c).mark_bar().encode(
            x=alt.X('churn_pct:Q', title='Taxa de Churn (%)'),
            y=alt.Y('referral_source:N', sort='-x', title='Canal'),
            color=alt.condition(alt.datum.churn_pct > 25, alt.value('#f43f5e'), alt.value('#34d399')),
            tooltip=['referral_source', 'contas', alt.Tooltip('churn_pct:Q', format='.1f')]
        )
        st.altair_chart(c_ref, use_container_width=True)
        st.caption("Eventos (30,2%) e Ads (23,5%) trazem contas frágeis; Parcerias (14,6%) é o canal com maior retenção e LTV.")

# ==============================================================================
# TAB 2: MATRIZ CARTESIANA DE QUADRANTES (SCATTER PLOT)
# ==============================================================================
with tab2:
    st.subheader("2. Matriz Cartesiana de Quadrantes: Segmentação Estratégica da Base")
    st.markdown("Distribuição das 500 contas por **MRR Mensal (Impacto Financeiro)** vs **Score de Risco de Churn (Probabilidade)**.")
    
    col2a, col2b = st.columns([3, 2])
    
    with col2a:
        scatter = alt.Chart(df_scores).mark_circle().encode(
            x=alt.X('churn_risk_score:Q', title='Score de Risco de Churn (0 a 1.0)', scale=alt.Scale(domain=[0.1, 0.9])),
            y=alt.Y('latest_mrr:Q', title=f'MRR da Conta ({simbolo})', scale=alt.Scale(domain=[0, 24000])),
            size=alt.Size('seats:Q', title='Licenças (Seats)', scale=alt.Scale(range=[30, 400])),
            color=alt.Color('quadrant:N', title='Quadrante Estratégico', scale=alt.Scale(
                domain=[
                    'Q1: Zona Crítica (Alto MRR + Alto Risco)',
                    'Q2: Cauda Vulnerável (Baixo MRR + Alto Risco)',
                    'Q3: Vacas Leiteiras (Alto MRR + Baixo Risco)',
                    'Q4: Base Estável (Baixo MRR + Baixo Risco)'
                ],
                range=['#f43f5e', '#fb923c', '#059669', '#38bdf8']
            )),
            tooltip=['account_name', 'account_id', 'industry', 'plan_tier', 'latest_mrr', 'churn_risk_score', 'quadrant']
        ).properties(height=480)
        
        # Linhas divisórias cartesianas
        rule_x = alt.Chart(pd.DataFrame({'x': [0.40]})).mark_rule(color='#64748b', strokeDash=[4, 4]).encode(x='x:Q')
        rule_y = alt.Chart(pd.DataFrame({'y': [1500]})).mark_rule(color='#64748b', strokeDash=[4, 4]).encode(y='y:Q')
        
        st.altair_chart(scatter + rule_x + rule_y, use_container_width=True)

    with col2b:
        st.markdown("#### **Resumo Executivo dos 4 Quadrantes**")
        
        for _, q in df_quadrants.iterrows():
            badge_color = "#f43f5e" if "Q1" in q['quadrant'] else ("#fb923c" if "Q2" in q['quadrant'] else ("#059669" if "Q3" in q['quadrant'] else "#38bdf8"))
            st.markdown(f"""
            <div style="background: #1e293b; border-left: 4px solid {badge_color}; padding: 10px 14px; margin-bottom: 10px; border-radius: 4px;">
                <div style="font-weight: 700; color: #f8fafc; font-size: 14px;">{q['quadrant']}</div>
                <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">
                    Contas: <strong>{q['contas']}</strong> | MRR Total: <strong>{fmt_money(q['mrr_total'])}</strong> | Ticket Médio: <strong>{fmt_money(q['mrr_medio'])}</strong>
                </div>
                <div style="font-size: 12px; color: {badge_color}; margin-top: 2px;">
                    Histórico de Churn: <strong>{q['churn_rate']}%</strong> | Escalações Médias: <strong>{q['escalacoes_medias']}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.info("💡 **Decisão Prescritiva:** O foco de choque imediato deve ser o **Q1 (Zona Crítica)**, onde 102 contas concentram **$462.530/mês de MRR** em risco direto.")

# ==============================================================================
# TAB 3: MOTIVOS DE CHURN & FEEDBACKS
# ==============================================================================
with tab3:
    st.subheader("3. Análise Qualitativa: Motivos Declarados e Feedbacks (600 Cancelamentos)")
    st.markdown("Decomposição dos `reason_codes`, solicitações de reembolso e precedentes de downgrade/upgrade.")
    
    col3a, col3b = st.columns(2)
    
    with col3a:
        st.markdown("#### **Motivos de Cancelamento (Reason Codes)**")
        c_reasons = alt.Chart(df_reasons).mark_bar(color='#38bdf8').encode(
            x=alt.X('event_count:Q', title='Volume de Cancelamentos'),
            y=alt.Y('reason_code:N', sort='-x', title='Motivo Declarado'),
            tooltip=['reason_code', 'event_count', 'pct_events', 'total_refund', 'preceded_by_downgrade', 'reactivations']
        )
        st.altair_chart(c_reasons, use_container_width=True)
        
        st.markdown(f"""
        - **Features (19,0%):** 114 cancelamentos com {fmt_money(df_reasons[df_reasons['reason_code']=='features']['total_refund'].values[0])} em reembolsos.
        - **Suporte (17,3%):** 104 cancelamentos diretamente atribuídos ao atendimento.
        - **Orçamento / Preço (32,5% combinado):** Budget e Pricing somam 195 eventos.
        """)

    with col3b:
        st.markdown("#### **Frequência dos Textos de Feedback**")
        c_feed = alt.Chart(df_feedback).mark_bar(color='#fb923c').encode(
            x=alt.X('occurrences:Q', title='Ocorrências'),
            y=alt.Y('feedback:N', sort='-x', title='Texto do Cliente'),
            tooltip=['feedback', 'occurrences', 'pct_total']
        )
        st.altair_chart(c_feed, use_container_width=True)
        
        st.markdown("""
        - **"too expensive" (26,8%):** 161 menções explícitas de percepção de preço desajustado.
        - **"missing features" (25,8%):** 155 menções de funcionalidades faltantes ou incompletas.
        - **"switched to competitor" (22,7%):** 136 clientes migraram diretamente para soluções rivais.
        """)

    st.markdown("---")
    st.markdown("#### **Padrões de Comportamento Precedente ao Churn**")
    cp1, cp2, cp3 = st.columns(3)
    with cp1:
        st.metric("Reativações Prévias", "10,0%", help="Contas que já haviam cancelado no passado e cancelaram novamente.")
    with cp2:
        st.metric("Precedidos por Downgrade", "10,0%", help="Contas que reduziram o plano nos 90 dias anteriores ao cancelamento fatal.")
    with cp3:
        st.metric("Total em Reembolsos", fmt_money(df_reasons['total_refund'].sum()), help="Reembolsos emitidos no momento do cancelamento.")

# ==============================================================================
# TAB 4: BENCHMARK DE CLIENTES RETIDOS (ICP SAUDÁVEL) & CONTRATOS
# ==============================================================================
with tab4:
    st.subheader("4. O que Deu Certo: Benchmark das 390 Contas Retidas")
    st.markdown("Comparativo estruturado entre as contas que permanecem fiéis e as que cancelaram, definindo o Perfil de Cliente Ideal (ICP).")
    
    col4a, col4b = st.columns(2)
    
    with col4a:
        st.markdown("#### **Contas Retidas (390) vs Contas Canceladas (110)**")
        df_bench_display = pd.DataFrame([
            {"Métrica": "MRR Médio por Conta", "Retidas (Ativas)": fmt_money(2520.38), "Canceladas": fmt_money(2322.20)},
            {"Métrica": "Licenças Médias (Seats)", "Retidas (Ativas)": "20,9 licenças", "Canceladas": "19,2 licenças"},
            {"Métrica": "Taxa de Erro em Features", "Retidas (Ativas)": "5,72%", "Canceladas": "5,39%"},
            {"Métrica": "Contratos Anuais (% Lock-in)", "Retidas (Ativas)": "54,6%", "Canceladas": "61,8%"},
            {"Métrica": "Auto-Renovação Ligada", "Retidas (Ativas)": "82,8%", "Canceladas": "82,7%"},
            {"Métrica": "Origem via Canal de Parceiros", "Retidas (Ativas)": "19,5%", "Canceladas": "11,8% (Baixa)"},
            {"Métrica": "Escalações Médias de Suporte", "Retidas (Ativas)": "0,18 chamados", "Canceladas": "0,22 chamados"}
        ])
        st.table(df_bench_display)

    with col4b:
        st.markdown("#### **Análise de Contratos: Anual vs Mensal e Auto-Renovação**")
        st.caption("Distribuição de Churn em 5.000 Assinaturas por Modelo de Contratação")
        
        df_contracts_clean = df_contracts[~df_contracts['is_trial']].copy()
        df_contracts_clean['modelo'] = df_contracts_clean['billing_frequency'].str.capitalize() + " (Auto-renew: " + df_contracts_clean['auto_renew_flag'].astype(str) + ")"
        
        c_cont = alt.Chart(df_contracts_clean).mark_bar(color='#34d399').encode(
            x=alt.X('churn_rate_pct:Q', title='Taxa de Churn (%)'),
            y=alt.Y('modelo:N', sort='-x', title='Modelo de Faturamento'),
            tooltip=['modelo', 'total_subs', 'churned_subs', 'churn_rate_pct', 'avg_mrr']
        )
        st.altair_chart(c_cont, use_container_width=True)
        st.info("💡 **Insight de Proteção:** Clientes trazidos por **Parcerias Estratégicas** têm retenção 65% superior aos clientes captados por Eventos. A retenção depende de qualificação na entrada.")

# ==============================================================================
# TAB 5: COCKPIT PRESCRITIVO DE CS
# ==============================================================================
with tab5:
    st.subheader("5. Cockpit Prescritivo de Customer Success (Ações por Conta)")
    st.markdown("Filtre as contas ativas prioritárias e execute os playbooks recomendados antes da janela fatal de cancelamento.")
    
    col5a, col5b, col5c = st.columns(3)
    with col5a:
        filtro_quadrante = st.multiselect(
            "Filtrar por Quadrante:",
            options=df_scores['quadrant'].unique(),
            default=['Q1: Zona Crítica (Alto MRR + Alto Risco)']
        )
    with col5b:
        filtro_plano = st.multiselect("Plano:", options=df_scores['plan_tier'].unique(), default=df_scores['plan_tier'].unique())
    with col5c:
        filtro_apenas_ativas = st.checkbox("Exibir apenas contas ativas (Foco em Retenção)", value=True)
        
    df_view_cs = df_scores.copy()
    if filtro_quadrante:
        df_view_cs = df_view_cs[df_view_cs['quadrant'].isin(filtro_quadrante)]
    if filtro_plano:
        df_view_cs = df_view_cs[df_view_cs['plan_tier'].isin(filtro_plano)]
    if filtro_apenas_ativas:
        df_view_cs = df_view_cs[~df_view_cs['churn_flag']]
        
    mrr_filtro = df_view_cs['latest_mrr'].sum()
    st.markdown(f"**Contas Selecionadas:** `{len(df_view_cs)}` | **MRR Sob Gestão:** `{fmt_money(mrr_filtro)}` (`{fmt_money(mrr_filtro*12)} ARR`)")
    
    st.dataframe(
        df_view_cs[['account_name', 'account_id', 'industry', 'plan_tier', 'latest_mrr', 'churn_risk_score', 'quadrant', 'recommended_action', 'total_escalations', 'avg_frt_minutes']],
        use_container_width=True,
        column_config={
            "latest_mrr": st.column_config.NumberColumn(f"MRR ({simbolo})", format=f"{simbolo}%.2f"),
            "churn_risk_score": st.column_config.ProgressColumn("Score Risco", min_value=0, max_value=1, format="%.2f"),
            "total_escalations": st.column_config.NumberColumn("Escalações", format="%d"),
            "avg_frt_minutes": st.column_config.NumberColumn("FRT (min)", format="%.0f min")
        },
        hide_index=True
    )
    
    csv_export = df_view_cs.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Exportar Lista de Contas para Operação de CS (CSV)",
        data=csv_export,
        file_name="ravenstack_cockpit_prioridades_cs.csv",
        mime="text/csv"
    )

# ==============================================================================
# TAB 6: SIMULADOR DE ROI & NOTA METODOLÓGICA
# ==============================================================================
with tab6:
    st.subheader("6. Simulador Financeiro de Retenção & Metodologia")
    
    col6a, col6b = st.columns(2)
    with col6a:
        st.markdown("#### **Simulador de Preservação de Receita**")
        meta_ent = st.slider("Preservação de Churn em Enterprise (%)", 0, 80, 35, 5)
        meta_pro = st.slider("Preservação de Churn em Pro (%)", 0, 80, 25, 5)
        custo_squad = st.number_input(f"Investimento Anual na Squad de Resiliência & CS ({simbolo})", value=int(120000 * cambio), step=int(10000 * cambio))
        
        ent_churn_mrr = df_scores[(df_scores['churn_flag']) & (df_scores['plan_tier'] == 'Enterprise')]['latest_mrr'].sum()
        pro_churn_mrr = df_scores[(df_scores['churn_flag']) & (df_scores['plan_tier'] == 'Pro')]['latest_mrr'].sum()
        
        mrr_salvo = (ent_churn_mrr * (meta_ent/100.0)) + (pro_churn_mrr * (meta_pro/100.0))
        arr_salvo = mrr_salvo * 12 * cambio
        retorno_liq = arr_salvo - custo_squad
        roi = (retorno_liq / custo_squad) * 100 if custo_squad > 0 else 0
        
    with col6b:
        st.markdown("#### **Resultado Econômico Projetado**")
        st.metric("ARR Anual Preservado", f"{simbolo}{arr_salvo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.metric("Retorno Líquido Anual (ARR - Investimento)", f"{simbolo}{retorno_liq:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), delta=f"{roi:.0f}% ROI")
        st.success(f"Preservar {meta_ent}% dos clientes Enterprise que cancelariam paga toda a operação em {custo_squad / (mrr_salvo*cambio):.1f} meses.")

    st.markdown("---")
    st.markdown("#### **Nota Metodológica e Conciliação de Dados (DuckDB)**")
    audit_display = pd.DataFrame([
        {"Entidade": "ravenstack_accounts.csv", "Volume": "500 contas", "Chave Primária": "account_id (100% único)", "Integridade": "0 órfãos", "Auditoria": "100% Consistente"},
        {"Entidade": "ravenstack_subscriptions.csv", "Volume": "5.000 assinaturas", "Chave Primária": "subscription_id (100% único)", "Integridade": "0 órfãos", "Auditoria": "Regra ARR == MRR * 12 (0 desvios)"},
        {"Entidade": "ravenstack_feature_usage.csv", "Volume": "25.000 logs", "Chave Primária": "usage_id", "Integridade": "0 órfãos", "Auditoria": "Uso médio constante em 24,6/mês"},
        {"Entidade": "ravenstack_support_tickets.csv", "Volume": "2.000 tickets", "Chave Primária": "ticket_id (100% único)", "Integridade": "0 órfãos", "Auditoria": "41,2% sem nota (Viés mapeado)"},
        {"Entidade": "ravenstack_churn_events.csv", "Volume": "600 eventos", "Chave Primária": "churn_event_id (100% único)", "Integridade": "0 órfãos", "Auditoria": "10% reativações e 10% downgrades"}
    ])
    st.table(audit_display)

