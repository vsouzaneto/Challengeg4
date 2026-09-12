-- ==============================================================================
-- 03_gold/retention_cohorts.sql
-- Matrizes de Coortes de Retenção: Logo Retention e Revenue Retention (NRR)
-- ==============================================================================

CREATE SCHEMA IF NOT EXISTS gold;

-- 1. BASE DE COORTES (Visão Intermediária)
CREATE OR REPLACE VIEW gold.vw_cohort_monthly_panel AS
WITH cohort_base AS (
    SELECT 
        a.account_id,
        a.plan_tier AS initial_plan,
        strftime(a.signup_date, '%Y-%m') AS cohort_month,
        year(a.signup_date) AS cohort_year,
        a.signup_date,
        s.mrr_amount AS initial_mrr
    FROM silver.accounts a
    JOIN silver.subscriptions s 
        ON a.account_id = s.account_id
    QUALIFY ROW_NUMBER() OVER (PARTITION BY a.account_id ORDER BY s.start_date ASC, s.subscription_id ASC) = 1
),
months_grid AS (
    SELECT UNNEST(generate_series(DATE '2021-02-01', DATE '2026-01-01', INTERVAL 1 MONTH))::DATE AS activity_month
)
SELECT 
    c.cohort_month,
    c.cohort_year,
    c.initial_plan,
    c.account_id,
    c.initial_mrr,
    m.activity_month,
    datediff('month', DATE (c.cohort_month || '-01'), m.activity_month) AS month_number,
    COALESCE(s.mrr_amount, 0.00) AS current_mrr,
    (s.mrr_amount > 0) AS is_active
FROM cohort_base c
CROSS JOIN months_grid m
LEFT JOIN silver.subscriptions s 
    ON c.account_id = s.account_id
   AND s.start_date <= (m.activity_month + INTERVAL 1 MONTH - INTERVAL 1 DAY)::DATE
   AND (s.effective_end_date IS NULL OR s.effective_end_date >= m.activity_month)
   AND s.is_quarantined = FALSE
WHERE m.activity_month >= DATE (c.cohort_month || '-01')
  AND datediff('month', DATE (c.cohort_month || '-01'), m.activity_month) <= 24
QUALIFY ROW_NUMBER() OVER (PARTITION BY c.account_id, m.activity_month ORDER BY s.start_date DESC, s.subscription_id DESC) = 1;

-- 2. TABELA AGREGADA: LOGO RETENTION (Por Safra Mensal)
CREATE OR REPLACE TABLE gold.agg_cohort_logo_retention AS
SELECT 
    cohort_month,
    count(DISTINCT account_id) AS cohort_size,
    round(count(DISTINCT CASE WHEN month_number = 1 AND is_active THEN account_id END) * 100.0 / count(DISTINCT account_id), 1) AS m1_ret_pct,
    round(count(DISTINCT CASE WHEN month_number = 2 AND is_active THEN account_id END) * 100.0 / count(DISTINCT account_id), 1) AS m2_ret_pct,
    round(count(DISTINCT CASE WHEN month_number = 3 AND is_active THEN account_id END) * 100.0 / count(DISTINCT account_id), 1) AS m3_ret_pct,
    round(count(DISTINCT CASE WHEN month_number = 6 AND is_active THEN account_id END) * 100.0 / count(DISTINCT account_id), 1) AS m6_ret_pct,
    round(count(DISTINCT CASE WHEN month_number = 12 AND is_active THEN account_id END) * 100.0 / count(DISTINCT account_id), 1) AS m12_ret_pct
FROM gold.vw_cohort_monthly_panel
GROUP BY cohort_month
ORDER BY cohort_month;

-- 3. TABELA AGREGADA: NET REVENUE RETENTION (NRR) (Por Safra Mensal)
CREATE OR REPLACE TABLE gold.agg_cohort_revenue_retention AS
SELECT 
    cohort_month,
    round(sum(initial_mrr), 2) AS initial_cohort_mrr,
    round(sum(CASE WHEN month_number = 1 THEN current_mrr ELSE 0 END) * 100.0 / nullif(sum(initial_mrr), 0), 1) AS m1_nrr_pct,
    round(sum(CASE WHEN month_number = 2 THEN current_mrr ELSE 0 END) * 100.0 / nullif(sum(initial_mrr), 0), 1) AS m2_nrr_pct,
    round(sum(CASE WHEN month_number = 3 THEN current_mrr ELSE 0 END) * 100.0 / nullif(sum(initial_mrr), 0), 1) AS m3_nrr_pct,
    round(sum(CASE WHEN month_number = 6 THEN current_mrr ELSE 0 END) * 100.0 / nullif(sum(initial_mrr), 0), 1) AS m6_nrr_pct,
    round(sum(CASE WHEN month_number = 12 THEN current_mrr ELSE 0 END) * 100.0 / nullif(sum(initial_mrr), 0), 1) AS m12_nrr_pct
FROM gold.vw_cohort_monthly_panel
GROUP BY cohort_month
ORDER BY cohort_month;

-- 4. CONSOLIDAÇÃO ANUAL DE COORTES (Visão Executiva)
CREATE OR REPLACE TABLE gold.agg_cohort_annual_summary AS
SELECT 
    cohort_year,
    count(DISTINCT account_id) AS total_accounts,
    round(sum(initial_mrr), 2) AS total_initial_mrr,
    round(count(DISTINCT CASE WHEN month_number = 3 AND is_active THEN account_id END) * 100.0 / count(DISTINCT account_id), 1) AS logo_ret_m3_pct,
    round(count(DISTINCT CASE WHEN month_number = 6 AND is_active THEN account_id END) * 100.0 / count(DISTINCT account_id), 1) AS logo_ret_m6_pct,
    round(count(DISTINCT CASE WHEN month_number = 12 AND is_active THEN account_id END) * 100.0 / count(DISTINCT account_id), 1) AS logo_ret_m12_pct,
    round(sum(CASE WHEN month_number = 12 THEN current_mrr ELSE 0 END) * 100.0 / nullif(sum(initial_mrr), 0), 1) AS revenue_ret_m12_nrr_pct
FROM gold.vw_cohort_monthly_panel
GROUP BY cohort_year
ORDER BY cohort_year;
