# LAB 04 — Retention & Revenue Risk

Notebook: `saas-retention-revenue-risk-analytics.ipynb`

Origem: [SaaS Retention & Revenue Risk Analytics](https://www.kaggle.com/code/bogdanamatrofailo/saas-retention-revenue-risk-analytics) (SPEC-008).

Alterações para Databricks:

- Remove `/kaggle/input/...`
- Primeiro tenta `spark.table(catalog.schema.ravenstack_*)` (Lab 01)
- Fallback: `pd.read_csv` em `dados/`
- Booleanos e datas normalizados (CSV traz `True`/`False` como texto)

O kernel original calcula KPI com `accounts.churn_flag`. No challenge 001 o label canônico é `churn_events` — use as duas visões e declare a divergência.
