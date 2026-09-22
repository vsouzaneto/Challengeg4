# LAB 04 — CRM fields × deal outcomes

Notebook: `0-2-do-crm-fields-actually-predict-deal-outcomes.ipynb`

Origem: [0.2 Do CRM Fields Actually Predict Deal Outcomes?](https://www.kaggle.com/code/vladimirbelsch/0-2-do-crm-fields-actually-predict-deal-outcomes) (SPEC-008).

Alterações para Databricks:

- Remove `/kaggle/input/...`
- Primeiro tenta `spark.table(catalog.schema.*)` (Lab 01)
- Fallback: `pd.read_csv` em `dados/`
- Datas normalizadas; `GTXPro` → `GTX Pro` **depois** da carga (o Lab 01 grava o valor cru)

O kernel original treina ranking só em Won/Lost. O brief pede ferramenta para o pipe **aberto** — este notebook é a base da lógica, não a entrega.
