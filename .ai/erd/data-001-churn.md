# ERD — 001 Churn (RavenStack) — schema observado

Fonte: `datasets/data-001-churn/*.csv` + README do dump. Leitura 2026-09-21.

```
ravenstack_accounts (500)
  PK account_id
        │
        │ 1:N  (min 2, med 10, max 19)
        ▼
ravenstack_subscriptions (5000)
  PK subscription_id
  FK account_id   0 órfãos
        │
        │ 1:N  (33 subs sem usage)
        ▼
ravenstack_feature_usage (25000)
  usage_id  NÃO único (21 dups)
  FK subscription_id   0 órfãos

ravenstack_accounts
        ├──── 1:N ──── ravenstack_support_tickets (2000)
        │              PK ticket_id · FK account_id · 8 contas sem ticket
        └──── 1:N ──── ravenstack_churn_events (600)
                       PK churn_event_id · 352 contas · máx 5/conta
```

## accounts — 500 × 10

| Coluna | Tipo lido | nunique | Notas |
|--------|-----------|---------|-------|
| `account_id` | ID `A-` + hex | 500 PK | |
| `account_name` | string | 500 | **não no brief** |
| `industry` | enum | 5 | DevTools, FinTech, Cybersecurity, HealthTech, EdTech |
| `country` | ISO-2 | 7 | US 291, UK, IN, AU, DE, CA, FR |
| `signup_date` | date | 370 | 2023-01-02 … 2024-12-31 |
| `referral_source` | enum | 5 | organic, ads, event, partner, other |
| `plan_tier` | enum | 3 | Basic, Pro, Enterprise (plano **inicial**) |
| `seats` | int | 1–163 | **não no brief** |
| `is_trial` | bool | 97 true | |
| `churn_flag` | bool | 110 true | **não canônico** — ver trap |

## subscriptions — 5 000 × 14

| Coluna | Tipo | Notas |
|--------|------|-------|
| `subscription_id` | PK | |
| `account_id` | FK | toda conta tem ≥1 (na prática ≥2) |
| `start_date` / `end_date` | date | `end_date` null ⇔ `churn_flag` false (4 514) |
| `plan_tier` | enum 3 | plano **na billing** — pode ≠ accounts |
| `seats` | int 1–189 | |
| `mrr_amount` / `arr_amount` | number | MRR 0–33 830; ARR ≈ 12× |
| `is_trial` | bool | 778 true |
| `upgrade_flag` / `downgrade_flag` | bool | 529 / 218 |
| `churn_flag` | bool | 486 true = tem `end_date` |
| `billing_frequency` | monthly \| annual | ~50/50 |
| `auto_renew_flag` | bool | 80% true |

## feature_usage — 25 000 × 8

| Coluna | Notas |
|--------|-------|
| `usage_id` | **21 duplicatas** — não usar como PK |
| `subscription_id` | 4 967 distinct; 33 subs sem linha |
| `usage_date` | 2023-01-01 … 2024-12-31 |
| `feature_name` | 40 valores `feature_1`…`feature_40` |
| `usage_count` | int |
| `usage_duration_secs` | int |
| `error_count` | 0–8 |
| `is_beta_feature` | 2 544 true (~10%) |

## support_tickets — 2 000 × 9

| Coluna | Notas |
|--------|-------|
| `ticket_id` | PK |
| `account_id` | 492 contas |
| `submitted_at` / `closed_at` | datetime |
| `resolution_time_hours` | 72 valores |
| `priority` | low, medium, high, **urgent** (~iguais) |
| `first_response_time_minutes` | 1–180 |
| `satisfaction_score` | **só 3, 4, 5** + 825 null (41%) — sem 1–2 |
| `escalation_flag` | 95 true |

## churn_events — 600 × 9

| Coluna | Notas |
|--------|-------|
| `churn_event_id` | PK |
| `account_id` | 352 distinct |
| `churn_date` | 2023-01-25 … 2024-12-31 |
| `reason_code` | features, support, budget, unknown, competitor, pricing |
| `refund_amount_usd` | 458 = 0; max 392.92 |
| `preceding_upgrade_flag` / `_downgrade_flag` | 123 / 53 |
| `is_reactivation` | 61 true |
| `feedback_text` | **3 frases** + 148 null: `too expensive`, `missing features`, `switched to competitor` |

## Trap de negócio

`accounts.churn_flag` e `churn_events` **divergem**. Análise de causa raiz usa o evento (+ reason/feedback). O flag é atributo denormalizado inconsistente.

Peso: `subscriptions.mrr_amount` / `arr_amount`, não count de contas.
