# Impacto no código — arquitetura de resposta executiva ao CEO

Fase 2b, 2026-09-22. Base inspecionada: `submission/luis-roquette`, HEAD `517bdcff8cdff3503e83d6ba6c978b30b1ef8754`. Os caminhos abaixo são relativos a `submissions/luis-roquette/solution/001-churn/`, salvo indicação contrária. Este documento recomenda mudanças; nenhuma foi implementada. Draft: `.specs/tasks/draft/implement-ceo-answer-architecture.feature.md`.

## Resultado da exploração

A mudança cabe nos módulos atuais, sem novas dependências, API, banco ou LLM. `diagnosis.py` deve produzir as novas evidências; `publish.py` deve montar uma resposta canônica de cinco blocos uma única vez; relatório e app devem consumi-la. A escada de evidências precisa ser separada da autorização operacional: um mecanismo pode merecer investigação sem produzir `confidence=accepted`, ranking de intervenção ou probabilidade individual.

A escolha humana registrada no diário inclui coortes em tempo relativo ao churn. Portanto, reorganizar apenas a tela ou reescrever o relatório não satisfaz o escopo.

## Fluxo atual e contratos existentes

| Etapa / arquivos | Interface atual | Comportamento e reutilização |
|---|---|---|
| `config.py:6`, `contracts.py:172` | `load_raw_tables(raw_dir: Path) -> dict[str, pd.DataFrame]` | Cinco nomes e SHA-256 fixos; CSV lido como string e convertido por schemas. Reutilizar sem afrouxar contratos. |
| `contracts.py:192`, `quality.py:20` | `validate_contracts(tables) -> pd.DataFrame`; `build_quality_report(tables) -> dict[str, Any]` | PK/FK, tipos, não negativos, ARR=12×MRR; contradições viram warnings. O validator atualiza as tabelas convertidas. Duplicados de usage são preservados; `add_usage_row_key` existe, mas não é chamado pelo CLI. |
| `panel.py:10`, `:16`, `:190` | `first_terminal_churn(churn_events) -> pd.Series`; `mrr_lost_at_churn(subscriptions, terminal_churn) -> pd.Series`; `build_account_panel(tables, cutoffs, chronology) -> pd.DataFrame` | Primeiro evento não reativação, MRR ativo no dia anterior, uma linha conta/cutoff/chronology; métricas 7/30/90 dias, nulos por ausência de cobertura, strict filtra eventos fora do lifecycle. Reutilizar esses cálculos para evitar um segundo motor de features. |
| `diagnosis.py:78`, `:262`, `:389` | `build_diagnostic_snapshot(panel)`; `evaluate_candidates(observed, strict, churn_events) -> tuple[DataFrame, DataFrame]`; `build_claim_checks(strict_panel) -> DataFrame` | Snapshot comum mais recente até 2024-11-30, somente assinatura ativa; seis candidatos, GLM ajustado, comparação observed/strict, amostra/cobertura, corroboração por motivos. Claims agregam últimos seis cutoffs por três coortes. |
| `modeling.py:201` | `evaluate_model(panel) -> tuple[dict[str, object], DataFrame | None]` | Split por hash de conta, treino até agosto, teste setembro–novembro; AP/lift/Brier/segmentos/convergência controlam scores. Preservar; não usar previsão como evidência causal. |
| `cli.py:22`, `publish.py:95` | `reproduce(raw_dir, output_dir) -> dict[str, Path]`; frozen dataclass `AnalysisResult` | CLI orquestra todas as análises e chama publicação/validação; dataclass contém qualidade, painel, claims, findings, segmentos, avaliação do modelo e scores opcionais. Único ponto de integração a estender. |
| `publish.py:181`, `:228`, `:296` | `_build_queue(result)`, `_build_watchlist(result)`, `_build_report(result, queue, watchlist)` | Fila somente accepted, deduplicada por conta; watchlist separada de validação; relatório sintetiza claims, findings, segmentos e ações. Há narrativa fixa mesmo quando os dados mudam. |
| `publish.py:543`, `:598`, `:618` | `publish_artifacts(result, output_dir)`; `validate_artifact_set(output_dir)`; `compare_artifact_sets(reference_dir, candidate_dir)` | Cada payload usa `.tmp` + replace; manifesto escrito por último. Conjunto exato de nove payloads e hashes é obrigatório. Comparação ignora somente timestamp e SHA. Atomicidade é por arquivo, não transação de diretório; leitor detecta conjuntos misturados e bloqueia. |
| `app.py:250–757` | Execução no topo do módulo; `read_csv`, `section_heading`, `format_display_frame`, `render_table` | Valida manifesto antes da leitura; três abas; não roda pipeline. Porém recalcula percentuais e escolhe narrativa independente do relatório. Reutilizar componentes de apresentação, filtros e exportação. |

## Lacunas demonstradas no código

O sistema não calcula se churn subiu: `claim_checks.csv` só contém uso e satisfação. `segment_metrics.csv` descreve um único snapshot, não a concentração da piora histórica. O painel rotula os próximos 30 dias a partir de fins de mês; isso não equivale ao mês calendário seguinte e pode deixar o dia 31 fora ou sobrepor dias em fevereiro. Não somar esses rótulos para apresentar churn mensal.

`evaluate_candidates` publica apenas `association_controlled` ou `inconclusive`, registra só o primeiro motivo de falha e dá `actionability=immediate` até a findings recusados. `_reason_corroborates` usa todos os primeiros eventos do dataset, sem restringir ao horizonte do snapshot. A coluna `source_tables` atribui as cinco tabelas a todos os candidatos, sem discriminar evidência específica. Esses campos não bastam para graduar força ou rastrear uma narrativa executiva.

`_build_report` sempre afirma que nenhuma hipótese causal passou, inclusive no ramo accepted; app fixa frases como “crescimento médio esconde erosão”. `STATUS_LABELS` não cobre `flat`/`insufficient` e o app divide por início sem tratar zero/nulo. Relatório e app precisam receber a mesma conclusão já calculada, inclusive em datasets de teste contrários à narrativa atual.

O README afirma falha `cross_table_gate` para renovação, mas o `findings.csv` inspecionado registra `association_gate`. Os números exploratórios do diário são contexto, não novos golden values: ainda não foram reproduzidos sob um contrato explícito de período, denominador e população.

## Mudança mínima proposta e arquivos afetados

Estimativa da implementação: **21 arquivos** — **16 modificações e 5 criações**, **zero exclusões**, **zero módulos novos**, **zero dependências novas**. São 13 arquivos existentes de implementação/testes/documentação mais três artefatos existentes modificados e cinco novos artefatos. Esta contagem não inclui arquivos SDD e diário mantidos pelo orquestrador, nem presume que saídas antigas inalteradas precisem entrar no diff.

| Arquivo existente a modificar | Símbolos / alteração concreta |
|---|---|
| `src/ravenstack_churn/config.py` | Centralizar períodos de comparação, offsets relativos e política de observação até 2024-12-31. Registrar parâmetros no manifesto; não hardcodear os resultados exploratórios. |
| `src/ravenstack_churn/panel.py` | Adicionar `build_event_aligned_panel(tables: dict[str, DataFrame], chronology: Literal["observed", "strict"]) -> DataFrame`. Reusar o construtor temporal para âncoras pré-evento e controles contemporâneos, com seleção explícita das linhas necessárias. Manter o contrato mensal existente; helper novo não deve reinterpretar scoring global como label observável. |
| `src/ravenstack_churn/diagnosis.py` | Adicionar `build_monthly_churn(tables) -> DataFrame`, `build_reason_distribution(tables, start, end) -> DataFrame`, `build_event_cohort_metrics(relative_panel) -> DataFrame`, `build_mechanism_scorecard(findings, cohort_metrics, reason_distribution) -> DataFrame`. Estender `evaluate_candidates` com resultados separados dos gates e corroboração limitada ao horizonte; preservar retorno de duas tabelas e campos operacionais existentes. |
| `src/ravenstack_churn/cli.py` | `reproduce`: executar análises novas após contratos/painéis, passar resultados por `AnalysisResult`, continuar validando todo conjunto. Não acrescentar um comando paralelo ou segunda execução analítica. |
| `src/ravenstack_churn/publish.py` | Estender `AnalysisResult`; adicionar `_build_ceo_answer(result) -> dict[str, Any]`; adaptar `_build_report` para receber a resposta pronta; atualizar payloads, lista exata de arquivos, parâmetros/schema do manifesto e validação semântica mínima da resposta. Reutilizar serialização, tabelas, ranks operacionais e bloqueio por integridade. |
| `app.py` | Ler `ceo_answer.json` e novas tabelas somente após validação; abrir com os cinco blocos; mostrar série mensal e coortes na aba Evidências. Remover cálculo duplicado de headline/decisão. Manter as três abas, tema, filtros, download e bloqueio de contato. Tratar watchlist vazia antes de calcular slider máximo. |
| `tests/test_panel.py` | Coortes relativas, âncoras estritamente anteriores, controles contemporâneos, cobertura e ausência de dados futuros; manter regressões atuais. |
| `tests/test_diagnosis.py` | Denominador mensal, limites de calendário, motivos deduplicados, scorecard, evidências insuficientes/rejeitadas e desempates sem causa fabricada. |
| `tests/test_publish.py` | Cinco blocos derivados, novas fontes/referências, preservação da fila, JSON válido sem NaN, checksums/conjunto obrigatório e equivalência de execuções. |
| `tests/test_app.py` | Mesma resposta canônica no app e relatório, cinco blocos nos estados inconclusivo/accepted/sem dados; manter testes de filtros e download; impedir execução analítica no app. |
| `tests/conftest.py` | Atualizar `analysis_result` e fixtures pequenas. Hoje `analysis_result.panel` só tem duas linhas de scoring, e segmentos/findings omitem colunas reais: não usar fallback silencioso como substituto de fixture aderente ao novo contrato. |
| `README.md` | Contrato de cinco blocos, novos artefatos, definição de períodos/população e limite das conclusões; corrigir divergência da renovação usando saídas regeneradas. |
| `Makefile` | Conservar `setup/test/reproduce/app/check`; fazer a receita de `check` interromper caso a reprodução falhe (`&&` ou shell fail-fast). Hoje a comparação vem após `;`, podendo mascarar código de saída anterior em um diretório parcialmente publicado. |

| Artefato | Ação | Contrato proposto |
|---|---|---|
| `artifacts/monthly_churn.csv` | Criar | `period_start, period_end, population, at_risk_accounts, terminal_churns, churn_rate, mrr_lost, excluded_events, observation_complete`. Chave período/população; denominador e política documentados. |
| `artifacts/reason_distribution.csv` | Criar | `period_start, period_end, reason_code, terminal_accounts, share, mrr_lost, eligible_events, excluded_events`. Primeiro churn terminal por conta, motivos desconhecidos explícitos, mesmo universo da janela declarada. |
| `artifacts/event_cohort_metrics.csv` | Criar | `metric, chronology, cohort, relative_window_start, relative_window_end, anchor_period_start, anchor_period_end, eligible_accounts, observed_accounts, coverage, value`. Cada métrica inclui unidade e comparador; dados ausentes não viram zero. |
| `artifacts/mechanism_scorecard.csv` | Criar | `mechanism_id, finding_id, evidence_level, temporal_support, cross_table_support, chronology_stable, coverage, association_supported, counterevidence, limitation, source_refs, recommended_validation`. Estado de cada critério separado, sem score arbitrário ponderado. |
| `artifacts/ceo_answer.json` | Criar | `schema_version`, períodos/política da população, `headline`, cinco `blocks` em ordem fixa e `evidence_refs`; blocos usam IDs `what_changed`, `where`, `strongest_mechanism`, `unknowns`, `next_actions`. Valores numéricos tipados + unidade/denominador, conclusão e nível de evidência. |
| `artifacts/findings.csv` | Modificar | Acrescentar metadados explícitos dos gates/janela/fontes; não transformar automaticamente hypothesis em accepted nem atribuir priority_rank a inconclusivos. |
| `artifacts/report.md` | Modificar | Os cinco blocos primeiro, com fonte/corte/limitação; detalhamento auditável depois. Mesmo headline, mecanismo e ações do JSON. |
| `artifacts/run_manifest.json` | Modificar | Incluir os cinco payloads novos, versão de contrato e parâmetros analíticos; validação passa a exigir 14 payloads + manifesto. |

Todos os artefatos antigos devem ser regenerados e comparados pela reprodução, ainda que vários permaneçam byte a byte iguais. `account_panel.csv`, `account_queue.csv`, `account_watchlist.csv`, `claim_checks.csv`, `segment_metrics.csv`, `quality_report.json` e `model_evaluation.json` mantêm seus contratos neste recorte. Se uma correção justificada mudar conteúdo, a contagem real do diff será maior e a mudança deverá ser explicada, nunca editada à mão.

## Semântica que deve constar da arquitetura

### O que mudou e onde

Definir uma população primária antes de implementar. A opção coerente com o painel é contas cadastradas e sem primeiro churn no início do período; para retenção paga, acrescentar assinatura ativa e rotular essa população separadamente. Numerador precisa pertencer ao denominador: churn de conta aberta depois do começo do mês é entrada no mês e exige definição própria, não inclusão silenciosa. Publicar exclusões/entrada de contas, meses completos, contagem e MRR perdido. Média ponderada de taxas usa somas de numeradores/denominadores, não média simples de percentuais. Não publicar p-valor ingênuo que presume independência entre exposições repetidas da mesma conta.

No bloco “onde”, os segmentos atuais servem como fotografia do último cutoff. Não usá-los para afirmar que toda a piora histórica foi ampla. Para essa afirmação, a implementação precisa calcular os mesmos recortes por período com denominadores e estratos suficientemente observados. Pode estender `monthly_churn.csv` com `dimension/segment` sem criar um sexto artefato; caso não o faça, a conclusão deve dizer expressamente que a evidência de concentração se limita ao snapshot de novembro. Sobreposições entre país/plano/indústria não são somáveis em MRR total.

### Coortes relativas

Casos usam âncora no primeiro churn terminal válido; features terminam antes do evento e só utilizam observações conhecidas naquele cutoff. Controles usam as mesmas datas de calendário e critérios de elegibilidade, permanecendo sem churn pelo horizonte de comparação observado. Não alinhar controles arbitrariamente ao fim do dataset, não selecionar apenas “sobreviventes eternos” e não duplicar uma conta como múltiplas observações independentes. Se houver reutilização de controle, registrar isso e evitar inferência que pressupõe independência.

Reutilizar `_add_usage_window`, `_add_support_window` e `_add_trends` pelo construtor existente, selecionando somente pares conta/âncora desejados; não copiar essas fórmulas. O produto cartesiano de todos os cutoffs por todas as contas pode aumentar custo: usar os cutoffs únicos necessários, medir o custo na implementação e extrair um helper de montagem de linha apenas se esse caminho demonstrar duplicação ou custo significativo. `build_account_panel` já filtra contas após churn; não pedir features no dia do churn e tentar recuperá-las depois.

### Escada de evidência e ação

Os níveis propostos são `confirmed_fact`, `supported_mechanism`, `plausible_hypothesis`, `rejected_claim`, com apresentação portuguesa. Eles graduam afirmações, não atestam causalidade. Fato confirmado significa resultado descritivo verificável no recorte declarado. Mecanismo sustentado exige precedência, comparação adequada, convergência de fontes, cobertura e estabilidade definidas; hipótese plausível explicita critérios faltantes. Afirmação rejeitada exige contraevidência observada: ausência de cobertura ou um intervalo amplo não é refutação.

Preservar `confidence`, `priority_rank` e `_build_queue` enquanto a arquitetura não aprovar uma mudança operacional explícita. O mecanismo mais forte pode ser uma hipótese para investigar; se não há evidência para escolher, declarar empate ou ausência de vencedor e oferecer próximo teste discriminante. Não promover a maior exposição financeira à “causa mais forte”. `next_actions` deve conter ação, responsável, prazo, métrica de sucesso e condição de revisão; distinguir auditoria de dados, validação de mecanismo e intervenção. Não expor causa como provada, receita recuperável ou autorização de contato a partir do scorecard.

## Integrações e padrões a preservar

`AnalysisResult` já é o contrato único, portanto basta acrescentar DataFrames das quatro novas análises; `_build_ceo_answer` pode permanecer em `publish.py`, sem circular import ou fábrica. `publish_artifacts` deve construir a resposta uma vez e passar a mesma instância à geração do relatório, persistindo-a para o app. O app mantém cálculos de apresentação, nunca decisões analíticas.

`first_terminal_churn`, `mrr_lost_at_churn`, `_events_between`, `_change`, `build_diagnostic_snapshot`, `rank_findings`, `_markdown_table`, `_json_text`, `validate_artifact_set` e `AppTest` cobrem a maior parte das necessidades. `numpy`, `pandas`, `scipy`, `statsmodels`, `scikit-learn` e `streamlit` já estão fixados para Python 3.12; `pyproject.toml` e `requirements.txt` não precisam mudar. Não instalar DoWhy, sobrevivência, SHAP, NLP, ORM ou biblioteca de gráficos.

Serialização merece atenção: o atual `json.dumps` permite NaN/Infinity e `_json_default` não intercepta todo float nativo não finito. O novo JSON executivo deve normalizar ausências para null e falhar com números inválidos, sem promover placeholders a fatos. Validar os cinco blocos, unicidade/validade das referências e o conjunto exato de artefatos além do hash; checksum sozinho confirma bytes, não semântica.

## Riscos e mitigação

| Risco | Nível | Evidência / mitigação |
|---|---|---|
| Reproduzir números históricos sem definir população | Alto | Painel 30 dias ≠ mês; diário usa contagens exploratórias. Fixture com fevereiro/dia 31, entradas no mês, múltiplos eventos e contas sem assinatura; derivar conclusões dos resultados. |
| Confundir força relativa com causa comprovada/ação | Alto | `confidence` atual é binário e ordenação secundária usa MRR. Separar nível da afirmação, prioridade operacional e fonte; testar que hipótese não entra na fila. |
| Vazamento e seleção nas coortes | Alto | Âncoras dependem do evento futuro para análise retrospectiva. Separar esta análise das features/model_scores; ancorar controles no mesmo calendário e contabilizar cobertura. |
| Divergência entre JSON, relatório, app e manifesto | Alto | App e relatório duplicam narrativa; conjunto é fixo. Construir resposta uma vez, testar todas as referências e renderizadores, bloquear ausência/corrupção. |
| Aumentar escopo e custo sem ganho explicativo | Médio | Full panel é laço de cutoffs×contas; UI já funcional. Reutilizar cálculos, manter modelo opcional como está, no máximo novos gráficos informativos nas abas existentes. |

## Testes e validação necessários

Os testes existentes cobrem ingestão/qualidade, temporalidade, gates, publicação e AppTest. Foram lidos, não executados nesta fase. Não há workflow versionado em `.github` no checkout inspecionado; o gate canônico existente é `make check`. Isso não prova ausência de checks remotos ou proteção de branch, que deverão ser inspecionados pelo orquestrador antes de push/PR.

| Arquivo de teste | Casos adicionais essenciais |
|---|---|
| `tests/test_panel.py` | Caso com evento pós-cutoff não altera features anteriores; janelas relativas e controle com mesma âncora; nulo sem cobertura; churn terminal antes do signup excluído/contabilizado; dezembro incompleto não vira resultado observado. |
| `tests/test_diagnosis.py` | Numerador/denominador e MRR calculados à mão em fixture pequena; calendário fevereiro/dia 31; evento repetido/reativação não duplica; motivo unknown preservado; intervalo de motivos respeita o período; apenas cobertura ruim não vira rejected; instabilidade impede supported; empate e ausência de vencedor. |
| `tests/test_publish.py` | Contrato dos cinco blocos e referências; conclusões mudam quando a tendência é flat/down; estado sem accepted mantém fatos e fila vazia; nova saída ausente/tamper/schema inválido bloqueia; JSON sem NaN/Infinity; duas reproduções determinísticas com mesmo conteúdo. |
| `tests/test_app.py` | Resposta renderizada corresponde ao JSON; ausência de dado não quebra ratio/rótulo; watchlist totalmente vazia não gera slider inválido; filtros e CSV preservados; chamada de análise durante app proibida por monkeypatch. |
| `tests/conftest.py` | Reusar fixtures pequenas, adicionar meses/coortes suficientes e resultados de evidência coerentes. Não depender de valores exploratórios do diário nem mascarar campos ausentes com defaults permissivos. |

Na implementação: rodar testes pontuais durante cada mudança; ao fechar, Ruff, formato, suíte completa, reprodução em temporário e comparação canônica via `make check`, no ambiente permitido pelas regras do projeto. Para atualizar os canônicos, `make reproduce` é o caminho existente, seguido da comparação independente. O manifesto atual registra test_status por variável de ambiente; não tratar esse texto isolado como prova de teste executado. Não executar gates pesados no Mac sem autorização aplicável.

Revisão final inclui leitura humana dos cinco blocos em até cinco minutos e inspeção visual desktop/mobile. Aprovação analítica significa números rastreáveis, honestidade das afirmações e ação útil; não significa necessariamente descobrir uma causa única ou publicar um modelo.
