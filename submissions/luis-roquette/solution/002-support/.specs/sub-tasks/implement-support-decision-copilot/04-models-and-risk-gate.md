# 04 — Classificação independente, calibração e gate

**Task File:** ../../tasks/done/implement-support-decision-copilot.feature.md
**Phase:** 2
**Model:** opus
**Agent:** sdd:ml-engineer
**Depends on:** 02
**Parallel with:** 05
**Note:** Caminhos relativos à solution `submissions/luis-roquette/solution/002-support/`. Tier complex por contrato compartilhado modeling/decision e seleção/calibração; dono exclusivo desses dois módulos.
**Goal:** Produzir modelos por domínio e decisão que sempre prioriza risco e invalidez sobre confiança.

Implementar `modeling.py` e `decision.py` exatamente conforme contratos de `Prediction`, `DomainModel.predict_one/predict_batch`, `ModelTrainingResult`, `RoutingPolicy`, `TicketSignals`, `derive_signals`, `decide_route`, `priority_score` e `evaluate_frozen_test`. Nesta etapa avaliação final é implementada/testada com fixtures, nunca chamada nos dados de teste reais.

#### Expected Output

`src/support_copilot/modeling.py`, `decision.py`, `tests/test_modeling.py`, `tests/test_decision.py`; configuração de risco versionada e resultados de desenvolvimento por domínio, sem substituir os modelos entre Customer e IT. A etapa 07 conectará geração real de artefatos ao pipeline.

#### Success Criteria

Dummy/NB/LR/SVC usam cinco folds idênticos só no treino; empate até 0,01 favorece simplicidade. Ganho <0,02 desativa classificação operacional. Calibração sigmoid e threshold usam subdivisões disjuntas dos 20%; gate não aceita threshold inexistente, nem confiança 1,0. Vetor zero/medição ausente propagam bloqueio em escalar/lote. Categorias de risco e contagens/exemplos sanitizados justificam política sem observar teste final.

#### Subtasks

1. Implementar candidatos/seleção por CV com vetorizador em cada fold e suportes por classe; registrar ablação de subject só como diagnóstico condicionado à auditoria.
2. Implementar calibração congelada, `Prediction` validada e zero-vector calculado pelo próprio vetorizador ajustado; não fabricar label/probabilidade para estados indisponíveis.
3. Implementar derivação única de sinais, regras Customer/IT e prioridade explicável; selecionar limite da grade pela mesma política aplicada na inferência, nunca pelo teste.
4. Implementar avaliação final pura com macro-F1/classes/confusão/log loss/ECE/risco-cobertura e denominadores/nulos; expor locks/configuração que o pipeline deverá respeitar.
5. Escrever testes próprios nos dois arquivos de testes: espionagem de IDs, ganho 0,019/0,020, limites, probabilidades adversariais, OOD indisponível com confiança 0,99, cada risco, prioridade desconhecida, domínio trocado e lote vazio; registrar execução e limitações no diário.

#### Blockers & Risks

| Tipo | Situação | Impact | Likelihood | Resolução ou mitigação |
|---|---|---|---|---|
| Risk | Leakage na CV/calibração ou retuning final | High | Medium | Espionar IDs e congelar configuração; final só após todos os locks na etapa 08. |
| Risk | Confiança 1,0 ou vetor zero contorna desativação | High | Medium | Estado explícito e precedência fail-closed no núcleo comum, com regressões escalar/lote. |
| Blocker | Classe ausente ou nenhum limiar com cobertura segura | High | High | Manter métricas de candidatos e status indisponível; nenhuma automação até nova versão validada. |
