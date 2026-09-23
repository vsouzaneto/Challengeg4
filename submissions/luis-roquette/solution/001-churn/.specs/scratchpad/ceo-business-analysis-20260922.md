# Phase 2c — Business analysis

Task: `.specs/tasks/draft/implement-ceo-answer-architecture.feature.md`.

1. Problema e público: CEO precisa conciliar churn, satisfação e uso; clareza do output é o valor, não UI/LLM.
2. Escopo: arquitetura A em cinco blocos, pipeline existente, nenhuma implementação nesta fase.
3. Fontes locais lidas: Makefile, pyproject.toml, README, config.py, cli.py, claim_checks.csv, findings.csv, tests/test_publish.py, tests/test_app.py e skill answer-first-churn criada pela fase de pesquisa.
4. Cenários: principal, confronto CS/Produto, auditoria, todos inconclusivos e dados/artefatos inválidos.
5. Risco central: confundir mecanismo inconclusivo com ausência de informação; associação não é causalidade.
6. Divergência tratada: satisfação overall sobe 3,959→4,021; deterioração 4,50→3,667 ocorre em churn_next_30d. Cobertura de tickets não prova representatividade da base de contas.
7. Critérios: 12 CK + 3 HR; 12 essential, 1 important, 0 optional e 2 pitfall; respostas sim/não. Cinco dimensões de rubric somam 1,0.
8. Checks reais: pytest direcionado em dois grupos, make reproduce, make check, make app. Nenhum executado nesta fase; suíte/preflight requerem ambiente autorizado.
9. Testes: unit, integration, ui, reproducibility e manual; 12 grupos CK com HR cobertos explicitamente.
10. Limites: números históricos/MRR/RR/p fornecidos no contexto são referências a reconciliar, não recalculados nesta fase. Nenhuma causalidade ou receita recuperável foi inventada. Initial User Prompt preservado literalmente. Nenhum código alterado.
