# 07 — Pipeline e aplicação integrados

**Task File:** ../../tasks/done/implement-support-decision-copilot.feature.md
**Phase:** 2
**Model:** opus
**Agent:** sdd:developer
**Depends on:** 03, 04, 05, 06
**Parallel with:** None
**Note:** Caminhos relativos à solution `submissions/luis-roquette/solution/002-support/`. Tier complex pela integração de módulos/contratos. Dono exclusivo de `app.py`, `ui.py`, `scripts/reproduce.py` e `tests/test_workflow.py` nesta etapa.
**Goal:** Tornar o fluxo inteiro executável, com estados de revisão pendente e falhas seguros antes de abrir teste real.

Integrar `load_artifacts`, `FeatureState`, `ArtifactBundle`, `render_queue`, `render_scorecard`, `render_it_lab`, `render_evidence` e o pipeline canônico. Fila é página inicial; enquanto teste real está lacrado, mostrar estado indisponível e causa. Fixtures sanitizadas demonstram o workflow nos testes, explicitamente sem valer como screenshot/métricas da entrega.

#### Expected Output

UI de quatro páginas, pipeline de desenvolvimento/locks/teste, Makefile completo e `tests/test_workflow.py`. Artefatos/manifests são publicados atomicamente com manifesto por último; `make demo` reutiliza ambiente preparado e não força rede/treino. Runtime SQLite/export persiste separado.

`tests/test_workflow.py::test_reproduce_twice_same_inputs` executa o pipeline duas vezes em diretórios temporários separados com as mesmas fixtures sanitizadas, seed, configuração e lock. Compara canonicamente fontes, splits, políticas, predições, tabelas, métricas e hashes lógicos; apenas `manifest.generated_at` pode diferir e é excluído nominalmente, com motivo documentado no teste. Nenhuma outra chave ou família de timestamps é ignorada; os hashes binários são validados contra o arquivo da própria execução, usando `logical_sha256` para equivalência entre serializações. Essa fixture exige igualdade dos valores canônicos, sem tolerância numérica genérica. Deve falhar se uma métrica, ID de split, política ou hash lógico mudar e passar se somente `generated_at` mudar.

Após a revisão da fase 2, o orquestrador sela **S07**: cópia byte a byte de `tests/test_workflow.py` em `data/runtime/validation/phase2-<workflow_sha256>/test_workflow.py`, ignorada pelo Git e sem edição durante a fase 3. Registra caminho, SHA-256 do arquivo e fingerprint do código/configuração/lock da fase 2 no diário. O teste usa a solution como diretório de trabalho e fixtures autocontidas; não deriva a raiz pelo caminho da cópia. Step 08 usa somente esse snapshot para o teste de reprodução durante o paralelo; step 10 verifica novamente o arquivo final consolidado.

#### Success Criteria

Formulário mantém ticket/versão/UUID corretos, permite quatro ações válidas e só confirma audit ID relido em nova conexão. Sem draft válido, aprovar fica desabilitado. Artefato corrompido/incompatível/stale bloqueia dependentes corretos com caminho/causa/`make reproduce`; um modelo IT ruim não derruba análise Customer. Hash/versão/caminho são verificados antes de joblib; normal use offline não chama rede.

#### Subtasks

1. Completar orquestração canônica com desenvolvimento antes dos locks e teste somente depois; preservar runtime, versões, hashes lógicos, configurações e estados indisponíveis.
2. Implementar validação de manifest/dependências/caminhos/symlinks/hashes antes de desserialização e invalidar caches por versão; não aceitar modelos enviados pelo usuário.
3. Montar páginas e controles nativos, fila/filtros/ordem/motivos/fontes, cenários separados, laboratório IT e evidências; sanitizar entrada, nunca recalibrar na UI.
4. Integrar submit com UUID estável, validação, leitura por nova conexão e download dos bytes persistidos; tratar erro de banco sem falso sucesso ou perda do formulário.
5. Escrever testes próprios em `tests/test_workflow.py` para quatro ações, troca de ticket, rerun, reinício/export, Critical/PII com score 1,0 sem aprovação, artefatos falhos isolados, offline e ausência de mutação/efeito externo; criar explicitamente `test_reproduce_twice_same_inputs` com o contrato de comparação acima. Executar a prova de reprodução e suas alterações adversariais, registrar o marco/revisão e entregar S07 selado antes de lançar steps 08/09.

#### Blockers & Risks

| Tipo | Situação | Impact | Likelihood | Resolução ou mitigação |
|---|---|---|---|---|
| Risk | Artefato de versão velha ou caminho malicioso é carregado | High | Medium | Schema/hash/dependências/raiz antes do joblib; cache versionado e testes de symlink/traversal. |
| Risk | Pipeline abre teste antes de revisão/locks | High | Medium | Gate central de lifecycle, teste que espiona acesso e nenhum template final antes do lock. |
| Risk | Rerun troca draft/ticket ou confirma sem persistência | High | Medium | Estado por domínio/ticket/versão, UUID por tentativa e leitura em nova conexão. |
