# Dados brutos (imutáveis)

Fonte: [CRM Sales Predictive Analytics](https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics) — licença CC0 (domínio público), o que permite redistribuir esta cópia para que a solução rode sem credenciais do Kaggle.

Baixado em 2026-09-22 via `https://www.kaggle.com/api/v1/datasets/download/agungpambudi/crm-sales-predictive-analytics`.

| Arquivo | Linhas | Observação |
|---|---|---|
| `sales_pipeline.csv` | 8.800 | Tabela central. `opportunity_id` único. |
| `accounts.csv` | 85 | Setor `technolgy` (typo original). |
| `products.csv` | 7 | Pipeline usa `GTXPro`, catálogo usa `GTX Pro`. |
| `sales_teams.csv` | 35 | 6 managers, 3 escritórios. |
| `metadata.csv` | 21 | Dicionário de dados do próprio dataset. |

**Regra:** nada nesta pasta é editado à mão. Limpeza acontece em código, em `solution/`, e é verificável por `SHA256SUMS`:

```bash
cd solution/data/raw && shasum -a 256 -c SHA256SUMS
```
