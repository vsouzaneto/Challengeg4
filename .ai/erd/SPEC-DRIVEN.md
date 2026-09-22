# SPEC-DRIVEN — como usar os CSVs

Evoluir análise/app sem inventar coluna, PK ou join entre challenges.

---

## Fonte de verdade

| Assunto | Onde |
|---------|------|
| Schema observado | [SPEC-REVERSE.md](SPEC-REVERSE.md) + ERD do serviço |
| Brief (pode estar velho) | `challenges/<id>/README.md` |
| Dicionário 003 | `datasets/build-003-lead-scorer/metadata.csv` |
| Dicionário 001 | `datasets/data-001-churn/README.md` |
| Spec | [../specs/SPEC-007-data-domains.md](../specs/SPEC-007-data-domains.md) |

Se brief e CSV divergirem, **CSV ganha** para o modelo; o brief ganha para o *deliverable*. Documentar a divergência.

---

## Regras

1. **Quatro silos.** Proibido join `account_id` (001) com `account` (003) ou e-mail (002).
2. **Não inventar coluna.** `engagement_rate`, `Topic_group`, `deal_score` não existem no dump — são derivados e devem ser nomeados como tal.
3. **PK só se único no disco.** `usage_id` (001) tem 21 dups — grain = linha, não o id.
4. **Label de churn (001)** = `churn_events`, não `accounts.churn_flag`.
5. **002 Dataset 2** só entra depois de existir o arquivo. Sem CSV, a spec de classificação 8 classes **não tem dado local**.
6. **003 produto:** normalizar `GTXPro` → `GTX Pro` no ETL (1 480 linhas). Sem isso o catálogo mente.
7. **003 conta nula:** Prospecting/Engaging sem `account` é estado válido. Não dropar na priorização de pipe aberto.
8. **004 creator:** agrupar por `creator_id`, não por `creator_name`.
9. **004 audience:** tratar como categoria, não como JSON de distribuição.
10. **Sem secrets / PII no `.ai`.** Não colar e-mail ou `feedback_text` identificável.

---

## Joins permitidos

| Serviço | Join | Tipo |
|---------|------|------|
| 001 | `subscriptions.account_id` = `accounts.account_id` | N:1, 0 órfãos, toda conta tem ≥2 subs |
| 001 | `feature_usage.subscription_id` = `subscriptions.subscription_id` | N:1, 0 órfãos, 33 subs sem usage |
| 001 | `support_tickets.account_id` = `accounts.account_id` | N:1, 0 órfãos, 8 contas sem ticket |
| 001 | `churn_events.account_id` = `accounts.account_id` | N:1, 0 órfãos |
| 002 | — | fato único |
| 003 | `pipeline.account` = `accounts.account` | N:1 opcional (null permitido) |
| 003 | `pipeline.sales_agent` = `sales_teams.sales_agent` | N:1 |
| 003 | `pipeline.product` = `products.product` **após** trim/`GTXPro` | N:1 |
| 004 | — | fato único; rollup por `creator_id` / `platform` / `is_sponsored` |

---

## Derivados permitidos (nomear)

| Nome sugerido | Fórmula / regra | Serviço |
|---------------|-----------------|---------|
| `is_subscription_active` | `end_date` is null ⇔ `churn_flag` false | 001 |
| `has_churn_event` | account ∈ `churn_events.account_id` | 001 |
| `ttr_hours` | só Closed; Open/Pending = null | 002 |
| `product_key` | `GTXPro` → `GTX Pro` | 003 |
| `is_open_deal` | stage ∈ {Prospecting, Engaging} | 003 |
| `engagement_rate` | `(likes+shares+comments_count)/views` | 004 |

---

## Qualidade

Mudança de dump (n, coluna, enum) = atualizar ERD + DATA-SOURCES + SPEC-007 na mesma entrega. Não “arredondar” 8 469 para 30 k.
