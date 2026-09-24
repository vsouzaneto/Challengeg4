# Web (React + Vite + Tailwind)

Interface que o vendedor abre na segunda-feira: fila "Trabalhar" (deals dentro do ciclo, ordenados
pela API por `priority_score`), fila "Confirmar ou encerrar" (parados há mais de 138 dias, maior
valor primeiro), drawer de explicação com os fatores do score e o contexto do CRM, visão do manager
(`/time`) e qualidade do modelo (`/qualidade`). O web **só apresenta**: nenhum score, tier ou
urgência é calculado aqui — tudo vem de `GET /api/v1/*` com tipos gerados do OpenAPI.

```bash
npm install
npm run dev          # http://localhost:5173 — proxy /api -> http://localhost:8000 (API FastAPI)
npm run dev:mock     # mesma UI com dados fictícios no navegador (MSW); não precisa de API nem pipeline
npm run test         # Vitest + Testing Library + MSW + vitest-axe
npm run lint         # eslint + prettier
npm run typecheck    # tsc -b
npm run build        # dist/ (o modo mock nunca entra no bundle)
npm run gen:api      # regenera src/api/schema.d.ts (ou `make gen-api` em solution/, sem API rodando)
npm run screenshots  # captura as telas em modo mock para process-log/screenshots (Playwright)
```

## Modo demonstração (`dev:mock`)

`vite --mode mock` serve o service worker do MSW a partir de `src/mocks/public` e `main.tsx`
carrega `src/mocks/browser.ts` só nesse modo (a checagem `import.meta.env.MODE === 'mock'` é
eliminada no build de produção). Os fixtures em `src/mocks/fixtures.ts` derivam dos exemplos do
`openapi.json` e do layout de `metrics.json` (`docs/specs/scoring-spec.md` §8). Cenários:
`?mock=missing` (503, artefatos ausentes), `?mock=error` (500) e `?mock=empty`.

## Estado na URL

`?as_of&region&manager&agent&n&sort&offset&deal&queue`. Filtros são hierárquicos (mudar região
limpa manager e vendedor; mudar manager limpa vendedor). `as_of` ausente é preenchido com
`default_as_of` de `/meta` via `replaceState`, para que todo link compartilhado fique datado.
`deal=` abre o drawer; Voltar do navegador fecha. `queue=confirm` abre a fila de parados.

## Estrutura

| Pasta               | Conteúdo                                                                                                                              |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `src/api/`          | `schema.d.ts` (gerado), `client.ts` (openapi-fetch + `ApiError` + headers `X-As-Of`/`X-Model-Version`), `queries.ts` (TanStack Query) |
| `src/lib/`          | estado da URL, formatação pt-BR (`Intl`), CSV, classificação visual dos reason codes (`reasons.ts`)                                   |
| `src/features/`     | feedback otimista (`POST /feedback`, desfazer, rollback) e adaptador de `metrics.json`                                                |
| `src/components/`   | `DealRow`, `DealDrawer` (dialog com focus trap), `Layout`, estados, gráficos em SVG/HTML puro                                         |
| `src/pages/`        | `QueuePage` (/), `TeamPage` (/time), `QualityPage` (/qualidade)                                                                       |
| `src/i18n/pt-BR.ts` | todo texto da interface                                                                                                               |
| `src/mocks/`        | fixtures e handlers MSW (dev e testes)                                                                                                |

Tokens do design system do G4 em `tailwind.config.ts` (contraste verificado em
`docs/design/design-tokens.md`); regras de acessibilidade em `docs/design/accessibility.md`.

## Decisões e limites conhecidos

- As duas filas são paginadas pela API (`GET /deals?queue=work|confirm`); o contador da outra aba e
  o tile "esfriando" (`min/max_days_in_engaging`) usam `limit=1` e leem `total`; o valor nominal da
  fila de parados vem de `PipelineSummary.total.nominal_zombie_value`.
- A fila "Confirmar ou encerrar" ordena por `-expected_value,days_in_engaging` porque `sales_price`
  não é campo ordenável na API; o valor exibido é `sales_price` (nominal, fora do forecast).
- `Reason.weight` já vem em pontos do score (0–100) e é exibido com uma casa decimal ("+0,6 pts").
- "Ocultar da minha fila" usa a ação `discard` da API e só afeta esta ferramenta; "Encerrado no CRM"
  registra `closed_in_crm` (o vendedor já encerrou no CRM; a ferramenta não altera o CRM); "desfazer"
  limpa o selo na sessão — o registro já enviado permanece no log da API (append-only).
- `MODEL_CONTRIBUTION` fica oculto enquanto o peso do modelo for zero (`metrics.summary.blend_model_weight`).
- Histórico da conta (setor, porte, deals anteriores) depende de endpoint ainda inexistente; o
  drawer mostra só o nome da conta.
