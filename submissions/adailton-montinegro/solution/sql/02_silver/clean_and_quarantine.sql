-- ==============================================================================
-- 02_silver/clean_and_quarantine.sql
-- Camada de Qualidade, Saneamento e Tabela de Quarentena no DuckDB
-- ==============================================================================

CREATE SCHEMA IF NOT EXISTS silver;

-- 1. TABELA DE QUARENTENA DE INCONSISTÊNCIAS
-- Não descarta dados silenciosamente: isola com rastreabilidade e impacto contábil
CREATE OR REPLACE TABLE silver.quarentena_inconsistencias AS
-- Anomalia 1: Assinaturas antigas sem end_date substituídas por novos planos (Phantom MRR)
SELECT
    uuid() AS quarantine_id,
    'subscriptions' AS source_table,
    s.subscription_id AS record_id,
    s.account_id,
    'HISTORICAL_OVERLAP_NO_END_DATE' AS anomaly_type,
    'Assinatura substituída por novo plano sem fechamento de end_date no sistema de cobrança' AS anomaly_description,
    s.mrr_amount AS impact_mrr,
    s.start_date AS reference_date,
    CURRENT_TIMESTAMP AS detected_at
FROM (
    SELECT *,
        LEAD(start_date) OVER (PARTITION BY account_id ORDER BY start_date, subscription_id) AS next_start_date
    FROM bronze.subscriptions
) s
WHERE s.end_date IS NULL AND s.next_start_date IS NOT NULL

UNION ALL

-- Anomalia 2: Chamados de suporte onde primeiro atendimento é posterior ao fechamento do ticket
SELECT
    uuid() AS quarantine_id,
    'support_tickets' AS source_table,
    t.ticket_id AS record_id,
    t.account_id,
    'INVALID_FIRST_RESPONSE_AFTER_CLOSE' AS anomaly_type,
    'Timestamp de primeira resposta registrado posterior ao encerramento do chamado' AS anomaly_description,
    0.00::DECIMAL(10,2) AS impact_mrr,
    CAST(t.submitted_at AS DATE) AS reference_date,
    CURRENT_TIMESTAMP AS detected_at
FROM bronze.support_tickets t
WHERE t.closed_at IS NOT NULL 
  AND t.submitted_at + (t.first_response_time_minutes || ' minutes')::INTERVAL > t.closed_at

UNION ALL

-- Anomalia 3: Transações com datas futuras além do corte operacional do dataset (2026-01-31)
SELECT
    uuid() AS quarantine_id,
    'subscriptions' AS source_table,
    s.subscription_id AS record_id,
    s.account_id,
    'FUTURE_DATED_TRANSACTION' AS anomaly_type,
    'Assinatura com data de início posterior ao corte operacional do dataset (2026-01-31)' AS anomaly_description,
    s.mrr_amount AS impact_mrr,
    s.start_date AS reference_date,
    CURRENT_TIMESTAMP AS detected_at
FROM bronze.subscriptions s
WHERE s.start_date > '2026-01-31';

-- 2. TABELA SANEADA: silver.accounts
CREATE OR REPLACE TABLE silver.accounts AS
SELECT
    account_id,
    TRIM(account_name) AS account_name,
    TRIM(industry) AS industry,
    UPPER(TRIM(country)) AS country,
    signup_date,
    TRIM(referral_source) AS referral_source,
    TRIM(plan_tier) AS plan_tier,
    seats,
    is_trial,
    churn_flag
FROM bronze.accounts;

-- 3. TABELA SANEADA: silver.subscriptions
-- Reconcilia end_dates implícitos e sinaliza contratos ativos
CREATE OR REPLACE TABLE silver.subscriptions AS
WITH sub_windowed AS (
    SELECT
        s.*,
        LEAD(s.start_date) OVER (PARTITION BY s.account_id ORDER BY s.start_date, s.subscription_id) AS next_start_date,
        ROW_NUMBER() OVER (PARTITION BY s.account_id ORDER BY s.start_date DESC, s.subscription_id DESC) AS rn_desc
    FROM bronze.subscriptions s
)
SELECT
    sw.subscription_id,
    sw.account_id,
    sw.start_date,
    sw.end_date,
    -- end_date efetivo: preenche o buraco histórico onde novo plano iniciou
    COALESCE(sw.end_date, sw.next_start_date) AS effective_end_date,
    TRIM(sw.plan_tier) AS plan_tier,
    sw.seats,
    sw.mrr_amount,
    sw.arr_amount,
    sw.is_trial,
    sw.upgrade_flag,
    sw.downgrade_flag,
    sw.churn_flag,
    sw.billing_frequency,
    sw.auto_renew_flag,
    -- Indicadores de estado operacional
    (sw.rn_desc = 1) AS is_latest_contract,
    (sw.rn_desc = 1 AND sw.churn_flag = FALSE AND (sw.end_date IS NULL OR sw.end_date > '2026-01-31')) AS is_currently_active,
    (q.record_id IS NOT NULL) AS is_quarantined
FROM sub_windowed sw
LEFT JOIN (
    SELECT DISTINCT record_id FROM silver.quarentena_inconsistencias WHERE source_table = 'subscriptions'
) q ON sw.subscription_id = q.record_id;

-- 4. TABELA SANEADA: silver.support_tickets
CREATE OR REPLACE TABLE silver.support_tickets AS
SELECT
    t.ticket_id,
    t.account_id,
    t.submitted_at,
    t.closed_at,
    t.resolution_time_hours,
    LOWER(TRIM(t.priority)) AS priority,
    t.first_response_time_minutes,
    t.satisfaction_score,
    t.escalation_flag,
    (q.record_id IS NOT NULL) AS is_sla_anomalous
FROM bronze.support_tickets t
LEFT JOIN (
    SELECT DISTINCT record_id FROM silver.quarentena_inconsistencias WHERE source_table = 'support_tickets'
) q ON t.ticket_id = q.record_id;

-- 5. TABELA SANEADA: silver.feature_usage
CREATE OR REPLACE TABLE silver.feature_usage AS
SELECT
    usage_id,
    subscription_id,
    usage_date,
    LOWER(TRIM(feature_name)) AS feature_name,
    usage_count,
    usage_duration_secs,
    error_count,
    is_beta_feature
FROM bronze.feature_usage;

-- 6. TABELA SANEADA: silver.churn_events
CREATE OR REPLACE TABLE silver.churn_events AS
SELECT
    churn_event_id,
    account_id,
    churn_date,
    LOWER(TRIM(reason_code)) AS reason_code,
    refund_amount_usd,
    preceding_upgrade_flag,
    preceding_downgrade_flag,
    is_reactivation,
    NULLIF(TRIM(feedback_text), '') AS feedback_text
FROM bronze.churn_events;
