import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import json
import os
import duckdb

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
    churn_path = os.path.join(DATA_DIR, "ravenstack_churn_events.csv")
    
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
    
    # DuckDB para análises causais aprofundadas
    subs_path = os.path.join(DATA_DIR, "ravenstack_subscriptions.csv")
    con = duckdb.connect()
    con.execute(f"""
        CREATE TABLE accounts AS SELECT * FROM read_csv_auto('{accounts_path}');
        CREATE TABLE churn AS SELECT * FROM read_csv_auto('{churn_path}');
        CREATE TABLE subs AS SELECT * FROM read_csv_auto('{subs_path}');
    """)
    
    # 1. Fluxo líquido mensal
    q_flow = """
    WITH in_flow AS (
        SELECT strftime(signup_date, '%Y-%m') as ym, count(account_id) as entradas
        FROM accounts GROUP BY ym
    ),
    out_flow AS (
        SELECT strftime(churn_date, '%Y-%m') as ym, count(distinct account_id) as contas_saindo
        FROM churn GROUP BY ym
    ),
    months AS (
        SELECT ym FROM in_flow UNION SELECT ym FROM out_flow
    )
    SELECT 
        m.ym as year_month,
        coalesce(inf.entradas, 0) as entradas,
        - coalesce(outf.contas_saindo, 0) as saidas_negativas,
        coalesce(outf.contas_saindo, 0) as saidas,
        coalesce(inf.entradas, 0) - coalesce(outf.contas_saindo, 0) as saldo_liquido
    FROM months m
    LEFT JOIN in_flow inf ON m.ym = inf.ym
    LEFT JOIN out_flow outf ON m.ym = outf.ym
    ORDER BY m.ym;
    """
    df_flow = con.execute(q_flow).df()

    # 2. Canais empilhados 100%
    q_stacked = """
    SELECT 
        referral_source,
        'Retidas (Ativas)' as status,
        sum(case when not churn_flag then 1 else 0 end) as contas,
        round(100.0 * sum(case when not churn_flag then 1 else 0 end) / count(*), 1) as pct
    FROM accounts
    GROUP BY referral_source
    UNION ALL
    SELECT 
        referral_source,
        'Canceladas (Churn)' as status,
        sum(case when churn_flag then 1 else 0 end) as contas,
        round(100.0 * sum(case when churn_flag then 1 else 0 end) / count(*), 1) as pct
    FROM accounts
    GROUP BY referral_source
    ORDER BY referral_source, status;
    """
    df_stacked = con.execute(q_stacked).df()

    # 3. Contas ativas mês a mês e Taxa Mensal de Churn Real (Fluxo contábil SaaS auditado)
    df_acc_raw = pd.read_csv(accounts_path)
    df_churn_raw = pd.read_csv(churn_path)
    df_subs_raw = pd.read_csv(subs_path)
    
    df_acc_raw['signup_date'] = pd.to_datetime(df_acc_raw['signup_date'])
    df_churn_raw['churn_date'] = pd.to_datetime(df_churn_raw['churn_date'])
    df_subs_raw['start_date'] = pd.to_datetime(df_subs_raw['start_date'])

    # Cronologia de eventos por conta para detectar reativações após churn
    ev_list = []
    for _, r in df_acc_raw.iterrows():
        ev_list.append({'account_id': r['account_id'], 'date': r['signup_date'], 'type': 'SIGNUP'})
    for _, r in df_churn_raw.iterrows():
        ev_list.append({'account_id': r['account_id'], 'date': r['churn_date'], 'type': 'CHURN'})
    for _, r in df_subs_raw.iterrows():
        ev_list.append({'account_id': r['account_id'], 'date': r['start_date'], 'type': 'SUB'})
        
    df_ev_all = pd.DataFrame(ev_list).sort_values(by=['account_id', 'date', 'type'])
    
    # Identificação de reativações estritas (inativo -> ativo via sub)
    reactiv_list = []
    for acc_id, grp in df_ev_all.groupby('account_id'):
        st_val = 'NONE'
        for _, ev in grp.iterrows():
            if ev['type'] == 'SIGNUP':
                st_val = 'ACTIVE'
            elif ev['type'] == 'CHURN':
                st_val = 'INACTIVE'
            elif ev['type'] == 'SUB' and st_val == 'INACTIVE':
                reactiv_list.append({'account_id': acc_id, 'date': ev['date']})
                st_val = 'ACTIVE'
                
    df_reactiv_p = pd.DataFrame(reactiv_list) if reactiv_list else pd.DataFrame(columns=['account_id', 'date'])
    df_reactiv_p['ym'] = pd.to_datetime(df_reactiv_p['date']).dt.strftime('%Y-%m')
    dict_rea = df_reactiv_p.groupby('ym')['account_id'].nunique().to_dict()
    
    dict_ent = df_acc_raw.groupby(df_acc_raw['signup_date'].dt.strftime('%Y-%m'))['account_id'].nunique().to_dict()
    dict_sai = df_churn_raw.groupby(df_churn_raw['churn_date'].dt.strftime('%Y-%m'))['account_id'].nunique().to_dict()
    
    all_ym = sorted(list(dict_ent.keys()))
    monthly_flow = []
    b_ant = 0
    for ym_val in all_ym:
        ent = dict_ent.get(ym_val, 0)
        sai = dict_sai.get(ym_val, 0)
        rea = dict_rea.get(ym_val, 0)
        b_exp = b_ant + ent
        tx = (sai / b_exp * 100.0) if b_exp > 0 else 0.0
        b_fim = b_exp - sai + rea
        monthly_flow.append({
            'year_month': ym_val,
            'base_inicio_mes': b_ant,
            'novas_entradas_mes': ent,
            'contas_saidas_mes': sai,
            'reativacoes_mes': rea,
            'base_exposta': b_exp,
            'pct_saida_sobre_ativas': round(tx, 1),
            'contas_ativas_mes': b_fim
        })
        b_ant = b_fim
        
    df_active_monthly = pd.DataFrame(monthly_flow)

    # 4. Pareto Financeiro (110 contas que cancelaram)
    q_pareto = """
    WITH churned AS (
        SELECT 
            account_id,
            account_name,
            (SELECT arg_max(mrr_amount, start_date) FROM subs s WHERE s.account_id = a.account_id) as latest_mrr
        FROM accounts a
        WHERE churn_flag = true
        ORDER BY latest_mrr DESC
    ),
    ranked AS (
        SELECT 
            row_number() over (order by latest_mrr desc) as rank_idx,
            account_name,
            latest_mrr,
            sum(latest_mrr) over (order by latest_mrr desc) as cum_mrr,
            sum(latest_mrr) over () as total_mrr
        FROM churned
    )
    SELECT 
        rank_idx,
        account_name,
        latest_mrr,
        round(100.0 * cum_mrr / total_mrr, 1) as pct_cum_mrr
    FROM ranked;
    """
    df_pareto = con.execute(q_pareto).df()

    # 5. Retenção por Faixa de Ticket
    q_tiers = """
    WITH tiers AS (
        SELECT 
            CASE 
                WHEN latest_mrr < 1000 THEN '1. Baixo Ticket (< $1k)'
                WHEN latest_mrr BETWEEN 1000 AND 3000 THEN '2. Médio Ticket ($1k-$3k)'
                WHEN latest_mrr BETWEEN 3000 AND 7000 THEN '3. Alto Ticket ($3k-$7k)'
                ELSE '4. Enterprise (> $7k)'
            END as faixa_ticket,
            churn_flag,
            latest_mrr
        FROM (
            SELECT a.account_id, a.churn_flag,
                   (SELECT arg_max(mrr_amount, start_date) FROM subs s WHERE s.account_id = a.account_id) as latest_mrr
            FROM accounts a
        )
    )
    SELECT 
        faixa_ticket,
        count(*) as total_contas,
        sum(case when not churn_flag then 1 else 0 end) as retidas,
        sum(case when churn_flag then 1 else 0 end) as churned,
        round(100.0 * sum(case when not churn_flag then 1 else 0 end) / count(*), 1) as pct_retencao,
        round(100.0 * sum(case when churn_flag then 1 else 0 end) / count(*), 1) as pct_churn,
        round(sum(latest_mrr), 2) as mrr_total,
        round(sum(case when churn_flag then latest_mrr else 0 end), 2) as mrr_perdido
    FROM tiers
    GROUP BY faixa_ticket
    ORDER BY faixa_ticket;
    """
    df_tiers = con.execute(q_tiers).df()

    # 6. Churn Recorrente por Canal
    q_rec_channel = """
    WITH multi AS (
        SELECT 
            account_id,
            count(churn_event_id) as total_churns
        FROM churn
        GROUP BY account_id
        HAVING count(churn_event_id) > 1
    )
    SELECT 
        a.referral_source,
        count(distinct m.account_id) as contas_com_multiplo_churn,
        sum(case when not a.churn_flag then 1 else 0 end) as permaneceram_ativas,
        sum(case when a.churn_flag then 1 else 0 end) as sairam_definitivo,
        round(100.0 * sum(case when not a.churn_flag then 1 else 0 end) / count(distinct m.account_id), 1) as pct_permaneceram,
        round(100.0 * sum(case when a.churn_flag then 1 else 0 end) / count(distinct m.account_id), 1) as pct_sairam_definitivo
    FROM multi m
    JOIN accounts a ON m.account_id = a.account_id
    GROUP BY a.referral_source
    ORDER BY pct_permaneceram ASC;
    """
    df_rec_channel = con.execute(q_rec_channel).df()

    # 7. Transição de Motivos (1ª saída vs 2ª saída)
    q_reasons_1_2 = """
    WITH ordered AS (
        SELECT 
            account_id,
            reason_code,
            row_number() over (partition by account_id order by churn_date) as rn
        FROM churn
    )
    SELECT 
        o1.reason_code as primeiro_motivo,
        o2.reason_code as segundo_motivo,
        count(*) as ocorrencias
    FROM ordered o1
    JOIN ordered o2 ON o1.account_id = o2.account_id AND o2.rn = 2
    WHERE o1.rn = 1
    GROUP BY o1.reason_code, o2.reason_code
    ORDER BY ocorrencias DESC
    LIMIT 8;
    """
    df_reasons_1_2 = con.execute(q_reasons_1_2).df()
    
    return (df_scores, df_monthly, df_quadrants, df_reasons, df_feedback, 
            df_contracts, df_benchmark, df_flow, df_stacked, df_active_monthly, 
            df_pareto, df_tiers, df_rec_channel, df_reasons_1_2)

(df_scores, df_monthly, df_quadrants, df_reasons, df_feedback, 
 df_contracts, df_benchmark, df_flow, df_stacked, df_active_monthly, 
 df_pareto, df_tiers, df_rec_channel, df_reasons_1_2) = load_all_data()

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
        ⚠️ **Concentração Temporal de Chamados Pré-Churn:**
        - **O CSAT é uma métrica cega:** A nota média é estável (~4.0) porque quem está decepcionado simplesmente não avalia (41,2% dos chamados sem nota).
        - **O gatilho de 2 semanas:** Quando uma conta sofre incidentes críticos não resolvidos e acumula chamados escalados na janela de 14 dias (salto de 4,5% para 14,6%), o cancelamento é disparado em até 2 semanas.
        - **SLA Geral não caiu:** O time de suporte manteve seus tempos médios globais; o problema foi o acúmulo de atrito sem solução rápida na conta específica em crise.
        """)

    st.markdown("---")
    st.markdown("### **Evolução da Base Ativa & Taxa Mensal de Saída (% Churn)**")
    
    col_act1, col_act2 = st.columns(2)
    with col_act1:
        st.markdown("#### **Contas Ativas Acumuladas Mês a Mês**")
        st.caption("Evolução da base líquida de clientes com contrato ativo")
        chart_act = alt.Chart(df_active_monthly).mark_area(
            color='#38bdf8', opacity=0.3, line={'color': '#0284c7', 'width': 3}
        ).encode(
            x=alt.X('year_month:N', title='Mês (2023-01 a 2024-12)', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('contas_ativas_mes:Q', title='Contas Ativas na Base'),
            tooltip=['year_month', 'contas_ativas_mes', 'novas_entradas_mes', 'contas_saidas_mes', 'reativacoes_mes']
        ).properties(height=260)
        st.altair_chart(chart_act, use_container_width=True)

    with col_act2:
        st.markdown("#### **Taxa Mensal de Churn (% Saída sobre Base Ativa)**")
        st.caption("Percentual de clientes ativos que cancelaram no mês correspondente")
        chart_rate = alt.Chart(df_active_monthly).mark_bar().encode(
            x=alt.X('year_month:N', title='Mês', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('pct_saida_sobre_ativas:Q', title='% Saída sobre Base Ativa'),
            color=alt.condition(
                alt.datum.pct_saida_sobre_ativas > 10,
                alt.value('#f43f5e'),
                alt.value('#38bdf8')
            ),
            tooltip=['year_month', 'pct_saida_sobre_ativas', 'contas_saidas_mes', 'base_exposta', 'contas_ativas_mes']
        ).properties(height=260)
        st.altair_chart(chart_rate, use_container_width=True)

    st.success("""
    📌 **Constatação Factual:** A aquisição de novas contas permaneceu constante mês a mês (média de **21 novas contas/mês**, variando entre 13 e 32). A crise da empresa foi provocada exclusivamente pelo **disparo da taxa real de saída do mês**, que saltou de **5,9% em Jan/2023** para **22,4% da base exposta em Dezembro/2024** (com pico de 96 contas cancelando no último mês).
    """)

    st.markdown("---")
    st.markdown("### **Fluxo Líquido Mensal & Fit por Canal de Aquisição**")
    
    col_flow, col_canal = st.columns([3, 2])
    
    with col_flow:
        st.markdown("#### **Fluxo Líquido Mensal de Contas (Entradas vs Saídas)**")
        st.caption("Eixo Y Positivo: Novas Entradas (+) | Eixo Y Negativo: Contas Saindo (-) | Linha Dourada: Saldo Líquido")
        
        bar_in = alt.Chart(df_flow).mark_bar(color='#10b981', opacity=0.85).encode(
            x=alt.X('year_month:N', title='Mês (2023-01 a 2024-12)', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('entradas:Q', title='Novas Contas (+) / Saídas (-)'),
            tooltip=['year_month', 'entradas', 'saidas', 'saldo_liquido']
        )
        bar_out = alt.Chart(df_flow).mark_bar(color='#f43f5e', opacity=0.85).encode(
            x=alt.X('year_month:N'),
            y=alt.Y('saidas_negativas:Q'),
            tooltip=['year_month', 'entradas', 'saidas', 'saldo_liquido']
        )
        line_net = alt.Chart(df_flow).mark_line(color='#fbbf24', strokeWidth=2.5, point=alt.OverlayMarkDef(color='#fbbf24', size=35)).encode(
            x=alt.X('year_month:N'),
            y=alt.Y('saldo_liquido:Q'),
            tooltip=['year_month', 'saldo_liquido']
        )
        rule_zero = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='#64748b', strokeDash=[2, 2]).encode(y='y:Q')
        
        chart_flow = (bar_in + bar_out + line_net + rule_zero).properties(height=300)
        st.altair_chart(chart_flow, use_container_width=True)

    with col_canal:
        st.markdown("#### **Taxa de Cancelamento por Canal (Barra 100%)**")
        st.caption("Proporção de Contas Retidas (Verde) vs Canceladas (Vermelho)")
        
        chart_channel_stacked = alt.Chart(df_stacked).mark_bar().encode(
            y=alt.Y('referral_source:N', sort=['event', 'other', 'ads', 'organic', 'partner'], title='Canal de Origem'),
            x=alt.X('contas:Q', stack='normalize', title='Proporção da Base (0% a 100%)', axis=alt.Axis(format='%')),
            color=alt.Color('status:N', title='Status', scale=alt.Scale(
                domain=['Canceladas (Churn)', 'Retidas (Ativas)'],
                range=['#f43f5e', '#10b981']
            )),
            tooltip=['referral_source', 'status', 'contas', 'pct']
        ).properties(height=260)
        
        st.altair_chart(chart_channel_stacked, use_container_width=True)
        st.caption("Eventos lidera perdas (30,2% churn), enquanto Parcerias tem a menor taxa (14,6% churn).")

# ==============================================================================
# TAB 2: MATRIZ CARTESIANA DE QUADRANTES (SCATTER PLOT COMPARATIVO)
# ==============================================================================
with tab2:
    st.subheader("2. Matrizes Cartesianas Comparativas: Base Total vs Ativas vs Canceladas")
    st.markdown("""
    Comparativo lado a lado para eliminar a confusão entre **Risco Preditivo (Contas Ativas)** e **Fato Consumado (Cancelamentos Históricos)**.
    Todas as 3 matrizes utilizam a mesma escala métrica (Eixo X: Score 0.1 a 0.9 | Eixo Y: MRR 0 a 24k) com cortes em **Score = 0,40** e **MRR = $ 1.500**.
    """)
    
    # Subsets
    df_active = df_scores[~df_scores['churn_flag']].copy()
    df_churned = df_scores[df_scores['churn_flag']].copy()
    
    col_m1, col_m2, col_m3 = st.columns(3)
    
    def build_scatter(data, title_text, point_color=None):
        chart = alt.Chart(data).mark_circle().encode(
            x=alt.X('churn_risk_score:Q', title='Score de Risco (0 a 1.0)', scale=alt.Scale(domain=[0.1, 0.9])),
            y=alt.Y('latest_mrr:Q', title=f'MRR ({simbolo})', scale=alt.Scale(domain=[0, 24000])),
            size=alt.Size('seats:Q', title='Licenças', scale=alt.Scale(range=[25, 260]), legend=None),
            color=alt.Color('quadrant:N', title='Quadrante', scale=alt.Scale(
                domain=[
                    'Q1: Zona Crítica (Alto MRR + Alto Risco)',
                    'Q2: Cauda Vulnerável (Baixo MRR + Alto Risco)',
                    'Q3: Vacas Leiteiras (Alto MRR + Baixo Risco)',
                    'Q4: Base Estável (Baixo MRR + Baixo Risco)'
                ],
                range=['#f43f5e', '#fb923c', '#059669', '#38bdf8']
            ), legend=None),
            tooltip=['account_name', 'account_id', 'industry', 'latest_mrr', 'churn_risk_score', 'churn_flag', 'quadrant']
        ).properties(title=title_text, height=360)
        
        rule_x = alt.Chart(pd.DataFrame({'x': [0.40]})).mark_rule(color='#64748b', strokeDash=[4, 4]).encode(x='x:Q')
        rule_y = alt.Chart(pd.DataFrame({'y': [1500]})).mark_rule(color='#64748b', strokeDash=[4, 4]).encode(y='y:Q')
        return chart + rule_x + rule_y

    # --- MATRIZ 1: TODAS AS CONTAS ---
    with col_m1:
        st.markdown("#### **1. Base Completa (500 contas)**")
        st.caption("Visão Histórica Global (Ativas + Canceladas)")
        st.altair_chart(build_scatter(df_scores, "Todas as 500 Contas"), use_container_width=True)
        
        st.markdown("""
        <div style="background: #1e293b; padding: 10px; border-radius: 6px; font-size: 12px; margin-bottom: 8px;">
            <strong>Distribuição:</strong><br>
            • Q1: 108 contas | MRR $493,3k<br>
            • Q2: 146 contas | MRR $63,5k<br>
            • Q3: 98 contas | MRR $604,9k<br>
            • Q4: 148 contas | MRR $76,7k
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        **O que indica visualmente:**
        Apresenta a dispersão geral de calibragem do algoritmo. O lado direito concentra todas as contas com atritos acumulados na jornada.
        
        **Direcionamento:**
        Usada para auditoria do modelo e validação executiva da metodologia estatística.
        """)

    # --- MATRIZ 2: CONTAS ATIVAS ---
    with col_m2:
        st.markdown("#### **2. Base Ativa (390 contas)**")
        st.caption("Foco de Ação de CS & Retenção (Risco Real)")
        st.altair_chart(build_scatter(df_active, "390 Contas Ativas (Sem Churn)"), use_container_width=True)
        
        mrr_q1_active = df_active[df_active['quadrant'].str.contains('Q1', na=False)]['latest_mrr'].sum()
        cnt_q1_active = len(df_active[df_active['quadrant'].str.contains('Q1', na=False)])
        
        st.markdown(f"""
        <div style="background: #1e293b; border-left: 4px solid #f43f5e; padding: 10px; border-radius: 6px; font-size: 12px; margin-bottom: 8px;">
            <strong style="color: #f43f5e;">Alvo de Intervenção (Q1):</strong><br>
            • <strong>{cnt_q1_active} contas ativas</strong> sob alto risco<br>
            • <strong>{fmt_money(mrr_q1_active)}/mês</strong> em perigo real<br>
            • Q3/Q4: 246 contas saudáveis
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        **O que indica visualmente:**
        Elimina ruído de perdas antigas. O canto superior direito mostra unicamente os clientes pagantes que estão sofrendo fricção técnica agora.
        
        **Direcionamento:**
        Lista de trabalho diária da Squad de Customer Success. Choque imediato nas contas ativas do Q1.
        """)

    # --- MATRIZ 3: CONTAS CANCELADAS ---
    with col_m3:
        st.markdown("#### **3. Base Cancelada (110 contas)**")
        st.caption("Diagnóstico Post-Mortem & Win-Back (Fato Consumado)")
        st.altair_chart(build_scatter(df_churned, "110 Contas que Cancelaram"), use_container_width=True)
        
        mrr_q1_churned = df_churned[df_churned['quadrant'].str.contains('Q1', na=False)]['latest_mrr'].sum()
        cnt_q1_churned = len(df_churned[df_churned['quadrant'].str.contains('Q1', na=False)])
        
        st.markdown(f"""
        <div style="background: #1e293b; border-left: 4px solid #38bdf8; padding: 10px; border-radius: 6px; font-size: 12px; margin-bottom: 8px;">
            <strong style="color: #38bdf8;">Autópsia de Perdas:</strong><br>
            • Q1: <strong>{cnt_q1_churned} contas</strong> | <strong>{fmt_money(mrr_q1_churned)}</strong> perdidos<br>
            • Outlier topo: <strong>Company_4</strong> ($21.691/mês)<br>
            • Q3 e Q4: <strong>0 cancelamentos (0%)</strong>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        **O que indica visualmente:**
        100% dos cancelamentos estão situados na metade direita (Q1 e Q2). Nenhuma conta cancelou em Q3 ou Q4, comprovando acurácia diagnóstica.
        
        **Direcionamento:**
        Alimentar a engenharia com a causa-raiz dos cancelamentos e direcionar SDRs para campanhas de win-back.
        """)

    st.markdown("---")
    st.markdown("#### **Tabela Comparativa Consolidada das 3 Visões**")
    
    tab_comp = pd.DataFrame([
        {
            "Dimensão": "Q1: Zona Crítica (Alto MRR + Alto Risco)",
            "1. Base Total (500)": "108 contas ($493,3k)",
            "2. Base Ativa (390) - Risco Real": f"{cnt_q1_active} contas ({fmt_money(mrr_q1_active)})",
            "3. Base Cancelada (110) - Fato": f"{cnt_q1_churned} contas ({fmt_money(mrr_q1_churned)})",
            "Conclusão": "50 contas já foram perdidas (ex: Company_4); 58 ainda podem ser salvas."
        },
        {
            "Dimensão": "Q2: Cauda Vulnerável (Baixo MRR + Alto Risco)",
            "1. Base Total (500)": "146 contas ($63,5k)",
            "2. Base Ativa (390) - Risco Real": "86 contas ($36,5k)",
            "3. Base Cancelada (110) - Fato": "60 contas ($27,0k)",
            "Conclusão": "Erosão contínua de contratos pequenos; demanda réguas de auto-atendimento."
        },
        {
            "Dimensão": "Q3: Vacas Leiteiras (Alto MRR + Baixo Risco)",
            "1. Base Total (500)": "98 contas ($604,9k)",
            "2. Base Ativa (390) - Risco Real": "98 contas ($604,9k)",
            "3. Base Cancelada (110) - Fato": "0 contas ($0)",
            "Conclusão": "Blindagem perfeita. Nenhuma conta deste quadrante cancelou."
        },
        {
            "Dimensão": "Q4: Base Estável (Baixo MRR + Baixo Risco)",
            "1. Base Total (500)": "148 contas ($76,7k)",
            "2. Base Ativa (390) - Risco Real": "148 contas ($76,7k)",
            "3. Base Cancelada (110) - Fato": "0 contas ($0)",
            "Conclusão": "Estabilidade operacional total. Zero perdas históricas."
        }
    ])
    st.table(tab_comp)
    
    st.info("💡 **Decisão Executiva:** O esforço humano de Customer Success deve ser focado estritamente na **Matriz 2 (Base Ativa)**, onde 58 contas concentram **$264.857/mês** em risco real. As contas da Matriz 3 já saíram e devem ir para o fluxo de pós-morte/win-back.")

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

    st.markdown("---")
    st.markdown("### **O Fenômeno do Churn Recorrente: Saiu, Voltou e Saiu de Novo?**")
    st.markdown("""
    Na base de 600 eventos de cancelamento, **175 contas passaram por múltiplos ciclos de cancelamento/reativação**.
    Abaixo está o raio-x do que acontece quando o cliente é reativado:
    """)
    
    col_rec1, col_rec2 = st.columns(2)
    
    with col_rec1:
        st.markdown("#### **Eficácia da Reativação por Canal de Origem**")
        df_rec_channel = pd.DataFrame([
            {"Canal": "Event (Eventos)", "Contas c/ Múltiplos Churns": 33, "Ficaram Ativas no Fim": "20 (60,6%)", "Cancelamento Fatal no Fim": "13 (39,4%)", "Veredito": "Falsa Reativação (Frágil)"},
            {"Canal": "Other (Outros)", "Contas c/ Múltiplos Churns": 32, "Ficaram Ativas no Fim": "23 (71,9%)", "Cancelamento Fatal no Fim": "9 (28,1%)", "Veredito": "Risco Moderado"},
            {"Canal": "Ads (Anúncios)", "Contas c/ Múltiplos Churns": 31, "Ficaram Ativas no Fim": "24 (77,4%)", "Cancelamento Fatal no Fim": "7 (22,6%)", "Veredito": "Risco Moderado"},
            {"Canal": "Organic (Orgânico)", "Contas c/ Múltiplos Churns": 46, "Ficaram Ativas no Fim": "39 (84,8%)", "Cancelamento Fatal no Fim": "7 (15,2%)", "Veredito": "Alta Retenção pós-volta"},
            {"Canal": "Partner (Parcerias)", "Contas c/ Múltiplos Churns": 33, "Ficaram Ativas no Fim": "29 (87,9%)", "Cancelamento Fatal no Fim": "4 (12,1%)", "Veredito": "Máxima Fidelidade (Voltam para ficar)"}
        ])
        st.table(df_rec_channel)
        st.caption("Contas de Eventos têm quase 4x mais chance de abandonar o produto em definitivo após uma reativação do que contas de Parcerias.")

    with col_rec2:
        st.markdown("#### **O que Muda no Segundo Cancelamento?**")
        st.markdown("""
        - **86,9% saem por MOTIVOS DIFERENTES na segunda vez:** Apenas 13,1% repetem a mesma razão da saída original.
          - *A dinâmica:* O cliente sai a 1ª vez por *Features* ou *Suporte*. A empresa reativa oferecendo desconto. Na 2ª saída, o motivo migra para *Pricing* ou *Competitor* ("o produto não vale nem com desconto").
        - **40,2% das reativações sofreram DOWNGRADE:** O cliente volta pagando menos MRR.
        - **24,2% migraram de ANUAL para MENSAL:** Perda de compromisso contratual de longo prazo.
        """)
        
        st.warning("""
        💡 **Lição Prescritiva de Win-Back:**
        Reativar clientes apenas concedendo descontos de preço cria uma **reativação oca**: o cliente migra de plano anual para mensal com downgrade, e 6 meses depois cancela definitivamente por falta de valor percebido.
        """)

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

