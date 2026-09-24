# Code review — Lead Scorer (solution/)

**Revisor:** agente `code-reviewer` (somente leitura) · **Data:** 2026-09-23 · **Escopo:** `pipeline/src/lead_scorer/**`, `shared/lead_scorer_contracts/**`, `api/src/**`, `web/src/**`, Dockerfiles, `docker-compose.yml`, `Makefile`, `.claude/hooks/*.py`.

**Critério do G4:** "o código é limpo o suficiente para outro dev dar manutenção?"

## Verificações executadas

| Projeto | ruff | mypy | testes |
|---|---|---|---|
| `shared/lead_scorer_contracts` | ok | ok | 5 passed |
| `api` | ok | ok (17 arquivos) | 57 passed |
| `pipeline` (`src`, `tests`) | ok | ok (38 arquivos) | 64 passed (63 s, JDK 21) |
| `pipeline` (`ruff check .` como no `make lint`) | **160 erros** em `analysis/` | — | — |
| `web` | eslint 0 erros (3 warnings) | `tsc -b` ok | 33 passed |

Árvore git limpa: nenhum arquivo do `web/` estava em edição durante a revisão.

## Findings (crítico → sugestão)

### 1. Alto · Fila "Confirmar ou encerrar" e contadores errados na visão de time/região

`solution/web/src/pages/QueuePage.tsx:22-42,50-56,68-76`

A página carrega até 500 deals **sem** o filtro `queue` e separa vivos/parados no cliente. Há 1.291 zumbis em 2.089 deals abertos (`_manifest.json`), então sem filtro de vendedor a resposta é truncada: a aba "Confirmar" mostra um subconjunto arbitrário (os parados que caíram no top 500 por `expected_value` de **todos** os deals), e as badges das abas, `staleValue`, `cooling` e `hot` são contados sobre a amostra truncada. O comentário "The API has no age filter" está desatualizado — a API já expõe `queue=work|confirm` e `min/max_days_in_engaging`.

**Correção:** uma query por aba com `queue=` na API e `total` do payload nos contadores; manter o `truncated` só como aviso de paginação.

### 2. Alto · "Top 10 parados por valor" é top 10 por valor entre os 50 mais antigos

`solution/web/src/pages/TeamPage.tsx:54-73`

`useDeals` pede `sort=-days_in_engaging, limit=50` e depois filtra/ordena por `expected_value` no cliente. Um zumbi de R$ 20 mil com 150 dias nunca aparece se houver 50 zumbis mais velhos. Rótulo da seção promete algo diferente do que é mostrado.

**Correção:** `queue=confirm&sort=-expected_value&limit=10` e remover o filtro/sort local.

### 3. Médio · `make lint` está vermelho (DoD)

`solution/Makefile:36` · `solution/pipeline/pyproject.toml:47-51`

`ruff check .` em `pipeline/` inclui `analysis/` (scripts de EDA) e falha com 160 erros; `src/` e `tests/` estão limpos. Quem seguir o README e rodar `make lint` conclui que o projeto não passa no próprio gate.

**Correção:** `extend-exclude = ["analysis"]` no `[tool.ruff]` do pipeline (ou uma seção `per-file-ignores` para `analysis/*`).

### 4. Médio · Contrato documenta `Reason.weight` em unidade diferente da implementada

`solution/shared/lead_scorer_contracts/src/lead_scorer_contracts/contracts.py:47-56,69-74,99-112` vs `solution/pipeline/src/lead_scorer/scoring/rules.py:9-15`

O contrato descreve o peso como "contribuição em p_win ou pontos de score" e os exemplos (`-0.18`, `0.09`, `0.05`) estão na unidade antiga (p_win); `rules.py` define **pontos de `priority_score`** para todos os códigos e a UI (`fmtWeight`) exibe assim. Swagger, `openapi.json` e `schema.d.ts` mostram exemplos enganosos para quem integrar.

**Correção:** descrição "pontos de priority_score (0-100)" e exemplos em pontos (ex.: `-9.6`, `+7.2`); alinhar `EXAMPLE_SCORED_DEAL`.

### 5. Médio · Limiar 138 / faixa "esfriando" replicados em três camadas

`solution/pipeline/src/lead_scorer/scoring/weights.py:18,36-37` · `solution/api/src/api/settings.py:14-16` · `solution/web/src/lib/reasons.ts:52-54` · `solution/web/src/lib/format.ts:42`

`zombie_days=138`, `late_action_days=100`, `COOLING_MIN_DAYS=101`, `ZOMBIE_DAYS`, `COOLING_DAYS=100` e `STALE_DAYS=100` (duplicado dentro do próprio web). A API já publica `zombie_threshold_days`/`cooling_min_days`, mas só `TeamPage` os usa; `QueuePage`/`DealRow` usam a constante local. Cenário: retreinar com ciclo máximo 150 → pipeline emite `ZOMBIE_RISK` em 150, API e UI seguem dividindo filas em 138.

**Correção:** publicar `ZOMBIE_DAYS`/`COOLING_MIN_DAYS` no pacote `lead_scorer_contracts` (fonte única para pipeline e API) e no `/meta`; web lê do payload e remove `STALE_DAYS`.

### 6. Médio · Recomputação da linhagem do gold em cada `count()`

`solution/pipeline/src/lead_scorer/data/gold.py:302,333,400-403,474-482`

`build_opportunity_features` conta o frame três vezes e `write_gold` faz `df.count()` **depois** do `write` sem `cache()`: cada ação reexecuta os seis `_join_dim` + cross joins. Não é bug de resultado, mas dobra/triplica o tempo do job e esconde o custo real de cada asserção.

**Correção:** `features.cache()` antes de `_assert_features_contract` (e `unpersist` ao final), ou obter as contagens lendo o parquet recém-escrito.

### 7. Baixo · Limiar de sobrecarga e mediana do time em bases diferentes

`solution/pipeline/src/lead_scorer/scoring/score.py:98-110`

`_overload_thr` é o percentil 75 de `open_deals_agent` **por deal** (`df.agg`), enquanto `_team_median_load` é por agente (`load_by_agent`). Um agente com muitos deals puxa o próprio limiar para cima; a docstring diz só "batch's 75th percentile".

**Correção:** calcular ambos sobre `load_by_agent` e dizer na docstring que a base é "por agente".

### 8. Baixo · Hooks com caminhos e checagens desatualizados

`.claude/hooks/session_start.py:52-59` · `.claude/hooks/guard_paths.py:35` · `.claude/hooks/guard_leakage.py:4`

Loop morto `for svc in (...): pass`; checagem de `solution/pyproject.toml` (não existe — layout é por subprojeto), então toda sessão imprime "projeto não iniciado"; mensagem aponta `solution/src/lead_scorer/data/clean.py` (caminho real: `solution/pipeline/src/...`); docstring cita `solution/src or solution/app`. Guardrails são parte da entrega ("hooks versionados"), então a imprecisão pesa.

**Correção:** iterar os quatro `pyproject.toml` reais, remover o loop e corrigir os caminhos.

### 9. Baixo · Imports não usados mantidos via `__all__`

`solution/api/src/api/routers/meta.py:10,14` · `solution/api/src/api/routers/feedback.py:10,74`

`list_as_of_partitions`/`read_model_version` e `repository` entram no `__all__` de um módulo de router só para o ruff não reclamar. Confunde quem procura quem usa o repositório.

**Correção:** remover os imports e os `__all__`.

### 10. Baixo · Leitura de artefato sem tratamento cai fora do envelope de erro

`solution/api/src/api/routers/model.py:57` · `solution/api/src/api/errors.py:110`

`json.loads(feature_list.json)` sem `try` → 500 genérico (fora de `{"error": ...}`) se o arquivo estiver corrompido, enquanto `metrics.json` na mesma função é tratado. `str(exc.detail)` assume string; `HTTPException.detail` pode ser dict.

**Correção:** mesmo `try/except json.JSONDecodeError` do `metrics.json`; `detail if isinstance(detail, str) else json.dumps(detail)`.

### 11. Baixo · Web reescreve valores do payload

`solution/web/src/lib/reasons.ts:26-28`

`asContext` força `direction='i'` e `weight=0` para os códigos de contexto, sobrescrevendo o que o pipeline enviou. Se uma versão futura der peso a `SECTOR_FIT`, a UI esconde silenciosamente — viola "web só apresenta".

**Correção:** agrupar por código sem alterar campos; se quiser proteção, mostrar aviso quando `CONTEXT_CODES` vier com peso ≠ 0.

### 12. Sugestão · Pequenos agrupados

- `gold.py:_join_dim` (linha 297) descarta `_wins_account` que `score.py:_account_wins` (linhas 92-95, 131) volta a juntar — manter a coluna evita um join.
- `ml/frame.py:44-48`: `me <= previous_month_end(cut)` é redundante com `if me >= cut: break`.
- `ml/pipeline.py:34` vs `:44`: dois defaults de `regParam` (0.01 e 0.1); usar `LR_PARAMS` como único default.
- `contracts.py:15` `SCHEMA_VERSION="1.1.0"` vs exemplo `"1.0.0"` em `api/schemas.py:68` e versão 1.0.0 do pacote.
- `Makefile:38`: `shared` não roda `ruff format --check` como os outros; `JAVA_HOME` via `/usr/libexec/java_home` é só macOS (o fallback funciona, mas documentar).
- `jobs/build_features.py:249`, `jobs/score.py:235`, `jobs/train.py:313`: `__import__("sys")` → `import sys`.
- `.claude/hooks/stop_quality_gate.py:46`: timeout de 240 s para a suíte Spark (63 s aqui) pode estourar em máquina lenta e bloquear o Stop sem diagnóstico.

## Veredito

**Aprovar com ajustes.** Nenhum achado bloqueia o pipeline ou a API: sem leakage, sem relógio real, joins protegidos por asserções de contagem, contrato validado nas duas pontas, suítes verdes. Os dois achados de nível alto estão no web e produzem números errados na visão de manager/time (filas e top 10 de parados) — corrigir antes do PR, junto com `make lint` (3), o contrato de `weight` (4) e a fonte única do limiar 138 (5). O restante é manutenção.

## O que está bem feito (para o README)

1. **Anti-leakage por construção, não por convenção:** gold separa fisicamente `opportunity_features`, `history_stats` e `labels`; `OUTCOME_COLUMNS` + `LeakageError`, `FORBIDDEN` verificado na importação de `ml/features.py`, único gate temporal em `compute_history(as_of)`, e hooks que bloqueiam `close_value`/`today()`/`randomSplit` em código de solução.
2. **Regras como expressões Spark puras:** cada regra é uma função `Column -> Column` sem UDF, com `Weights` frozen e validado (`w_p + w_v + w_u = 100`), unidade única para `Reason.weight` e ordenação determinística (`array_sort` com desempate por ordinal).
3. **Contrato único do parquet ao navegador:** `ScoredDeal` num pacote compartilhado (ADR 0007), validado pelo job `score` lendo de volta o parquet escrito e pela API no boot; tipos TS gerados do OpenAPI e usados de fato (`openapi-fetch`).
4. **Falha ruidosa em todo lugar certo:** CSV com `StructType` + `FAILFAST`, checksums SHA256 do raw, `RowLossError` nos joins do silver, contagens de referência do snapshot, `_assert_features_contract` (linhas e ids únicos), erros da API sempre em `{"error": {code, message, hint}}` com o comando para resolver.
5. **Reprodutibilidade operacional:** `uv.lock` por projeto, manifests com git sha, checksums, parâmetros e PSI, seeds fixas, `as_of` propagado em todos os jobs, imagens multi-stage não-root com healthcheck e `cap_drop: ALL`.
