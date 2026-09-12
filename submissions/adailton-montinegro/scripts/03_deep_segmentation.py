import duckdb
import pandas as pd

DATA_DIR = "/Users/montinegro/G4 AI Master/data/churn"
con = duckdb.connect(database=':memory:')

con.execute(f"""
    CREATE TABLE accounts AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_accounts.csv');
    CREATE TABLE subscriptions AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_subscriptions.csv');
    CREATE TABLE feature_usage AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_feature_usage.csv');
    CREATE TABLE support_tickets AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_support_tickets.csv');
    CREATE TABLE churn_events AS SELECT * FROM read_csv_auto('{DATA_DIR}/ravenstack_churn_events.csv');
""")

print("=== 1. EVOLUÇÃO TEMPORAL: CHURN, USO E RECEITA POR TRIMESTRE ===")
df_temporal = con.execute("""
    SELECT 
        cast(year(churn_date) as varchar) || '-Q' || cast(quarter(churn_date) as varchar) as quarter,
        count(*) as churn_events_count,
        count(distinct account_id) as churned_accounts,
        round(sum(refund_amount_usd), 2) as total_refunds
    FROM churn_events
    GROUP BY 1
    ORDER BY 1
""").df()
print("Evolução dos Eventos de Churn:")
print(df_temporal.to_string(index=False))

df_usage_trend = con.execute("""
    SELECT 
        cast(year(usage_date) as varchar) || '-Q' || cast(quarter(usage_date) as varchar) as quarter,
        count(*) as total_events,
        sum(usage_count) as total_usage,
        sum(error_count) as total_errors,
        round(100.0 * sum(error_count) / sum(usage_count), 2) as error_rate_pct
    FROM feature_usage
    GROUP BY 1
    ORDER BY 1
""").df()
print("\nEvolução do Uso de Produto:")
print(df_usage_trend.to_string(index=False))

print("\n=== 2. SEGMENTAÇÃO POR INDÚSTRIA E CANAL DE AQUISIÇÃO ===")
df_ind = con.execute("""
    SELECT 
        industry,
        count(*) as total_accounts,
        sum(CASE WHEN churn_flag THEN 1 ELSE 0 END) as churned,
        round(100.0 * sum(CASE WHEN churn_flag THEN 1 ELSE 0 END) / count(*), 1) as churn_rate_pct,
        round(avg(seats), 1) as avg_seats
    FROM accounts
    GROUP BY industry
    ORDER BY churn_rate_pct DESC
""").df()
print("Churn por Indústria:")
print(df_ind.to_string(index=False))

df_ref = con.execute("""
    SELECT 
        referral_source,
        count(*) as total_accounts,
        sum(CASE WHEN churn_flag THEN 1 ELSE 0 END) as churned,
        round(100.0 * sum(CASE WHEN churn_flag THEN 1 ELSE 0 END) / count(*), 1) as churn_rate_pct
    FROM accounts
    GROUP BY referral_source
    ORDER BY churn_rate_pct DESC
""").df()
print("\nChurn por Canal de Aquisição:")
print(df_ref.to_string(index=False))

print("\n=== 3. SEGMENTAÇÃO POR FREQUÊNCIA DE COBRANÇA E AUTO-RENEW ===")
df_sub_attr = con.execute("""
    SELECT 
        s.billing_frequency,
        s.auto_renew_flag,
        count(*) as total_subs,
        sum(CASE WHEN s.churn_flag THEN 1 ELSE 0 END) as churned_subs,
        round(100.0 * sum(CASE WHEN s.churn_flag THEN 1 ELSE 0 END) / count(*), 1) as sub_churn_rate_pct,
        round(sum(s.mrr_amount), 2) as total_mrr
    FROM subscriptions s
    GROUP BY s.billing_frequency, s.auto_renew_flag
    ORDER BY s.billing_frequency, s.auto_renew_flag
""").df()
print(df_sub_attr.to_string(index=False))

print("\n=== 4. IMPACTO DE UPGRADE / DOWNGRADE ===")
df_up_down = con.execute("""
    SELECT 
        upgrade_flag,
        downgrade_flag,
        count(*) as total_subs,
        sum(CASE WHEN churn_flag THEN 1 ELSE 0 END) as churned_subs,
        round(100.0 * sum(CASE WHEN churn_flag THEN 1 ELSE 0 END) / count(*), 1) as churn_rate_pct
    FROM subscriptions
    GROUP BY upgrade_flag, downgrade_flag
""").df()
print(df_up_down.to_string(index=False))

print("\n=== 5. ANÁLISE DE IMPACTO FINANCEIRO: MRR PERDIDO ===")
df_mrr_loss = con.execute("""
    SELECT 
        a.plan_tier,
        count(distinct a.account_id) as total_accounts,
        sum(CASE WHEN a.churn_flag THEN 1 ELSE 0 END) as churned_accounts,
        round(sum(CASE WHEN a.churn_flag THEN s.mrr_amount ELSE 0 END), 2) as lost_mrr,
        round(sum(CASE WHEN NOT a.churn_flag THEN s.mrr_amount ELSE 0 END), 2) as active_mrr,
        round(100.0 * sum(CASE WHEN a.churn_flag THEN s.mrr_amount ELSE 0 END) / sum(s.mrr_amount), 1) as mrr_churn_rate_pct
    FROM accounts a
    JOIN (
        -- Pegar a última assinatura de cada conta
        SELECT account_id, plan_tier, mrr_amount, row_number() over (partition by account_id order by start_date desc) as rn
        FROM subscriptions
    ) s ON a.account_id = s.account_id AND s.rn = 1
    GROUP BY a.plan_tier
    ORDER BY lost_mrr DESC
""").df()
print(df_mrr_loss.to_string(index=False))

