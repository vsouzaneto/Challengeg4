# ERD — índice (schema observado nos CSVs)

Leitura **2026-09-21** dos dumps em `datasets/` (gitignored). Não há SQL/Prisma. Grain = uma linha de CSV.

Os quatro domínios **não** compartilham entidade. `account_id` do 001 ≠ `account` do 003.

| Serviço | Pasta CSV | Arquivos | n observado | Diagrama |
|---------|-----------|----------|-------------|----------|
| 001 Churn | `datasets/data-001-churn/` | 5 `ravenstack_*.csv` | 500 / 5 000 / 25 000 / 2 000 / 600 | [data-001-churn.md](data-001-churn.md) |
| 002 Support | `datasets/process-002-support/` | **1** `customer_support_tickets.csv` | 8 469 | [process-002-support.md](process-002-support.md) |
| 003 Lead Scorer | `datasets/build-003-lead-scorer/` | 4 fatos + `metadata.csv` | 85 / 7 / 35 / 8 800 | [build-003-lead-scorer.md](build-003-lead-scorer.md) |
| 004 Social | `datasets/marketing-004-social/` | 1 `social_media_dataset.csv` | 52 214 × 27 cols | [marketing-004-social.md](marketing-004-social.md) |

| Doc | Papel |
|-----|-------|
| [SPEC-REVERSE.md](SPEC-REVERSE.md) | O que os CSVs **são** (chaves, nulos, enums, traps) |
| [SPEC-DRIVEN.md](SPEC-DRIVEN.md) | Como cruzar sem inventar coluna ou join |
| Inventário | [../architecture/DATA-SOURCES.md](../architecture/DATA-SOURCES.md) |
| Spec | [../specs/SPEC-007-data-domains.md](../specs/SPEC-007-data-domains.md) |

## Ausente no disco

| Esperado pelo brief | Status 2026-09-21 |
|---------------------|-------------------|
| 002 Dataset 2 — IT Service Ticket Classification (~48 k, `Document` + `Topic_group`) | **não está** na pasta. O zip só contém o mesmo `customer_support_tickets.csv`. |
| Coluna `engagement rate` no 004 | **não existe**. Calcular `(likes+shares+comments_count)/views`. |

Não completar Dataset 2 de memória. Se o Kaggle for baixado depois, reamostrar e bump da spec.
