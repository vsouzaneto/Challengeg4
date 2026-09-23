# Evidência local e matriz de cobertura

## Identidade da execução

| Campo | Evidência |
|---|---|
| Comando canônico | `bash scripts/preflight.sh` |
| Ambientes gerenciados | integral: `codex-preflight-657v7q4ggx7f5557`; focais pós-revisão: `codex-preflight-pwq7q4pr75pfx5q`; ambos via `codespace-manager` |
| Reprodução no Mac | Não executada: gates pesados são exclusivos do Codespace por regra operacional |
| Python | `Python 3.11.15`, provisionado por `uv==0.10.10` |
| Revisão Git do último preflight integral concluído | `e052e4e226a8962fc338380e6cebb2e6446dc86b` |
| Revisão Git dos focais pós-revisão | `9228ffdf3ff760efe0ecfb9b107d9a537c26789b` |
| Diff | Limpo; `EXACT_SHA` conferido antes de cada execução registrada |
| SHA-256 de `requirements.txt` | `43a420f22b5e31ceadf0946434689dca39359c7a69d358e4636ee6c0fb344843` |
| Fingerprint dados/modelo do último integral | `515a0c991c0fc58c705463ed8067d01860e3338d563b88e3987c411b1a18c0fd` |
| Source digest do último integral | `8c65922c2654ed480e7d8024f27c6f9936e6ab207817a4b3ef0fe5eefe3390f2` |

O último preflight canônico integral concluído terminou com `PREFLIGHT OK`: 74 testes em 92,458 s, avaliação real, startup e jornada Playwright renderizada no SHA `e052e4e`. Após o retrabalho da revisão, seis focais passaram em 26,818 s no SHA exato `9228ffd`: ordenação canônica, seleção nativa, pin/horário localizado, identidade única da fonte e jornadas AppTest/Playwright para rotas rejeitadas e portfólio vazio. Não existe resultado integral pós-correção: o owner determinou o bypass explícito dessa repetição; uma execução já iniciada foi interrompida e não é contabilizada. TC-47 continua não executado.

O segundo retrabalho residual adicionou regressões em `2dbc3e5` e implementação em `af046c4` para seleção única entre grades e transparência do suporte histórico em Prospecting. Por bypass explícito do owner e ausência de Codespace limpo do repositório, esses quatro testes foram revisados estaticamente, mas não executados. Os únicos gates pós-mudança são `py_compile`, `bash -n scripts/preflight.sh` e `git diff --check`, todos aprovados; não se reivindica GREEN executado.

### Gate final da entrega

A revisão final publicada inicialmente foi `d1c351fef9f7a4cea36a4095e6c4eb1468b40c5d`. Ela passou por `py_compile`, validação sintática do preflight, `git diff --check` com preservação deliberada dos CSVs-fonte, auditoria de escopo/tamanho/segredos/links e jornada Playwright focal do portal com o vídeo real. O navegador confirmou doze etapas, vídeo H.264/AAC de 6min05s em 1280 × 720 e zero erros de console.

O preflight integral final **não foi concluído**. A primeira orquestração chegou ao Codespace e recuperou o commit exato, mas uma comparação montada com SHA completo incorreto encerrou o comando antes dos testes. A segunda aguardava/iniciava outro Codespace quando Luis determinou explicitamente o bypass por congestionamento. A execução foi interrompida e não é contabilizada como evidência de teste. Esta limitação permanece exposta; o último integral válido continua sendo o já registrado acima.

## Entrega Git e tentativa de publicação — 2026-09-22

| Campo | Evidência |
|---|---|
| Branch publicada | `submission/luis-roquette-003-lead-scorer` |
| Revisão inicialmente publicada | `aa70dc6435e9df85c512007e3d1c008e4cf78876` |
| Correção da identidade da fonte | `14d0296`: o diretório explícito deixou de ser resolvido como seu pai |
| Pull request | [#140 — [Submission] Luis Roquette — Challenge 003](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/pull/140) |
| Base / estado inicial | `upstream/main`; aberto e mergeable; nenhum check configurado ou pendente |
| Regras verificadas | sem workflows versionados; rulesets vazios; `main` do fork sem branch protection |
| Identidade calculada apó a correção | fonte `7e25ba0ecbda9e3e06e89141182dc538e8407af543adca676ad23632f345d311`; fingerprint `2003cb28535c6a4b48e038c6bf1412081d6588b30ab0e2b1396a6f2b5c1173eb` |
| Streamlit Community Cloud | tentativa chegou ao consentimento OAuth do GitHub; publicação não submetida sem a autorização interativa do owner |
| URL / TC-47 / screenshots | pendentes; nenhuma URL, prova live ou captura é reivindicada |

O owner dispensou explicitamente apenas a repetição do preflight integral. Essa exceção não substitui a publicação, a renderização live nem o TC-47. Assim que o OAuth for autorizado, o deploy deve usar o fork `luisroquette/ai-master-challenge`, a branch acima e o entrypoint `submissions/luis-roquette/solution/003-lead-scorer/app.py`; depois, o verificador deve receber a identidade efetivamente renderizada.

A regressão TC-40 agora reconstrói o digest dos quatro arquivos reais e rejeita implicitamente o digest constante de arquivos ausentes. O ambiente local não possui `streamlit`, portanto o método `unittest` versionado não iniciou; nenhuma instalação ou preflight foi feita por causa do bypass. A mesma asserção focal executada diretamente contra `scoring.py` passou (`FOCAL SOURCE IDENTITY OK`), assim como `py_compile`, `bash -n scripts/preflight.sh` e `git diff --check`.

## Snapshot real já congelado

| Tabela | Linhas |
|---|---:|
| `sales_pipeline.csv` | 8.800 |
| `accounts.csv` | 85 |
| `products.csv` | 7 |
| `sales_teams.csv` | 35 |

São 6.711 oportunidades fechadas e 2.089 ativas. O split temporal validado usa 4.027 registros de treino, 1.349 de calibração e 1.335 de teste. As quatro combinações `logistic/full`, `logistic/fallback`, `boosting/full` e `boosting/fallback` são resultados obrigatórios. Na evidência anterior ao passo 04, todas foram rejeitadas por `fewer_than_two_supported_bands`; portanto, a UI deve manter 100% das ativas em estados relativos ou insuficientes e não pode renderizar probabilidade nem receita esperada probabilística.

## Cobertura TC-01–46

| Casos | Métodos estáveis |
|---|---|
| TC-01–07 | `test_TC01_real_provenance`; `test_TC02_direct_and_archive_verified_promotion`; família `test_TC03_*`; família `test_TC04_*`; `test_TC05_price_boundaries`; `test_TC06_normalization_identity_and_cardinality`; `test_TC07_accounting_and_no_history` |
| TC-08–17 | `test_TC08_closed_membership_disjoint_tied_dates`; `test_TC09_cutoff_boundary_neighbors`; `test_TC10_empty_periods_and_single_class_diagnostics`; `test_TC11_train_frozen_support_exact_exclusions_and_feature_names`; famílias `test_TC12_*`, `test_TC13_*`; `test_TC14_real_four_routes_frozen_policy_and_complete_evidence`; `test_TC15_*`; `test_TC16_*`; `test_TC17_calibration_fit_consumes_only_intermediate_ids` |
| TC-18–27 | `test_TC18_probability_publication_decision_table`; `test_TC19_loss_equality_strict_epsilon_boundaries`; famílias `test_TC20_*`, `test_TC21_*`; `test_TC22_TC23_band_first_partitioned_ranking_and_lexical_ties`; `test_TC24_rejected_routes_suppress_probability_and_expected_revenue`; `test_TC25_prospecting_nested_smoothing_is_hand_reconstructable`; `test_TC26_sparse_backoff_and_support_boundaries`; `test_TC27_prospecting_contract_never_exposes_probability_revenue` |
| TC-28–39 | `test_TC28_logistic_raw_and_calibrated_affine_reconstruct_outputs`; `test_TC29_boosting_tree_paths_reconstruct_raw_margin`; `test_TC30_factor_summary_preserves_value_sign_and_absent_direction`; `test_TC31_TC32_versioned_playbook_uses_only_actionable_evidence`; famílias `test_TC33_*` a `test_TC39_*`, incluindo AppTest e `test_TC34_TC35_TC36_TC37_TC38_TC39_rendered_journeys` |
| TC-40–46 | famílias `test_TC40_*`; `test_TC41_cached_bundle_reuses_training_for_same_identity`; `test_TC42_seeded_active_scores_are_deterministic_and_stage_safe`; família `test_TC43_*`; `test_TC44_offline_runtime_denies_external_and_permits_loopback`; `test_TC45_preflight_failure_injection_returns_nonzero`; `test_TC46_clean_startup_owns_only_its_child_without_recursion` |

Status: TC-01–46 ficaram verdes no último preflight integral anterior ao retrabalho (74/74, SHA `e052e4e`). O delta pós-revisão está verde nos seis focais do SHA `9228ffd`; não se reivindica um novo 79/79 integral por causa do bypass explícito do owner. O método `test_live_verifier_local_contract_is_not_TC47` testa localmente os erros do verificador, mas não reivindica o TC-47.

## Mapa de cobertura CK

| Checklist | Evidência principal | Estado nesta fase |
|---|---|---|
| CK-1–5 | TC-01–07: proveniência, recuperação, esquema, normalização e diagnósticos | comprovado |
| CK-6–16 | TC-08–24: cortes temporais, rotas, features proibidas, calibração, seleção e supressão | comprovado |
| CK-17–23 | TC-25–32: backoff Prospecting, explicações reconstruíveis e playbook | comprovado |
| CK-24–32 | TC-33–42: abas, contextos, filtros, detalhes, pins, cache e determinismo | comprovado |
| CK-33–34, CK-36–38 | TC-43–46, inspeção estrutural e jornada renderizada; zero API de IA | comprovado |
| CK-35 | bootstrap Python 3.11 reproduzido no Codespace; reprodução pesada no Mac não executada por política operacional | parcial |
| CK-39–49 | documentação inicial presente; screenshots, URL e TC-47 dependem das fases 05/06 | pendente da entrega |
| CK-50 | documentação não faz afirmação causal | conforme: resposta **NÃO** |

## Resultados reais das quatro rotas

| Candidato/rota | Brier (baseline `0,228038`) | Log loss (baseline `0,648628`) | Resultado |
|---|---:|---:|---|
| `logistic/full` | `0,227178` | `0,646784` | rejeitada: `fewer_than_two_supported_bands` |
| `logistic/fallback` | `0,227719` | `0,647981` | rejeitada: `fewer_than_two_supported_bands` |
| `boosting/full` | `0,227151` | `0,646719` | rejeitada: `fewer_than_two_supported_bands` |
| `boosting/fallback` | `0,227741` | `0,648029` | rejeitada: `fewer_than_two_supported_bands` |

As 2.089 oportunidades ativas ficaram em prioridade `relative`; zero ficaram em `insufficient_data`. Nenhuma rota rejeitada publicou `probability` ou `expected_revenue`.

## Jornada renderizada

- Vendedor: ambas as abas, portfólio próprio, detalhe e linha `Dados insuficientes` sem probabilidade/receita esperada.
- Gestor: equipe, filtros exatos, detalhe, prioridade temporária com autor/horário e limpeza por recálculo.
- A lista usa no máximo 25 linhas por página, seleção única no `st.dataframe` nativo e botão acessível `Abrir <opportunity_id>` como fallback; o resumo `Filtros aplicados` confirma o estado final antes da ação.
- As jornadas pós-revisão provaram que rotas probabilísticas rejeitadas não expõem probabilidade/receita esperada em nenhuma superfície e que um portfólio realmente vazio não exibe detalhes nem pin.
- O retrabalho residual unifica seleção nativa e fallback na mesma fonte de verdade por estágio/página, invalida grades irmãs e acrescenta nos detalhes Prospecting observações históricas, suporte efetivo e peso do prior; o pin relativo mantém o valor potencial. As novas jornadas que cobrem essa afirmação estão escritas, mas pendem de execução pelo bypass registrado acima.
- App real: startup e identidade completa (`revision`, `fingerprint`, `source_digest`) verificadas pelo gate `startup`.
- O texto renderizado confirmou título, aviso do protótipo, filtro do vendedor e identidade completa. Não há captura versionada; nenhuma imagem é reivindicada.

## Limites e próxima evidência

- Os dados são estáticos e `Prospecting` não possui rótulos completos de desfecho.
- As associações não são causais; não há evidência de que uma ação aumente fechamento ou receita.
- Pins duram apenas na sessão. Não há autenticação, escrita no CRM, drift ou retreino agendado.
- O teste final usado na escolha cria otimismo pós-seleção; mudanças de política tornam a releitura exploratória.
- Escala exige piloto controlado, captura de intervenção/desfecho, auditoria segmentada e recalibração periódica.
