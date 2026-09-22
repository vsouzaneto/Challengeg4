---
status: passing
canonical: false
area: dados
created: 2026-09-21
last_updated: 2026-09-21
---

# SPEC-009 Lab Databricks — challenge 001

Pacote em `notebook-data-001-churn/`. Brief e colunas: [SPEC-001](SPEC-001-churn.md) + CSV em `dados/` (CSV ganha).

## Comportamento visível

O candidato sobe a pasta no Workspace Databricks, roda Lab 01 e passa a ter 5 tabelas Delta com o mesmo schema dos CSVs. Lab 02 e Lab 04 leem essas tabelas. Não há massa Receita Federal / CNPJ.

## Contrato

| Artefato | Deve |
| --- | --- |
| `dados/ravenstack_*.csv` | 500 / 5000 / 25000 / 2000 / 600 linhas; colunas = header |
| Lab 01 | `spark.read.csv` → Delta `catalog.schema.ravenstack_*`; falha se coluna ou n de linha divergir |
| Lab 02 | SQL só com colunas reais; mostra trap `churn_flag` ≠ evento |
| Lab 04 | Sem `/kaggle/input`; Delta primeiro, CSV fallback; bool/data normalizados |
| Widgets | `catalog_name` (default `workspace`), `schema_name` (`ravenstack`), `data_path` opcional |

Label canônico = `ravenstack_churn_events`. Lab 04 ainda plota KPI com `accounts.churn_flag` (origem Kaggle) — a doc do lab declara a divergência.

## Verificação

- [x] Headers dos 5 CSVs conferidos no disco (2026-09-21).
- [x] Lab 01 lista o contrato e valida n de linhas.
- [x] Lab 04 sem path Kaggle.
- [x] Pacote no Workspace: `/Workspace/Users/adrianoaguiaralves@gmail.com/ai-master-challenge/notebook-data-001-churn`.
- [x] Job [lab-001-churn-execution](https://dbc-0dea39b3-be1e.cloud.databricks.com/jobs/463412912486977).
- [ ] Run now do Job **não** disparado na primeira entrega (tabelas `ravenstack_*` existem no UC).
- [x] Dashboard [lab-001-churn-ceo](https://dbc-0dea39b3-be1e.cloud.databricks.com/dashboardsv3/01f1b611c23d1c1d8abb2e1d9847d535/published?o=7474644277755368).
- [x] Ao vivo (2026-09-21): `ACTIVE`, published, `embed_credentials=true`. Embed local 200.
- [x] Persona do host `localhost:3010`: `ceo` / CEO RavenStack / Receita. Painel padrão `01f1b611c23d1c1d8abb2e1d9847d535`.
- [x] Genie [lab-001-churn-genie](https://dbc-0dea39b3-be1e.cloud.databricks.com/genie/rooms/01f1b6165ad01ca4a5f3b95c6d3d3609?o=7474644277755368) (`01f1b6165ad01ca4a5f3b95c6d3d3609`). Sala chatbot `/room/churn`.

## Evidência

2026-09-21: pasta reorganizada (`01`–`04` + `dados/`). Kernel SPEC-008 copiado para `04_ANALISE_retention/`.

## Sucesso / falha

- Sucesso: Lab 01 cria 5 tabelas; Lab 02 mostra contas; Lab 04 desenha KPIs sem `/kaggle/input`.
- Falha: inventar coluna; usar `churn_flag` como única verdade; apontar Receita Federal.
