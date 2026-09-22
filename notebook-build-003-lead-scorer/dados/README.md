# `dados/` — CRM (challenge 003)

Contado no disco em 2026-09-21. Não inventar coluna.

| Arquivo | Linhas | Colunas |
| --- | ---: | --- |
| `accounts.csv` | 85 | `account`, `sector`, `year_established`, `revenue`, `employees`, `office_location`, `subsidiary_of` |
| `products.csv` | 7 | `product`, `series`, `sales_price` |
| `sales_teams.csv` | 35 | `sales_agent`, `manager`, `regional_office` |
| `sales_pipeline.csv` | 8800 | `opportunity_id`, `sales_agent`, `product`, `account`, `deal_stage`, `engage_date`, `close_date`, `close_value` |
| `metadata.csv` | 21 | `Table`, `Field`, `Description` — dicionário, não fato |

Joins: `account`, `product`, `sales_agent`. Hub = `sales_pipeline`.

`GTXPro` (1480) não casa com `GTX Pro`. `account` null em 1425 abertos. 5 agentes sem deal. `close_value` null se aberto; 0 se Lost.
