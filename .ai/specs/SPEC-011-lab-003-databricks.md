---
status: passing
canonical: false
area: revops
created: 2026-09-21
last_updated: 2026-09-21
---

# SPEC-011 Lab Databricks — challenge 003

Pacote em `notebook-build-003-lead-scorer/`. Brief e colunas: [SPEC-003](SPEC-003-lead-scorer.md) + CSV em `dados/` (CSV ganha).

## Comportamento visível

O candidato sobe a pasta no Workspace Databricks, roda Lab 01 e passa a ter `workspace.crm.accounts` / `products` / `sales_teams` / `sales_pipeline` (+ `metadata`). Lab 02 e Lab 04 leem essas tabelas. Não há massa Receita Federal / CNPJ.

## Contrato

| Artefato | Deve |
| --- | --- |
| `dados/*.csv` | 85 / 7 / 35 / 8800 / 21 linhas; colunas = header |
| Lab 01 | `spark.read.csv` → Delta; falha se coluna ou n de linha divergir; **não** reescreve `GTXPro` |
| Lab 02 | SQL só com colunas reais; mostra órfão `GTXPro`, conta nula, agentes sem deal |
| Lab 04 | Sem `/kaggle/input`; Delta primeiro, CSV fallback; normaliza `GTXPro` depois da carga |
| Widgets | `catalog_name` (default `workspace`), `schema_name` (`crm`), `data_path` opcional |

Lab 04 ranqueia Won/Lost. O brief pede ferramenta para o pipe aberto — o lab não substitui o deliverable.

## Verificação

- [x] Headers e n de linhas conferidos no disco (2026-09-21).
- [x] Lab 01 lista o contrato e valida n de linhas.
- [x] Lab 04 sem path Kaggle.
- [x] Pacote no Workspace: `/Workspace/Users/adrianoaguiaralves@gmail.com/ai-master-challenge/notebook-build-003-lead-scorer`.
- [x] Job [lab-003-crm-execution](https://dbc-0dea39b3-be1e.cloud.databricks.com/jobs/335361037070072).
- [ ] Run now do Job **não** disparado na primeira entrega (tabelas `crm.*` existem no UC).
- [x] Dashboard [lab-003-crm-seller](https://dbc-0dea39b3-be1e.cloud.databricks.com/dashboardsv3/01f1b611cd0118a78e40dc8a5f8a3609/published?o=7474644277755368).
- [x] Ao vivo (2026-09-21): `ACTIVE`, published, `embed_credentials=true`. Embed local 200.
- [x] Persona do host `localhost:3010`: `revops` / Head de RevOps / RevOps. Painel padrão `01f1b611cd0118a78e40dc8a5f8a3609`.
- [x] Genie [lab-003-crm-genie](https://dbc-0dea39b3-be1e.cloud.databricks.com/genie/rooms/01f1b6165c871b51a8ec3e632bffa2ac?o=7474644277755368) (`01f1b6165c871b51a8ec3e632bffa2ac`). Sala chatbot `/room/crm`.

## Evidência

2026-09-21: pasta reorganizada (`01`–`04` + `dados/`). Kernel SPEC-008 copiado para `04_ANALISE_crm/`.

## Sucesso / falha

- Sucesso: Lab 01 cria 5 tabelas; Lab 02 mostra `GTXPro` órfão; Lab 04 roda sem `/kaggle/input`.
- Falha: inventar coluna; inner-join conta no pipe aberto; apontar Receita Federal; tratar Lab 04 como a ferramenta do vendedor.
