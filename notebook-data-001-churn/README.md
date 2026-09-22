

# Hands-On LAB — Challenge 001 (RavenStack / churn)

Pacote Databricks do [challenge 001](../challenges/data-001-churn/README.md): ingestão dos 5 CSVs, Assistant e análise de retenção / risco de receita.

Não use a massa da Receita Federal deste template. Fonte: [SaaS Subscription & Churn Analytics](https://www.kaggle.com/datasets/rivalytics/saas-subscription-and-churn-analytics-dataset) (MIT), arquivos em `dados/`.

## Estrutura

| Pasta | Papel |
| --- | --- |
| `dados/` | 5 `ravenstack_*.csv` — contrato de colunas no README da pasta |
| `01_LAB_importando_dados/` | Ingestão CSV → Delta (`workspace.ravenstack.ravenstack_*`) |
| `02_LAB_Assistant/` | Perguntas ao Assistant só com colunas reais + [Genie](https://dbc-0dea39b3-be1e.cloud.databricks.com/genie/rooms/01f1b6165ad01ca4a5f3b95c6d3d3609?o=7474644277755368) |
| `03_LAB_Dashboard/` | Entregável CEO — `lab03_dashboard.ipynb` |
| `04_ANALISE_retention/` | Kernel Kaggle adaptado para Databricks |
| `images/` `material/` | Artefatos opcionais do lab |

## Ementa

| # | Tópico | Duração |
| -- | -- | -- |
| 01 | Contexto RavenStack + objetivo do CEO | 20 min |
| 02 | Databricks + AI/BI | 20 min |
| 03 | Lab 01 — ingestão dos 5 CSVs | 30 min |
| 04 | Lab 02 — Assistant (joins + trap `churn_flag`) | 30 min |
| 05 | Lab 03 — Dashboard AI/BI | 40 min |
| 06 | Lab 04 — Retention & Revenue Risk | 40 min |

## Como rodar no Databricks

1. Importe `notebook-data-001-churn` para o Workspace (a pasta `dados/` precisa ir junto).
2. Widgets iguais em todos os labs: `catalog_name=workspace`, `schema_name=ravenstack`.
3. **Run All** no Lab 01. Sem isso o Lab 02 e o 04 não acham as tabelas.
4. Se o auto-path falhar, `data_path` = `/Workspace/Users/<voce>/notebook-data-001-churn/dados`.

Label canônico de churn = linha em `ravenstack_churn_events`. `accounts.churn_flag` diverge — ver [SPEC-001](../.ai/specs/SPEC-001-churn.md).

## Referências

- [CSV no Databricks](https://docs.databricks.com/aws/en/query/formats/csv)
- [Delta](https://docs.databricks.com/aws/en/delta/tutorial)
- [Assistant](https://docs.databricks.com/aws/en/notebooks/databricks-assistant-faq)
- [AI/BI Dashboards](https://docs.databricks.com/aws/en/ai-bi/)
- Kernel de partida: [SaaS Retention & Revenue Risk Analytics](https://www.kaggle.com/code/bogdanamatrofailo/saas-retention-revenue-risk-analytics)

## Comunidade Databricks Brasil

<a href="https://github.com/Databricks-BR"><img src="https://raw.githubusercontent.com/Databricks-BR/Databricks-BR/main/images/databricks-br.png" style="width: 40px; height: 40px;"></a>
