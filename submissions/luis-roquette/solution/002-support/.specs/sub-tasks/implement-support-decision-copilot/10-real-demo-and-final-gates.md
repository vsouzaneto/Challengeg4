# 10 — Demonstração real, evidência persistida e fechamento

**Task File:** ../../tasks/done/implement-support-decision-copilot.feature.md
**Phase:** 3
**Model:** sonnet
**Agent:** sdd:test-engineer
**Depends on:** 08, 09
**Parallel with:** None
**Note:** Caminhos relativos à solution `submissions/luis-roquette/solution/002-support/`. Tier typical: execução dos contratos/gates já estabelecidos e captura de evidência, sem novo desenho. Falha que exige mudança de contrato retorna ao dono do módulo.
**Goal:** Comprovar a aplicação real e fechar apenas critérios sustentados por estado renderizado/persistido.

Executar os Regular Checks da SPEC e demonstrar fila, decisão, reinício, export, scorecard e texto IT. Capturar `evidence/screenshot.png` real e `evidence/decisions-demo.csv` como cópia revisada de export persistido, incluindo aprovação/edição e escalonamento efetivos. Se não existe draft seguro após avaliação, a evidência de aprovação continua bloqueada; não usar fixtures para fechá-la.

#### Expected Output

Screenshot/CSV reais sanitizados; `evidence/metrics.json` referencia hash/IDs/versões e relação com captura. READMEs sem alegações pendentes disfarçadas e diário com comandos/exit status/SHA/diff, revisões e correções. Entrega preparada, sem inferir autorização de push/PR/publicação.

#### Success Criteria

Audit IDs da UI existem depois de reiniciar e coincidem com export baixado/persistido; campos/fórmulas são conferidos em planilha. Teclado/foco/labels/contraste e estados de erro são observados em navegador real. `make doctor`, `make test`, `make lint`, `make reproduce`, workflow test e `git diff --check` passam no estado pretendido; suíte completa/reprodução pesada usam gerenciador. Nenhum arquivo público sai de `submissions/luis-roquette/` e nenhum raw/banco/binário/PII entra no diff.

#### Subtasks

1. Escrever teste próprio final em `tests/test_workflow.py` para correlacionar IDs de eventos, bytes/hash do export e metadados públicos; após conclusão de 08 e 09, executar `test_reproduce_twice_same_inputs` e `test_delivery_documentation_contract` no arquivo final consolidado e a suíte canônica completa. S07 sustenta somente a execução paralela de 08, não substitui este gate final. Manter fixtures claramente separadas de evidence real.
2. Demonstrar ações reais autorizadas apenas locais, reiniciar, reler IDs, baixar arquivo e verificar fórmula/NULL/campos; capturar tela sanitizada e revisar todos os exemplos públicos manualmente.
3. Rodar os gates canônicos no SHA/diff exato via `codespace-manager`, com browser/GUI local quando necessário; corrigir falhas na origem com regressão e repetir gates aplicáveis, sem bypass.
4. Consolidar metrics/export/screenshot/READMEs com resultados reais, estados desativados e limitações; verificar rubricas humanas e hashes/locks sem alterar política pelo teste.
5. Conferir diff/ignore/licenças e arquivos explícitos, registrar revisão única da fase e pendências externas restantes; só declarar DoD quando CK-1–20 tiverem evidência e nenhuma revisão humana obrigatória estiver oculta.

#### Blockers & Risks

| Tipo | Situação | Impact | Likelihood | Resolução ou mitigação |
|---|---|---|---|---|
| Blocker | Assistência segura desativada impede aprovação real | High | High | Reportar exatamente o critério pendente; preservar gate e não fabricar decisão para screenshot. |
| Risk | Screenshot/export expõe PII ou não corresponde ao banco | High | Medium | Revisão manual e correlação ID/hash após nova conexão; excluir publicação até corrigir. |
| Risk | Gate remoto validou outro estado ou root ignore oculta entrega | Medium | Medium | Provar fingerprint SHA/diff e inventariar arquivos públicos explicitamente; nunca staging amplo de raw/runtime. |
