-- ==============================================================================
-- 03_gold/facts.sql
-- Modelagem Dimensional: Tabelas Fato na Camada Gold
-- ==============================================================================

CREATE SCHEMA IF NOT EXISTS gold;

-- 1. FATO ASSINATURAS (fato_assinaturas)
CREATE OR REPLACE TABLE gold.fato_assinaturas AS
SELECT
    s.subscription_id,
    s.account_id,
    s.start_date,
    s.end_date,
    s.effective_end_date,
    s.plan_tier,
    s.seats,
    s.mrr_amount,
    s.arr_amount,
    s.is_trial,
    s.upgrade_flag,
    s.downgrade_flag,
    s.churn_flag,
    s.billing_frequency,
    s.auto_renew_flag,
    s.is_latest_contract,
    s.is_currently_active
FROM silver.subscriptions s
WHERE s.is_quarantined = FALSE;

-- 2. FATO EVENTOS DE USO (fato_eventos_uso)
CREATE OR REPLACE TABLE gold.fato_eventos_uso AS
SELECT
    u.usage_id,
    u.subscription_id,
    s.account_id,
    s.plan_tier,
    u.usage_date,
    strftime(u.usage_date, '%Y-%m') AS usage_month,
    u.feature_name,
    u.usage_count,
    u.usage_duration_secs,
    u.error_count,
    u.is_beta_feature,
    CASE WHEN u.usage_count > 0 THEN round(u.error_count * 100.0 / u.usage_count, 2) ELSE 0 END AS error_rate_pct
FROM silver.feature_usage u
JOIN silver.subscriptions s ON u.subscription_id = s.subscription_id;

-- 3. FATO ATENDIMENTO (fato_atendimento)
CREATE OR REPLACE TABLE gold.fato_atendimento AS
SELECT
    t.ticket_id,
    t.account_id,
    a.plan_tier,
    t.submitted_at,
    t.closed_at,
    strftime(t.submitted_at, '%Y-%m') AS ticket_month,
    t.resolution_time_hours,
    t.priority,
    t.first_response_time_minutes,
    t.satisfaction_score,
    CASE 
        WHEN t.satisfaction_score IS NULL THEN 'Sem Avaliação'
        WHEN t.satisfaction_score <= 2.0 THEN 'Insatisfeito (1-2)'
        WHEN t.satisfaction_score = 3.0 THEN 'Neutro (3)'
        ELSE 'Satisfeito (4-5)'
    END AS csat_tier,
    t.escalation_flag,
    t.is_sla_anomalous
FROM silver.support_tickets t
JOIN silver.accounts a ON t.account_id = a.account_id;

-- 4. FATO CHURN (fato_churn)
CREATE OR REPLACE TABLE gold.fato_churn AS
SELECT
    c.churn_event_id,
    c.account_id,
    s.plan_tier,
    c.churn_date,
    strftime(c.churn_date, '%Y-%m') AS churn_month,
    c.reason_code,
    s.mrr_amount AS churned_mrr,
    c.refund_amount_usd,
    c.preceding_upgrade_flag,
    c.preceding_downgrade_flag,
    c.is_reactivation,
    c.feedback_text
FROM silver.churn_events c
JOIN silver.subscriptions s 
    ON c.account_id = s.account_id 
   AND c.churn_date = s.end_date 
   AND s.churn_flag = TRUE;
