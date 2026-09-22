# Fontes de dados — inventário observado 2026-09-21

CSVs em `datasets/` (gitignored). Colunas e n abaixo = **dump local**, não só o brief. Reverse: [../erd/SPEC-REVERSE.md](../erd/SPEC-REVERSE.md).

## Política

1. Não commitar dataset. Sem `KAGGLE_API_TOKEN` neste `.ai/`.
2. Brief desatualizado → CSV ganha no ERD; brief ganha no deliverable; anotar o gap.
3. Relistar licença só como no brief / README do dump.

## 001 — Churn

| Campo | Valor |
|-------|-------|
| Path | `datasets/data-001-churn/` |
| Kaggle | [SaaS Subscription & Churn Analytics](https://www.kaggle.com/datasets/rivalytics/saas-subscription-and-churn-analytics-dataset) |
| Extra | `README.md` do dump (River @ Rivalytics, MIT-like, sintético) |

| Arquivo | n | PK | FK / trap |
|---------|---|-----|-----------|
| `ravenstack_accounts.csv` | 500 × 10 | `account_id` | `churn_flag` ≠ eventos |
| `ravenstack_subscriptions.csv` | 5 000 × 14 | `subscription_id` | `account_id` 0 órfãos; `end_date` 90% null |
| `ravenstack_feature_usage.csv` | 25 000 × 8 | `usage_id` **21 dups** | `subscription_id` 0 órfãos; 33 subs sem usage |
| `ravenstack_support_tickets.csv` | 2 000 × 9 | `ticket_id` | CSAT 41% null; só 3–5 |
| `ravenstack_churn_events.csv` | 600 × 9 | `churn_event_id` | 352 contas; feedback 3 frases |

Janela 2023–2024. ERD: [erd/data-001-churn.md](../erd/data-001-churn.md).

## 002 — Support

| Campo | Valor |
|-------|-------|
| Path | `datasets/process-002-support/` |
| Presente | `customer_support_tickets.csv` **8 469 × 17** (brief dizia ~30 k) |
| Zip | `process-002-support.zip` = o mesmo CSV |
| Ausente | Dataset 2 IT classification (~48 k) |

ERD: [erd/process-002-support.md](../erd/process-002-support.md).

## 003 — Lead Scorer

| Campo | Valor |
|-------|-------|
| Path | `datasets/build-003-lead-scorer/` |
| Extra | `metadata.csv` (dicionário) |

| Arquivo | n | Chave | Trap |
|---------|---|-------|------|
| `accounts.csv` | 85 × 7 | `account` | `subsidiary_of` não é FK; typo `technolgy` |
| `products.csv` | 7 × 3 | `product` | |
| `sales_teams.csv` | 35 × 3 | `sales_agent` | 5 sem deal |
| `sales_pipeline.csv` | 8 800 × 8 | `opportunity_id` | `GTXPro` 1 480; account null 1 425 |

ERD: [erd/build-003-lead-scorer.md](../erd/build-003-lead-scorer.md).

## 004 — Social

| Campo | Valor |
|-------|-------|
| Path | `datasets/marketing-004-social/social_media_dataset.csv` |
| n | **52 214 × 27** |
| Ausente | coluna `engagement rate` |

PK `id`; UK `content_id`. Creator = `creator_id` (5 000), não `creator_name`. ERD: [erd/marketing-004-social.md](../erd/marketing-004-social.md).

## Conclusão

Serving do git = zero CSV versionado. O clone local desta máquina **tem** os quatro dumps; o 002 está incompleto frente ao brief. Qualquer n arredondado (“30k”, “52k”) no README público não substitui esta página.
