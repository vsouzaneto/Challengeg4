import duckdb
import pandas as pd
import numpy as np
import json
import os

DATA_DIR = "/Users/montinegro/G4 AI Master/data/churn"
OUTPUT_DIR = "/Users/montinegro/G4 AI Master/repo/submissions/adailton-montinegro/artifacts"
SCORES_FILE = f"{OUTPUT_DIR}/ravenstack_account_risk_scores.csv"

con = duckdb.connect(database=':memory:')

con.execute(f"""
    CREATE TABLE accounts AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_accounts.csv');
    CREATE TABLE subscriptions AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_subscriptions.csv');
    CREATE TABLE feature_usage AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_feature_usage.csv');
    CREATE TABLE support_tickets AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_support_tickets.csv');
    CREATE TABLE churn_events AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_churn_events.csv');
""")

print("=== 1. SÉRIE TEMPORAL MENSAL CONTÍNUA (24 MESES) ===")
df_monthly = con.execute("""
    WITH monthly_calendar AS (
        SELECT unnest(generate_series(date '2023-01-01', date '2024-12-01', interval '1 month')) as month_start
    ),
    cal AS (
        SELECT 
            month_start,
            strftime(month_start, '%Y-%m') as year_month
        FROM monthly_calendar
    ),
    signups AS (
        SELECT 
            strftime(signup_date, '%Y-%m') as year_month,
            count(distinct account_id) as new_accounts
        FROM accounts
        GROUP BY 1
    ),
    churns AS (
        SELECT 
            strftime(churn_date, '%Y-%m') as year_month,
            count(*) as churn_events,
            count(distinct account_id) as churned_accounts,
            round(sum(refund_amount_usd), 2) as total_refunds
        FROM churn_events
        GROUP BY 1
    ),
    usage AS (
        SELECT 
            strftime(f.usage_date, '%Y-%m') as year_month,
            count(distinct s.account_id) as active_using_accounts,
            sum(f.usage_count) as total_usage,
            sum(f.error_count) as total_errors,
            round(100.0 * sum(f.error_count) / nullif(sum(f.usage_count), 0), 2) as error_rate_pct
        FROM feature_usage f
        JOIN subscriptions s ON f.subscription_id = s.subscription_id
        GROUP BY 1
    )
    SELECT 
        c.year_month,
        coalesce(s.new_accounts, 0) as new_accounts,
        coalesce(u.active_using_accounts, 0) as active_using_accounts,
        coalesce(u.total_usage, 0) as total_usage,
        round(coalesce(u.total_usage, 0) / nullif(u.active_using_accounts, 0), 1) as usage_per_active_account,
        coalesce(ch.churn_events, 0) as churn_events,
        coalesce(ch.churned_accounts, 0) as churned_accounts,
        coalesce(ch.total_refunds, 0.0) as total_refunds,
        coalesce(u.error_rate_pct, 0.0) as error_rate_pct
    FROM cal c
    LEFT JOIN signups s ON c.year_month = s.year_month
    LEFT JOIN churns ch ON c.year_month = ch.year_month
    LEFT JOIN usage u ON c.year_month = u.year_month
    ORDER BY c.year_month
""").df()
print(df_monthly.to_string(index=False))

print("\n=== 2. MATRIZ DE QUADRANTES (MRR vs RISCO / ERRO) ===")
df_scores = pd.read_csv(SCORES_FILE)

# Definição determinística de 4 Quadrantes
# Limite MRR Mediano / Executivo: $1.500
# Limite Risco: Score 0.40 ou Churn
def assign_quadrant(row):
    high_mrr = row['latest_mrr'] > 1500
    high_risk = (row['churn_risk_score'] >= 0.40) or bool(row['churn_flag'])
    
    if high_mrr and high_risk:
        return 'Q1: Zona Crítica (Alto MRR + Alto Risco)'
    elif not high_mrr and high_risk:
        return 'Q2: Cauda Vulnerável (Baixo MRR + Alto Risco)'
    elif high_mrr and not high_risk:
        return 'Q3: Vacas Leiteiras (Alto MRR + Baixo Risco)'
    else:
        return 'Q4: Base Estável (Baixo MRR + Baixo Risco)'

df_scores['quadrant'] = df_scores.apply(assign_quadrant, axis=1)

df_quadrant_summary = df_scores.groupby('quadrant').agg(
    contas=('account_id', 'count'),
    mrr_total=('latest_mrr', 'sum'),
    mrr_medio=('latest_mrr', 'mean'),
    churn_rate=('churn_flag', 'mean'),
    score_medio=('churn_risk_score', 'mean'),
    taxa_erro_media=('error_rate_pct', 'mean'),
    escalacoes_medias=('total_escalations', 'mean')
).reset_index()
df_quadrant_summary['mrr_total'] = df_quadrant_summary['mrr_total'].round(2)
df_quadrant_summary['mrr_medio'] = df_quadrant_summary['mrr_medio'].round(2)
df_quadrant_summary['churn_rate'] = (df_quadrant_summary['churn_rate'] * 100).round(1)
df_quadrant_summary['score_medio'] = df_quadrant_summary['score_medio'].round(2)
df_quadrant_summary['taxa_erro_media'] = df_quadrant_summary['taxa_erro_media'].round(2)
df_quadrant_summary['escalacoes_medias'] = df_quadrant_summary['escalacoes_medias'].round(2)

print(df_quadrant_summary.to_string(index=False))

print("\n=== 3. ANÁLISE DETALHADA DE FEEDBACKS E REASON CODES ===")
df_reasons = con.execute("""
    SELECT 
        reason_code,
        count(*) as event_count,
        round(100.0 * count(*) / (SELECT count(*) FROM churn_events), 1) as pct_events,
        round(avg(refund_amount_usd), 2) as avg_refund,
        round(sum(refund_amount_usd), 2) as total_refund,
        sum(CASE WHEN preceding_upgrade_flag THEN 1 ELSE 0 END) as preceded_by_upgrade,
        sum(CASE WHEN preceding_downgrade_flag THEN 1 ELSE 0 END) as preceded_by_downgrade,
        sum(CASE WHEN is_reactivation THEN 1 ELSE 0 END) as reactivations
    FROM churn_events
    GROUP BY reason_code
    ORDER BY event_count DESC
""").df()
print(df_reasons.to_string(index=False))

df_feedback_text = con.execute("""
    SELECT 
        coalesce(feedback_text, '[Sem feedback]') as feedback,
        count(*) as occurrences,
        round(100.0 * count(*) / (SELECT count(*) FROM churn_events), 1) as pct_total
    FROM churn_events
    GROUP BY 1
    ORDER BY occurrences DESC
""").df()
print("\nFrequência dos Textos de Feedback:")
print(df_feedback_text.to_string(index=False))

print("\n=== 4. ANÁLISE DE CONTRATOS: FREQUÊNCIA, AUTO-RENEW E TRIAL ===")
df_contracts = con.execute("""
    SELECT 
        s.billing_frequency,
        s.auto_renew_flag,
        s.is_trial,
        count(distinct s.subscription_id) as total_subs,
        sum(CASE WHEN s.churn_flag THEN 1 ELSE 0 END) as churned_subs,
        round(100.0 * sum(CASE WHEN s.churn_flag THEN 1 ELSE 0 END) / count(*), 1) as churn_rate_pct,
        round(avg(s.mrr_amount), 2) as avg_mrr
    FROM subscriptions s
    GROUP BY 1, 2, 3
    ORDER BY s.billing_frequency, s.auto_renew_flag, s.is_trial
""").df()
print(df_contracts.to_string(index=False))

print("\n=== 5. BENCHMARK DAS 390 CONTAS RETIDAS VS 110 CHURNEADAS ===")
df_benchmark = con.execute("""
    WITH acc_metrics AS (
        SELECT 
            a.account_id,
            a.churn_flag,
            a.plan_tier,
            a.industry,
            a.referral_source,
            a.seats,
            s.billing_frequency,
            s.auto_renew_flag,
            s.mrr_amount,
            coalesce(u.error_rate, 0.0) as error_rate,
            coalesce(t.total_tickets, 0) as total_tickets,
            coalesce(t.escalations, 0) as escalations,
            coalesce(t.avg_frt, 90.0) as avg_frt
        FROM accounts a
        JOIN (
            SELECT account_id, billing_frequency, auto_renew_flag, mrr_amount,
                   row_number() over (partition by account_id order by start_date desc) as rn
            FROM subscriptions
        ) s ON a.account_id = s.account_id AND s.rn = 1
        LEFT JOIN (
            SELECT s.account_id, round(100.0 * sum(f.error_count) / nullif(sum(f.usage_count), 0), 2) as error_rate
            FROM subscriptions s JOIN feature_usage f ON s.subscription_id = f.subscription_id GROUP BY 1
        ) u ON a.account_id = u.account_id
        LEFT JOIN (
            SELECT account_id, count(*) as total_tickets, sum(CASE WHEN escalation_flag THEN 1 ELSE 0 END) as escalations,
                   avg(first_response_time_minutes) as avg_frt
            FROM support_tickets GROUP BY 1
        ) t ON a.account_id = t.account_id
    )
    SELECT 
        churn_flag,
        count(*) as total_contas,
        round(avg(mrr_amount), 2) as mrr_medio,
        round(avg(seats), 1) as seats_medio,
        round(avg(error_rate), 2) as taxa_erro_media_pct,
        round(avg(total_tickets), 1) as tickets_medios,
        round(avg(escalations), 2) as escalacoes_medias,
        round(avg(avg_frt), 1) as frt_medio_min,
        round(100.0 * sum(CASE WHEN billing_frequency = 'annual' THEN 1 ELSE 0 END) / count(*), 1) as pct_contratos_anuais,
        round(100.0 * sum(CASE WHEN auto_renew_flag THEN 1 ELSE 0 END) / count(*), 1) as pct_auto_renew,
        round(100.0 * sum(CASE WHEN referral_source = 'partner' THEN 1 ELSE 0 END) / count(*), 1) as pct_canal_partner
    FROM acc_metrics
    GROUP BY churn_flag
""").df()
print(df_benchmark.to_string(index=False))

# Salvar tudo em JSON consolidado
advanced_data = {
    "monthly_timeline": df_monthly.to_dict(orient="records"),
    "quadrants_summary": df_quadrant_summary.to_dict(orient="records"),
    "churn_reasons": df_reasons.to_dict(orient="records"),
    "feedback_frequencies": df_feedback_text.to_dict(orient="records"),
    "contracts_breakdown": df_contracts.to_dict(orient="records"),
    "retention_benchmark": df_benchmark.to_dict(orient="records")
}

with open(f"{OUTPUT_DIR}/advanced_analytics.json", "w", encoding="utf-8") as f:
    json.dump(advanced_data, f, indent=2, ensure_ascii=False)

# Atualizar o CSV com a coluna quadrant
df_scores.to_csv(SCORES_FILE, index=False)

print(f"\nDados analíticos avançados consolidados em: {OUTPUT_DIR}/advanced_analytics.json")
print(f"Scores atualizados com quadrantes em: {SCORES_FILE}")
