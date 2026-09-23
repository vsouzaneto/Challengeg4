# 06 — Recuperação segura e protocolo de revisão

**Task File:** ../../tasks/done/implement-support-decision-copilot.feature.md
**Phase:** 2
**Model:** opus
**Agent:** sdd:ml-engineer
**Depends on:** 02, 04
**Parallel with:** 05
**Note:** Caminhos relativos à solution `submissions/luis-roquette/solution/002-support/`. Tier complex por integridade da avaliação e seleção não trivial. Esta etapa implementa o protocolo; avaliações humanas reais pertencem à etapa 08.
**Goal:** Recuperar apenas precedentes permitidos e bloquear drafts até evidência humana independente.

Implementar `src/support_copilot/retrieval.py`: `fit_retriever`, `TicketRetriever.suggest`, `SourceMatch`, `RetrievalPolicy`, `RetrievalResult`, `RetrievalMetrics`, `evaluate_retriever` e CLI `prepare-review`/`lock-review`. Consumir `TicketSignals` derivados pelo núcleo da etapa 04, sem reconstituir confiança/sinais ou oferecer draft fora de `suggest`.

#### Expected Output

`retrieval.py` e `tests/test_retrieval.py`; protocolo de pacote/CSV documentado no docstring de módulo de `src/support_copilot/retrieval.py`, com âncoras 1–5, autoria, timestamps, packet ID/hashes e decisões `pending_review/enabled/disabled/insufficient_evidence`. Step 06 é o único proprietário desse documento e da ajuda CLI correspondente; não edita `README.md`, que pode estar sendo alterado pelo step 05. Step 09 referencia/consolida esse protocolo nos READMEs depois. Só template de calibração pode ser gerado sem locks finais.

#### Success Criteria

Índice contém apenas descrições/resoluções sanitizadas, fechadas, não vazias de treino Customer. Top-3 tem desempate estável e score de similaridade explícito. Critical/sensível/ambíguo/OOD/PII/inválido bloqueiam draft mesmo com score 1,0; PII/invalidez bloqueiam consulta/fontes. Templates têm 30 consultas elegíveis estratificadas sem seleção por score alto; falta de suporte/revisão não vira sucesso. Teste exige locks e nunca altera limite.

#### Subtasks

1. Implementar índice TF-IDF/cosseno com proveniência e exclusão de IDs/grupos de calibração/teste; resolver fontes ausentes sem geração livre.
2. Implementar `suggest(..., signals=...)` com todos os bloqueios internos antes de materializar draft e retorno `draft=null` justificado.
3. Implementar seleção seeded de pacotes/validação de rubricas e grade de threshold 0,20–0,90/0,10, exigindo médias/segurança e denominador não vazio conforme SPEC.
4. Implementar CLI com hashes/locks e separação calibração/teste; documentar insuficiência e impossibilidade de habilitar a mesma versão após abrir teste como `disabled/pending_review` exclusivamente no docstring de módulo de `src/support_copilot/retrieval.py` e na ajuda CLI desse arquivo. Não editar README em paralelo ao step 05.
5. Escrever testes próprios em `tests/test_retrieval.py`: treino-only, empate/top-3, fontes vazias, score 1,0 com cada risco, pacote <30/incompleto/adulterado, ausência de autor, gate de teste e imutabilidade de threshold; registrar resultados no diário.

#### Blockers & Risks

| Tipo | Situação | Impact | Likelihood | Resolução ou mitigação |
|---|---|---|---|---|
| Risk | UI reconstrói resposta a partir de fonte bloqueada | High | Medium | Único produtor de draft é `suggest`; teste de integração posterior prova botão desabilitado. |
| Risk | Revisão seleciona só bons scores ou usa teste para ajustar | High | Medium | Elegibilidade independente do score, pacote/hash/lock e avaliação final somente leitura. |
| Blocker | Menos de 30 consultas seguras ou rubrica humana ausente | High | High | `insufficient_evidence`/`pending_review`, sem duplicação; CK-12 permanece pendente até evidência válida. |
