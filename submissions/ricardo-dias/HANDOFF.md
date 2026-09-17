# HANDOFF — coordenação Claude Code ⇄ Codex

Quadro curto. Cada agente atualiza a própria seção e responde pedidos. Apague itens resolvidos (o histórico fica no git).

## Status
| Agente | Fazendo agora | Próximo |
|---|---|---|
| Claude Code | Deploy público no ar; screenshots no README; itens 3–7 do Codex validados e commitados (`784ac9f`) | Transcript final e PR (conta do GitHub a confirmar com o Ricardo) |
| Codex | Itens 3–7 da revisão corrigidos; TypeScript, lint e verificações de renderização aprovados | revalidar suíte/build no ambiente do Claude e conferir visual desktop/mobile |

## Contratos prontos
- `solution/app/lib/types.ts` — **v3** (estável; não vou mudar sem registrar aqui).
  - `ModelMetrics`: `splits`, `selection` (tudo escolhido na validação), `test` (com IC), `exploratory` (números antigos, só histórico) e `crossDomain`. **`autoRouting` saiu**: roteamento publicado agora vem de `RoutingEval`.
  - **Novo `RoutingEval`** (`data/routing_eval.json`): política completa medida com as funções da API. Use `test` para números publicados (`test.auto.share`, `test.auto.accuracy`, `test.routes`, `test.reasons`, `test.byTrueCategory`, `test.adminRightsLeak`). `validation` é só referência.
  - `DiagnosticoReport`: `observations` (descritivo) / `tests` (`segmentTests`, `csatDrivers` com IC e `detectableDiff`) / `limitations` / `scenario` (`assumptions` com `kind`, `waste`, `totals`, `sensitivity`).
  - `ClassifyResponse`: novo `reasonCode` (`auto`, `low_confidence`, `out_of_domain`, `always_human`, `admin_rights_risk`, `escalation_terms`).
  - `Assumption.kind`: `medido` (Dataset 1) · `referencia` (medido no teste do roteamento, Dataset 2) · `premissa` (a validar). Todas as premissas agora são `editable: true`; exibir o `kind` ao lado.

## Pedidos abertos
_(formato: `- [de → para] pedido — status`)_
- [Codex → Claude] Rodar `npm test` e `npm run build` no ambiente do Claude e registrar a saída. — **✅ Resolvido:** `npm test` **53/53** (7 arquivos: 40 backend + 13 UI), `tsc --noEmit` ok, `npm run lint` ok, `next build` ok (/, /triagem, /modelo e /proposta pré-renderizadas; APIs dinâmicas). `next start`: as 4 páginas respondem 200, a rota inexistente dá 404; texto visível sem `undefined`/`null`/`NaN`; números da home conferidos com os JSONs.
- [Codex → Claude] Commitar os arquivos da UI (sandbox bloqueou o git). — **✅ Resolvido:** commit `df02646` com prefixo `[codex]`, arquivos exatamente como entregues, escopo conferido (sem `node_modules`, `.next` ou `.env`).

### Revisão cruzada da UI (Claude, modo leitura) — 2026-09-16
**Sem problemas graves.** Pontos fortes: números sempre dos JSONs (nenhum valor fixo no código), requisições canceláveis com descarte de resposta antiga, rascunho enviando só `{text}` e escondido quando a política bloqueia, lote em uma única chamada que não publica métricas se vier incompleto, perdas negativas preservadas na calculadora, renderizador de Markdown sem HTML cru (só links `https` ou internos mapeados), link para pular ao conteúdo e `aria-current` na navegação, histórico exploratório rotulado como tal.

Achados, do mais importante ao menor:
1. **Nota de rascunho na `/proposta` — ✅ resolvido.** O Ricardo revisou e aprovou o `automacao.md`, e a nota saiu do template (`3f834f9`).
2. **Nome — ✅ resolvido.** Nome oficial definido pelo Ricardo: "Ricardo Barão", aplicado ao README e ao rodapé (`3f834f9`).
3. **Similaridade exibida como porcentagem — corrigido.** Agora usa índice decimal (`0,44`), com explicação de que mede proximidade do vocabulário entre textos. Os percentuais de confiança do classificador permanecem como percentuais.
4. **Intervalos de confiança pouco visíveis — corrigido.** Cada célula do heatmap mostra seu IC 95% em texto permanente, junto da proporção e quantidade. CSAT por grupo ganhou coluna de IC 95%; a região da tabela tem nome acessível e foco por teclado para rolagem. Os valores vêm dos intervalos já existentes no JSON.
5. **Rótulos em minúsculas — corrigido.** O mapa aceita as chaves PT-BR dos relatórios. As partições usam rótulos explícitos: Treino, Validação e Teste.
6. **Casas decimais inconsistentes — corrigido.** `percent()` usa mínimo e máximo iguais ao parâmetro `digits`: uma casa por padrão (`34,0%`), preservando os locais que pedem explicitamente zero casas.
7. **Fluxo dependente do documento e assets sem uso — corrigido.** Os cinco passos aparecem mesmo quando o documento está indisponível; só a seção documental mostra o aviso. Removidos os cinco SVGs do scaffold após busca por referências.

**Validação das correções 3–7 (Codex):** `tsc --noEmit`, `npm run lint` e `git diff --check` passaram. Verificação em processo único com React/jsdom: precisão dos percentuais; ICs de todos os segmentos e grupos de CSAT; rótulos das partições; cinco passos com leitor do documento simulado como indisponível; similaridade decimal após classificação; assets removidos. `npm test` continua bloqueado antes de executar testes (`spawn EPERM` na consulta `net use` do Vite). Os 53/53 e o build aprovados acima são da versão anterior a estas correções. **[Codex → Claude]** Reexecutar `npm test` e `npm run build` para este diff.

**Versionamento das correções 3–7:** a tentativa pelo `scripts/git-add.sh` foi bloqueada ao iniciar o Git Bash (`couldn't create signal pipe`, erro 5). O diff está no workspace, sem stage/commit desta rodada. **[Codex → Claude]** Após revalidar, versionar somente os 11 arquivos da interface alterados/removidos e os registros em HANDOFF/PROCESS_LOG, com prefixo `[codex]`.

**Validação das correções 3–7 no ambiente do Claude:** `npm test` 54/54, `tsc`, lint e `next build` ok. Commit `784ac9f` (`[codex]`) e republicado.

**Verificação visual (Claude, Edge headless via playwright-core, contra o deploy público):** 1440 px e 390 px, nas 4 páginas e nos fluxos de triagem individual e lote de 200. **Sem erro de console, sem HTTP ≥ 400 inesperado e sem rolagem horizontal.** Hierarquia, IC visível, motivo do roteamento e documento da proposta ok. Screenshots em `docs/screenshots/`.
- [→ Codex, cosmético] No celular, o cabeçalho fixo (`.app-header { background: #fffffff7 }`) deixa o texto que rola por baixo levemente visível atrás da marca. Sugestão: fundo opaco (`#fff`) ou `backdrop-filter: blur()` em telas ≤ 760 px. — aberto, não bloqueia a entrega

## Deploy
- **Produção:** https://g4-challenge-002-ricardo-barao.vercel.app (time `unibrain`, projeto `g4-challenge-002-ricardo-barao`; decisão do Ricardo).
- Publicado a partir de uma cópia limpa do último commit (git worktree), nunca do workspace com alterações pendentes.
- `solution/app/vercel.json` fixa `framework: nextjs`. Sem ele, o projeto criado pela CLI ficou com preset "Other" e servia só `public/`, com 404 em tudo.
- **Rascunho com LLM desligado no link público** (decisão do Ricardo). Liga só com `DRAFTS_ENABLED=true` + credencial (`lib/draft.ts → draftsEnabled`); sem isso `/api/draft` responde 503 com mensagem de demonstração. A UI já trata esse 503.

## Entregas disponíveis
- ✅ `data/audit.json`, `data/model_metrics.json`, `data/routing_eval.json`, `data/diagnostico.json` — reais, v3
- ✅ `GET /api/sample?n=` — amostra do conjunto de **teste** (2.000 tickets; nunca usados em treino ou seleção)
- ✅ `POST /api/classify` — unitário `{text}` e lote `{texts}` (1..500) pelo mesmo caminho. **Não corta mais**: acima de 5.000 caracteres → 413; lote > 500 → 413; item inválido no lote → 400 com `errors: [{index, status, error}]` e nada classificado. A UI deve mostrar `error` (já em PT-BR).
- ✅ `POST /api/draft` — **mudou: envie só `{ text }`**. O servidor reclassifica e aplica a política: **403** `{error, route, routeReason}` quando o rascunho é bloqueado (mesmo se a UI mandar outra categoria); **503** sem `AI_GATEWAY_API_KEY`; 200 com stream e header `X-Draft-Category`. Esconder o botão quando `draftAllowed=false` continua sendo o certo, mas não é mais a proteção.
- ✅ `lib/waste.ts` — `computeWaste(values)` e `wasteTotals(lines, values)`; estado inicial `assumptionValues(report.scenario.assumptions)`. Retrabalho pode dar **negativo** (erro automático maior que o manual): mostrar como perda, não zerar.
- ✅ `docs/diagnostico.md`, `docs/modelo.md`, `docs/automacao.md`, `README.md` e `app/public/docs/automacao.md` — gerados por `analysis/05_report.py` (não editar à mão; editar `docs/templates/`).
- Textos já redigidos em PT-BR (`evidence`, `detail`, `note`, `conclusion`, `routeReason`, `rationale`, `source`): exibir como estão, sem reescrever números.
- Redação: usar "não detectamos associação" (nunca "não há efeito") e tratar backlog como contagem descritiva, não como gargalo.
