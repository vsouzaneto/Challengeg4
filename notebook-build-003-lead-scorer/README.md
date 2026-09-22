<img src="https://raw.githubusercontent.com/Databricks-BR/lab_agosto_2025/main/images/head_lab.png">

# Hands-On LAB — Challenge 003 (CRM / lead scorer)

Pacote Databricks do [challenge 003](../challenges/build-003-lead-scorer/README.md): ingestão dos 4 CSVs do CRM (+ dicionário), Assistant e o experimento de ranking Won/Lost.

Não use a massa da Receita Federal deste template. Fonte: [CRM Sales Predictive Analytics](https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics) (CC0), arquivos em `dados/`.

O brief pede **ferramenta que o vendedor abre** — o Lab 04 é a lógica de score (base), não a entrega.

## Estrutura

| Pasta | Papel |
| --- | --- |
| `dados/` | `accounts`, `products`, `sales_teams`, `sales_pipeline` + `metadata` — contrato no README da pasta |
| `01_LAB_importando_dados/` | Ingestão CSV → Delta (`workspace.crm.*`) |
| `02_LAB_Assistant/` | Perguntas ao Assistant só com colunas reais + [Genie](https://dbc-0dea39b3-be1e.cloud.databricks.com/genie/rooms/01f1b6165c871b51a8ec3e632bffa2ac?o=7474644277755368) |
| `03_LAB_Dashboard/` | Entregável vendedor — `lab03_dashboard.ipynb` |
| `04_ANALISE_crm/` | Kernel Kaggle adaptado (ranking Won/Lost) |
| `images/` `material/` | Artefatos opcionais do lab |

## Ementa

| # | Tópico | Duração |
| -- | -- | -- |
| 01 | Contexto RevOps + pedido da Head | 20 min |
| 02 | Databricks + AI/BI | 20 min |
| 03 | Lab 01 — ingestão dos CSVs (85 / 7 / 35 / 8800) | 30 min |
| 04 | Lab 02 — Assistant (órfão `GTXPro`, conta nula, close_value) | 30 min |
| 05 | Lab 03 — Dashboard AI/BI | 40 min |
| 06 | Lab 04 — CRM fields × deal outcomes | 40 min |

## Como rodar no Databricks

1. Importe `notebook-build-003-lead-scorer` para o Workspace (a pasta `dados/` precisa ir junto).
2. Widgets iguais em todos os labs: `catalog_name=workspace`, `schema_name=crm`.
3. **Run All** no Lab 01. Sem isso o Lab 02 e o 04 não acham as tabelas.
4. Se o auto-path falhar, `data_path` = `/Workspace/Users/<voce>/notebook-build-003-lead-scorer/dados`.

Armadilhas do dump (CSV ganha): `GTXPro` ≠ `GTX Pro`; `account` null em 1425 abertos; `close_value` null no pipe aberto (0 = Lost). Ver [SPEC-003](../.ai/specs/SPEC-003-lead-scorer.md).

## Referências

- [CSV no Databricks](https://docs.databricks.com/aws/en/query/formats/csv)
- [Delta](https://docs.databricks.com/aws/en/delta/tutorial)
- [Assistant](https://docs.databricks.com/aws/en/notebooks/databricks-assistant-faq)
- [AI/BI Dashboards](https://docs.databricks.com/aws/en/ai-bi/)
- Kernel de partida: [0.2 Do CRM Fields Actually Predict Deal Outcomes?](https://www.kaggle.com/code/vladimirbelsch/0-2-do-crm-fields-actually-predict-deal-outcomes)

## Comunidade Databricks Brasil

<a href="https://github.com/Databricks-BR"><img src="https://raw.githubusercontent.com/Databricks-BR/Databricks-BR/main/images/databricks-br.png" style="width: 40px; height: 40px;"></a>
