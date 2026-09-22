---
status: passing
canonical: false
area: marketing
created: 2026-09-21
last_updated: 2026-09-21
---

# SPEC-012 Lab Databricks — challenge 004

Pacote em `notebook-marketing-004-social/`. Brief e colunas: [SPEC-004](SPEC-004-social.md) + CSV em `dados/` (CSV ganha).

## Comportamento visível

O candidato sobe a pasta no Workspace Databricks, roda Lab 01 e passa a ter `workspace.social.social_media_dataset` com as 27 colunas do CSV. Lab 02 e Lab 04 leem essa tabela. Não há massa Receita Federal / CNPJ.

## Contrato

| Artefato | Deve |
| --- | --- |
| `dados/social_media_dataset.csv` | 52214 linhas; 27 colunas = header |
| Lab 01 | `spark.read.csv` → Delta; falha se coluna ou n de linha divergir; não cria `engagement_rate` |
| Lab 02 | SQL só com colunas reais; taxa derivada; controle platform × category × sponsor; trap `creator_name` |
| Lab 04 | Sem `/kaggle/input`; Delta primeiro, CSV fallback |
| Widgets | `catalog_name` (default `workspace`), `schema_name` (`social`), `data_path` opcional |

Brief vs disco: sem `engagement_rate`; audiência é bucket; sem custo; métricas quase constantes.

## Verificação

- [x] Header e 52214 linhas conferidos no disco (2026-09-21).
- [x] Lab 01 lista o contrato e valida n de linhas.
- [x] Lab 04 sem path Kaggle.
- [x] Pacote no Workspace (notebooks + README). CSV 23 MB em `/Volumes/workspace/social/dados`.
- [x] Job [lab-004-social-execution](https://dbc-0dea39b3-be1e.cloud.databricks.com/jobs/22696065654490).
- [x] Lab 01: `creator_id` permanece string (`creator_586`); não fazer cast para int.
- [x] Lab 04: `%pip install xgboost textblob shap` no job serverless.
- [x] Lab 04: SHAP `tree_path_dependent` + matriz 3D (`shap_values[:, :, 4]`) no shap atual.
- [x] Dashboard [lab-004-social-media](https://dbc-0dea39b3-be1e.cloud.databricks.com/dashboardsv3/01f1b611d0801412b387d62b0dc4d8d6/published?o=7474644277755368).
- [x] Ao vivo (2026-09-21): `ACTIVE`, published, `embed_credentials=true`. Embed local 200.
- [x] Persona do host `localhost:3010`: `marketing` / Head de Marketing / Marketing. Painel padrão `01f1b611d0801412b387d62b0dc4d8d6`.
- [x] Genie [lab-004-social-genie](https://dbc-0dea39b3-be1e.cloud.databricks.com/genie/rooms/01f1b6165d6e1a8bbb831d2a78fd6929?o=7474644277755368) (`01f1b6165d6e1a8bbb831d2a78fd6929`). Sala chatbot `/room/social`.

## Evidência

2026-09-21: pasta reorganizada (`01`–`04` + `dados/`). Kernel SPEC-008 destino `04_ANALISE_social/`.

## Sucesso / falha

- Sucesso: Lab 01 cria 1 tabela; Lab 02 mostra taxa controlada; Lab 04 roda sem `/kaggle/input`.
- Falha: inventar `engagement_rate` nativo; média crua org/ads como conclusão; apontar Receita Federal; usar `creator_name` como PK.
