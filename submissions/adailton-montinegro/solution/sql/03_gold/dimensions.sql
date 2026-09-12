-- ==============================================================================
-- 03_gold/dimensions.sql
-- Modelagem Dimensional: Dimensões de Negócio na Camada Gold
-- ==============================================================================

CREATE SCHEMA IF NOT EXISTS gold;

-- 1. DIMENSÃO DE CONTAS (dim_accounts)
CREATE OR REPLACE TABLE gold.dim_accounts AS
SELECT
    a.account_id,
    a.account_name,
    a.industry,
    a.country,
    a.signup_date,
    strftime(a.signup_date, '%Y-%m') AS signup_cohort_month,
    year(a.signup_date) AS signup_year,
    a.referral_source,
    a.plan_tier,
    a.seats,
    a.is_trial,
    a.churn_flag,
    c.churn_date,
    c.reason_code AS primary_churn_reason,
    datediff('month', a.signup_date, COALESCE(c.churn_date, DATE '2026-01-31')) AS account_lifespan_months
FROM silver.accounts a
LEFT JOIN (
    -- Pega o primeiro ou mais recente evento de churn associado à conta
    SELECT account_id, min(churn_date) AS churn_date, arg_min(reason_code, churn_date) AS reason_code
    FROM silver.churn_events
    GROUP BY account_id
) c ON a.account_id = c.account_id;

-- 2. DIMENSÃO DE PLANOS (dim_plans)
CREATE OR REPLACE TABLE gold.dim_plans AS
SELECT 
    plan_tier,
    CASE 
        WHEN plan_tier = 'Enterprise' THEN 200.00
        WHEN plan_tier = 'Pro' THEN 80.00
        WHEN plan_tier = 'Basic' THEN 30.00
    END AS base_price_per_seat,
    CASE 
        WHEN plan_tier = 'Enterprise' THEN 'Suporte Dedicado 24/7, SLA 99.9%, Acesso Antecipado a Betas'
        WHEN plan_tier = 'Pro' THEN 'Suporte Prioritário Comercial, Analytics Avançado'
        WHEN plan_tier = 'Basic' THEN 'Suporte Comunitário Standard, Features Core'
    END AS tier_benefits
FROM (SELECT DISTINCT plan_tier FROM silver.subscriptions);
