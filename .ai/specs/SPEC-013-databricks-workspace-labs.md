---
status: passing
canonical: false
area: plataforma
created: 2026-09-21
last_updated: 2026-09-21
---

# SPEC-013 Workspace Databricks — upload + plano de execução

Workspace: [dbc-0dea39b3-be1e](https://dbc-0dea39b3-be1e.cloud.databricks.com/browse?o=7474644277755368). Pasta: `/Workspace/Users/adrianoaguiaralves@gmail.com/ai-master-challenge/`.

CLI Databricks não estava no PATH. Upload via Workspace REST API (token só em env; não gravado neste git).

## Comportamento visível

Os quatro pacotes de lab aparecem no Workspace. Job serverless: Lab 01 → Lab 02 → **Lab 03 (entregável)** → Lab 04. Notebook: `03_LAB_Dashboard/lab03_dashboard.ipynb` (SPEC-014).

## Jobs

| Pack | Workspace | Job | Schema | data_path |
| --- | --- | --- | --- | --- |
| 001 churn | `.../notebook-data-001-churn` | [lab-001-churn-execution](https://dbc-0dea39b3-be1e.cloud.databricks.com/jobs/463412912486977) (`463412912486977`) | `ravenstack` | `/Workspace/Users/adrianoaguiaralves@gmail.com/ai-master-challenge/notebook-data-001-churn/dados` |
| 002 support | `.../notebook-process-002-support` | [lab-002-support-execution](https://dbc-0dea39b3-be1e.cloud.databricks.com/jobs/888714546284385) (`888714546284385`) | `supportiq` | `/Workspace/Users/adrianoaguiaralves@gmail.com/ai-master-challenge/notebook-process-002-support/dados` |
| 003 crm | `.../notebook-build-003-lead-scorer` | [lab-003-crm-execution](https://dbc-0dea39b3-be1e.cloud.databricks.com/jobs/335361037070072) (`335361037070072`) | `crm` | `/Workspace/Users/adrianoaguiaralves@gmail.com/ai-master-challenge/notebook-build-003-lead-scorer/dados` |
| 004 social | `.../notebook-marketing-004-social` | [lab-004-social-execution](https://dbc-0dea39b3-be1e.cloud.databricks.com/jobs/22696065654490) (`22696065654490`) | `social` | `/Volumes/workspace/social/dados` (CSV 23 MB; Workspace import > 10 MB falhou) |

Catalog Unity: `workspace`. Widgets dos notebooks: `catalog_name`, `schema_name`, `data_path`.

## Plano de execução (todos os packs)

1. **01_LAB_importando_dados** — Job task `01_import`. Cria Delta. Bloqueia o resto.
2. **02_LAB_Assistant** — Task `02_assistant` (`depends_on` 01). SQL / Assistant.
3. **03_LAB_Dashboard** — Task `03_dashboard` (`depends_on` 02). Entregável (ENTREGAVEIS.md). Dashboard AI/BI publicado (SPEC-014).
4. **04_ANALISE_*** — Task `04_analise` (`depends_on` 03). Kernel adaptado.

Rodar: Jobs → job do pack → **Run now**. Ou abrir cada notebook e Run All, Lab 01 primeiro.

Dados: Catalog Explorer [explore/data](https://dbc-0dea39b3-be1e.cloud.databricks.com/explore/data?o=7474644277755368) depois do Lab 01 (`workspace.<schema>.*`).

## Verificação

- [x] 001–003: notebooks + CSVs + READMEs no Workspace.
- [x] Jobs 001, 002, 003 criados.
- [x] CSV 004 em `/Volumes/workspace/social/dados/social_media_dataset.csv`.
- [x] Job 004 criado (`22696065654490`).
- [ ] Run now dos 4 jobs **não** disparado na primeira entrega.
- [x] Hotfix 002: `multiLine` + Delta column mapping `name` (espaços em `Ticket ID`). Job **SUCCESS**.
- [x] Hotfix 004: `creator_id` string; `%pip` + SHAP `tree_path_dependent`/shape 3D. Job **SUCCESS**.
- [x] Genie Lab 02: [001](https://dbc-0dea39b3-be1e.cloud.databricks.com/genie/rooms/01f1b6165ad01ca4a5f3b95c6d3d3609?o=7474644277755368) [002](https://dbc-0dea39b3-be1e.cloud.databricks.com/genie/rooms/01f1b6165bac181a9836cde73e8e7556?o=7474644277755368) [003](https://dbc-0dea39b3-be1e.cloud.databricks.com/genie/rooms/01f1b6165c871b51a8ec3e632bffa2ac?o=7474644277755368) [004](https://dbc-0dea39b3-be1e.cloud.databricks.com/genie/rooms/01f1b6165d6e1a8bbb831d2a78fd6929?o=7474644277755368). SPEC-018.
- [x] Dashboards AI/BI publicados: [001](https://dbc-0dea39b3-be1e.cloud.databricks.com/dashboardsv3/01f1b611c23d1c1d8abb2e1d9847d535/published?o=7474644277755368) [002](https://dbc-0dea39b3-be1e.cloud.databricks.com/dashboardsv3/01f1b611c9d4161bac29737cf1c07d47/published?o=7474644277755368) [003](https://dbc-0dea39b3-be1e.cloud.databricks.com/dashboardsv3/01f1b611cd0118a78e40dc8a5f8a3609/published?o=7474644277755368) [004](https://dbc-0dea39b3-be1e.cloud.databricks.com/dashboardsv3/01f1b611d0801412b387d62b0dc4d8d6/published?o=7474644277755368).
- [x] Conferência ao vivo (2026-09-21): os 4 `ACTIVE`, published, `embed_credentials=true`, warehouse `1dfbeda79d9a368d`.
- [x] Embed em [http://localhost:3010/](http://localhost:3010/) (`src/monorepos/aibi-dashboards-external-embedding`) devolve config dos 4. Service principal `aibi-external-embedding`; segredo só no `.env` local.
- [x] Host `localhost:3010` troca Alice/Bob por quatro personas, uma por lab: CEO RavenStack (Receita), Diretor de Operações (Operações), Head de RevOps (RevOps), Head de Marketing (Marketing). Cada uma abre o dashboard do próprio lab. `external_viewer_id` + `external_value` seguem o contrato de embed.
- [x] SCIM do workspace (2026-09-21): `USER_COUNT` 1. `POST /api/2.0/preview/scim/v2/Users` das quatro personas devolve 409 — o workspace trata alias com `+` do mesmo Gmail como a mesma identidade do administrador. Não há assento separado para criar.
- [x] Domínios aprovados (2026-09-21): `PATCH /api/2.0/settings/types/aibi_dash_embed_ws_apprvd_domains/names/default` gravou `localhost:3010`, `localhost:3020`, `127.0.0.1:3010`, `127.0.0.1:3020`. A lista estava vazia. O setting `aibi_dashboard_embedding_access_policy` não existe neste workspace (404). Doc: [embed admin](https://docs.databricks.com/aws/en/ai-bi/admin/embed).
- [ ] Confirmar no browser, depois de atualizar a página, se o iframe de [http://localhost:3020/sdk/dashboards](http://localhost:3020/sdk/dashboards) deixou de mostrar “Embedding dashboards is not available in this workspace”.

## Evidência

2026-09-21: REST `workspace/import` (JUPYTER + AUTO). DBFS FileStore público recusado (`PERMISSION_DENIED`). User `adrianoaguiaralves@gmail.com`.

## Sucesso / falha

- Sucesso: pasta dos 4 packs no Workspace; 4 jobs listados; Lab 01 grava Delta.
- Falha: token em arquivo do git; inventar coluna; pular Lab 01.

## Segurança

PAT não entra em SPEC, README, commit ou `mcp.json`. Se o token foi colado no chat, rotacionar no Databricks.
