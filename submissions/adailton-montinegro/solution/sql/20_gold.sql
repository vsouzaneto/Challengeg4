-- Gold contains reviewable facts and derived analytical universes. It never
-- reconciles competing churn definitions into a fabricated single truth.

CREATE TABLE gold.quality_rule_catalog (
    rule_id VARCHAR PRIMARY KEY,
    table_name VARCHAR NOT NULL,
    severity VARCHAR NOT NULL,
    description VARCHAR NOT NULL
);

INSERT INTO gold.quality_rule_catalog VALUES
('account_missing_id', 'accounts', 'error', 'Conta sem identificador.'),
('account_duplicate_id_conflict', 'accounts', 'error', 'Mesmo account_id possui conteúdos divergentes.'),
('account_duplicate_surplus', 'accounts', 'error', 'Linha duplicada excedente.'),
('account_invalid_signup_date', 'accounts', 'error', 'Data de cadastro ausente ou inválida.'),
('account_invalid_seats', 'accounts', 'error', 'Quantidade de licenças ausente ou não positiva.'),
('account_invalid_boolean', 'accounts', 'error', 'Flag booleana inválida.'),
('account_unknown_plan', 'accounts', 'warning', 'Plano fora do domínio conhecido.'),
('account_unknown_referral_source', 'accounts', 'warning', 'Canal de aquisição ausente.'),
('subscription_missing_id', 'subscriptions', 'error', 'Assinatura sem identificador.'),
('subscription_duplicate_id_conflict', 'subscriptions', 'error', 'Mesmo subscription_id possui conteúdos divergentes.'),
('subscription_duplicate_surplus', 'subscriptions', 'error', 'Linha duplicada excedente.'),
('subscription_orphan_account', 'subscriptions', 'error', 'Assinatura não referencia uma conta elegível.'),
('subscription_invalid_start_date', 'subscriptions', 'error', 'Início da assinatura ausente ou inválido.'),
('subscription_end_before_start', 'subscriptions', 'error', 'Fim da assinatura anterior ao início.'),
('subscription_start_before_signup', 'subscriptions', 'error', 'Assinatura começa antes do cadastro da conta.'),
('subscription_invalid_seats', 'subscriptions', 'error', 'Quantidade de licenças ausente ou não positiva.'),
('subscription_invalid_amount', 'subscriptions', 'error', 'MRR/ARR ausente ou negativo.'),
('subscription_invalid_boolean', 'subscriptions', 'error', 'Flag booleana inválida.'),
('subscription_arr_mrr_mismatch', 'subscriptions', 'warning', 'ARR difere de doze vezes o MRR.'),
('subscription_unknown_billing_frequency', 'subscriptions', 'warning', 'Frequência de cobrança fora do domínio conhecido.'),
('subscription_account_plan_mismatch', 'subscriptions', 'warning', 'Plano da assinatura diverge do snapshot da conta.'),
('subscription_overlap_unresolved', 'subscriptions', 'warning', 'Assinatura se sobrepõe a outra sem dimensão de produto.'),
('usage_missing_id', 'feature_usage', 'error', 'Uso sem identificador.'),
('usage_duplicate_id_conflict', 'feature_usage', 'error', 'Mesmo usage_id possui conteúdos divergentes.'),
('usage_duplicate_surplus', 'feature_usage', 'error', 'Linha duplicada excedente.'),
('usage_orphan_subscription', 'feature_usage', 'error', 'Uso não referencia uma assinatura elegível.'),
('usage_invalid_date', 'feature_usage', 'error', 'Data de uso ausente ou inválida.'),
('usage_invalid_measure', 'feature_usage', 'error', 'Métrica de uso ausente ou negativa.'),
('usage_invalid_boolean', 'feature_usage', 'error', 'Flag booleana inválida.'),
('usage_before_signup', 'feature_usage', 'error', 'Uso anterior ao cadastro da conta.'),
('usage_before_subscription', 'feature_usage', 'error', 'Uso anterior ao início da assinatura.'),
('usage_after_subscription', 'feature_usage', 'error', 'Uso posterior ao fim da assinatura.'),
('usage_unknown_feature', 'feature_usage', 'warning', 'Feature ausente ou desconhecida.'),
('support_missing_id', 'support_tickets', 'error', 'Ticket sem identificador.'),
('support_duplicate_id_conflict', 'support_tickets', 'error', 'Mesmo ticket_id possui conteúdos divergentes.'),
('support_duplicate_surplus', 'support_tickets', 'error', 'Linha duplicada excedente.'),
('support_orphan_account', 'support_tickets', 'error', 'Ticket não referencia uma conta elegível.'),
('support_invalid_submitted_at', 'support_tickets', 'error', 'Data de abertura ausente ou inválida.'),
('support_closed_before_submitted', 'support_tickets', 'error', 'Fechamento anterior à abertura.'),
('support_before_signup', 'support_tickets', 'error', 'Ticket anterior ao cadastro da conta.'),
('support_invalid_resolution_time', 'support_tickets', 'error', 'Tempo de resolução negativo.'),
('support_invalid_response_time', 'support_tickets', 'error', 'Tempo de primeira resposta negativo.'),
('support_invalid_csat', 'support_tickets', 'error', 'Satisfação fora da escala de 1 a 5.'),
('support_invalid_boolean', 'support_tickets', 'error', 'Flag booleana inválida.'),
('support_missing_csat', 'support_tickets', 'warning', 'Ticket sem avaliação de satisfação.'),
('support_unknown_priority', 'support_tickets', 'warning', 'Prioridade fora do domínio conhecido.'),
('churn_missing_id', 'churn_events', 'error', 'Evento de churn sem identificador.'),
('churn_duplicate_id_conflict', 'churn_events', 'error', 'Mesmo churn_event_id possui conteúdos divergentes.'),
('churn_duplicate_surplus', 'churn_events', 'error', 'Linha duplicada excedente.'),
('churn_orphan_account', 'churn_events', 'error', 'Evento não referencia uma conta elegível.'),
('churn_invalid_date', 'churn_events', 'error', 'Data do evento ausente ou inválida.'),
('churn_before_signup', 'churn_events', 'error', 'Evento anterior ao cadastro da conta.'),
('churn_invalid_refund', 'churn_events', 'error', 'Reembolso ausente ou negativo.'),
('churn_invalid_boolean', 'churn_events', 'error', 'Flag booleana inválida.'),
('churn_snapshot_disagreement', 'churn_events', 'warning', 'Conta com evento histórico não está churnada no snapshot.'),
('churn_unknown_reason', 'churn_events', 'warning', 'Motivo do evento ausente ou desconhecido.'),
('churn_missing_feedback', 'churn_events', 'warning', 'Evento sem texto de feedback.');

CREATE TABLE gold.quality_issues AS
WITH all_rows AS (
    SELECT 'accounts' AS table_name, source_row_number, account_id AS record_id,
           account_id, NULL::VARCHAR AS subscription_id, quality_flags
    FROM stage.accounts
    UNION ALL
    SELECT 'subscriptions', source_row_number, subscription_id, account_id,
           subscription_id, quality_flags
    FROM stage.subscriptions
    UNION ALL
    SELECT 'feature_usage', source_row_number, usage_id, account_id,
           subscription_id, quality_flags
    FROM stage.feature_usage
    UNION ALL
    SELECT 'support_tickets', source_row_number, ticket_id, account_id,
           NULL::VARCHAR, quality_flags
    FROM stage.support_tickets
    UNION ALL
    SELECT 'churn_events', source_row_number, churn_event_id, account_id,
           NULL::VARCHAR, quality_flags
    FROM stage.churn_events
), exploded AS (
    SELECT table_name, source_row_number, record_id, account_id, subscription_id,
           UNNEST(STRING_SPLIT(quality_flags, '|')) AS rule_id
    FROM all_rows
    WHERE quality_flags <> ''
)
SELECT
    MD5(CONCAT_WS('¦', e.table_name, CAST(e.source_row_number AS VARCHAR), e.rule_id)) AS issue_id,
    e.rule_id,
    e.table_name,
    e.source_row_number,
    e.record_id,
    e.account_id,
    e.subscription_id,
    r.severity,
    r.description AS issue_detail
FROM exploded e
JOIN gold.quality_rule_catalog r USING (rule_id);

CREATE TABLE gold.quality_summary AS
WITH table_totals AS (
    SELECT 'accounts' AS table_name, COUNT(*) AS total_rows FROM raw.accounts
    UNION ALL SELECT 'subscriptions', COUNT(*) FROM raw.subscriptions
    UNION ALL SELECT 'feature_usage', COUNT(*) FROM raw.feature_usage
    UNION ALL SELECT 'support_tickets', COUNT(*) FROM raw.support_tickets
    UNION ALL SELECT 'churn_events', COUNT(*) FROM raw.churn_events
), issue_counts AS (
    SELECT rule_id, COUNT(*) AS failed_rows,
           COUNT(DISTINCT COALESCE(account_id, record_id)) AS affected_entities
    FROM gold.quality_issues
    GROUP BY rule_id
)
SELECT r.rule_id, r.table_name, r.severity,
       COALESCE(i.failed_rows, 0) AS failed_rows,
       t.total_rows,
       ROUND(100.0 * COALESCE(i.failed_rows, 0) / NULLIF(t.total_rows, 0), 2) AS failure_pct,
       COALESCE(i.affected_entities, 0) AS affected_entities,
       CASE
           WHEN COALESCE(i.failed_rows, 0) = 0 THEN 'Observed'
           ELSE 'Conditional'
       END AS metric_state
FROM gold.quality_rule_catalog r
JOIN table_totals t USING (table_name)
LEFT JOIN issue_counts i USING (rule_id)
ORDER BY r.table_name, r.severity DESC, r.rule_id;

CREATE TABLE gold.account_snapshot AS
WITH cutoff AS (
    SELECT data_cutoff FROM stage.dataset_bounds
), active_paid_subscriptions AS (
    SELECT s.account_id, s.subscription_id, s.mrr_amount
    FROM stage.subscriptions s, cutoff c
    WHERE s.is_eligible
      AND NOT s.is_trial
      AND s.start_date <= c.data_cutoff
      AND (s.end_date IS NULL OR s.end_date >= c.data_cutoff)
), revenue_proxy AS (
    SELECT account_id, MAX(mrr_amount) AS mrr_proxy_conservative,
           SUM(mrr_amount) AS mrr_proxy_additive,
           COUNT(*) AS active_paid_subscription_count
    FROM active_paid_subscriptions
    GROUP BY account_id
), event_ledger AS (
    SELECT account_id, COUNT(*) AS valid_churn_event_count
    FROM stage.churn_events
    WHERE is_eligible
    GROUP BY account_id
), overlap AS (
    SELECT account_id, BOOL_OR(has_unresolved_overlap) AS has_subscription_overlap
    FROM stage.subscriptions
    GROUP BY account_id
)
SELECT
    a.account_id,
    a.account_name,
    a.industry,
    a.country,
    a.referral_source,
    a.plan_tier,
    a.seats,
    a.is_trial,
    a.churn_flag AS snapshot_churn_flag,
    a.signup_date,
    COALESCE(e.valid_churn_event_count, 0) > 0 AS has_valid_churn_event,
    COALESCE(e.valid_churn_event_count, 0) AS valid_churn_event_count,
    COALESCE(o.has_subscription_overlap, FALSE) AS has_subscription_overlap,
    r.mrr_proxy_conservative,
    r.mrr_proxy_additive,
    CASE
        WHEN r.account_id IS NULL THEN 'Unavailable'
        WHEN r.active_paid_subscription_count = 1 AND NOT COALESCE(o.has_subscription_overlap, FALSE) THEN 'Derived'
        ELSE 'Conditional'
    END AS revenue_confidence
FROM stage.accounts a
LEFT JOIN revenue_proxy r USING (account_id)
LEFT JOIN event_ledger e USING (account_id)
LEFT JOIN overlap o USING (account_id)
WHERE a.is_eligible;

CREATE TABLE gold.monthly_events AS
WITH dates AS (
    SELECT MIN(signup_date) AS min_date, MAX(signup_date) AS max_date
    FROM stage.accounts WHERE is_eligible
    UNION ALL
    SELECT MIN(churn_date), MAX(churn_date)
    FROM stage.churn_events WHERE churn_date IS NOT NULL
), bounds AS (
    SELECT DATE_TRUNC('month', MIN(min_date))::DATE AS min_month,
           DATE_TRUNC('month', MAX(max_date))::DATE AS max_month
    FROM dates
), months AS (
    SELECT UNNEST(GENERATE_SERIES(min_month, max_month, INTERVAL '1 month'))::DATE AS month_start
    FROM bounds
), signups AS (
    SELECT DATE_TRUNC('month', signup_date)::DATE AS month_start, COUNT(*) AS new_accounts
    FROM stage.accounts WHERE is_eligible GROUP BY 1
), churns AS (
    SELECT DATE_TRUNC('month', churn_date)::DATE AS month_start,
           COUNT(*) AS raw_churn_events,
           COUNT(*) FILTER (WHERE is_eligible) AS valid_churn_events,
           COUNT(DISTINCT account_id) FILTER (WHERE is_eligible) AS distinct_accounts_with_valid_churn_events
    FROM stage.churn_events
    WHERE churn_date IS NOT NULL
    GROUP BY 1
)
SELECT m.month_start,
       COALESCE(s.new_accounts, 0) AS new_accounts,
       COALESCE(c.raw_churn_events, 0) AS raw_churn_events,
       COALESCE(c.valid_churn_events, 0) AS valid_churn_events,
       COALESCE(c.distinct_accounts_with_valid_churn_events, 0) AS distinct_accounts_with_valid_churn_events,
       CASE WHEN COALESCE(c.raw_churn_events, 0) = 0 THEN 100.0
            ELSE ROUND(100.0 * c.valid_churn_events / c.raw_churn_events, 2) END AS event_coverage_pct
FROM months m
LEFT JOIN signups s USING (month_start)
LEFT JOIN churns c USING (month_start)
ORDER BY m.month_start;

CREATE TABLE gold.segment_snapshot AS
WITH long_dimensions AS (
    SELECT account_id, snapshot_churn_flag, mrr_proxy_conservative, mrr_proxy_additive,
           'plan_tier' AS dimension_name, plan_tier AS segment_value FROM gold.account_snapshot
    UNION ALL
    SELECT account_id, snapshot_churn_flag, mrr_proxy_conservative, mrr_proxy_additive,
           'industry', industry FROM gold.account_snapshot
    UNION ALL
    SELECT account_id, snapshot_churn_flag, mrr_proxy_conservative, mrr_proxy_additive,
           'referral_source', referral_source FROM gold.account_snapshot
    UNION ALL
    SELECT account_id, snapshot_churn_flag, mrr_proxy_conservative, mrr_proxy_additive,
           'country', country FROM gold.account_snapshot
)
SELECT dimension_name, segment_value, COUNT(*) AS total_accounts,
       COUNT(*) FILTER (WHERE snapshot_churn_flag) AS snapshot_churned_accounts,
       ROUND(100.0 * COUNT(*) FILTER (WHERE snapshot_churn_flag) / COUNT(*), 2) AS snapshot_churn_rate_pct,
       ROUND(SUM(mrr_proxy_conservative), 2) AS mrr_proxy_conservative,
       ROUND(SUM(mrr_proxy_additive), 2) AS mrr_proxy_additive,
       ROUND(100.0 * (
           ((COUNT(*) FILTER (WHERE snapshot_churn_flag)::DOUBLE / COUNT(*)) + 1.96 * 1.96 / (2 * COUNT(*)))
           / (1 + 1.96 * 1.96 / COUNT(*))
           - 1.96 * SQRT(
               ((COUNT(*) FILTER (WHERE snapshot_churn_flag)::DOUBLE / COUNT(*))
                * (1 - COUNT(*) FILTER (WHERE snapshot_churn_flag)::DOUBLE / COUNT(*)) / COUNT(*))
               + 1.96 * 1.96 / (4 * COUNT(*) * COUNT(*))
           ) / (1 + 1.96 * 1.96 / COUNT(*))
       ), 2) AS wilson_ci_low_pct,
       ROUND(100.0 * (
           ((COUNT(*) FILTER (WHERE snapshot_churn_flag)::DOUBLE / COUNT(*)) + 1.96 * 1.96 / (2 * COUNT(*)))
           / (1 + 1.96 * 1.96 / COUNT(*))
           + 1.96 * SQRT(
               ((COUNT(*) FILTER (WHERE snapshot_churn_flag)::DOUBLE / COUNT(*))
                * (1 - COUNT(*) FILTER (WHERE snapshot_churn_flag)::DOUBLE / COUNT(*)) / COUNT(*))
               + 1.96 * 1.96 / (4 * COUNT(*) * COUNT(*))
           ) / (1 + 1.96 * 1.96 / COUNT(*))
       ), 2) AS wilson_ci_high_pct,
       'Chi-square'::VARCHAR AS global_test_name,
       NULL::DOUBLE AS global_p_value,
       NULL::DOUBLE AS cramers_v,
       NULL::VARCHAR AS global_interpretation
FROM long_dimensions
GROUP BY dimension_name, segment_value
ORDER BY dimension_name, segment_value;

CREATE TABLE gold.churn_reasons AS
WITH valid AS (
    SELECT reason_code, COUNT(*) AS valid_churn_events,
           COUNT(DISTINCT account_id) AS distinct_accounts,
           SUM(refund_amount_usd) AS refund_amount_usd
    FROM stage.churn_events
    WHERE is_eligible
    GROUP BY reason_code
), raw_reason AS (
    SELECT reason_code, COUNT(*) AS raw_reason_events
    FROM stage.churn_events
    GROUP BY reason_code
), total AS (
    SELECT COUNT(*) AS total_valid FROM stage.churn_events WHERE is_eligible
)
SELECT r.reason_code,
       COALESCE(v.valid_churn_events, 0) AS valid_churn_events,
       COALESCE(v.distinct_accounts, 0) AS distinct_accounts,
       ROUND(COALESCE(v.refund_amount_usd, 0), 2) AS refund_amount_usd,
       ROUND(100.0 * COALESCE(v.valid_churn_events, 0) / NULLIF(t.total_valid, 0), 2) AS event_share_pct,
       ROUND(100.0 * COALESCE(v.valid_churn_events, 0) / NULLIF(r.raw_reason_events, 0), 2) AS coverage_pct
FROM raw_reason r
LEFT JOIN valid v USING (reason_code)
CROSS JOIN total t
ORDER BY valid_churn_events DESC, reason_code;

CREATE TABLE gold.pre_event_signals AS
WITH usage_next_event AS (
    SELECT u.account_id, u.usage_id,
           DATE_DIFF('day', u.usage_date, c.next_churn_date) AS days_before_churn,
           u.usage_count, u.error_count
    FROM stage.feature_usage u
    JOIN LATERAL (
        SELECT MIN(churn_date) AS next_churn_date
        FROM stage.churn_events c
        WHERE c.is_eligible
          AND c.account_id = u.account_id
          AND c.churn_date >= u.usage_date
    ) c ON c.next_churn_date IS NOT NULL
    WHERE u.is_eligible
), support_next_event AS (
    SELECT t.account_id, t.ticket_id,
           DATE_DIFF('day', CAST(t.submitted_at AS DATE), c.next_churn_date) AS days_before_churn,
           t.escalation_flag, t.satisfaction_score
    FROM stage.support_tickets t
    JOIN LATERAL (
        SELECT MIN(churn_date) AS next_churn_date
        FROM stage.churn_events c
        WHERE c.is_eligible
          AND c.account_id = t.account_id
          AND c.churn_date >= CAST(t.submitted_at AS DATE)
    ) c ON c.next_churn_date IS NOT NULL
    WHERE t.is_eligible
), usage_windowed AS (
    SELECT CASE WHEN days_before_churn <= 14 THEN '0-14'
                WHEN days_before_churn <= 30 THEN '15-30'
                WHEN days_before_churn <= 60 THEN '31-60'
                WHEN days_before_churn <= 90 THEN '61-90'
                ELSE '91+' END AS window_label,
           CASE WHEN days_before_churn <= 14 THEN 1 WHEN days_before_churn <= 30 THEN 2
                WHEN days_before_churn <= 60 THEN 3 WHEN days_before_churn <= 90 THEN 4 ELSE 5 END AS window_order,
           COUNT(*) AS usage_events, COUNT(DISTINCT account_id) AS usage_accounts,
           SUM(usage_count) AS usage_count, SUM(error_count) AS error_count
    FROM usage_next_event
    GROUP BY 1, 2
), support_windowed AS (
    SELECT CASE WHEN days_before_churn <= 14 THEN '0-14'
                WHEN days_before_churn <= 30 THEN '15-30'
                WHEN days_before_churn <= 60 THEN '31-60'
                WHEN days_before_churn <= 90 THEN '61-90'
                ELSE '91+' END AS window_label,
           CASE WHEN days_before_churn <= 14 THEN 1 WHEN days_before_churn <= 30 THEN 2
                WHEN days_before_churn <= 60 THEN 3 WHEN days_before_churn <= 90 THEN 4 ELSE 5 END AS window_order,
           COUNT(*) AS support_tickets, COUNT(DISTINCT account_id) AS support_accounts,
           COUNT(*) FILTER (WHERE escalation_flag) AS escalated_tickets,
           COUNT(satisfaction_score) AS rated_tickets,
           AVG(satisfaction_score) AS avg_csat
    FROM support_next_event
    GROUP BY 1, 2
), windows AS (
    SELECT * FROM (VALUES ('0-14', 1), ('15-30', 2), ('31-60', 3), ('61-90', 4), ('91+', 5))
      AS t(window_label, window_order)
)
SELECT w.window_label, w.window_order,
       COALESCE(u.usage_events, 0) AS usage_events,
       COALESCE(u.usage_accounts, 0) AS usage_accounts,
       COALESCE(u.usage_count, 0) AS usage_count,
       COALESCE(u.error_count, 0) AS error_count,
       CASE WHEN COALESCE(u.usage_count, 0) = 0 THEN NULL
            ELSE ROUND(100.0 * u.error_count / u.usage_count, 2) END AS error_rate_pct,
       COALESCE(s.support_tickets, 0) AS support_tickets,
       COALESCE(s.support_accounts, 0) AS support_accounts,
       COALESCE(s.escalated_tickets, 0) AS escalated_tickets,
       CASE WHEN COALESCE(s.support_tickets, 0) = 0 THEN NULL
            ELSE ROUND(100.0 * s.escalated_tickets / s.support_tickets, 2) END AS escalation_rate_pct,
       COALESCE(s.rated_tickets, 0) AS rated_tickets,
       ROUND(s.avg_csat, 2) AS avg_csat
FROM windows w
LEFT JOIN usage_windowed u USING (window_label, window_order)
LEFT JOIN support_windowed s USING (window_label, window_order)
ORDER BY w.window_order;

CREATE TABLE gold.account_triage_base AS
WITH cutoff AS (
    SELECT data_cutoff FROM stage.dataset_bounds
), usage_features AS (
    SELECT a.account_id,
           COUNT(u.usage_id) AS valid_usage_events,
           MAX(u.usage_date) AS last_usage_date,
           SUM(u.usage_count) FILTER (WHERE u.usage_date > c.data_cutoff - INTERVAL '30 days') AS recent_usage,
           SUM(u.usage_count) FILTER (WHERE u.usage_date > c.data_cutoff - INTERVAL '60 days'
                                      AND u.usage_date <= c.data_cutoff - INTERVAL '30 days') AS prior_usage,
           SUM(u.usage_count) FILTER (WHERE u.usage_date > c.data_cutoff - INTERVAL '90 days') AS usage_90d,
           SUM(u.error_count) FILTER (WHERE u.usage_date > c.data_cutoff - INTERVAL '90 days') AS errors_90d
    FROM gold.account_snapshot a
    CROSS JOIN cutoff c
    LEFT JOIN stage.feature_usage u ON a.account_id = u.account_id AND u.is_eligible
    GROUP BY a.account_id
), usage_coverage AS (
    SELECT account_id, COUNT(*) AS raw_usage_events,
           COUNT(*) FILTER (WHERE is_eligible) AS eligible_usage_events
    FROM stage.feature_usage
    WHERE account_id IS NOT NULL
    GROUP BY account_id
), support_features AS (
    SELECT a.account_id,
           COUNT(t.ticket_id) FILTER (WHERE t.submitted_at > c.data_cutoff - INTERVAL '90 days') AS total_tickets,
           COUNT(t.ticket_id) FILTER (WHERE t.submitted_at > c.data_cutoff - INTERVAL '90 days'
                                      AND t.escalation_flag) AS escalated_tickets,
           AVG(t.satisfaction_score) FILTER (WHERE t.submitted_at > c.data_cutoff - INTERVAL '90 days') AS avg_csat
    FROM gold.account_snapshot a
    CROSS JOIN cutoff c
    LEFT JOIN stage.support_tickets t ON a.account_id = t.account_id AND t.is_eligible
    GROUP BY a.account_id
), support_coverage AS (
    SELECT account_id, COUNT(*) AS raw_support_events,
           COUNT(*) FILTER (WHERE is_eligible) AS eligible_support_events
    FROM stage.support_tickets
    WHERE account_id IS NOT NULL
    GROUP BY account_id
), features AS (
    SELECT a.*,
           DATE_DIFF('day', u.last_usage_date, c.data_cutoff) AS usage_recency_days,
           CASE WHEN COALESCE(u.prior_usage, 0) = 0 THEN NULL
                ELSE ROUND(100.0 * (COALESCE(u.recent_usage, 0) - u.prior_usage) / u.prior_usage, 2) END AS usage_trend_pct,
           CASE WHEN COALESCE(u.usage_90d, 0) = 0 THEN NULL
                ELSE ROUND(100.0 * COALESCE(u.errors_90d, 0) / u.usage_90d, 2) END AS error_rate_pct,
           COALESCE(s.total_tickets, 0) AS total_tickets,
           CASE WHEN COALESCE(s.total_tickets, 0) = 0 THEN NULL
                ELSE ROUND(100.0 * s.escalated_tickets / s.total_tickets, 2) END AS escalation_rate_pct,
           s.avg_csat,
           COALESCE(u.valid_usage_events, 0) AS valid_usage_events,
           COALESCE(uc.raw_usage_events, 0) AS raw_usage_events,
           COALESCE(uc.eligible_usage_events, 0) AS eligible_usage_events,
           COALESCE(sc.raw_support_events, 0) AS raw_support_events,
           COALESCE(sc.eligible_support_events, 0) AS eligible_support_events
    FROM gold.account_snapshot a
    CROSS JOIN cutoff c
    LEFT JOIN usage_features u USING (account_id)
    LEFT JOIN usage_coverage uc USING (account_id)
    LEFT JOIN support_features s USING (account_id)
    LEFT JOIN support_coverage sc USING (account_id)
    WHERE NOT a.snapshot_churn_flag
), components AS (
    SELECT *,
        CASE WHEN valid_usage_events = 0 THEN NULL
             WHEN usage_recency_days >= 90 THEN 100.0
             WHEN usage_recency_days >= 60 THEN 80.0
             WHEN usage_recency_days >= 30 THEN 60.0
             WHEN usage_recency_days >= 14 THEN 35.0 ELSE 0.0 END AS inactivity_score,
        CASE WHEN usage_trend_pct IS NULL THEN NULL
             WHEN usage_trend_pct <= -75 THEN 100.0
             WHEN usage_trend_pct <= -50 THEN 75.0
             WHEN usage_trend_pct <= -25 THEN 50.0
             WHEN usage_trend_pct < 0 THEN 25.0 ELSE 0.0 END AS decline_score,
        CASE WHEN error_rate_pct IS NULL THEN NULL
             WHEN error_rate_pct >= 10 THEN 100.0
             WHEN error_rate_pct >= 7.5 THEN 75.0
             WHEN error_rate_pct >= 5 THEN 50.0
             WHEN error_rate_pct > 0 THEN 25.0 ELSE 0.0 END AS error_score,
        CASE WHEN total_tickets >= 5 THEN 100.0 WHEN total_tickets >= 3 THEN 70.0
             WHEN total_tickets >= 1 THEN 30.0 ELSE 0.0 END AS ticket_score,
        CASE WHEN escalation_rate_pct IS NULL THEN NULL
             WHEN escalation_rate_pct >= 20 THEN 100.0
             WHEN escalation_rate_pct > 0 THEN 60.0 ELSE 0.0 END AS escalation_score,
        CASE WHEN avg_csat IS NULL THEN NULL WHEN avg_csat <= 2 THEN 100.0
             WHEN avg_csat <= 3 THEN 70.0 WHEN avg_csat < 4 THEN 40.0 ELSE 0.0 END AS csat_score
    FROM features
)
SELECT *,
       (CASE WHEN inactivity_score IS NOT NULL THEN 30 ELSE 0 END
        + CASE WHEN decline_score IS NOT NULL THEN 25 ELSE 0 END
        + CASE WHEN error_score IS NOT NULL THEN 15 ELSE 0 END
        + 10
        + CASE WHEN escalation_score IS NOT NULL THEN 15 ELSE 0 END
        + CASE WHEN csat_score IS NOT NULL THEN 5 ELSE 0 END) AS available_weight,
       ROUND(100.0 * (eligible_usage_events + eligible_support_events)
             / NULLIF(raw_usage_events + raw_support_events, 0), 2) AS valid_event_pct
FROM components;

CREATE TABLE gold.account_triage_scored AS
SELECT *,
       ROUND((COALESCE(inactivity_score, 0) * 30
              + COALESCE(decline_score, 0) * 25
              + COALESCE(error_score, 0) * 15
              + ticket_score * 10
              + COALESCE(escalation_score, 0) * 15
              + COALESCE(csat_score, 0) * 5) / NULLIF(available_weight, 0), 1) AS triage_score,
       ROUND(available_weight * COALESCE(valid_event_pct, 100.0) / 100.0, 1) AS evidence_coverage_pct
FROM gold.account_triage_base;

CREATE TABLE gold.account_triage_signals AS
WITH signals AS (
    SELECT account_id, 'Uso sem atividade recente' AS signal, inactivity_score * 0.30 AS contribution
    FROM gold.account_triage_scored WHERE inactivity_score > 0
    UNION ALL SELECT account_id, 'Queda de uso recente', decline_score * 0.25
    FROM gold.account_triage_scored WHERE decline_score > 0
    UNION ALL SELECT account_id, 'Taxa de erro elevada', error_score * 0.15
    FROM gold.account_triage_scored WHERE error_score > 0
    UNION ALL SELECT account_id, 'Carga recente de suporte', ticket_score * 0.10
    FROM gold.account_triage_scored WHERE ticket_score > 0
    UNION ALL SELECT account_id, 'Escalações recentes', escalation_score * 0.15
    FROM gold.account_triage_scored WHERE escalation_score > 0
    UNION ALL SELECT account_id, 'Satisfação recente baixa', csat_score * 0.05
    FROM gold.account_triage_scored WHERE csat_score > 0
    UNION ALL SELECT account_id, 'Telemetria válida insuficiente', 0.01
    FROM gold.account_triage_scored WHERE available_weight < 50
), ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY contribution DESC, signal) AS signal_rank
    FROM signals
)
SELECT * FROM ranked;

CREATE TABLE gold.account_triage AS
SELECT
    s.account_id,
    s.account_name,
    s.plan_tier,
    s.industry,
    s.referral_source,
    s.snapshot_churn_flag,
    COALESCE(s.triage_score, 0.0) AS triage_score,
    CASE WHEN s.evidence_coverage_pct < 45 THEN 'Data gap'
         WHEN COALESCE(s.triage_score, 0) >= 75 THEN 'Critical'
         WHEN COALESCE(s.triage_score, 0) >= 50 THEN 'High'
         WHEN COALESCE(s.triage_score, 0) >= 25 THEN 'Watch'
         ELSE 'Low' END AS triage_band,
    CASE WHEN s.evidence_coverage_pct >= 75 THEN 'High'
         WHEN s.evidence_coverage_pct >= 45 THEN 'Medium'
         ELSE 'Low' END AS evidence_confidence,
    s.evidence_coverage_pct,
    COALESCE(MAX(g.signal) FILTER (WHERE g.signal_rank = 1), 'Nenhum sinal comportamental elevado') AS signal_1,
    COALESCE(MAX(g.signal) FILTER (WHERE g.signal_rank = 2), 'Sem sinal adicional') AS signal_2,
    COALESCE(MAX(g.signal) FILTER (WHERE g.signal_rank = 3), 'Sem sinal adicional') AS signal_3,
    s.usage_recency_days,
    s.usage_trend_pct,
    s.error_rate_pct,
    s.total_tickets,
    s.escalation_rate_pct,
    ROUND(s.avg_csat, 2) AS avg_csat,
    s.mrr_proxy_conservative,
    s.mrr_proxy_additive
FROM gold.account_triage_scored s
LEFT JOIN gold.account_triage_signals g USING (account_id)
GROUP BY ALL;

CREATE TABLE gold.analysis_scope AS
WITH scopes AS (
    SELECT 'accounts_snapshot' AS scope_id, 'Snapshot declarado de contas' AS scope_label,
           (SELECT COUNT(*) FROM raw.accounts) AS raw_rows,
           (SELECT COUNT(*) FROM stage.accounts WHERE is_eligible) AS eligible_rows,
           'Observed' AS confidence_state, 'account' AS grain,
           'churn_flag é snapshot declarado, não evento mensal.' AS notes
    UNION ALL
    SELECT 'subscriptions_observed', 'Assinaturas observadas', COUNT(*),
           COUNT(*) FILTER (WHERE is_eligible), 'Observed', 'subscription',
           'Sobreposições permanecem sinalizadas.'
    FROM stage.subscriptions
    UNION ALL
    SELECT 'usage_temporal', 'Uso temporal elegível', COUNT(*),
           COUNT(*) FILTER (WHERE is_eligible), 'Derived', 'usage event',
           'Exclui duplicidade e eventos fora da vigência/cadastro.'
    FROM stage.feature_usage
    UNION ALL
    SELECT 'support_temporal', 'Suporte temporal elegível', COUNT(*),
           COUNT(*) FILTER (WHERE is_eligible), 'Derived', 'support ticket',
           'CSAT ausente é aviso, não descarte.'
    FROM stage.support_tickets
    UNION ALL
    SELECT 'churn_event_ledger', 'Ledger histórico de eventos de churn', COUNT(*),
           COUNT(*) FILTER (WHERE is_eligible), 'Derived', 'churn event',
           'Não equivale ao estado atual da conta.'
    FROM stage.churn_events
    UNION ALL
    SELECT 'account_revenue_proxy', 'Intervalo proxy de MRR por conta',
           (SELECT COUNT(*) FROM gold.account_snapshot),
           (SELECT COUNT(*) FROM gold.account_snapshot WHERE mrr_proxy_conservative IS NOT NULL),
           'Conditional', 'account',
           'Proxy conservador=max MRR individual; proxy aditivo=soma das assinaturas pagas ativas.'
    UNION ALL
    SELECT 'account_triage', 'Índice de triagem para contas sem flag de churn no snapshot',
           (SELECT COUNT(*) FROM gold.account_snapshot WHERE NOT snapshot_churn_flag),
           (SELECT COUNT(*) FROM gold.account_triage), 'Conditional',
           'account without snapshot churn flag',
           'Sem flag de churn no snapshot; atividade atual não reconciliada. Não é probabilidade.'
)
SELECT scope_id, scope_label, raw_rows, eligible_rows,
       raw_rows - eligible_rows AS quarantined_rows,
       ROUND(100.0 * eligible_rows / NULLIF(raw_rows, 0), 2) AS coverage_pct,
       confidence_state, grain, notes
FROM scopes;

CREATE TABLE gold.metric_catalog (
    metric_id VARCHAR,
    metric_label VARCHAR,
    definition VARCHAR,
    grain VARCHAR,
    universe_id VARCHAR,
    confidence_state VARCHAR,
    value_status VARCHAR,
    limitation VARCHAR
);

INSERT INTO gold.metric_catalog VALUES
('snapshot_churn_rate', 'Churn no snapshot declarado', 'Contas com accounts.churn_flag=true / contas elegíveis.', 'account', 'accounts_snapshot', 'Observed', 'Available', 'Não mede churn mensal.'),
('valid_churn_events', 'Eventos históricos válidos de churn', 'Contagem de churn_events após o signup da conta.', 'churn event', 'churn_event_ledger', 'Derived', 'Available', 'Uma conta pode possuir múltiplos eventos.'),
('monthly_logo_churn', 'Logo churn mensal', 'Contas que perderam sua última assinatura paga / base pagante inicial.', 'account-month', 'none', 'Unavailable', 'Unavailable', 'Eventos não identificam assinatura e state machine não reconcilia.'),
('mrr_proxy_conservative', 'MRR proxy conservador', 'Maior MRR individual entre assinaturas pagas ativas da conta no corte.', 'account', 'account_revenue_proxy', 'Conditional', 'Available', 'Não é limite matemático; não identifica módulos ou versões de contrato.'),
('mrr_proxy_additive', 'MRR proxy aditivo', 'Soma do MRR das assinaturas pagas ativas da conta no corte.', 'account', 'account_revenue_proxy', 'Conditional', 'Available', 'Não é limite matemático e pode superestimar receita em sobreposições.'),
('grr', 'Gross Revenue Retention', 'MRR retido antes de expansão / MRR inicial.', 'account-month', 'none', 'Unavailable', 'Unavailable', 'Movimentos de MRR não reconciliam por conta e período.'),
('nrr', 'Net Revenue Retention', 'MRR final de clientes existentes / MRR inicial.', 'account-month', 'none', 'Unavailable', 'Unavailable', 'Movimentos de expansão, contração e churn não são identificáveis.'),
('triage_score', 'Índice de triagem', 'Média ponderada de sinais válidos de uso, erro e suporte.', 'account without snapshot churn flag', 'account_triage', 'Conditional', 'Available', 'Sem flag de churn no snapshot; atividade atual não reconciliada. Não é probabilidade nem efeito causal.');
