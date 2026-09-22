---
status: passing
canonical: false
area: plataforma
created: 2026-09-21
last_updated: 2026-09-21
---

# SPEC-018 Genie + salas fixas do chatbot

Quatro espaços Genie (um por pack Lab 02) e quatro salas fixas em `src/monorepos/e2e-chatbot-app-next`. CSV ganha. Histórico continua desativado.

Workspace: [dbc-0dea39b3-be1e](https://dbc-0dea39b3-be1e.cloud.databricks.com/browse?o=7474644277755368). Warehouse `1dfbeda79d9a368d`.

## Comportamento visível

Em [http://localhost:3030/](http://localhost:3030/) a sidebar mostra **Chat**, **Recolher a barra lateral**, **Nova conversa**, o aviso “O histórico está desativado — as conversas não são salvas.” e o grupo **Salas Genie** com:

| Sala | Pack | Schema | Space |
| --- | --- | --- | --- |
| 001 Churn | `notebook-data-001-churn` | `ravenstack` | [lab-001-churn-genie](https://dbc-0dea39b3-be1e.cloud.databricks.com/genie/rooms/01f1b6165ad01ca4a5f3b95c6d3d3609?o=7474644277755368) (`01f1b6165ad01ca4a5f3b95c6d3d3609`) |
| 002 Suporte | `notebook-process-002-support` | `supportiq` | [lab-002-support-genie](https://dbc-0dea39b3-be1e.cloud.databricks.com/genie/rooms/01f1b6165bac181a9836cde73e8e7556?o=7474644277755368) (`01f1b6165bac181a9836cde73e8e7556`) |
| 003 CRM | `notebook-build-003-lead-scorer` | `crm` | [lab-003-crm-genie](https://dbc-0dea39b3-be1e.cloud.databricks.com/genie/rooms/01f1b6165c871b51a8ec3e632bffa2ac?o=7474644277755368) (`01f1b6165c871b51a8ec3e632bffa2ac`) |
| 004 Social | `notebook-marketing-004-social` | `social` | [lab-004-social-genie](https://dbc-0dea39b3-be1e.cloud.databricks.com/genie/rooms/01f1b6165d6e1a8bbb831d2a78fd6929?o=7474644277755368) (`01f1b6165d6e1a8bbb831d2a78fd6929`) |

Cada sala abre `/room/<alias>`, sugere as perguntas do Lab 02 e manda o texto ao Genie. A conversa fica só na memória do browser.

## Contrato

- Tabelas = FQN `workspace.<schema>.*` do Lab 01. Sem `Topic_group`, sem `engagement_rate` nativo, sem `metadata` como fato, sem CNPJ.
- Instruções = prompt bônus do `lab02_assistant.ipynb` de cada pack.
- Env do chatbot: `GENIE_SPACE_ID_CHURN` / `_SUPPORT` / `_CRM` / `_SOCIAL`. IDs não são segredo; PAT não entra no git.
- `GET /api/genie/rooms` lista as 4 salas. `POST /api/genie/:alias/messages` com `{content, conversationId?}`: 404 alias desconhecido, 400 content vazio, 503 space id ausente, 502 falha Databricks.
- AppKit `GenieChat` não é o runtime deste app (Express + React).

## Verificação

- [x] Quatro espaços criados via `POST /api/2.0/genie/spaces` (2026-09-21).
- [x] `packages/core/src/lab-rooms.ts` + proxy `server/src/routes/genie.ts` + UI `SidebarRooms` / `RoomPage`.
- [x] Testes: `tests/unit/lab-rooms.test.ts`, `tests/routes/genie.test.ts`; `/api/config` ainda devolve 200 e 4 rooms.
- [x] `GET http://localhost:3031/api/genie/rooms` (2026-09-21): 4 salas `configured=true`. `POST` vazio = 400; alias desconhecido = 404. `GET /api/config` history=false.
- [x] Smoke Genie sala churn: 500 contas; 352 com `churn_event_id`; SQL devolvido.
- [ ] Clique autenticado em `localhost:3030` (sidebar + 4 salas) — o agente não tem a sessão Databricks do browser.

## Evidência

2026-09-21: CLI Databricks ausente no PATH; REST com token só em env. `serialized_space` v2; `data_sources.tables` ordenadas por `identifier`.

## Sucesso / falha

- Sucesso: cada sala responde SQL só com colunas do CSV do pack.
- Falha: inventar coluna; persistir histórico; um único space para os 4 packs; gravar PAT em SPEC/README/commit.

## Segurança

PAT não entra em SPEC, README, commit ou `mcp.json`. Se o token foi colado no chat, rotacionar no Databricks.
