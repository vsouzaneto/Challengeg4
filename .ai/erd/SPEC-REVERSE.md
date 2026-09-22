# SPEC-REVERSE — domínios de dado (CSVs)

| Campo | Valor |
|-------|-------|
| **Path** | `datasets/<serviço>/` (gitignored) |
| **Leitura** | 2026-09-21 · `pandas` + `csv.DictReader` |
| **SQL** | nenhum |

Quatro silos. Nenhum arquivo cruza de pasta.

## 001 — RavenStack (churn)

Cinco CSVs. FKs **sem órfão** (`account_id`, `subscription_id`). README local do dataset confirma o desenho.

```
accounts 500 ──1:N── subscriptions 5000 ──1:N── feature_usage 25000
    │                      (33 subs sem usage)
    ├──1:N── support_tickets 2000   (8 accounts sem ticket)
    └──1:N── churn_events 600       (352 accounts distintos; máx. 5/conta)
```

| Fato | PK observada | n | Nulos |
|------|--------------|---|-------|
| `ravenstack_accounts` | `account_id` único | 500 | 0 |
| `ravenstack_subscriptions` | `subscription_id` único | 5 000 | `end_date` 90,3% (= `churn_flag` false) |
| `ravenstack_feature_usage` | `usage_id` **não** único (21 dups) | 25 000 | 0 |
| `ravenstack_support_tickets` | `ticket_id` único | 2 000 | `satisfaction_score` 41,2% |
| `ravenstack_churn_events` | `churn_event_id` único | 600 | `feedback_text` 24,7% |

**Trap:** `accounts.churn_flag` (110 true) **≠** presença em `churn_events` (352 accounts). 35 flagged sem evento; 277 com evento e flag false. Não usar o flag como label canônico — o evento é o fato.

Janela: 2023-01-01 … 2024-12-31. `feature_name` = `feature_1`…`feature_40`. CSAT só 3/4/5. Feedback só 3 frases.

## 002 — Support tickets

Um fato. Brief prometia ~30 k + 2º dataset. Disco: **8 469** linhas, 17 colunas. Zip = o mesmo CSV.

```
ticket 8469
  PK Ticket ID
  (sem FK)
```

Nulos alinhados ao status:

| Status | n | Resolution / TTR / CSAT | FRT |
|--------|---|-------------------------|-----|
| Closed | 2 769 | preenchidos | preenchido |
| Open | 2 819 | nulos | **nulos** |
| Pending Customer Response | 2 881 | nulos | preenchido |

Colunas físicas ≠ brief: `Customer Email|Age|Gender` (não `Email|Age|Gender`); extra `Date of Purchase`. `Ticket Type` tem **5** valores (brief citou 3).

Dataset 2 (`Document`, `Topic_group`) **ausente**.

## 003 — CRM pipeline

Hub `sales_pipeline` (8 800). Dimensões por **nome**, não UUID.

```
accounts 85  ←──?──  sales_pipeline 8800  ──→  products 7
                         │
                    sales_teams 35
```

| Join | Resultado |
|------|-----------|
| `pipeline.account` → `accounts.account` | 0 órfãos **quando não-nulo**; **1 425 null** (Prospecting 337 + Engaging 1 088). Won/Lost sempre têm conta. |
| `pipeline.sales_agent` → `sales_teams.sales_agent` | 0 órfãos; **5 agentes sem deal** |
| `pipeline.product` → `products.product` | **1 480 órfãos**: valor `GTXPro` vs catálogo `GTX Pro` |

`close_value` / `close_date` nulos ⇔ stage aberto. Lost ⇒ `close_value == 0`. Won min 38. `subsidiary_of` (15/85) aponta a **nomes que não estão** em `accounts` — não é self-FK.

Extra: `metadata.csv` (dicionário, 3 cols). Typos no dump: `technolgy`, `Philipines`.

## 004 — Social posts

Uma fato, 52 214 × 27. Grain = post.

| Esperado no brief | Observado |
|-------------------|-----------|
| `engagement rate` | **coluna ausente** — derivar |
| audience *distribution* | **um bucket** (`19-25`, `male`, `UK`) |
| ~52 k | 52 214 |
| plataformas 5 | Bilibili, YouTube, Instagram, RedNote, TikTok (quase iguais) |

`id` (int) e `content_id` (string) ambos únicos, **não iguais**. `creator_id` 5 000; `creator_name` ~10 nomes **por** creator — nome não é dimensão estável. `content_url` só 28 037 distintos. `is_sponsored` false ⇒ `disclosure_type=none`, `sponsor_category=Not sponsors` (sponsor_name mesmo assim preenchido).

Métricas quase sintéticas: views 9 676–10 551; engagement calculado ≈ 0,199 ± 0,005 (orgânico ≈ patrocinado).

Datas parseáveis: 2023-05-29 … 2025-05-28 (`M/D/YY I:MM AM`).

## O que os CSVs não são

- Banco relacional com constraints.
- PII real (001 é sintético; 002 tem e-mail no dump — tratar como dado de exercício).
- Join 001↔002↔003↔004.
