# 08 — Revisão humana e avaliação final independente

**Task File:** ../../tasks/done/implement-support-decision-copilot.feature.md
**Phase:** 3
**Model:** opus
**Agent:** sdd:ml-engineer
**Depends on:** 07
**Parallel with:** 09
**Note:** Caminhos relativos à solution `submissions/luis-roquette/solution/002-support/`. Tier complex por integridade da avaliação. Agente prepara/verifica; somente humano preenche julgamentos de qualidade.
**Goal:** Produzir medições reais e locks auditáveis, mantendo bloqueios explícitos onde a evidência não sustenta assistência.

Usar `scripts/reproduce.py`, `python -m support_copilot.retrieval prepare-review --artifacts artifacts --split calibration` e `lock-review --artifacts artifacts --rubric evidence/retrieval-calibration-rubric.csv`. Só liberar teste depois de modelo/calibração/regras/thresholds e decisão de recuperação congelados. Não abrir teste enquanto se aguarda revisão de calibração para depois habilitar a mesma versão.

#### Expected Output

`evidence/retrieval-calibration-rubric.csv` e `evidence/retrieval-test-rubric.csv` com revisão humana real; locks/manifest/filas/métricas reais sob artifacts e agregados revisados `evidence/metrics.json`, `evidence/operational-summary.json`. Não criar CSV preenchido por agente nem evidência favorável sintética.

#### Success Criteria

Duas amostras independentes de 30 casos elegíveis recebem autoria/data/escalas/notas sanitizadas; teste não reajusta limite. Modelos têm métricas por domínio e os rejeitados permanecem documentados. Reprovação final só desativa assistência. Reprodução repetida conserva splits/políticas/resultados canônicos; a única chave temporal excluída é `manifest.generated_at`, e eventual comparação numérica dos dados reais segue a tolerância explícita da arquitetura, sem ignorar campos adicionais.

Durante o paralelo com step 09, não ler/coletar/executar o `tests/test_workflow.py` mutável nem a suíte inteira. Executar somente o node ID `test_reproduce_twice_same_inputs` de **S07**, cópia selada produzida pelo step 07 em `data/runtime/validation/phase2-<workflow_sha256>/test_workflow.py`. A partir da solution, usar `.venv/bin/pytest -c pyproject.toml --import-mode=importlib data/runtime/validation/phase2-<workflow_sha256>/test_workflow.py::test_reproduce_twice_same_inputs -q`, substituindo o hash pelo registro real do diário. Conferir seu SHA-256 antes e depois, além do fingerprint do código/configuração/lock; divergência bloqueia a execução, nunca recria silenciosamente o snapshot. Testes novos desta etapa são selecionados explicitamente em modeling/retrieval. Step 10, após 08 e 09, executa a suíte final consolidada.

#### Subtasks

1. Rodar desenvolvimento real pelo gerenciador no SHA/diff exato, revisar fontes/qualidade/grupos e preparar pacote de calibração sem abrir final.
2. Apresentar ao humano os 30 casos e rubrica concreta; aguardar preenchimento/validação, registrando a pendência externa. Se houver insuficiência, manter bloqueio e CK-12 incompleto.
3. Validar/lockar a decisão de calibração; congelar toda configuração, liberar teste e obter os 30 julgamentos humanos independentes sem retuning.
4. Escrever testes próprios adicionais em `tests/test_retrieval.py` e `tests/test_modeling.py` para lifecycle completo, hashes stale e teste imutável; executar explicitamente esses arquivos e o teste de reprodução somente pelo snapshot S07/hash verificado. Repetir a comparação com fontes/lock reais idênticos; não coletar o workflow mutável ou suíte inteira enquanto 09 edita.
5. Publicar somente agregados sanitizados/revisados, atualizar relação Customer/IT sem unir linhas, registrar gates/limitações e entregar IDs de casos reais seguros à demonstração; comunicar impedimento se não existir aprovação possível.

#### Blockers & Risks

| Tipo | Situação | Impact | Likelihood | Resolução ou mitigação |
|---|---|---|---|---|
| Blocker | Humano ainda não avaliou ou não há 30 casos elegíveis | High | High | Solicitar apenas revisão concreta; seguir documentação independente, mas não completar CK-12 nem inventar notas. |
| Risk | Resultados finais induzem alteração de threshold | High | Medium | Lock validado e teste somente leitura; falha desativa, nova versão exige avaliação nova. |
| Risk | Teste muda durante execução paralela de 09 | Medium | Medium | S07 selado com hash antes/depois, node ID explícito e código/configuração fixos; suíte consolidada apenas no step 10. |
| Blocker | Nenhum draft real seguro para aprovação exigida no DoD | High | High | Preservar abstinência, registrar evidência pendente e solicitar decisão de escopo ao dono; não reduzir o gate. |
