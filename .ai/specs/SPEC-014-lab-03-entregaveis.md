---
status: passing
canonical: false
area: entrega
created: 2026-09-21
last_updated: 2026-09-21
---

# SPEC-014 Lab 03 — entregáveis dos 4 challenges

Contrato de conteúdo: [ENTREGAVEIS.md](../../ENTREGAVEIS.md) + SPEC-001–004. CSV ganha. Kernel Kaggle = Lab 04 (partida), não o entregável.

## Comportamento visível

Depois do Lab 01, o candidato abre o dashboard AI/BI publicado (ou `03_LAB_Dashboard/lab03_dashboard.ipynb` → Run All). Os tiles usam as mesmas queries do notebook, com tabelas `workspace.<schema>.*`.

## Contrato

| Pack | Notebook | Dashboard | Deve entregar |
| --- | --- | --- | --- |
| 001 | `notebook-data-001-churn/03_LAB_Dashboard/lab03_dashboard.ipynb` | [lab-001-churn-ceo](https://dbc-0dea39b3-be1e.cloud.databricks.com/dashboardsv3/01f1b611c23d1c1d8abb2e1d9847d535/published?o=7474644277755368) (`01f1b611c23d1c1d8abb2e1d9847d535`) | Causa cruzando 5 tabelas; segmentos; 25 `account_id` com ARR; ações. Label = `churn_events` |
| 002 | `notebook-process-002-support/03_LAB_Dashboard/lab03_dashboard.ipynb` | [lab-002-support-ops](https://dbc-0dea39b3-be1e.cloud.databricks.com/dashboardsv3/01f1b611c9d4161bac29737cf1c07d47/published?o=7474644277755368) (`01f1b611c9d4161bac29737cf1c07d47`) | Gargalo p95 horas; CSAT Closed; horas; roteador `route`; o que não automatizar. Sem `Topic_group` |
| 003 | `notebook-build-003-lead-scorer/03_LAB_Dashboard/lab03_dashboard.ipynb` | [lab-003-crm-seller](https://dbc-0dea39b3-be1e.cloud.databricks.com/dashboardsv3/01f1b611cd0118a78e40dc8a5f8a3609/published?o=7474644277755368) (`01f1b611cd0118a78e40dc8a5f8a3609`) | Pipe aberto com `score` + `why`; não ordena por `close_value` |
| 004 | `notebook-marketing-004-social/03_LAB_Dashboard/lab03_dashboard.ipynb` | [lab-004-social-media](https://dbc-0dea39b3-be1e.cloud.databricks.com/dashboardsv3/01f1b611d0801412b387d62b0dc4d8d6/published?o=7474644277755368) (`01f1b611d0801412b387d62b0dc4d8d6`) | Taxa derivada controlada; org vs ads cru vs controlado; audiência bucket; estratégia. Sem `engagement_rate` nativo |

Job: 01_import → 02_assistant → **03_dashboard** → 04_analise. Lab 02 também tem espaço Genie (SPEC-018).

Painéis gráficos comuns (colunas reais; sem inventar métrica persistida no CSV):

| Seção | 001 | 002 | 003 | 004 |
| --- | --- | --- | --- | --- |
| Ranking | eventos por país | p95 horas por canal | win rate do agente | taxa derivada |
| Galeria | contas com evento | fila aberta sem e-mail | pipe aberto | posts |
| Classificação | `reason_code` | `Ticket Type` | `deal_stage` | `content_type` |
| Segmentação | industry × plan | canal × prioridade × tipo | `sector` | platform × categoria |
| Imagem | indisponível | indisponível | indisponível | proxy `content_type` |
| Modelo / matriz / curva / viés | evento de churn | CSAT ≥ 4 | Won vs Lost | taxa > mediana |

## Verificação

- [x] Quatro `lab03_dashboard.ipynb` no disco (2026-09-21).
- [x] ENTREGAVEIS.md aponta os notebooks.
- [x] Upload Workspace + jobs com task `03_dashboard` (2026-09-21).
- [x] Quatro dashboards Lakeview publicados (2026-09-21). Warehouse `1dfbeda79d9a368d`. `.lvdash.json` em cada `03_LAB_Dashboard`.
- [x] Conferência ao vivo (2026-09-21): `lab-001-churn-ceo`, `lab-002-support-ops`, `lab-003-crm-seller`, `lab-004-social-media` estão `ACTIVE` e published. `GET /api/dashboard/embed-config` em `localhost:3010` responde 200 para os quatro.
- [x] Host `localhost:3010` entra com a persona do lab (CEO RavenStack, Diretor de Operações, Head de RevOps, Head de Marketing) e abre o dashboard correspondente.
- [x] Domínios de embed aprovados: `localhost:3010`, `localhost:3020`, `127.0.0.1:3010`, `127.0.0.1:3020`.
- [x] Painéis gráficos (2026-09-21): cada Lab 03 tem as 9 seções pedidas (`lib/lab03_panels` + cópia em `03_LAB_Dashboard/lab03_panels`). Página Lakeview **Paineis** com barras SQL. Modelo / matriz / curva / viés no notebook.
- [x] `python -m pytest tests/test_lab03_panels.py` — 10 passed.
- [ ] Confirmar no browser se o iframe em `localhost:3020/sdk/dashboards` deixou de recusar a incorporação.
- [ ] Reimportar os `.lvdash.json` no Workspace para a página **Paineis** aparecer no dashboard publicado.

## Sucesso / falha

- Sucesso: dashboard publicado abre tiles com números e uma lista acionável depois do Lab 01.
- Falha: inventar coluna; `churn_flag` / `close_value` / `Topic_group` / `engagement_rate` nativo como verdade.
