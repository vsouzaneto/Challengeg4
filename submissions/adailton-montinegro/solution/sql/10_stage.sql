-- Stage preserves every raw row, casts safely and records why a row cannot be
-- used in a given analytical universe. No date, status or amount is imputed.

CREATE TABLE stage.accounts AS
WITH typed AS (
    SELECT
        source_row_number,
        NULLIF(TRIM(account_id), '') AS account_id,
        COALESCE(NULLIF(TRIM(account_name), ''), 'Unknown') AS account_name,
        COALESCE(NULLIF(TRIM(industry), ''), 'Unknown') AS industry,
        COALESCE(NULLIF(UPPER(TRIM(country)), ''), 'Unknown') AS country,
        TRY_CAST(NULLIF(TRIM(signup_date), '') AS DATE) AS signup_date,
        COALESCE(NULLIF(LOWER(TRIM(referral_source)), ''), 'unknown') AS referral_source,
        CASE LOWER(TRIM(plan_tier))
            WHEN 'basic' THEN 'Basic'
            WHEN 'pro' THEN 'Pro'
            WHEN 'enterprise' THEN 'Enterprise'
            ELSE COALESCE(NULLIF(TRIM(plan_tier), ''), 'Unknown')
        END AS plan_tier,
        TRY_CAST(NULLIF(TRIM(seats), '') AS INTEGER) AS seats,
        TRY_CAST(NULLIF(TRIM(is_trial), '') AS BOOLEAN) AS is_trial,
        TRY_CAST(NULLIF(TRIM(churn_flag), '') AS BOOLEAN) AS churn_flag,
        MD5(CONCAT_WS('¦', account_id, account_name, industry, country, signup_date,
                      referral_source, plan_tier, seats, is_trial, churn_flag)) AS row_hash
    FROM raw.accounts
), duplicate_stats AS (
    SELECT account_id, COUNT(*) AS duplicate_count,
           COUNT(DISTINCT row_hash) AS duplicate_variant_count
    FROM typed
    GROUP BY account_id
), ranked AS (
    SELECT t.*, d.duplicate_count, d.duplicate_variant_count,
           ROW_NUMBER() OVER (PARTITION BY t.account_id ORDER BY t.source_row_number) AS duplicate_rank
    FROM typed t
    JOIN duplicate_stats d ON t.account_id IS NOT DISTINCT FROM d.account_id
), classified AS (
    SELECT *,
        CASE
            WHEN account_id IS NULL THEN 'account_missing_id'
            WHEN duplicate_count > 1 AND duplicate_variant_count > 1 THEN 'account_duplicate_id_conflict'
            WHEN duplicate_rank > 1 THEN 'account_duplicate_surplus'
            WHEN signup_date IS NULL THEN 'account_invalid_signup_date'
            WHEN seats IS NULL OR seats <= 0 THEN 'account_invalid_seats'
            WHEN is_trial IS NULL OR churn_flag IS NULL THEN 'account_invalid_boolean'
        END AS primary_reject_reason,
        CONCAT_WS('|',
            CASE WHEN account_id IS NULL THEN 'account_missing_id' END,
            CASE WHEN duplicate_count > 1 AND duplicate_variant_count > 1 THEN 'account_duplicate_id_conflict' END,
            CASE WHEN duplicate_rank > 1 THEN 'account_duplicate_surplus' END,
            CASE WHEN signup_date IS NULL THEN 'account_invalid_signup_date' END,
            CASE WHEN seats IS NULL OR seats <= 0 THEN 'account_invalid_seats' END,
            CASE WHEN is_trial IS NULL OR churn_flag IS NULL THEN 'account_invalid_boolean' END,
            CASE WHEN plan_tier NOT IN ('Basic', 'Pro', 'Enterprise') THEN 'account_unknown_plan' END,
            CASE WHEN referral_source = 'unknown' THEN 'account_unknown_referral_source' END
        ) AS quality_flags
    FROM ranked
)
SELECT *, primary_reject_reason IS NULL AS is_eligible
FROM classified;

CREATE TABLE stage.subscriptions_pre AS
WITH typed AS (
    SELECT
        r.source_row_number,
        NULLIF(TRIM(r.subscription_id), '') AS subscription_id,
        NULLIF(TRIM(r.account_id), '') AS account_id,
        TRY_CAST(NULLIF(TRIM(r.start_date), '') AS DATE) AS start_date,
        TRY_CAST(NULLIF(TRIM(r.end_date), '') AS DATE) AS end_date,
        CASE LOWER(TRIM(r.plan_tier))
            WHEN 'basic' THEN 'Basic'
            WHEN 'pro' THEN 'Pro'
            WHEN 'enterprise' THEN 'Enterprise'
            ELSE COALESCE(NULLIF(TRIM(r.plan_tier), ''), 'Unknown')
        END AS plan_tier,
        TRY_CAST(NULLIF(TRIM(r.seats), '') AS INTEGER) AS seats,
        TRY_CAST(NULLIF(TRIM(r.mrr_amount), '') AS DOUBLE) AS mrr_amount,
        TRY_CAST(NULLIF(TRIM(r.arr_amount), '') AS DOUBLE) AS arr_amount,
        TRY_CAST(NULLIF(TRIM(r.is_trial), '') AS BOOLEAN) AS is_trial,
        TRY_CAST(NULLIF(TRIM(r.upgrade_flag), '') AS BOOLEAN) AS upgrade_flag,
        TRY_CAST(NULLIF(TRIM(r.downgrade_flag), '') AS BOOLEAN) AS downgrade_flag,
        TRY_CAST(NULLIF(TRIM(r.churn_flag), '') AS BOOLEAN) AS churn_flag,
        COALESCE(NULLIF(LOWER(TRIM(r.billing_frequency)), ''), 'unknown') AS billing_frequency,
        TRY_CAST(NULLIF(TRIM(r.auto_renew_flag), '') AS BOOLEAN) AS auto_renew_flag,
        MD5(CONCAT_WS('¦', r.subscription_id, r.account_id, r.start_date, r.end_date,
                      r.plan_tier, r.seats, r.mrr_amount, r.arr_amount, r.is_trial,
                      r.upgrade_flag, r.downgrade_flag, r.churn_flag,
                      r.billing_frequency, r.auto_renew_flag)) AS row_hash
    FROM raw.subscriptions r
), duplicate_stats AS (
    SELECT subscription_id, COUNT(*) AS duplicate_count,
           COUNT(DISTINCT row_hash) AS duplicate_variant_count
    FROM typed
    GROUP BY subscription_id
), ranked AS (
    SELECT t.*, d.duplicate_count, d.duplicate_variant_count,
           ROW_NUMBER() OVER (PARTITION BY t.subscription_id ORDER BY t.source_row_number) AS duplicate_rank
    FROM typed t
    JOIN duplicate_stats d ON t.subscription_id IS NOT DISTINCT FROM d.subscription_id
), joined AS (
    SELECT r.*, a.account_id AS matched_account_id, a.signup_date AS account_signup_date,
           a.plan_tier AS account_plan_tier
    FROM ranked r
    LEFT JOIN stage.accounts a ON r.account_id = a.account_id AND a.is_eligible
), classified AS (
    SELECT *,
        CASE
            WHEN subscription_id IS NULL THEN 'subscription_missing_id'
            WHEN duplicate_count > 1 AND duplicate_variant_count > 1 THEN 'subscription_duplicate_id_conflict'
            WHEN duplicate_rank > 1 THEN 'subscription_duplicate_surplus'
            WHEN account_id IS NULL OR matched_account_id IS NULL THEN 'subscription_orphan_account'
            WHEN start_date IS NULL THEN 'subscription_invalid_start_date'
            WHEN end_date IS NOT NULL AND end_date < start_date THEN 'subscription_end_before_start'
            WHEN account_signup_date IS NOT NULL AND start_date < account_signup_date THEN 'subscription_start_before_signup'
            WHEN seats IS NULL OR seats <= 0 THEN 'subscription_invalid_seats'
            WHEN mrr_amount IS NULL OR mrr_amount < 0 OR arr_amount IS NULL OR arr_amount < 0 THEN 'subscription_invalid_amount'
            WHEN is_trial IS NULL OR upgrade_flag IS NULL OR downgrade_flag IS NULL
              OR churn_flag IS NULL OR auto_renew_flag IS NULL THEN 'subscription_invalid_boolean'
        END AS primary_reject_reason,
        CONCAT_WS('|',
            CASE WHEN subscription_id IS NULL THEN 'subscription_missing_id' END,
            CASE WHEN duplicate_count > 1 AND duplicate_variant_count > 1 THEN 'subscription_duplicate_id_conflict' END,
            CASE WHEN duplicate_rank > 1 THEN 'subscription_duplicate_surplus' END,
            CASE WHEN account_id IS NULL OR matched_account_id IS NULL THEN 'subscription_orphan_account' END,
            CASE WHEN start_date IS NULL THEN 'subscription_invalid_start_date' END,
            CASE WHEN end_date IS NOT NULL AND end_date < start_date THEN 'subscription_end_before_start' END,
            CASE WHEN account_signup_date IS NOT NULL AND start_date < account_signup_date THEN 'subscription_start_before_signup' END,
            CASE WHEN seats IS NULL OR seats <= 0 THEN 'subscription_invalid_seats' END,
            CASE WHEN mrr_amount IS NULL OR mrr_amount < 0 OR arr_amount IS NULL OR arr_amount < 0 THEN 'subscription_invalid_amount' END,
            CASE WHEN is_trial IS NULL OR upgrade_flag IS NULL OR downgrade_flag IS NULL
                       OR churn_flag IS NULL OR auto_renew_flag IS NULL THEN 'subscription_invalid_boolean' END,
            CASE WHEN mrr_amount IS NOT NULL AND arr_amount IS NOT NULL
                       AND ABS(arr_amount - 12 * mrr_amount) > 0.01 THEN 'subscription_arr_mrr_mismatch' END,
            CASE WHEN billing_frequency NOT IN ('monthly', 'annual') THEN 'subscription_unknown_billing_frequency' END,
            CASE WHEN account_plan_tier IS NOT NULL AND plan_tier <> account_plan_tier THEN 'subscription_account_plan_mismatch' END
        ) AS quality_flags
    FROM joined
)
SELECT *, primary_reject_reason IS NULL AS is_eligible
FROM classified;

CREATE TEMP TABLE subscription_overlap_rows AS
SELECT DISTINCT source_row_number
FROM (
    SELECT s1.source_row_number
    FROM stage.subscriptions_pre s1
    JOIN stage.subscriptions_pre s2
      ON s1.account_id = s2.account_id
     AND s1.source_row_number <> s2.source_row_number
     AND s1.is_eligible AND s2.is_eligible
     AND GREATEST(s1.start_date, s2.start_date)
         <= LEAST(COALESCE(s1.end_date, DATE '9999-12-31'),
                  COALESCE(s2.end_date, DATE '9999-12-31'))
);

CREATE TABLE stage.subscriptions AS
SELECT p.* EXCLUDE (quality_flags),
       o.source_row_number IS NOT NULL AS has_unresolved_overlap,
       CONCAT_WS('|', NULLIF(p.quality_flags, ''),
           CASE WHEN o.source_row_number IS NOT NULL THEN 'subscription_overlap_unresolved' END
       ) AS quality_flags
FROM stage.subscriptions_pre p
LEFT JOIN subscription_overlap_rows o USING (source_row_number);

CREATE TABLE stage.feature_usage AS
WITH typed AS (
    SELECT
        r.source_row_number,
        NULLIF(TRIM(r.usage_id), '') AS usage_id,
        NULLIF(TRIM(r.subscription_id), '') AS subscription_id,
        TRY_CAST(NULLIF(TRIM(r.usage_date), '') AS DATE) AS usage_date,
        COALESCE(NULLIF(TRIM(r.feature_name), ''), 'Unknown') AS feature_name,
        TRY_CAST(NULLIF(TRIM(r.usage_count), '') AS BIGINT) AS usage_count,
        TRY_CAST(NULLIF(TRIM(r.usage_duration_secs), '') AS DOUBLE) AS usage_duration_secs,
        TRY_CAST(NULLIF(TRIM(r.error_count), '') AS BIGINT) AS error_count,
        TRY_CAST(NULLIF(TRIM(r.is_beta_feature), '') AS BOOLEAN) AS is_beta_feature,
        MD5(CONCAT_WS('¦', r.usage_id, r.subscription_id, r.usage_date, r.feature_name,
                      r.usage_count, r.usage_duration_secs, r.error_count, r.is_beta_feature)) AS row_hash
    FROM raw.feature_usage r
), duplicate_stats AS (
    SELECT usage_id, COUNT(*) AS duplicate_count,
           COUNT(DISTINCT row_hash) AS duplicate_variant_count
    FROM typed
    GROUP BY usage_id
), ranked AS (
    SELECT t.*, d.duplicate_count, d.duplicate_variant_count,
           ROW_NUMBER() OVER (PARTITION BY t.usage_id ORDER BY t.source_row_number) AS duplicate_rank
    FROM typed t
    JOIN duplicate_stats d ON t.usage_id IS NOT DISTINCT FROM d.usage_id
), joined AS (
    SELECT r.*, s.account_id, s.start_date AS subscription_start_date,
           s.end_date AS subscription_end_date, a.signup_date AS account_signup_date
    FROM ranked r
    LEFT JOIN stage.subscriptions s ON r.subscription_id = s.subscription_id AND s.is_eligible
    LEFT JOIN stage.accounts a ON s.account_id = a.account_id AND a.is_eligible
), classified AS (
    SELECT *,
        CASE
            WHEN usage_id IS NULL THEN 'usage_missing_id'
            WHEN duplicate_count > 1 AND duplicate_variant_count > 1 THEN 'usage_duplicate_id_conflict'
            WHEN duplicate_rank > 1 THEN 'usage_duplicate_surplus'
            WHEN subscription_id IS NULL OR account_id IS NULL THEN 'usage_orphan_subscription'
            WHEN usage_date IS NULL THEN 'usage_invalid_date'
            WHEN usage_count IS NULL OR usage_count < 0 OR usage_duration_secs IS NULL
              OR usage_duration_secs < 0 OR error_count IS NULL OR error_count < 0 THEN 'usage_invalid_measure'
            WHEN is_beta_feature IS NULL THEN 'usage_invalid_boolean'
            WHEN account_signup_date IS NOT NULL AND usage_date < account_signup_date THEN 'usage_before_signup'
            WHEN subscription_start_date IS NOT NULL AND usage_date < subscription_start_date THEN 'usage_before_subscription'
            WHEN subscription_end_date IS NOT NULL AND usage_date > subscription_end_date THEN 'usage_after_subscription'
        END AS primary_reject_reason,
        CONCAT_WS('|',
            CASE WHEN usage_id IS NULL THEN 'usage_missing_id' END,
            CASE WHEN duplicate_count > 1 AND duplicate_variant_count > 1 THEN 'usage_duplicate_id_conflict' END,
            CASE WHEN duplicate_rank > 1 THEN 'usage_duplicate_surplus' END,
            CASE WHEN subscription_id IS NULL OR account_id IS NULL THEN 'usage_orphan_subscription' END,
            CASE WHEN usage_date IS NULL THEN 'usage_invalid_date' END,
            CASE WHEN usage_count IS NULL OR usage_count < 0 OR usage_duration_secs IS NULL
                       OR usage_duration_secs < 0 OR error_count IS NULL OR error_count < 0 THEN 'usage_invalid_measure' END,
            CASE WHEN is_beta_feature IS NULL THEN 'usage_invalid_boolean' END,
            CASE WHEN account_signup_date IS NOT NULL AND usage_date < account_signup_date THEN 'usage_before_signup' END,
            CASE WHEN subscription_start_date IS NOT NULL AND usage_date < subscription_start_date THEN 'usage_before_subscription' END,
            CASE WHEN subscription_end_date IS NOT NULL AND usage_date > subscription_end_date THEN 'usage_after_subscription' END,
            CASE WHEN feature_name = 'Unknown' THEN 'usage_unknown_feature' END
        ) AS quality_flags
    FROM joined
)
SELECT *, primary_reject_reason IS NULL AS is_eligible
FROM classified;

CREATE TABLE stage.support_tickets AS
WITH typed AS (
    SELECT
        r.source_row_number,
        NULLIF(TRIM(r.ticket_id), '') AS ticket_id,
        NULLIF(TRIM(r.account_id), '') AS account_id,
        TRY_CAST(NULLIF(TRIM(r.submitted_at), '') AS TIMESTAMP) AS submitted_at,
        TRY_CAST(NULLIF(TRIM(r.closed_at), '') AS TIMESTAMP) AS closed_at,
        TRY_CAST(NULLIF(TRIM(r.resolution_time_hours), '') AS DOUBLE) AS resolution_time_hours,
        COALESCE(NULLIF(LOWER(TRIM(r.priority)), ''), 'unknown') AS priority,
        TRY_CAST(NULLIF(TRIM(r.first_response_time_minutes), '') AS DOUBLE) AS first_response_time_minutes,
        TRY_CAST(NULLIF(TRIM(r.satisfaction_score), '') AS DOUBLE) AS satisfaction_score,
        TRY_CAST(NULLIF(TRIM(r.escalation_flag), '') AS BOOLEAN) AS escalation_flag,
        MD5(CONCAT_WS('¦', r.ticket_id, r.account_id, r.submitted_at, r.closed_at,
                      r.resolution_time_hours, r.priority, r.first_response_time_minutes,
                      r.satisfaction_score, r.escalation_flag)) AS row_hash
    FROM raw.support_tickets r
), duplicate_stats AS (
    SELECT ticket_id, COUNT(*) AS duplicate_count,
           COUNT(DISTINCT row_hash) AS duplicate_variant_count
    FROM typed
    GROUP BY ticket_id
), ranked AS (
    SELECT t.*, d.duplicate_count, d.duplicate_variant_count,
           ROW_NUMBER() OVER (PARTITION BY t.ticket_id ORDER BY t.source_row_number) AS duplicate_rank
    FROM typed t
    JOIN duplicate_stats d ON t.ticket_id IS NOT DISTINCT FROM d.ticket_id
), joined AS (
    SELECT r.*, a.account_id AS matched_account_id, a.signup_date AS account_signup_date
    FROM ranked r
    LEFT JOIN stage.accounts a ON r.account_id = a.account_id AND a.is_eligible
), classified AS (
    SELECT *,
        CASE
            WHEN ticket_id IS NULL THEN 'support_missing_id'
            WHEN duplicate_count > 1 AND duplicate_variant_count > 1 THEN 'support_duplicate_id_conflict'
            WHEN duplicate_rank > 1 THEN 'support_duplicate_surplus'
            WHEN account_id IS NULL OR matched_account_id IS NULL THEN 'support_orphan_account'
            WHEN submitted_at IS NULL THEN 'support_invalid_submitted_at'
            WHEN closed_at IS NOT NULL AND closed_at < submitted_at THEN 'support_closed_before_submitted'
            WHEN account_signup_date IS NOT NULL AND CAST(submitted_at AS DATE) < account_signup_date THEN 'support_before_signup'
            WHEN resolution_time_hours IS NOT NULL AND resolution_time_hours < 0 THEN 'support_invalid_resolution_time'
            WHEN first_response_time_minutes IS NOT NULL AND first_response_time_minutes < 0 THEN 'support_invalid_response_time'
            WHEN satisfaction_score IS NOT NULL AND (satisfaction_score < 1 OR satisfaction_score > 5) THEN 'support_invalid_csat'
            WHEN escalation_flag IS NULL THEN 'support_invalid_boolean'
        END AS primary_reject_reason,
        CONCAT_WS('|',
            CASE WHEN ticket_id IS NULL THEN 'support_missing_id' END,
            CASE WHEN duplicate_count > 1 AND duplicate_variant_count > 1 THEN 'support_duplicate_id_conflict' END,
            CASE WHEN duplicate_rank > 1 THEN 'support_duplicate_surplus' END,
            CASE WHEN account_id IS NULL OR matched_account_id IS NULL THEN 'support_orphan_account' END,
            CASE WHEN submitted_at IS NULL THEN 'support_invalid_submitted_at' END,
            CASE WHEN closed_at IS NOT NULL AND closed_at < submitted_at THEN 'support_closed_before_submitted' END,
            CASE WHEN account_signup_date IS NOT NULL AND CAST(submitted_at AS DATE) < account_signup_date THEN 'support_before_signup' END,
            CASE WHEN resolution_time_hours IS NOT NULL AND resolution_time_hours < 0 THEN 'support_invalid_resolution_time' END,
            CASE WHEN first_response_time_minutes IS NOT NULL AND first_response_time_minutes < 0 THEN 'support_invalid_response_time' END,
            CASE WHEN satisfaction_score IS NOT NULL AND (satisfaction_score < 1 OR satisfaction_score > 5) THEN 'support_invalid_csat' END,
            CASE WHEN escalation_flag IS NULL THEN 'support_invalid_boolean' END,
            CASE WHEN satisfaction_score IS NULL THEN 'support_missing_csat' END,
            CASE WHEN priority NOT IN ('low', 'medium', 'high', 'urgent') THEN 'support_unknown_priority' END
        ) AS quality_flags
    FROM joined
)
SELECT *, primary_reject_reason IS NULL AS is_eligible
FROM classified;

CREATE TABLE stage.churn_events AS
WITH typed AS (
    SELECT
        r.source_row_number,
        NULLIF(TRIM(r.churn_event_id), '') AS churn_event_id,
        NULLIF(TRIM(r.account_id), '') AS account_id,
        TRY_CAST(NULLIF(TRIM(r.churn_date), '') AS DATE) AS churn_date,
        COALESCE(NULLIF(LOWER(TRIM(r.reason_code)), ''), 'unknown') AS reason_code,
        TRY_CAST(NULLIF(TRIM(r.refund_amount_usd), '') AS DOUBLE) AS refund_amount_usd,
        TRY_CAST(NULLIF(TRIM(r.preceding_upgrade_flag), '') AS BOOLEAN) AS preceding_upgrade_flag,
        TRY_CAST(NULLIF(TRIM(r.preceding_downgrade_flag), '') AS BOOLEAN) AS preceding_downgrade_flag,
        TRY_CAST(NULLIF(TRIM(r.is_reactivation), '') AS BOOLEAN) AS is_reactivation,
        NULLIF(TRIM(r.feedback_text), '') AS feedback_text,
        MD5(CONCAT_WS('¦', r.churn_event_id, r.account_id, r.churn_date, r.reason_code,
                      r.refund_amount_usd, r.preceding_upgrade_flag,
                      r.preceding_downgrade_flag, r.is_reactivation, r.feedback_text)) AS row_hash
    FROM raw.churn_events r
), duplicate_stats AS (
    SELECT churn_event_id, COUNT(*) AS duplicate_count,
           COUNT(DISTINCT row_hash) AS duplicate_variant_count
    FROM typed
    GROUP BY churn_event_id
), ranked AS (
    SELECT t.*, d.duplicate_count, d.duplicate_variant_count,
           ROW_NUMBER() OVER (PARTITION BY t.churn_event_id ORDER BY t.source_row_number) AS duplicate_rank
    FROM typed t
    JOIN duplicate_stats d ON t.churn_event_id IS NOT DISTINCT FROM d.churn_event_id
), joined AS (
    SELECT r.*, a.account_id AS matched_account_id, a.signup_date AS account_signup_date,
           a.churn_flag AS snapshot_churn_flag
    FROM ranked r
    LEFT JOIN stage.accounts a ON r.account_id = a.account_id AND a.is_eligible
), classified AS (
    SELECT *,
        CASE
            WHEN churn_event_id IS NULL THEN 'churn_missing_id'
            WHEN duplicate_count > 1 AND duplicate_variant_count > 1 THEN 'churn_duplicate_id_conflict'
            WHEN duplicate_rank > 1 THEN 'churn_duplicate_surplus'
            WHEN account_id IS NULL OR matched_account_id IS NULL THEN 'churn_orphan_account'
            WHEN churn_date IS NULL THEN 'churn_invalid_date'
            WHEN account_signup_date IS NOT NULL AND churn_date < account_signup_date THEN 'churn_before_signup'
            WHEN refund_amount_usd IS NULL OR refund_amount_usd < 0 THEN 'churn_invalid_refund'
            WHEN preceding_upgrade_flag IS NULL OR preceding_downgrade_flag IS NULL
              OR is_reactivation IS NULL THEN 'churn_invalid_boolean'
        END AS primary_reject_reason,
        CONCAT_WS('|',
            CASE WHEN churn_event_id IS NULL THEN 'churn_missing_id' END,
            CASE WHEN duplicate_count > 1 AND duplicate_variant_count > 1 THEN 'churn_duplicate_id_conflict' END,
            CASE WHEN duplicate_rank > 1 THEN 'churn_duplicate_surplus' END,
            CASE WHEN account_id IS NULL OR matched_account_id IS NULL THEN 'churn_orphan_account' END,
            CASE WHEN churn_date IS NULL THEN 'churn_invalid_date' END,
            CASE WHEN account_signup_date IS NOT NULL AND churn_date < account_signup_date THEN 'churn_before_signup' END,
            CASE WHEN refund_amount_usd IS NULL OR refund_amount_usd < 0 THEN 'churn_invalid_refund' END,
            CASE WHEN preceding_upgrade_flag IS NULL OR preceding_downgrade_flag IS NULL
                       OR is_reactivation IS NULL THEN 'churn_invalid_boolean' END,
            CASE WHEN snapshot_churn_flag = FALSE THEN 'churn_snapshot_disagreement' END,
            CASE WHEN reason_code = 'unknown' THEN 'churn_unknown_reason' END,
            CASE WHEN feedback_text IS NULL THEN 'churn_missing_feedback' END
        ) AS quality_flags
    FROM joined
)
SELECT *, primary_reject_reason IS NULL AS is_eligible
FROM classified;

CREATE TABLE stage.dataset_bounds AS
SELECT
    LEAST(
        (SELECT MIN(signup_date) FROM stage.accounts WHERE signup_date IS NOT NULL),
        (SELECT MIN(start_date) FROM stage.subscriptions WHERE start_date IS NOT NULL),
        (SELECT MIN(usage_date) FROM stage.feature_usage WHERE usage_date IS NOT NULL),
        (SELECT MIN(CAST(submitted_at AS DATE)) FROM stage.support_tickets WHERE submitted_at IS NOT NULL),
        (SELECT MIN(churn_date) FROM stage.churn_events WHERE churn_date IS NOT NULL)
    ) AS source_start_date,
    GREATEST(
        (SELECT MAX(signup_date) FROM stage.accounts WHERE signup_date IS NOT NULL),
        (SELECT MAX(start_date) FROM stage.subscriptions WHERE start_date IS NOT NULL),
        (SELECT MAX(usage_date) FROM stage.feature_usage WHERE usage_date IS NOT NULL),
        (SELECT MAX(CAST(submitted_at AS DATE)) FROM stage.support_tickets WHERE submitted_at IS NOT NULL),
        (SELECT MAX(churn_date) FROM stage.churn_events WHERE churn_date IS NOT NULL)
    ) AS data_cutoff;
