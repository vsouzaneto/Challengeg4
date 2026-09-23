# Step 05 — Publicar resposta canônica e validar o conjunto

**Task File:** `.specs/tasks/todo/implement-ceo-answer-architecture.feature.md` (raiz da solução; acompanhar o mesmo basename quando movida de status).
**Phase:** 2 — Resposta executiva consistente.
**Model:** opus.
**Agent:** general:opus.
**Depends on:** 04.
**Parallel with:** None.
**Note:** Caminhos relativos a `submissions/luis-roquette/solution/001-churn/`. Opus por contrato compartilhado, referências e integridade de publicação. Um escritor, app parado e nenhum leitor concorrente; não implementar transação de diretório ou hot reload. Reutilizar publish.py, sem camada ou dependência nova.
**Goal:** Fazer JSON, relatório, tabelas e manifesto exprimirem uma única resposta rastreável, mesmo sem mecanismo sustentado.

**Interfaces:**

- `AnalysisResult` recebe `monthly_churn`, `reason_distribution`, `event_cohort_metrics` e `mechanism_scorecard`, todos `pd.DataFrame` obrigatórios.
- Produz `_build_ceo_answer(result: AnalysisResult) -> dict[str, object]` e altera `_build_report(..., answer: dict[str, object]) -> str` para consumir o mesmo objeto.
- `publish_artifacts(result, output_dir) -> dict[str, Path]` grava 14 payloads e o manifesto; `validate_artifact_set(output_dir) -> dict[str, object]` valida estrutura e semântica.
- Step 06 consome apenas arquivos já validados; Step 07 documenta o contrato efetivamente publicado.

Estender `AnalysisResult` em `publish.py` com os quatro DataFrames da arquitetura e finalizar passagem em `cli.reproduce`. `publish_artifacts` serializa evidências, determina `analysis_id`, constrói `_build_ceo_answer(result)` uma vez e passa o mesmo objeto a `_build_report`. Migrar de uma vez publicação, conjunto exato, schemas, validação e fixtures para 14 payloads mais manifesto. O app será atualizado no Step 06 para apresentar a resposta já pronta.

#### Expected Output

Criar por reprodução somente `artifacts/monthly_churn.csv`, `reason_distribution.csv`, `event_cohort_metrics.csv`, `mechanism_scorecard.csv`, `ceo_answer.json`; regenerar os existentes quando o resultado legítimo mudar. Manifesto contém schema, parâmetros, políticas, unidades, hashes e analysis_id determinístico. Relatório abre com os cinco blocos e metodologia depois.

#### Success Criteria

- Blocos em ordem `what_changed/where/strongest_mechanism/unknowns/next_actions`, headline/claims/ações derivados dos dados, não da narrativa exploratória.
- JSON sem NaN/Infinity; todo ID, comparador e EvidenceRef resolve linha/colunas/fonte/período; hash correto com schema inválido continua recusado.
- Ações têm função responsável, prazo, população, métrica, avanço/parada e evidência/lacuna; intervenção proposta só com mecanismo sustentado, sem promessa financeira ou contato.
- `analysis_id` exclui autorreferência e relatório/resposta de sua entrada; duas reproduções com mesmas entradas são equivalentes segundo comparador existente. Cobertura: CK-1–CK-12 na publicação, HR-1–HR-3; dashboard pendente do Step 06.

#### Subtasks

1. Migrar `AnalysisResult`, montagem em `cli.py` e fixtures completas em `tests/conftest.py` para quatro novas tabelas; usar gates finalizados do Step 04, sem recálculo analítico nos renderizadores.
2. Implementar `_build_ceo_answer`/`_build_report` e ações, com claims numéricos tipados, fontes/limites, states flat/down/insufficient/no-data, empate/ausência de mecanismo e recuperação null/not_estimated.
3. Atualizar `publish_artifacts`, serialização e `validate_artifact_set`: conjunto exato, hashes, schema/tipos/nulabilidade/unidades, referências únicas sem ciclos, finite numbers, cinco blocos e manifesto por último; analysis_id dos inputs/parâmetros/evidências serializadas.
4. Escrever regressões em `tests/test_publish.py`: mesma resposta/relatório, fila e watchlist, todos inconclusivos/accepted, MRR parcial, zero/nulo, tamper/ausência, hash recomputado com schema/ref inválida, duplicate IDs, inf/nan, parâmetros distintos e determinismo. Executar `.venv/bin/python -m pytest -q tests/test_publish.py` no ambiente autorizado.
5. Parar leitores, executar `make reproduce` no ambiente autorizado e validar conjunto de 15 arquivos; registrar valores/deltas/referências da resposta que os Steps 06/07 consumirão. Não editar artefatos manualmente nem atualizar snapshot sem causa explicada.

#### Blockers & Risks

| Blocker / Risk | Impact | Likelihood | Mitigation / Resolution |
|---|---|---|---|
| Contrato parcial quebra fixtures/CLI/leitor | Alto | Alta | Migrar dataclass, writer e validator juntos; fixtures completas e ausência obrigatória falha explicitamente. |
| Hash válido encobre referências falsas | Alto | Média | Resolver PK/chaves/colunas e tipos; testes atualizam hash mas mantêm falha semântica. |
| Narrativa continua fixa em no-data/accepted | Alto | Alta | Casos contrários à narrativa atual e mesma instância em report/JSON; fatos independem de mecanismo. |
| Leitura simultânea mistura gerações | Alto | Média | Operação offline documentada, manifesto por último e validação antes de iniciar app; concorrência fora do escopo. |
