-- ==============================================================================
-- 01_bronze/ingest.sql
-- Ingestão Determinística das 5 Tabelas Brutas RavenStack no DuckDB
-- ==============================================================================

CREATE SCHEMA IF NOT EXISTS bronze;

-- Ingestão de Contas (ravenstack_accounts)
CREATE OR REPLACE TABLE bronze.accounts AS
SELECT
    account_id::VARCHAR AS account_id,
    account_name::VARCHAR AS account_name,
    industry::VARCHAR AS industry,
    country::VARCHAR AS country,
    signup_date::DATE AS signup_date,
    referral_source::VARCHAR AS referral_source,
    plan_tier::VARCHAR AS plan_tier,
    seats::INTEGER AS seats,
    is_trial::BOOLEAN AS is_trial,
    churn_flag::BOOLEAN AS churn_flag
FROM read_csv_auto('submissions/adailton-montinegro/solution/data/raw/ravenstack_accounts.csv');

-- Ingestão de Assinaturas (ravenstack_subscriptions)
CREATE OR REPLACE TABLE bronze.subscriptions AS
SELECT
    subscription_id::VARCHAR AS subscription_id,
    account_id::VARCHAR AS account_id,
    start_date::DATE AS start_date,
    end_date::DATE AS end_date,
    plan_tier::VARCHAR AS plan_tier,
    seats::INTEGER AS seats,
    mrr_amount::DECIMAL(10,2) AS mrr_amount,
    arr_amount::DECIMAL(10,2) AS arr_amount,
    is_trial::BOOLEAN AS is_trial,
    upgrade_flag::BOOLEAN AS upgrade_flag,
    downgrade_flag::BOOLEAN AS downgrade_flag,
    churn_flag::BOOLEAN AS churn_flag,
    billing_frequency::VARCHAR AS billing_frequency,
    auto_renew_flag::BOOLEAN AS auto_renew_flag
FROM read_csv_auto('submissions/adailton-montinegro/solution/data/raw/ravenstack_subscriptions.csv');

-- Ingestão de Eventos de Uso (ravenstack_feature_usage)
CREATE OR REPLACE TABLE bronze.feature_usage AS
SELECT
    usage_id::VARCHAR AS usage_id,
    subscription_id::VARCHAR AS subscription_id,
    usage_date::DATE AS usage_date,
    feature_name::VARCHAR AS feature_name,
    usage_count::INTEGER AS usage_count,
    usage_duration_secs::INTEGER AS usage_duration_secs,
    error_count::INTEGER AS error_count,
    is_beta_feature::BOOLEAN AS is_beta_feature
FROM read_csv_auto('submissions/adailton-montinegro/solution/data/raw/ravenstack_feature_usage.csv');

-- Ingestão de Tickets de Suporte (ravenstack_support_tickets)
CREATE OR REPLACE TABLE bronze.support_tickets AS
SELECT
    ticket_id::VARCHAR AS ticket_id,
    account_id::VARCHAR AS account_id,
    submitted_at::TIMESTAMP AS submitted_at,
    closed_at::TIMESTAMP AS closed_at,
    resolution_time_hours::DECIMAL(10,2) AS resolution_time_hours,
    priority::VARCHAR AS priority,
    first_response_time_minutes::INTEGER AS first_response_time_minutes,
    satisfaction_score::DECIMAL(3,1) AS satisfaction_score,
    escalation_flag::BOOLEAN AS escalation_flag
FROM read_csv_auto('submissions/adailton-montinegro/solution/data/raw/ravenstack_support_tickets.csv');

-- Ingestão de Eventos de Churn (ravenstack_churn_events)
CREATE OR REPLACE TABLE bronze.churn_events AS
SELECT
    churn_event_id::VARCHAR AS churn_event_id,
    account_id::VARCHAR AS account_id,
    churn_date::DATE AS churn_date,
    reason_code::VARCHAR AS reason_code,
    refund_amount_usd::DECIMAL(10,2) AS refund_amount_usd,
    preceding_upgrade_flag::BOOLEAN AS preceding_upgrade_flag,
    preceding_downgrade_flag::BOOLEAN AS preceding_downgrade_flag,
    is_reactivation::BOOLEAN AS is_reactivation,
    feedback_text::VARCHAR AS feedback_text
FROM read_csv_auto('submissions/adailton-montinegro/solution/data/raw/ravenstack_churn_events.csv');
