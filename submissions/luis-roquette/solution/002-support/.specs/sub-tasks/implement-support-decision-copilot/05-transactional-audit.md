# 05 — Auditoria SQLite e exportação atômica

**Task File:** ../../tasks/done/implement-support-decision-copilot.feature.md
**Phase:** 2
**Model:** opus
**Agent:** sdd:developer
**Depends on:** 02
**Parallel with:** 04, 06
**Note:** Caminhos relativos à solution `submissions/luis-roquette/solution/002-support/`. Tier complex obrigatório por integridade de dados. Não alterar modeling/decision/retrieval; snapshot factual segue contrato fixado na SPEC e fixtures tipadas.
**Goal:** Persistir decisões sanitizadas sem duplicação/perda e fornecer bytes exportados idênticos ao arquivo salvo.

Implementar `src/support_copilot/store.py` com `DecisionEvent`, `StoredDecision`, `initialize_store`, `record_decision`, `list_decisions`, `ExportResult` e `export_decisions_csv`. Usar sanitizador de `data.py`; sem ORM/migração destrutiva. `data/runtime/decisions.sqlite3` é separado dos artefatos de reprodução.

#### Expected Output

`store.py`, `tests/test_store.py`, banco/schema v1 e exports runtime ignorados; README descreve campos, NULL, idempotência e transformação de fórmulas no CSV. Nenhuma evidência pública é fabricada nesta etapa.

#### Success Criteria

UUID repetido idêntico retorna mesmo ID; payload divergente falha. Falha transacional preserva registros anteriores, versão desconhecida não recria banco. Ações/razões/draft/final são validados após sanitização; `edit_ratio` segue `SequenceMatcher` e é nulo onde não se aplica. CSV inclui todos os campos, lê snapshot commitado e neutraliza prefixos de fórmula inclusive whitespace/control chars. Rename não sobrescreve export anterior.

#### Subtasks

1. Criar dataclasses e schema/versão/constraint UNIQUE com conexões fechadas e transações explícitas; normalizar strings opcionais vazias para nulo.
2. Implementar validação do snapshot e quatro ações, sanitização na fronteira, idempotência, UTC e diferença de edição sem inventar campos indisponíveis.
3. Implementar listagem e export CSV estável UTF-8/LF, listas JSON, formula neutralization e temporário irmão/rename; retornar bytes/hash/contagem reais.
4. Escrever testes próprios em `tests/test_store.py` para rollback, reinício por nova conexão, UUID divergente, schema desconhecido, PII nos motivos/edições, ações sem draft e falha de export.
5. Acrescentar teste de round-trip de todos os campos e variantes de fórmula; executar gates aplicáveis, documentar comportamento e registrar evidência no diário, mantendo dados runtime fora do Git.

#### Blockers & Risks

| Tipo | Situação | Impact | Likelihood | Resolução ou mitigação |
|---|---|---|---|---|
| Risk | Rerun duplica evento ou confirma escrita parcial | High | Medium | UUID estável/UNIQUE, transação e nova leitura na integração; injeção de falhas. |
| Risk | CSV abre fórmula ou perde distinção de NULL | High | Medium | Neutralização de prefixos, schema explícito e round-trip; validar em planilha na etapa 10. |
| Blocker | Banco existente tem versão desconhecida ou sem permissão | High | Low | Bloquear escrita com causa/correção; preservar arquivo e eventos, sem reset automático. |
