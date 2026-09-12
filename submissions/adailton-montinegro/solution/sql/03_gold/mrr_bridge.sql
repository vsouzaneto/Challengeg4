-- ==============================================================================
-- 03_gold/mrr_bridge.sql
-- Tabela Analítica Agregada de Decomposição Mensal de Receita (MRR Bridge)
-- ==============================================================================

CREATE SCHEMA IF NOT EXISTS gold;

CREATE OR REPLACE TABLE gold.agg_mrr_bridge AS
WITH months AS (
    SELECT UNNEST(generate_series(DATE '2021-02-01', DATE '2026-01-01', INTERVAL 1 MONTH))::DATE AS m_start,
           (m_start + INTERVAL 1 MONTH - INTERVAL 1 DAY)::DATE AS m_end
),
account_months AS (
    SELECT 
        m.m_start,
        a.account_id,
        a.signup_date,
        s.subscription_id,
        s.plan_tier,
        s.mrr_amount
    FROM months m
    CROSS JOIN silver.accounts a
    LEFT JOIN silver.subscriptions s 
        ON a.account_id = s.account_id
       AND s.start_date <= m.m_end
       AND (s.effective_end_date IS NULL OR s.effective_end_date >= m.m_start)
       AND s.is_quarantined = FALSE
    QUALIFY ROW_NUMBER() OVER (PARTITION BY m.m_start, a.account_id ORDER BY s.start_date DESC, s.subscription_id DESC) = 1
),
monthly_account_mrr AS (
    SELECT 
        m_start,
        account_id,
        signup_date,
        COALESCE(mrr_amount, 0.00) AS mrr,
        plan_tier,
        LAG(COALESCE(mrr_amount, 0.00), 1, 0.00) OVER (PARTITION BY account_id ORDER BY m_start) AS prev_mrr
    FROM account_months
),
bridge_monthly AS (
    SELECT 
        m_start AS month_date,
        strftime(m_start, '%Y-%m') AS year_month,
        round(sum(prev_mrr), 2) AS beginning_mrr,
        round(sum(CASE WHEN prev_mrr = 0.00 AND mrr > 0.00 AND signup_date >= m_start THEN mrr ELSE 0.00 END), 2) AS new_mrr,
        round(sum(CASE WHEN prev_mrr = 0.00 AND mrr > 0.00 AND signup_date < m_start THEN mrr ELSE 0.00 END), 2) AS reactivation_mrr,
        round(sum(CASE WHEN prev_mrr > 0.00 AND mrr > prev_mrr THEN mrr - prev_mrr ELSE 0.00 END), 2) AS expansion_mrr,
        round(sum(CASE WHEN prev_mrr > 0.00 AND mrr > 0.00 AND mrr < prev_mrr THEN prev_mrr - mrr ELSE 0.00 END), 2) AS contraction_mrr,
        round(sum(CASE WHEN prev_mrr > 0.00 AND mrr = 0.00 THEN prev_mrr ELSE 0.00 END), 2) AS churned_mrr,
        round(sum(mrr), 2) AS ending_mrr,
        count(DISTINCT CASE WHEN mrr > 0.00 THEN account_id END) AS active_accounts,
        count(DISTINCT CASE WHEN prev_mrr > 0.00 AND mrr = 0.00 THEN account_id END) AS churned_accounts
    FROM monthly_account_mrr
    GROUP BY m_start
)
SELECT 
    b.*,
    round(b.new_mrr + b.expansion_mrr - b.contraction_mrr - b.churned_mrr + b.reactivation_mrr, 2) AS net_mrr,
    CASE WHEN b.beginning_mrr > 0 THEN round(b.churned_mrr * 100.0 / b.beginning_mrr, 2) ELSE 0.00 END AS gross_revenue_churn_rate_pct,
    CASE WHEN b.beginning_mrr > 0 THEN round((b.beginning_mrr + b.expansion_mrr - b.contraction_mrr - b.churned_mrr) * 100.0 / b.beginning_mrr, 2) ELSE 100.00 END AS net_revenue_retention_pct,
    CASE WHEN (b.contraction_mrr + b.churned_mrr) > 0 THEN round((b.new_mrr + b.expansion_mrr + b.reactivation_mrr) / (b.contraction_mrr + b.churned_mrr), 2) ELSE NULL END AS saas_quick_ratio
FROM bridge_monthly b
ORDER BY month_date;
