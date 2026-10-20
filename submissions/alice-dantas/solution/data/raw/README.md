# Dados brutos

Os CSVs **não são versionados** (decisão D-2 do [PRD](../../../docs/prd.md)). Para rodar a solução:

1. Baixe pelo navegador o dataset [CRM Sales Predictive Analytics](https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics) (licença CC0). Não é preciso token do Kaggle.
2. Copie os arquivos abaixo para esta pasta (`solution/data/raw/`), sem renomear.
3. Confira com `.venv/bin/python -m leadscorer check-data` (a partir de `solution/`).

| Arquivo | Obrigatório | SHA-256 auditado |
| --- | --- | --- |
| `sales_pipeline.csv` | Sim | `825ce8f6c32d4009548b468df3173d55a46fd73f2531f532c5459371dc52adf2` |
| `products.csv` | Sim | `7c1c8cbbdb6d4c286902e1985eeb529a36366d6a43f43cd4a93c4b1da2a6eb84` |
| `sales_teams.csv` | Sim | `aeff1272ebe196f5a27e3fc0578aa27abf48ed9ae461aa344fb95990e5ad8bd1` |
| `accounts.csv` | Sim | `e5242324768a563fc632cddfed49a29acbbf2892b8a3c6453cc9650de9ae0358` |
| `metadata.csv` | Não (só a auditoria usa) | `22b34e498d07e3d7f322afdbf81d70a5dc0a389792944e50ca2af86a3597f0af` |

Com outro hash, a solução roda, mas avisa "dados diferentes da versão auditada", e os números do PRD deixam de ser garantidos.
