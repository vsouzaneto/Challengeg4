# Dados e proveniência

O projeto usa o dataset CRM Sales Predictive Analytics indicado pelo challenge ([fonte no Kaggle](https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics)). A especificação do challenge declara licença CC0. Os CSVs fornecidos acompanham `solution/data/raw/`.

- `sales_pipeline.csv`: 8.800 oportunidades, chave `opportunity_id`.
- `accounts.csv`: 85 contas.
- `products.csv`: 7 produtos e preço de catálogo.
- `sales_teams.csv`: 35 vendedores, managers e regiões.
- `metadata.csv`: dicionário auxiliar dos campos.

O pipeline é a tabela central. As dimensões são associadas com left joins `many_to_one`, sem eliminar oportunidades sem conta. `GTXPro` é normalizado para `GTX Pro` apenas na camada preparada. A ausência de conta não tem causa confirmada; valores ausentes não são fabricados.

A referência `2017-12-31` é demonstrativa. A idade desde `engage_date` não indica último contato. `close_date` e `close_value` não alimentam a prioridade de oportunidades abertas.
