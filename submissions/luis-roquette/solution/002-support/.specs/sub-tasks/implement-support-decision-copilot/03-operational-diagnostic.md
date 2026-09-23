# 03 — Diagnóstico operacional executável

**Task File:** ../../tasks/done/implement-support-decision-copilot.feature.md
**Phase:** 1
**Model:** sonnet
**Agent:** sdd:data-engineer
**Depends on:** 02
**Parallel with:** None
**Note:** Caminhos relativos à solution `submissions/luis-roquette/solution/002-support/`. Tier typical: fórmulas e contratos já decididos, um módulo analítico com apresentação mínima.
**Goal:** Entregar um marco executável de diagnóstico Customer Support e cenários honestos.

Implementar `src/support_copilot/analytics.py`: `add_operational_fields`, `grouped_bottlenecks`, `recoverable_excess_hours`, `satisfaction_associations`, `operational_summary`, `ScenarioAssumptions` e `scenario_projection`. Consumir exclusivamente frames sanitizados de `data.py`. Integrar modo diagnóstico de `scripts/reproduce.py` e uma página de leitura em `app.py`/`ui.py`; fila/modelos permanecem explicitamente indisponíveis nesta fase.

#### Expected Output

`analytics.py`, `tests/test_analytics.py`, renderização mínima `render_scorecard` e relatórios sob `artifacts/analytics/`: `operational-summary.json`, `bottlenecks.csv`, `waste-opportunities.csv`, `satisfaction-associations.csv`, `satisfaction-model.json`, `automation-opportunities.csv`. O último declara evidência IT ainda ausente, sem inventar conexão entre registros.

#### Success Criteria

`make reproduce` produz diagnóstico de desenvolvimento e `make demo` o mostra. Intervalos incluem apenas fechados/datas válidas/ordenadas, com exclusões reconciliadas; primeira resposta/resolução total continuam não observáveis. Grupos com menos de 30 válidos não estimam excesso. Ridge abaixo do ganho de MAE de 2% retorna `no_reliable_signal`. Premissas alteram só projeções.

#### Subtasks

1. Implementar intervalos e agregados por canal/prioridade/tipo/combinações, preservando nulos e precedência mutuamente exclusiva das exclusões.
2. Implementar excesso não negativo sobre pares tipo/prioridade e relatório de satisfação com pré-processamento dentro dos folds, baseline e importância somente quando suportada.
3. Implementar cenários com validação de finitude/faixas e registrar premissas editáveis sem converter proxy em economia realizada.
4. Integrar relatórios/manifests e página diagnóstica mínima, mantendo desenvolvimento separado de qualquer avaliação final; registrar resultado no diário.
5. Escrever testes próprios em `tests/test_analytics.py` para denominadores, 29/30 casos, timestamps inválidos, melhoria abaixo/igual ao corte, cenários inválidos e invariância histórica; adicionar smoke da página em `tests/test_workflow.py` e verificar marco executável.

#### Blockers & Risks

| Tipo | Situação | Impact | Likelihood | Resolução ou mitigação |
|---|---|---|---|---|
| Risk | Intervalo observado rotulado como resolução total | Medium | High | Nomes explícitos, denominadores e teste de rótulo na página/relatório. |
| Risk | Satisfação sem sinal apresentada como explicação causal | Medium | High | Baseline/CV, status negativo obrigatório, importância só com suporte e linguagem de associação. |
| Blocker | Nenhum grupo elegível ou nota utilizável | Medium | Medium | Saída nula com motivos e contagens; manter painel funcionando sem fabricar achados. |
