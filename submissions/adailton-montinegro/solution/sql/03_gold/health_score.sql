-- ==============================================================================
-- 03_gold/health_score.sql
-- Modelo Heurístico de Health Score (0 a 100) e Segmentação de Risco de Churn
-- ==============================================================================

CREATE SCHEMA IF NOT EXISTS gold;

CREATE OR REPLACE TABLE gold.agg_account_health_score AS
WITH account_usage_stats AS (
    SELECT 
        s.account_id,
        count(u.usage_id) AS total_usage_events,
        sum(u.usage_count) AS total_usage_count,
        sum(u.error_count) AS total_errors,
        sum(CASE WHEN u.is_beta_feature THEN u.error_count ELSE 0 END) AS beta_errors,
        max(u.usage_date) AS last_usage_date
    FROM silver.subscriptions s
    JOIN silver.feature_usage u ON s.subscription_id = u.subscription_id
    GROUP BY s.account_id
),
account_support_stats AS (
    SELECT 
        t.account_id,
        count(*) AS total_tickets,
        count(CASE WHEN t.escalation_flag THEN 1 END) AS escalated_tickets,
        count(CASE WHEN t.satisfaction_score <= 2.0 THEN 1 END) AS low_csat_tickets,
        avg(t.satisfaction_score) AS avg_csat,
        avg(t.resolution_time_hours) AS avg_resolution_hours,
        max(t.submitted_at) AS last_ticket_date
    FROM silver.support_tickets t
    GROUP BY t.account_id
),
account_contract_stats AS (
    SELECT 
        s.account_id,
        s.plan_tier,
        s.mrr_amount,
        s.billing_frequency,
        s.auto_renew_flag,
        s.downgrade_flag,
        s.upgrade_flag,
        s.is_currently_active
    FROM silver.subscriptions s
    WHERE s.is_latest_contract = TRUE
),
scoring AS (
    SELECT 
        a.account_id,
        a.account_name,
        a.industry,
        a.country,
        c.plan_tier,
        c.mrr_amount,
        c.is_currently_active,
        a.churn_flag,
        COALESCE(u.total_usage_count, 0) AS usage_count,
        COALESCE(u.total_errors, 0) AS total_errors,
        COALESCE(t.total_tickets, 0) AS total_tickets,
        COALESCE(t.low_csat_tickets, 0) AS low_csat_tickets,
        COALESCE(t.escalated_tickets, 0) AS escalated_tickets,
        COALESCE(t.avg_csat, 3.5) AS avg_csat,
        
        -- 1. Pilar Engajamento (Base 30 pontos)
        LEAST(30, GREATEST(0, CAST(round(COALESCE(u.total_usage_count, 0) * 0.5) AS INT))) AS score_engagement,
        
        -- 2. Pilar Estabilidade Técnica (Base 25 pontos, deduz erros)
        GREATEST(0, 25 - (COALESCE(u.total_errors, 0) * 4)) AS score_stability,
        
        -- 3. Pilar Suporte e Experiência (Base 25 pontos, deduz escalações e notas baixas)
        GREATEST(0, 25 - (COALESCE(t.low_csat_tickets, 0) * 6) - (COALESCE(t.escalated_tickets, 0) * 5)) AS score_support,
        
        -- 4. Pilar Contratual (Base 20 pontos)
        (CASE WHEN c.downgrade_flag THEN 0 ELSE 10 END) +
        (CASE WHEN c.auto_renew_flag THEN 5 ELSE 0 END) +
        (CASE WHEN c.billing_frequency = 'annual' THEN 5 ELSE 0 END) AS score_contract
    FROM silver.accounts a
    JOIN account_contract_stats c ON a.account_id = c.account_id
    LEFT JOIN account_usage_stats u ON a.account_id = u.account_id
    LEFT JOIN account_support_stats t ON a.account_id = t.account_id
)
SELECT 
    s.*,
    (s.score_engagement + s.score_stability + s.score_support + s.score_contract) AS health_score,
    CASE 
        WHEN (s.score_engagement + s.score_stability + s.score_support + s.score_contract) >= 70 THEN 'Verde (Saudável)'
        WHEN (s.score_engagement + s.score_stability + s.score_support + s.score_contract) >= 50 THEN 'Amarelo (Atenção)'
        ELSE 'Vermelho (Crítico / Risco Alto)'
    END AS risk_tier,
    -- Estimativa de ARR em risco
    CASE 
        WHEN (s.score_engagement + s.score_stability + s.score_support + s.score_contract) < 50 AND s.is_currently_active THEN s.mrr_amount * 12
        ELSE 0.00
    END AS arr_at_risk
FROM scoring s
ORDER BY health_score ASC;
