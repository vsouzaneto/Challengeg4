<img src="https://raw.githubusercontent.com/Databricks-BR/lab_agosto_2025/main/images/head_lab.png">

# LAB 01 — Importando os dados RavenStack

Notebook: `lab01_carga_csv.ipynb`

Lê `../dados/ravenstack_*.csv` (colunas do header, linha a linha) e grava Delta em `catalog.schema` (default `workspace.ravenstack`).

Valida: 500 / 5000 / 25000 / 2000 / 600 linhas e o conjunto exato de colunas. Se o CSV mudar, o lab falha de propósito.

Widgets: `catalog_name`, `schema_name`, `data_path`.
