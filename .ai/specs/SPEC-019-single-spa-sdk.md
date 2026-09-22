---
status: passing
canonical: false
area: frontend
created: 2026-09-21
last_updated: 2026-09-21
---

# SPEC-019 Single-SPA — SDK dos monorepos

O frontend em [http://localhost:3020/](http://localhost:3020/) é o root-config ([single-spa 6](https://single-spa.js.org/docs/examples/)). Dois apps registrados; cada um chama o monorepo que já sobe na própria porta.

## Comportamento visível

Header com **Chatbot** e **Dashboards** no menu principal (sem dropdown SDK). A rota do host monta o iframe do filho via `registerApplication` + `start()`.

| Host | App | Origem |
| --- | --- | --- |
| `/sdk/chatbot` | `@g4/chatbot` | [http://localhost:3030/](http://localhost:3030/) (`e2e-chatbot-app-next`) |
| `/sdk/dashboards` | `@g4/dashboards` | [http://localhost:3010/](http://localhost:3010/) (`aibi-dashboards-external-embedding`) |

Os filhos continuam independentes (auth, `/api`, Genie, embed). O host não reescreve as APIs deles.

## Contrato

- Catálogo: `src/frontend/lib/spa/applications.ts`. Override: `NEXT_PUBLIC_SPA_CHATBOT_ORIGIN`, `NEXT_PUBLIC_SPA_DASHBOARDS_ORIGIN`.
- Lifecycles `bootstrap` / `mount` / `unmount` em `iframe-application.ts`. Slot `#single-spa-slot`.
- Iframe do chatbot abre com `?embed=1`. Nesse modo o `SiteHeader` G4 do monorepo some — o header do host 3020 é o único.
- Filhos aceitam frame de `localhost:3020` (`frame-ancestors`).
- Sem SystemJS compartilhando React: chatbot é React 18 + Express; dashboards é React 18 + Flask; o host é Next 16 / React 19.

## Verificação

- [x] Rotas `/sdk/chatbot` e `/sdk/dashboards` no App Router.
- [x] Menu principal: Chatbot → `/sdk/chatbot`, Dashboards → `/sdk/dashboards`. Sem item SDK.
- [x] `npm test` em `src/frontend` (`scripts/check-spa.mjs`).
- [x] `GET` 200 em `/sdk/chatbot`, `/sdk/dashboards` e `/sdk/chatbot/room/churn` com `#single-spa-slot`. Origens 3030 e 3010 no ar.
- [ ] Clique em Chatbot / Dashboards no header (o agente não tem Chromium neste ambiente).

## Sucesso / falha

- Sucesso: 3020/sdk/chatbot mostra o chatbot de 3030; 3020/sdk/dashboards mostra o embed de 3010; sair da rota desmonta o app.
- Falha: misturar os backends; inventar uma terceira sala; gravar segredo no catálogo.
