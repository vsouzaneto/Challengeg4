# Graphify — rastreabilidade dos achados

## Escopo

- Corpus: Challenge 001, incluindo código, documentação, PDF, imagens e transcrições locais dos dois vídeos.
- Grafo: 348 nós, 779 relações e 13 comunidades.
- Regra de evidência: grau e centralidade descrevem a estrutura do grafo; não comprovam execução ou causalidade de negócio.

## God Nodes

Os dez nós centrais são funções extraídas do código e permanecem classificados como evidência estrutural:

1. `publish_artifacts()` — publica e conecta os artefatos finais.
2. `build_account_panel()` — constrói o painel analítico por conta.
3. `reproduce()` — orquestra a reprodução do diagnóstico.
4. `select_first_terminal_events()` — seleciona o primeiro evento terminal.
5. `evaluate_candidates()` — avalia hipóteses candidatas.
6. `_build_ceo_answer()` — monta a resposta executiva canônica.
7. `_coerce_tables()` — aplica contratos às tabelas.
8. `build_monthly_churn()` — calcula churn mensal.
9. `validate_artifact_set()` — valida o conjunto publicado.
10. `build_quality_report()` — consolida controles de qualidade.

## Surprising Connections

1. Paradoxo visual ↔ divergência entre população agregada e coorte: **INFERRED**; conceitos equivalentes aparecem no PDF e no source pack, mas a aresta não representa causalidade.
2. Oito gates ↔ método de oito etapas: **INFERRED**; semelhança metodológica entre PDF e source pack.
3. Três viradas humanas ↔ abstenção causal com ação: **INFERRED**; relação conceitual, não prova empírica.
4. Seis hipóteses inconclusivas ↔ abstenção causal com ação: **INFERRED**; confirmada como consistência narrativa, não como causa de churn.
5. `test_raw_files_match_published_checksums()` → `sha256_file()`: **EXTRACTED**; chamada confirmada em `tests/test_contracts.py` e `src/ravenstack_churn/config.py`.

## Suggested Questions

1. `publish_artifacts()` conecta runtime, testes, dashboard e artefatos porque centraliza a materialização da saída; isso é arquitetura, não prova de runtime.
2. `build_account_panel()` conecta painel e testes porque os fixtures validam o contrato do painel.
3. `reproduce()` cruza CLI, runtime, diagnóstico, painel e modelagem porque é o orquestrador de reprodução.
4. As duas relações inferidas de `build_account_panel()` devem permanecer **INFERRED** até validação explícita dos caminhos `observed_panel()` e `strict_panel()`.
5. Os 22 nós fracamente conectados são, em maioria, documentos, conceitos e o marcador do pacote; não justificam refatoração automática.
6. A baixa coesão da comunidade de runtime decorre de dependências utilitárias amplas; separar exige evidência de manutenção ou mudança conjunta.
7. A baixa coesão da comunidade de diagnóstico decorre da amplitude do módulo analítico; o grafo, sozinho, não prova necessidade de divisão.

## Diagnóstico de integridade

- Grafo final: zero endpoints ausentes ou pendentes.
- Uma auto-relação permanece em `_json_ready()`: é recursão real confirmada em `publish.py:231`, não corrupção.
- O SVG duplicava o conteúdo do PNG equivalente e não foi reextraído após travar a inspeção vetorial.
- Relações inferidas continuam marcadas como `INFERRED`; nenhuma foi promovida a fato.
