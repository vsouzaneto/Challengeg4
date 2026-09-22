<img src="https://raw.githubusercontent.com/Databricks-BR/lab_agosto_2025/main/images/head_lab.png">

# Hands-On LAB — Challenge 004 (Social / engagement)

Pacote Databricks do [challenge 004](../challenges/marketing-004-social/README.md): ingestão do CSV de 52 214 posts, Assistant e o kernel de engagement.

Não use a massa da Receita Federal deste template. Fonte: [Social Media Sponsorship & Engagement Dataset](https://www.kaggle.com/datasets/omenkj/social-media-sponsorship-and-engagement-dataset) (MIT), arquivo em `dados/`.

## Estrutura

| Pasta | Papel |
| --- | --- |
| `dados/` | `social_media_dataset.csv` — 52214 × 27; contrato no README da pasta |
| `01_LAB_importando_dados/` | Ingestão CSV → Delta (`workspace.social.social_media_dataset`) |
| `02_LAB_Assistant/` | Perguntas ao Assistant só com colunas reais + [Genie](https://dbc-0dea39b3-be1e.cloud.databricks.com/genie/rooms/01f1b6165d6e1a8bbb831d2a78fd6929?o=7474644277755368) |
| `03_LAB_Dashboard/` | Entregável Marketing — `lab03_dashboard.ipynb` |
| `04_ANALISE_social/` | Kernel Kaggle adaptado para Databricks |
| `images/` | Artefatos opcionais do lab |

## Ementa

| # | Tópico | Duração |
| -- | -- | -- |
| 01 | Contexto Marketing + pedido do Head | 20 min |
| 02 | Databricks + AI/BI | 20 min |
| 03 | Lab 01 — ingestão do CSV (52 214 posts) | 30 min |
| 04 | Lab 02 — Assistant (taxa derivada, controle org/ads) | 30 min |
| 05 | Lab 03 — Dashboard AI/BI | 40 min |
| 06 | Lab 04 — Engagement analyser | 40 min |

## Como rodar no Databricks

1. Importe `notebook-marketing-004-social` para o Workspace (a pasta `dados/` precisa ir junto).
2. Widgets iguais em todos os labs: `catalog_name=workspace`, `schema_name=social`.
3. **Run All** no Lab 01. Sem isso o Lab 02 e o 04 não acham a tabela.
4. Se o auto-path falhar, `data_path` = `/Workspace/Users/<voce>/notebook-marketing-004-social/dados`.

Armadilhas do dump (CSV ganha): sem `engagement_rate`; taxa por view ≈ 0,199; `creator_name` ≠ PK; audiência é bucket; sem custo de sponsor. Ver [SPEC-004](../.ai/specs/SPEC-004-social.md).

## Referências

- [CSV no Databricks](https://docs.databricks.com/aws/en/query/formats/csv)
- [Delta](https://docs.databricks.com/aws/en/delta/tutorial)
- [Assistant](https://docs.databricks.com/aws/en/notebooks/databricks-assistant-faq)
- [AI/BI Dashboards](https://docs.databricks.com/aws/en/ai-bi/)
- Kernel de partida: [aba Code do dataset](https://www.kaggle.com/datasets/omenkj/social-media-sponsorship-and-engagement-dataset/code)

## Comunidade Databricks Brasil

<a href="https://github.com/Databricks-BR"><img src="https://raw.githubusercontent.com/Databricks-BR/Databricks-BR/main/images/databricks-br.png" style="width: 40px; height: 40px;"></a>
