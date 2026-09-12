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

print("=== 1. QUANDO AS CONTAS QUE CHURNEARAM EM 2024-Q4 FORAM ADQUIRIDAS? (ANÁLISE DE COORTE) ===")
df_cohort_q4 = con.execute("""
    SELECT 
        cast(year(a.signup_date) as varchar) || '-Q' || cast(quarter(a.signup_date) as varchar) as signup_quarter,
        count(distinct c.account_id) as churned_in_q4_2024,
        count(distinct a.account_id) as total_cohort_size,
        round(100.0 * count(distinct c.account_id) / count(distinct a.account_id), 1) as pct_cohort_churned_in_q4
    FROM accounts a
    LEFT JOIN churn_events c ON a.account_id = c.account_id 
        AND c.churn_date BETWEEN date '2024-10-01' AND date '2024-12-31'
    GROUP BY 1
    ORDER BY 1
""").df()
print(df_cohort_q4.to_string(index=False))

print("\n=== 2. CICLO DE VIDA (TENURE EM DIAS ATÉ O CHURN) ===")
df_tenure = con.execute("""
    SELECT 
        a.plan_tier,
        round(avg(datediff('day', a.signup_date, c.churn_date)), 1) as avg_days_to_churn,
        round(median(datediff('day', a.signup_date, c.churn_date)), 1) as median_days_to_churn,
        min(datediff('day', a.signup_date, c.churn_date)) as min_days,
        max(datediff('day', a.signup_date, c.churn_date)) as max_days
    FROM accounts a
    JOIN churn_events c ON a.account_id = c.account_id
    GROUP BY a.plan_tier
""").df()
print(df_tenure.to_string(index=False))

print("\n=== 3. ANÁLISE DE TIMING DE TICKETS DE SUPORTE PRÉ-CHURN ===")
df_ticket_lead = con.execute("""
    WITH ticket_churn_delta AS (
        SELECT 
            t.account_id,
            t.ticket_id,
            t.priority,
            t.first_response_time_minutes,
            t.resolution_time_hours,
            t.escalation_flag,
            t.satisfaction_score,
            c.churn_date,
            t.submitted_at,
            datediff('day', cast(t.submitted_at as date), c.churn_date) as days_before_churn
        FROM support_tickets t
        JOIN churn_events c ON t.account_id = c.account_id
        WHERE cast(t.submitted_at as date) <= c.churn_date
    )
    SELECT 
        CASE 
            WHEN days_before_churn <= 14 THEN '0-14 dias antes'
            WHEN days_before_churn <= 30 THEN '15-30 dias antes'
            WHEN days_before_churn <= 60 THEN '31-60 dias antes'
            ELSE '60+ dias antes'
        END as window,
        count(*) as ticket_count,
        round(avg(first_response_time_minutes), 1) as avg_frt,
        round(avg(resolution_time_hours), 1) as avg_res_hours,
        round(100.0 * sum(CASE WHEN escalation_flag THEN 1 ELSE 0 END) / count(*), 1) as escalation_pct,
        round(avg(satisfaction_score), 2) as avg_csat,
        round(100.0 * sum(CASE WHEN satisfaction_score IS NULL THEN 1 ELSE 0 END) / count(*), 1) as unrated_csat_pct
    FROM ticket_churn_delta
    GROUP BY 1
    ORDER BY min(days_before_churn)
""").df()
print(df_ticket_lead.to_string(index=False))

print("\n=== 4. AS CONTAS ENTERPRISE QUE CHURNEARAM: PERFIL E MOTIVOS ===")
df_ent_churn = con.execute("""
    SELECT 
        a.account_id,
        a.account_name,
        a.industry,
        a.seats,
        c.reason_code,
        c.feedback_text,
        c.refund_amount_usd,
        c.preceding_downgrade_flag,
        s.mrr_amount
    FROM accounts a
    JOIN churn_events c ON a.account_id = c.account_id
    JOIN (
        SELECT account_id, mrr_amount, row_number() over (partition by account_id order by start_date desc) as rn
        FROM subscriptions
    ) s ON a.account_id = s.account_id AND s.rn = 1
    WHERE a.plan_tier = 'Enterprise' AND a.churn_flag = True
    ORDER BY s.mrr_amount DESC
    LIMIT 10
""").df()
print(df_ent_churn.to_string(index=False))

