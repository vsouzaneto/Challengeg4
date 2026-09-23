# 02 — Dados sanitizados, splits e manifesto

**Task File:** ../../tasks/done/implement-support-decision-copilot.feature.md
**Phase:** 1
**Model:** opus
**Agent:** sdd:data-engineer
**Depends on:** 01
**Parallel with:** None
**Note:** Caminhos relativos à solution `submissions/luis-roquette/solution/002-support/`. Tier complex por contrato compartilhado e integridade dos splits; teste final permanece lacrado.
**Goal:** Entregar somente dados sanitizados e contratos reproduzíveis aos consumidores dos dois domínios.

Implementar em `src/support_copilot/data.py` os loaders, `sanitize_text`, `sanitize_customer_frame`, `DatasetSplit`, `make_split`, tipos `Manifest` e `write_manifest` definidos na Architecture Overview. Namespaces/taxonomias nunca se misturam. Resolver a política conservadora de quarentena de nomes não comprovadamente sanitizados antes de disponibilizar texto aos demais módulos; não alegar anonimização universal.

#### Expected Output

`data.py`, `tests/test_data.py`, entradas de dados no Makefile e README técnico; `scripts/reproduce.py` inicia ingestão/qualidade/splits de desenvolvimento. Fontes brutas e artefatos permanecem ignorados. Manifesto inclui fonte/schema/contagens/grupos/IDs/versões, campos futuros explicitamente indisponíveis e hashes canônicos sem autorreferência.

#### Success Criteria

Schemas/IDs e taxonomia IT são validados na fonte real; PII conhecida é removida e suspeita fica fora de treino/UI/export/logs. Splits 60/20/20 estratificados seeded têm IDs e grupos disjuntos; duplicatas/conflitos e insuficiência aparecem nas contagens. Criar IDs/split de teste é permitido, consumir suas features/labels antes de locks não é. Falha de download informa URLs/nomes/destino sem credenciais ou dados inventados.

#### Subtasks

1. Implementar loaders com colunas permitidas, hashes da fonte, identificação por domínio e validação sem ecoar valores brutos em erro.
2. Implementar sanitização comum, quarentena e revisão de amostras; remover identificadores/demografia antes de persistir qualquer derivado.
3. Implementar agrupamento canônico, representante determinístico, conflito em quarentena e splits com suporte verificável; registrar arredondamentos e limitação de near-duplicates.
4. Implementar `Manifest`/`write_manifest` atômico e pipeline inicial de desenvolvimento; documentar fontes e retomada manual no README/Makefile sem abrir dados finais.
5. Escrever testes próprios em `tests/test_data.py` para PII/nomes suspeitos, schemas, duplicatas conflitantes, escassez, IDs/grupos disjuntos, determinismo e JSON finito; executar gates aplicáveis e atualizar diário.

#### Blockers & Risks

| Tipo | Situação | Impact | Likelihood | Resolução ou mitigação |
|---|---|---|---|---|
| Risk | Nome livre ou PII residual segue para artefato | High | High | Quarentena conservadora e revisão manual; nunca publicar amostra sem inspeção. |
| Risk | Templates quase iguais contaminam treino/teste | High | High | Auditoria canônica antes do freeze; rever agrupamento antes de medir, documentando limites. |
| Blocker | Fonte pública ausente/schema alterado/suporte insuficiente | High | Medium | Mostrar causa e obtenção manual; marcar domínio indisponível, sem duplicar linhas nem fabricar CSV. |
