import duckdb
import pandas as pd
import numpy as np
from lifelines import KaplanMeierFitter
import json

DATA_DIR = "/Users/montinegro/G4 AI Master/data/churn"
con = duckdb.connect(database=':memory:')

con.execute(f"""
    CREATE TABLE accounts AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_accounts.csv');
    CREATE TABLE subscriptions AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_subscriptions.csv');
    CREATE TABLE feature_usage AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_feature_usage.csv');
    CREATE TABLE support_tickets AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_support_tickets.csv');
    CREATE TABLE churn_events AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_churn_events.csv');
""")

print("==================================================================")
print("=== HIPÓTESE 1: O DILEMA DO PRODUTO (USO vs ERROS vs BETAS) ===")
print("==================================================================")

# Comparar uso médio e taxa de erros entre contas churneadas vs não churneadas
df_usage_churn = con.execute("""
    WITH account_usage AS (
        SELECT 
            s.account_id,
            count(f.usage_id) as total_events,
            sum(f.usage_count) as total_count,
            sum(f.usage_duration_secs) as total_duration_secs,
            sum(f.error_count) as total_errors,
            sum(CASE WHEN f.is_beta_feature THEN f.error_count ELSE 0 END) as beta_errors,
            sum(CASE WHEN f.is_beta_feature THEN f.usage_count ELSE 0 END) as beta_usage_count,
            round(100.0 * sum(f.error_count) / nullif(sum(f.usage_count), 0), 2) as overall_error_rate,
            round(100.0 * sum(CASE WHEN f.is_beta_feature THEN f.error_count ELSE 0 END) / 
                  nullif(sum(CASE WHEN f.is_beta_feature THEN f.usage_count ELSE 0 END), 0), 2) as beta_error_rate
        FROM subscriptions s
        JOIN feature_usage f ON s.subscription_id = f.subscription_id
        GROUP BY s.account_id
    )
    SELECT 
        a.churn_flag,
        a.plan_tier,
        count(distinct a.account_id) as n_accounts,
        round(avg(u.total_count), 1) as avg_usage_count,
        round(avg(u.total_errors), 1) as avg_errors,
        round(avg(u.overall_error_rate), 2) as avg_error_rate_pct,
        round(avg(u.beta_errors), 1) as avg_beta_errors,
        round(avg(u.beta_error_rate), 2) as avg_beta_error_rate_pct
    FROM accounts a
    LEFT JOIN account_usage u ON a.account_id = u.account_id
    GROUP BY a.churn_flag, a.plan_tier
    ORDER BY a.plan_tier, a.churn_flag
""").df()
print(df_usage_churn.to_string(index=False))

print("\n--- Features com maior taxa de erro e correlação com Churn ---")
df_feat_errors = con.execute("""
    SELECT 
        f.feature_name,
        f.is_beta_feature,
        count(distinct s.account_id) as accounts_using,
        sum(f.usage_count) as total_usage,
        sum(f.error_count) as total_errors,
        round(100.0 * sum(f.error_count) / sum(f.usage_count), 2) as error_rate_pct,
        round(100.0 * count(distinct CASE WHEN a.churn_flag THEN s.account_id END) / count(distinct s.account_id), 1) as churn_rate_pct
    FROM feature_usage f
    JOIN subscriptions s ON f.subscription_id = s.subscription_id
    JOIN accounts a ON s.account_id = a.account_id
    GROUP BY f.feature_name, f.is_beta_feature
    ORDER BY total_errors DESC
    LIMIT 10
""").df()
print(df_feat_errors.to_string(index=False))

print("\n==================================================================")
print("=== HIPÓTESE 2: O DILEMA DO SUPORTE (CSAT vs FRT vs ESCALAÇÕES) ===")
print("==================================================================")

# Analisar o viés de não-resposta no CSAT e tickets por conta churneada vs não churneada
df_support_bias = con.execute("""
    WITH account_tickets AS (
        SELECT 
            account_id,
            count(*) as total_tickets,
            avg(satisfaction_score) as avg_csat,
            count(satisfaction_score) as rated_tickets,
            count(*) - count(satisfaction_score) as unrated_tickets,
            round(100.0 * (count(*) - count(satisfaction_score)) / count(*), 1) as unrated_pct,
            avg(first_response_time_minutes) as avg_frt_min,
            avg(resolution_time_hours) as avg_res_hours,
            sum(CASE WHEN escalation_flag THEN 1 ELSE 0 END) as escalations,
            sum(CASE WHEN priority IN ('high', 'urgent') THEN 1 ELSE 0 END) as urgent_tickets,
            avg(CASE WHEN priority IN ('high', 'urgent') THEN first_response_time_minutes END) as urgent_frt_min
        FROM support_tickets
        GROUP BY account_id
    )
    SELECT 
        a.churn_flag,
        a.plan_tier,
        count(distinct a.account_id) as n_accounts,
        round(avg(t.total_tickets), 1) as avg_tickets,
        round(avg(t.avg_csat), 2) as avg_reported_csat,
        round(avg(t.unrated_pct), 1) as avg_unrated_pct,
        round(avg(t.avg_frt_min), 1) as avg_frt_min,
        round(avg(t.urgent_frt_min), 1) as avg_urgent_frt_min,
        round(avg(t.escalations), 1) as avg_escalations
    FROM accounts a
    LEFT JOIN account_tickets t ON a.account_id = t.account_id
    GROUP BY a.churn_flag, a.plan_tier
    ORDER BY a.plan_tier, a.churn_flag
""").df()
print(df_support_bias.to_string(index=False))

print("\n--- Tickets de alta prioridade / urgentes: Churn vs Retido ---")
df_urgent_analysis = con.execute("""
    SELECT 
        a.churn_flag,
        t.priority,
        count(*) as ticket_count,
        round(avg(t.first_response_time_minutes), 1) as avg_frt_min,
        round(avg(t.resolution_time_hours), 1) as avg_res_hours,
        round(100.0 * sum(CASE WHEN t.escalation_flag THEN 1 ELSE 0 END) / count(*), 1) as escalation_pct,
        round(avg(t.satisfaction_score), 2) as avg_csat
    FROM support_tickets t
    JOIN accounts a ON t.account_id = a.account_id
    GROUP BY a.churn_flag, t.priority
    ORDER BY t.priority, a.churn_flag
""").df()
print(df_urgent_analysis.to_string(index=False))

print("\n==================================================================")
print("=== HIPÓTESE 3: MOTIVOS DE CHURN, REFUNDS E FEEDBACK ===")
print("==================================================================")
df_reasons = con.execute("""
    SELECT 
        reason_code,
        count(*) as event_count,
        round(100.0 * count(*) / (SELECT count(*) FROM churn_events), 1) as pct_events,
        round(avg(refund_amount_usd), 2) as avg_refund,
        sum(refund_amount_usd) as total_refund,
        sum(CASE WHEN preceding_upgrade_flag THEN 1 ELSE 0 END) as preceded_by_upgrade,
        sum(CASE WHEN preceding_downgrade_flag THEN 1 ELSE 0 END) as preceded_by_downgrade,
        sum(CASE WHEN is_reactivation THEN 1 ELSE 0 END) as is_reactivation
    FROM churn_events
    GROUP BY reason_code
    ORDER BY event_count DESC
""").df()
print(df_reasons.to_string(index=False))

print("\n--- Amostras de feedback por motivo de churn ---")
df_samples = con.execute("""
    SELECT reason_code, feedback_text
    FROM churn_events
    WHERE feedback_text IS NOT NULL
    QUALIFY row_number() OVER (PARTITION BY reason_code ORDER BY churn_date DESC) <= 2
""").df()
for _, r in df_samples.iterrows():
    print(f"[{r['reason_code']}]: \"{r['feedback_text']}\"")

print("\n==================================================================")
print("=== HIPÓTESE 4: ANÁLISE DE SOBREVIVÊNCIA (KAPLAN-MEIER) ===")
print("==================================================================")

# Calcular tempo até churn ou tempo de observação por conta
df_survival = con.execute("""
    WITH acc_summary AS (
        SELECT 
            a.account_id,
            a.plan_tier,
            a.industry,
            a.signup_date,
            a.churn_flag,
            coalesce(min(c.churn_date), date '2024-12-31') as end_or_censor_date
        FROM accounts a
        LEFT JOIN churn_events c ON a.account_id = c.account_id
        GROUP BY a.account_id, a.plan_tier, a.industry, a.signup_date, a.churn_flag
    )
    SELECT 
        account_id,
        plan_tier,
        industry,
        datediff('day', signup_date, end_or_censor_date) as duration_days,
        CASE WHEN churn_flag THEN 1 ELSE 0 END as event_observed
    FROM acc_summary
""").df()

kmf = KaplanMeierFitter()
print("Mediana de Sobrevivência Geral:")
kmf.fit(df_survival['duration_days'], event_observed=df_survival['event_observed'])
print(f"Probabilidade acumulada de sobrevivência aos 90 dias: {kmf.predict(90):.3f}")
print(f"Probabilidade acumulada de sobrevivência aos 180 dias: {kmf.predict(180):.3f}")
print(f"Probabilidade acumulada de sobrevivência aos 365 dias: {kmf.predict(365):.3f}")

print("\nSobrevivência estratificada por Plan Tier:")
for tier in ['Basic', 'Pro', 'Enterprise']:
    sub_df = df_survival[df_survival['plan_tier'] == tier]
    kmf.fit(sub_df['duration_days'], event_observed=sub_df['event_observed'], label=tier)
    print(f"[{tier}] 90d: {kmf.predict(90):.3f} | 180d: {kmf.predict(180):.3f} | 365d: {kmf.predict(365):.3f} | Churn final: {sub_df['event_observed'].mean():.1%}")

