# Step 07 — Documentar definições e fechar o gate de reprodução

**Task File:** `.specs/tasks/todo/implement-ceo-answer-architecture.feature.md` (raiz da solução; acompanhar o mesmo basename quando movida de status).
**Phase:** 2 — Resposta executiva consistente.
**Model:** sonnet.
**Agent:** general:sonnet.
**Depends on:** 05.
**Parallel with:** 06.
**Note:** Caminhos relativos a `submissions/luis-roquette/solution/001-churn/`. Sonnet: README e encadeamento local do Makefile, sem algoritmo/contrato novo; não é haiku por envolver documentação semântica e teste de comportamento. Ownership: `README.md`, `Makefile` e regressão do gate em `tests/test_publish.py`; Step 06 edita apenas app/test_app. Não executar gate completo enquanto houver escrita concorrente: fechamento conjunto pertence à revisão da fase.
**Goal:** Tornar a resposta reproduzível e seus limites claros, com erro de reprodução interrompendo o check antes do compare.

**Interfaces:**

- Consome o conjunto validado e os valores efetivos do Step 05; README não recalcula nem fixa referência exploratória.
- Preserva alvos públicos `setup`, `test`, `reproduce`, `app` e `check` do `Makefile`.
- Produz um `check` fail-fast: retorno não zero de reprodução impede a chamada de `ravenstack_churn.cli compare`; sucesso continua chegando ao compare.

Documentar definições realmente implementadas e valores do conjunto validado do Step 05. Corrigir a divergência atual entre README e findings usando artefatos, sem impor referência antiga. Manter `setup/test/reproduce/app/check`; aplicar fail-fast à receita de `check`, preservando todos os gates. Deixar uma regressão mínima no pytest existente para que falha de reprodução não possa ser mascarada por compare.

#### Expected Output

README com cinco blocos, 14 payloads mais manifesto, calendário/população/unidades, escada de evidência, reprodução e premissa de um escritor/app parado. Makefile com o mesmo preflight canônico, interrompendo na falha de reprodução; teste isolado sem dataset/ambiente externo.

#### Success Criteria

- Documentação corresponde aos IDs/valores/limites de `ceo_answer.json` e findings; não afirma causa/receita recuperável ou generaliza coorte.
- Teste executável injeta reprodução com exit não zero e prova que compare não roda; caminho de sucesso continua chegando a compare.
- Nenhum check/teste é removido/afrouxado; gate completo final será executado após união de 06/07 no mesmo diff.
- Premissa de publicação offline e comandos/ambiente autorizado estão explícitos. Cobertura: CK-6, CK-8–CK-12, HR-1–HR-3.

#### Subtasks

1. Ler README, Makefile e artefatos validados do Step 05; listar divergências reais de definições/conclusões para corrigir, sem editar código analítico.
2. Atualizar README com contrato executivo, populações/períodos/MRR/cobertura, incerteza, motivos versus mecanismo, mapa de artefatos e ações proporcionais.
3. Documentar um escritor, app parado e validação antes de leitura, limites de TOCTOU, comandos canônicos e ambiente autorizado; sem hot reload ou deploy novo.
4. Corrigir receita `check` com encadeamento fail-fast mínimo; preservar Ruff, formato, pytest, reprodução temporária, compare e limpeza segura do diretório temporário.
5. Escrever regressão mínima em `tests/test_publish.py` usando `tmp_path` e subprocess/stub sem dependência nova: invocar a receita real com Python stub, falhar somente na reprodução, registrar se compare foi chamado; testar sucesso também. Executar o teste direcionado no ambiente permitido e entregar evidências para `make check`/revisão renderizada da fase após 06.

#### Blockers & Risks

| Blocker / Risk | Impact | Likelihood | Mitigation / Resolution |
|---|---|---|---|
| README repete diagnóstico antigo | Alto | Alta | Conferir ceo_answer/findings do mesmo analysis_id e documentar resultados efetivos. |
| Shell executa compare após erro de reprodução | Alto | Alta | Encadeamento fail-fast e stub que falha só na etapa de reprodução, não em gates anteriores. |
| Teste exige suíte real ou entra em recursão | Médio | Média | Stub de Python despacha argumentos sem executar pytest/reprodução; teste observa receita real em temporário. |
| Gate final roda antes de 06 terminar | Alto | Média | Teste local direcionado neste step; suíte/reprodução/renderização finais apenas após união na revisão da fase. |
