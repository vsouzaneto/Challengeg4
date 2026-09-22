# LAB 04 — SupportIQ

Notebook: `supportiq-customer-support-intelligence-platform.ipynb`

Origem: [SupportIQ – Customer Support Intelligence Platform](https://www.kaggle.com/code/hanumathureddygari/supportiq-customer-support-intelligence-platform) (SPEC-008).

Alterações para Databricks:

- Remove `/kaggle/input/...` e `kagglehub`
- Primeiro tenta `spark.table(catalog.schema.customer_support_tickets)` (Lab 01)
- Fallback: `pd.read_csv` em `dados/`
- Datas/timestamps e CSAT normalizados

O kernel original é diagnóstico + protótipo no Dataset 1. Dataset 2 continua ausente — classificador de 8 `Topic_group` não tem ground truth neste pacote.
