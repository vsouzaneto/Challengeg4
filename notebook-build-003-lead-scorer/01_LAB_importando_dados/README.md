# LAB 01 — Importando os dados CRM

Notebook: `lab01_carga_csv.ipynb`

Lê `../dados/*.csv` (colunas do header) e grava Delta em `catalog.schema` (default `workspace.crm`).

Valida: 85 / 7 / 35 / 8800 / 21 linhas e o conjunto exato de colunas. Se o CSV mudar, o lab falha de propósito.

Não reescreve `GTXPro` → `GTX Pro` na ingestão. Widgets: `catalog_name`, `schema_name`, `data_path`.