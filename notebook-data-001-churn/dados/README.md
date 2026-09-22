# `dados/` — RavenStack (challenge 001)

Contado no disco em 2026-09-21. Não inventar coluna.

| Arquivo | Linhas | Colunas |
| --- | ---: | --- |
| `ravenstack_accounts.csv` | 500 | `account_id`, `account_name`, `industry`, `country`, `signup_date`, `referral_source`, `plan_tier`, `seats`, `is_trial`, `churn_flag` |
| `ravenstack_subscriptions.csv` | 5000 | `subscription_id`, `account_id`, `start_date`, `end_date`, `plan_tier`, `seats`, `mrr_amount`, `arr_amount`, `is_trial`, `upgrade_flag`, `downgrade_flag`, `churn_flag`, `billing_frequency`, `auto_renew_flag` |
| `ravenstack_feature_usage.csv` | 25000 | `usage_id`, `subscription_id`, `usage_date`, `feature_name`, `usage_count`, `usage_duration_secs`, `error_count`, `is_beta_feature` |
| `ravenstack_support_tickets.csv` | 2000 | `ticket_id`, `account_id`, `submitted_at`, `closed_at`, `resolution_time_hours`, `priority`, `first_response_time_minutes`, `satisfaction_score`, `escalation_flag` |
| `ravenstack_churn_events.csv` | 600 | `churn_event_id`, `account_id`, `churn_date`, `reason_code`, `refund_amount_usd`, `preceding_upgrade_flag`, `preceding_downgrade_flag`, `is_reactivation`, `feedback_text` |

Joins: `account_id`, `subscription_id`. `usage_id` tem 21 duplicatas — não é PK.

Label canônico de churn = `ravenstack_churn_events`. `accounts.churn_flag` não bate com o evento.
