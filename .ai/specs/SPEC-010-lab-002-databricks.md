---
status: passing
canonical: false
area: ops-cx
created: 2026-09-21
last_updated: 2026-09-21
---

# SPEC-010 Lab Databricks — challenge 002

Pacote em `notebook-process-002-support/`. Brief e colunas: [SPEC-002](SPEC-002-support.md) + CSV em `dados/` (CSV ganha).

## Comportamento visível

O candidato sobe a pasta no Workspace Databricks, roda Lab 01 e passa a ter `workspace.supportiq.customer_support_tickets` com as 17 colunas do CSV. Lab 02 e Lab 04 leem essa tabela. Não há massa Receita Federal / CNPJ. Não há Dataset 2.

## Contrato

| Artefato | Deve |
| --- | --- |
| `dados/customer_support_tickets.csv` | 8469 linhas; 17 colunas = header (espaços inclusos) |
| Lab 01 | `spark.read.csv` → Delta `catalog.schema.customer_support_tickets`; falha se coluna ou n de linha divergir |
| Lab 02 | SQL só com colunas reais (backtick); horas = TTR − FRT em Closed |
| Lab 04 | Sem `/kaggle/input`; Delta primeiro, CSV fallback |
| Widgets | `catalog_name` (default `workspace`), `schema_name` (`supportiq`), `data_path` opcional |

Brief vs disco (não “corrigir” o CSV): ~30k → 8469; Type 3 → 5; `Time to Resolution` é datetime; Dataset 2 ausente.

## Verificação

- [x] Header e 8469 linhas conferidos no disco (2026-09-21).
- [x] Lab 01 lista o contrato e valida n de linhas.
- [x] Lab 04 sem path Kaggle / kagglehub.
- [x] Pacote no Workspace: `/Workspace/Users/adrianoaguiaralves@gmail.com/ai-master-challenge/notebook-process-002-support`.
- [x] Job [lab-002-support-execution](https://dbc-0dea39b3-be1e.cloud.databricks.com/jobs/888714546284385).
- [x] Lab 01: `multiLine=true` — sem isso Spark lê 18762 linhas (texto com newline).
- [x] Lab 01: Delta column mapping `name` — Unity Catalog recusa espaço em `Ticket ID` etc.
- [x] Dashboard [lab-002-support-ops](https://dbc-0dea39b3-be1e.cloud.databricks.com/dashboardsv3/01f1b611c9d4161bac29737cf1c07d47/published?o=7474644277755368).
- [x] Ao vivo (2026-09-21): `ACTIVE`, published, `embed_credentials=true`. Embed local 200.
- [x] Persona do host `localhost:3010`: `operacoes` / Diretor de Operações / Operações. Painel padrão `01f1b611c9d4161bac29737cf1c07d47`.
- [x] Genie [lab-002-support-genie](https://dbc-0dea39b3-be1e.cloud.databricks.com/genie/rooms/01f1b6165bac181a9836cde73e8e7556?o=7474644277755368) (`01f1b6165bac181a9836cde73e8e7556`). Sala chatbot `/room/support`.

## Evidência

2026-09-21: pasta reorganizada (`01`–`04` + `dados/`). Kernel SPEC-008 copiado para `04_ANALISE_supportiq/`.

## Sucesso / falha

- Sucesso: Lab 01 cria 1 tabela; Lab 02 mostra gargalo em horas; Lab 04 desenha KPIs sem `/kaggle/input`.
- Falha: inventar `Topic_group`; tratar TTR como horas; apontar Receita Federal; dump de e-mail no PR.
