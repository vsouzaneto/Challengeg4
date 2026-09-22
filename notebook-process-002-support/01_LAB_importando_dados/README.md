# LAB 01 — Importando os dados SupportIQ

Notebook: `lab01_carga_csv.ipynb`

Lê `../dados/customer_support_tickets.csv` (17 colunas do header, incluindo espaços) e grava Delta em `catalog.schema` (default `workspace.supportiq`).

Valida: 8469 linhas e o conjunto exato de colunas. Se o CSV mudar, o lab falha de propósito.

Spark: `multiLine=true` — `Ticket Description` / `Resolution` têm quebra de linha (sem isso o reader inventa ~18k linhas).

Delta: column mapping `name` — Unity Catalog recusa espaço em nome de coluna sem isso.

Widgets: `catalog_name`, `schema_name`, `data_path`.
