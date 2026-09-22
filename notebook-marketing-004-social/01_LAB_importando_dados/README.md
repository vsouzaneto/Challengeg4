<img src="https://raw.githubusercontent.com/Databricks-BR/lab_agosto_2025/main/images/head_lab.png">

# LAB 01 — Importando os dados Social

Notebook: `lab01_carga_csv.ipynb`

Lê `../dados/social_media_dataset.csv` (27 colunas do header) e grava Delta em `catalog.schema` (default `workspace.social`).

Valida: 52214 linhas e o conjunto exato de colunas. Se o CSV mudar, o lab falha de propósito.

`creator_id` é string (`creator_586`), não int. `id` é o inteiro.

Widgets: `catalog_name`, `schema_name`, `data_path`.
