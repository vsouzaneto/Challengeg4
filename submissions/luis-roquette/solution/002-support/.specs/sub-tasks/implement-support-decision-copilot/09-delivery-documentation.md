# 09 — Documentação executiva e reprodução

**Task File:** ../../tasks/done/implement-support-decision-copilot.feature.md
**Phase:** 3
**Model:** sonnet
**Agent:** sdd:tech-writer
**Depends on:** 07
**Parallel with:** 08
**Note:** Caminhos relativos à solution `submissions/luis-roquette/solution/002-support/`. Tier typical: documentação multi-arquivo conforme template estabelecido. Não editar evidence nem diário em paralelo; encaminhar sua nota ao orquestrador.
**Goal:** Preparar documentação utilizável e honesta, pronta para receber as evidências reais da avaliação/demonstração.

Reutilizar `templates/submission-template.md` da raiz do repositório em `../../README.md`; escrever README técnico da solution. Consultar pesquisa/diário sem sobrescrever atualizações dos demais agentes. Enquanto etapa 08 roda, métricas/screenshots ainda não produzidos são marcados pendentes, nunca números ou links afirmados como comprovados.

#### Expected Output

`../../README.md` executivo e `README.md` técnico com três perguntas do diretor, arquitetura breve, setup, comandos reais, fontes, rubricas, limitações, privacidade/export e referência ao diário. Etapa 10 substitui pendências apenas pelos resultados efetivos.

#### Success Criteria

Um leitor encontra comandos/nomes dos CSVs/retomada manual e distingue observado/medido/projetado, associação/causalidade e local/remoto/persistido. Perfil não informado não é inventado. Texto descreve funções desativadas e requisito humano, sem atribuir aprovação ou gate inexistente. Links de artefatos existentes resolvem; futuros estão claramente pendentes.

#### Subtasks

1. Ler template/guia oficial e mapear campos às respostas/evidências do Challenge 002, mantendo toda documentação pública na submissão.
2. Consolidar README técnico com Python/lock, setup/data/reproduce/demo/doctor/test/lint, execução offline preparada e falha de download; incorporar/referenciar o protocolo cuja fonte única é o docstring de `src/support_copilot/retrieval.py`, entregue pelo step 06.
3. Redigir README executivo com limitações temporais/sinal/PII, separação de domínios, custos como cenários e checklist visível de evidências ainda pendentes.
4. Escrever teste documental próprio `test_delivery_documentation_contract` em `tests/test_workflow.py`, validando links locais existentes, comandos e ausência de paths raw/runtime como evidência pública; executar apenas esse node ID durante o paralelo. Esta etapa é dona do arquivo mutável durante a fase 3; etapa 08 executa exclusivamente a cópia imutável S07 do step 07 e escreve seus testes em modeling/retrieval. Não alterar S07, código de implementação, configuração ou lock.
5. Revisar contra o template e executar checagem documental; fornecer ao orquestrador a nota contemporânea com arquivos/verificações para inserção serial no diário. Não publicar/pushar nem capturar screenshot fictício.

#### Blockers & Risks

| Tipo | Situação | Impact | Likelihood | Resolução ou mitigação |
|---|---|---|---|---|
| Risk | Métrica provisória ou gate não executado vira alegação final | Medium | High | Marcar pendente e exigir substituição por evidência da etapa 10 antes do fechamento. |
| Risk | Docs e avaliação acessam versão mutável do mesmo teste | Medium | Medium | 09 edita READMEs/workflow; 08 executa S07 selado e edita evidence/retrieval test/modeling test; suíte final só após o join no step 10. |
| Blocker | Informação de perfil ou número real ausente | Low | Medium | Usar `Não informado`/pendência explícita, sem fabricar conteúdo. |
