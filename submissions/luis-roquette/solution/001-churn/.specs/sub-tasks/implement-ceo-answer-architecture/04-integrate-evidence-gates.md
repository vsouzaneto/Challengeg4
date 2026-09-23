# Step 04 — Integrar coortes, gates e base analítica executável

**Task File:** `.specs/tasks/todo/implement-ceo-answer-architecture.feature.md` (raiz da solução; acompanhar o mesmo basename quando movida de status).
**Phase:** 1 — Base analítica verificável.
**Model:** opus.
**Agent:** general:opus.
**Depends on:** 02, 03.
**Parallel with:** None.
**Note:** Caminhos relativos a `submissions/luis-roquette/solution/001-churn/`. Opus por integridade de inferência/confiança operacional e integração diagnosis/CLI/publicação. Não mudar `AnalysisResult` ou conjunto obrigatório de payloads ainda: essa migração indivisível pertence ao Step 05. Esta fase entrega motor analítico e aplicação legada executáveis, não a resposta executiva final.
**Goal:** Finalizar evidências e confiança antes de ranking/fila e fechar a primeira fase com regressões e canônicos coerentes.

**Interfaces:**

- Consome `monthly_churn`, `reason_distribution` e os painéis `observed/strict` do Step 03.
- Produz `build_event_cohort_metrics(event_panel: pd.DataFrame) -> pd.DataFrame` e `build_mechanism_scorecard(findings: pd.DataFrame, event_metrics: pd.DataFrame, reasons: pd.DataFrame) -> pd.DataFrame`.
- Estende `evaluate_candidates(observed, strict, churn_events, event_metrics, reasons) -> tuple[pd.DataFrame, pd.DataFrame]`; todos os gates terminam antes de `rank_findings` e `_build_queue`.
- Entrega quatro DataFrames ao Step 05: histórico, motivos, métricas relativas e scorecard; nenhum é publicado nesta fase.

Em `diagnosis.py`, adicionar `build_event_cohort_metrics` e `build_mechanism_scorecard`; enriquecer `evaluate_candidates` com gates separados e consumir histórico/motivos do Step 02 e painel relativo do Step 03. Adaptar `cli.py` para calcular essas evidências na sequência única e alimentar os candidatos antes da publicação existente. Os quatro DataFrames ficam disponíveis para a ligação pelo Step 05; não criar campos opcionais falsos ou payloads transitórios.

#### Expected Output

Métricas, findings e scorecard coerentes, referências determinísticas, seis candidatos conservados e `accepted` somente após todos os gates. Pipeline atual roda e regenera seus dez arquivos canônicos sob a política corrigida; app existente lê esse conjunto. Evidências novas são verificadas diretamente e só serão persistidas como novos payloads no Step 05.

#### Success Criteria

- Satisfação usa ponderação por respostas dentro da âncora e por casos entre âncoras; fixture 1,4/4 com pesos 1:3 resulta 3,35; âncora sem respostas é excluída explicitamente.
- Todas as condições têm pass/fail/unavailable e razões, Holm restringe seis testes, motivos pertencem ao horizonte e gates precedem rank/fila.
- Falha de ajuste, pouca amostra/cobertura ou IC amplo não viram rejected_claim; mecanismos empatados ou ausentes preservam fatos e fila vazia quando não accepted.
- `make reproduce` e `make check` passam no ambiente autorizado, hashes de origem intactos e mudanças de QA/painel/claims/modelo explicadas. Cobertura analítica: CK-2–CK-8, CK-11, HR-1–HR-3; comunicação final permanece devida na fase 2.

#### Subtasks

1. Integrar DataFrames dos Steps 02/03 em `diagnosis.py`; agregar cobertura de contas/âncoras/respostas, ponderações e bootstrap por conta preservando todas as participações e o mesmo conjunto de âncoras comparáveis.
2. Enriquecer `evaluate_candidates`/`_reason_corroborates`: temporalidade, amostra/cobertura, associação com Holm, estabilidade strict/observed e corroboração no horizonte; registrar todos os gates/razões, respeitando limiares da arquitetura.
3. Construir scorecard e metadados de `build_claim_checks`, com fatos/hipóteses/rejeições corretamente separados; ajustar confiança antes de `rank_findings` e `_build_queue`, adaptar chamadas em `cli.py` e fixtures afetadas sem mudar ainda o contrato de payloads.
4. Escrever testes em `tests/test_diagnosis.py` e regressões necessárias em `tests/test_publish.py`/`tests/conftest.py`: ponderação 3,35, cobertura nula, reused controls, cada gate, Holm, não convergência, empate, todos inconclusivos, accepted e fila restrita. Executar testes direcionados no ambiente autorizado.
5. Com app parado, executar `make reproduce` e `make check` no commit/diff exato via ambiente autorizado; regenerar dez canônicos existentes, comparar hashes dos CSVs brutos, registrar deltas versus referências e verificar aplicação legada ainda legível. A revisão única da fase ocorre depois deste fechamento.

#### Blockers & Risks

| Blocker / Risk | Impact | Likelihood | Mitigation / Resolution |
|---|---|---|---|
| Média de médias/pooling global distorce satisfação | Alto | Alta | Fixture de duas âncoras com resultado 3,35 e bootstrap que recalcula ambos os níveis. |
| Scorecard muda confiança após fila construída | Alto | Alta | Completar todos os gates em evaluate_candidates antes de rank/publicação; teste accepted→inconclusive remove fila. |
| Inconclusão interpretada como efeito nulo/refutação | Alto | Alta | Testar IC amplo, baixo poder, fit indisponível e enunciado rejeitado com contraevidência específica. |
| Gate canônico bloqueado ou dados antigos divergentes | Alto | Média | Corrigir causa, repetir no mesmo diff; nunca bypass ou editar artefato manualmente; não avançar fase com falha. |
