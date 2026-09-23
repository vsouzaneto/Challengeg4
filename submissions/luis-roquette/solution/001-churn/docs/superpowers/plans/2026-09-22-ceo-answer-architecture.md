# CEO Answer Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** responder à pergunta do CEO com uma conclusão canônica, rastreável e acionável, mesmo quando nenhum mecanismo de churn for sustentado.

**Architecture:** o pipeline calcula histórico, coortes e gates uma vez; `publish.py` constrói uma resposta canônica em cinco blocos. Relatório e dashboard consomem a mesma resposta, sem recalcular decisões.

**Tech Stack:** Python 3.12, pandas, NumPy, SciPy, statsmodels, pytest e Streamlit já instalados.

**Spec:** `submissions/luis-roquette/solution/001-churn/.specs/tasks/in-progress/implement-ceo-answer-architecture.feature.md`

## Global Constraints

- Não adicionar dependência, API paga, LLM, integração externa ou deploy.
- Preservar os cinco CSVs brutos, checksums e trabalho paralelo; artefatos são sempre regenerados.
- `strict` é a leitura executiva; `observed` é sensibilidade. Associação não vira causalidade.
- Inconclusão, baixa potência ou falha de ajuste não equivalem a afirmação rejeitada.
- Todo comando `Run:` deste plano é executado dentro do Codespace do repositório: primeiro `codespace-manager list`; depois `codespace-manager run <nome> -- 'cd <raiz-da-solucao> && <comando>'`. Não executar os comandos diretamente no Mac e não usar bypass.
- Agentes de steps não alteram o índice Git nem criam commits. O orquestrador faz commits somente após o teste/review do step sequencial ou a sincronização completa de um grupo paralelo.

## Review Focus

1. Evento inválido seguido de válido deve selecionar o primeiro terminal válido, sem descartar a conta.
2. Bootstrap por conta deve materializar ocorrências duplicadas do sorteio, preservando todos os meses/âncoras de cada ocorrência.
3. Ausência deve permanecer nula com causa; zero exige universo observado e vazio.
4. Todos os mecanismos inconclusivos devem conservar fatos, esvaziar a fila e produzir ações de validação.
5. Checksum válido não deve aceitar referência, tipo, ID, unidade ou schema semanticamente inválido.

## File Map

- Modify: `src/ravenstack_churn/config.py` — parâmetros versionados.
- Modify: `src/ravenstack_churn/panel.py`, `quality.py`, `diagnosis.py`, `cli.py`, `publish.py` — seleção, evidências, gates e publicação.
- Modify: `app.py`, `README.md`, `Makefile` — apresentação, documentação e gate.
- Test: `tests/test_panel.py`, `test_quality.py`, `test_diagnosis.py`, `test_publish.py`, `test_app.py`, `conftest.py`.
- Create by reproduction: cinco artefatos novos; regenerar os dez existentes sem edição manual.

---

### Task 1: Unificar seleção terminal, QA e MRR

**Files:**

- Modify: `src/ravenstack_churn/config.py`
- Modify: `src/ravenstack_churn/panel.py`
- Modify: `src/ravenstack_churn/quality.py`
- Modify: `src/ravenstack_churn/publish.py`
- Test: `tests/test_panel.py`, `tests/test_quality.py`

**Interfaces:**

- Produces: `select_first_terminal_events(accounts, churn_events, observation_end) -> tuple[pd.DataFrame, pd.DataFrame]`.
- Produces: `first_terminal_churn(churn_events, accounts, observation_end) -> pd.Series`.
- Preserves: `mrr_lost_at_churn(subscriptions, terminal_churn) -> pd.Series`, com dtype nullable.

- [x] **Step 1: escrever os testes RED da seleção**

```python
def test_first_terminal_churn_uses_valid_event_after_invalid_event(): ...
def test_missing_reactivation_flag_is_not_terminal(): ...
def test_mrr_unknown_is_not_zero(): ...
```

- [x] **Step 2: confirmar RED**

Run: `.venv/bin/python -m pytest -q tests/test_panel.py tests/test_quality.py`

Expected: FAIL nos novos casos porque a implementação atual deduplica antes de validar e não possui a nova assinatura.

- [x] **Step 3: implementar o contrato mínimo**

```python
def select_first_terminal_events(
    accounts: pd.DataFrame,
    churn_events: pd.DataFrame,
    observation_end: pd.Timestamp,
) -> tuple[pd.DataFrame, pd.DataFrame]: ...
```

Migrar todos os callers; QA usa a mesma seleção e mantém contagens das linhas brutas excluídas.

- [x] **Step 4: confirmar GREEN e callers únicos**

Run: `.venv/bin/python -m pytest -q tests/test_panel.py tests/test_quality.py`

Run: `rg -n "first_terminal_churn|select_first_terminal_events|mrr_lost_at_churn" src tests`

Expected: PASS; nenhum consumidor mantém a política antiga.

- [x] **Step 5: entregar o diff; o orquestrador registra o checkpoint**

```bash
git add src/ravenstack_churn/config.py src/ravenstack_churn/panel.py src/ravenstack_churn/quality.py src/ravenstack_churn/publish.py tests/test_panel.py tests/test_quality.py
git commit -m "refactor(churn): unify terminal event policy"
```

O agente não executa esses comandos; informa arquivos e testes ao orquestrador, que revisa e então os executa.

### Task 2: Calcular histórico, segmentos e motivos

**Files:**

- Modify: `src/ravenstack_churn/diagnosis.py`
- Test: `tests/test_diagnosis.py`

**Interfaces:**

- Produces: `build_monthly_churn(tables, terminal_events) -> pd.DataFrame`.
- Produces: `build_reason_distribution(tables, terminal_events) -> pd.DataFrame`.
- Consumed by: Task 4; Task 5 serializa sem recalcular.

- [x] **Step 1: escrever testes RED com resultados calculáveis à mão**

```python
def test_monthly_churn_uses_registered_at_start_denominator(): ...
def test_period_bootstrap_counts_duplicate_account_draws(): ...
def test_segment_comparator_is_disjoint_complement(): ...
def test_reason_distribution_uses_first_valid_event_in_window(): ...
```

- [x] **Step 2: confirmar RED**

Run: `.venv/bin/python -m pytest -q tests/test_diagnosis.py -k "monthly_churn or period_bootstrap or segment_comparator or reason_distribution"`

Expected: FAIL porque as funções ainda não existem.

- [x] **Step 3: implementar histórico e motivos**

```python
def build_monthly_churn(
    tables: dict[str, pd.DataFrame], terminal_events: pd.DataFrame
) -> pd.DataFrame: ...

def build_reason_distribution(
    tables: dict[str, pd.DataFrame], terminal_events: pd.DataFrame
) -> pd.DataFrame: ...
```

Wilson vale por mês; contrastes repetidos usam bootstrap clusterizado por conta, com identificador de ocorrência do sorteio.

- [x] **Step 4: confirmar GREEN e determinismo**

Run: `.venv/bin/python -m pytest -q tests/test_diagnosis.py`

Expected: PASS duas vezes com seed 42 e schemas presentes mesmo sem linhas.

- [x] **Step 5: entregar o diff sem commit**

Informar arquivos, testes e limitações ao orquestrador; aguardar o Step 3. Não executar `git add` ou `git commit` durante o grupo paralelo.

### Task 3: Construir painel relativo ao churn

**Files:**

- Modify: `src/ravenstack_churn/panel.py`
- Test: `tests/test_panel.py`

**Interfaces:**

- Produces: `build_event_aligned_panel(tables, terminal_events, chronology) -> pd.DataFrame`.
- Row key: `account_id/anchor_date/cohort/relative_window_start/relative_window_end/chronology`.
- Consumed by: Task 4; nunca por scoring ou fila.

- [x] **Step 1: escrever testes RED de vazamento e elegibilidade**

```python
def test_event_aligned_features_stop_day_before_churn(): ...
def test_control_may_churn_after_outcome_horizon(): ...
def test_strict_and_observed_share_anchors_and_labels(): ...
```

- [ ] **Step 2: confirmar RED**

Run: `.venv/bin/python -m pytest -q tests/test_panel.py -k "event_aligned or control_may or share_anchors"`

Expected: FAIL porque o painel relativo ainda não existe.

Não executado: Luis determinou bypass do preflight durante a contenção do Codespace compartilhado. Os testes foram escritos antes da implementação, mas o estado RED não foi reivindicado retroativamente.

- [x] **Step 3: implementar reusando os helpers atuais**

```python
def build_event_aligned_panel(
    tables: dict[str, pd.DataFrame],
    terminal_events: pd.DataFrame,
    chronology: Literal["observed", "strict"],
) -> pd.DataFrame: ...
```

Não duplicar fórmulas de uso/suporte; extrair montagem de linha apenas se o produto cartesiano se tornar necessário.

- [x] **Step 4: confirmar GREEN e ausência de scoring**

Run: `.venv/bin/python -m pytest -q tests/test_panel.py`

Run: `rg -n "build_event_aligned_panel" src/ravenstack_churn`

Expected: PASS; somente `cli.py`/diagnóstico integram o painel.

- [x] **Step 5: entregar o diff; o orquestrador integra Tasks 2 e 3**

```bash
git add src/ravenstack_churn/diagnosis.py src/ravenstack_churn/panel.py tests/test_diagnosis.py tests/test_panel.py
git commit -m "feat(churn): add historical and event-aligned evidence"
```

Somente o orquestrador executa esses comandos depois que ambos os agentes terminarem, o diff integrado for revisado e os testes de Tasks 2/3 passarem juntos.

Adaptação autorizada: a execução deixou de ser paralela e passou a ser cronológica. A Task 2 foi commitada antes da Task 3; esta entrega usa commit local separado e permanece sem push.

### Task 4: Integrar métricas, gates e escada de evidência

**Files:**

- Modify: `src/ravenstack_churn/diagnosis.py`
- Modify: `src/ravenstack_churn/cli.py`
- Test: `tests/test_diagnosis.py`, `tests/test_publish.py`, `tests/conftest.py`

**Interfaces:**

- Produces: `build_event_cohort_metrics(event_panel) -> pd.DataFrame`.
- Produces: `build_mechanism_scorecard(findings, event_metrics, reasons) -> pd.DataFrame`.
- Extends: `evaluate_candidates(observed, strict, churn_events, event_metrics, reasons)`.

- [x] **Step 1: escrever testes RED dos gates e enums**

```python
def test_satisfaction_two_level_weighting_is_3_35(): ...
def test_wide_interval_remains_plausible_and_inconclusive(): ...
def test_all_gates_finish_before_queue_eligibility(): ...
def test_holm_can_only_restrict_acceptance(): ...
```

- [x] **Step 2: confirmar RED**

Run: `.venv/bin/python -m pytest -q tests/test_diagnosis.py tests/test_publish.py -k "3_35 or plausible or gates_finish or holm"`

Expected: FAIL porque scorecard, métricas e gates separados ainda não existem.

- [x] **Step 3: implementar os contratos mínimos**

```python
EVIDENCE_LEVELS = {
    "confirmed_fact", "supported_mechanism", "plausible_hypothesis", "rejected_claim"
}
GATE_STATES = {"pass", "fail", "unavailable"}
```

Calcular todos os gates antes de confiança, ranking e fila; `fail` de sustentação não cria `rejected_claim`.

- [x] **Step 4: confirmar GREEN e fechar a Fase 1** — gate integral retomado no Codespace sobre o SHA exato: duas suítes com `80 passed`, Ruff e formato verdes, duas reproduções completas e `artifact_sets=equal`.

Run: `.venv/bin/python -m pytest -q tests/test_diagnosis.py tests/test_panel.py tests/test_quality.py tests/test_publish.py`

Run no ambiente autorizado: `make reproduce && make check`

Expected: aplicação legada e dez arquivos atuais permanecem válidos; quatro DataFrames novos existem em memória, ainda não publicados.

- [x] **Step 5: entregar o diff; o orquestrador registra o checkpoint local**

```bash
git add src/ravenstack_churn/diagnosis.py src/ravenstack_churn/cli.py tests/test_diagnosis.py tests/test_publish.py tests/conftest.py
git commit -m "feat(churn): integrate evidence gates"
```

O agente não executa esses comandos; o orquestrador os executa após a revisão da Fase 1.

### Task 5: Publicar a resposta canônica

**Files:**

- Modify: `src/ravenstack_churn/publish.py`
- Modify: `src/ravenstack_churn/cli.py`
- Modify: `tests/conftest.py`
- Test: `tests/test_publish.py`
- Create by reproduction: cinco novos artefatos em `artifacts/`

**Interfaces:**

- Extends: `AnalysisResult` com quatro DataFrames obrigatórios.
- Produces: `_build_ceo_answer(result) -> dict[str, object]`.
- Changes: `_build_report(..., answer) -> str`.
- Publishes: 14 payloads + `run_manifest.json`.

- [x] **Step 1: escrever testes RED do contrato e da integridade**

```python
def test_ceo_answer_and_report_share_claim_ids_and_values(): ...
def test_rehashed_invalid_reference_is_rejected(): ...
def test_all_inconclusive_keeps_facts_and_empty_queue(): ...
def test_analysis_id_is_stable_and_non_recursive(): ...
```

- [x] **Step 2: confirmar RED**

Run: `.venv/bin/python -m pytest -q tests/test_publish.py`

Expected: FAIL nos novos testes porque os cinco payloads e a validação semântica não existem.

- [x] **Step 3: implementar escrita e validação como migração indivisível**

```python
def _build_ceo_answer(result: AnalysisResult) -> dict[str, object]: ...
def _build_report(
    result: AnalysisResult,
    queue: pd.DataFrame,
    watchlist: pd.DataFrame,
    answer: dict[str, object],
) -> str: ...
```

Serializar tabelas primeiro, calcular `analysis_id`, construir resposta uma vez, escrever manifesto por último e validar tipos, IDs, refs, unidades e finitude.

- [x] **Step 4: confirmar GREEN e reprodução** — 14 payloads mais manifesto regenerados, validados e reproduzidos deterministicamente; artefatos finais publicados no commit `e9627ea`.

Run: `.venv/bin/python -m pytest -q tests/test_publish.py`

Run no ambiente autorizado: `make reproduce`

Expected: 15 arquivos totais; duas reproduções equivalentes; nenhum NaN/Infinity em JSON.

- [x] **Step 5: entregar o diff; o orquestrador registra o checkpoint local**

```bash
git add src/ravenstack_churn/publish.py src/ravenstack_churn/cli.py tests/conftest.py tests/test_publish.py artifacts
git commit -m "feat(churn): publish canonical CEO answer"
```

O agente não executa esses comandos; o orquestrador os executa após validar o contrato indivisível.

### Task 6: Renderizar a mesma resposta no dashboard

**Files:**

- Modify: `app.py`
- Test: `tests/test_app.py`

**Interfaces:**

- Consumes: `ceo_answer.json` e quatro tabelas somente após `validate_artifact_set`.
- Produces: apresentação; nenhuma função analítica ou decisão nova.

- [x] **Step 1: escrever testes RED de apresentação**

```python
def test_dashboard_starts_with_five_canonical_blocks(): ...
def test_dashboard_never_recomputes_analysis(): ...
def test_invalid_artifact_set_blocks_decision_view(): ...
```

- [x] **Step 2: confirmar RED**

Run: `.venv/bin/python -m pytest -q tests/test_app.py`

Expected: FAIL porque a abertura ainda não consome `ceo_answer.json`.

- [x] **Step 3: implementar renderização mínima**

Reusar `section_heading`, `format_display_frame` e `render_table`; remover narrativa duplicada e tratar `flat`, `insufficient`, nulo e watchlist vazia.

- [x] **Step 4: confirmar GREEN e conteúdo renderizado** — AppTest incluído na suíte de `80 passed`; dashboard inspecionado ao vivo em desktop e viewport móvel de 390×844, com os cinco blocos, abas e conteúdo canônico coerentes.

Run: `.venv/bin/python -m pytest -q tests/test_app.py`

Run: `make app`

Expected: cinco blocos aparecem antes da metodologia; desktop/mobile mostram os mesmos IDs/valores do JSON.

- [x] **Step 5: entregar o diff sem commit**

Informar arquivos, testes e evidência renderizada ao orquestrador; aguardar o Step 7. Não executar `git add` ou `git commit` durante o grupo paralelo.

### Task 7: Documentar e fechar o gate integrado

**Files:**

- Modify: `README.md`
- Modify: `Makefile`
- Test: `tests/test_publish.py`

**Interfaces:**

- Preserves: `setup`, `test`, `reproduce`, `app`, `check`.
- Guarantees: falha de reprodução impede `compare`; sucesso alcança `compare`.

- [x] **Step 1: escrever teste RED do fail-fast**

```python
def test_check_stops_before_compare_when_reproduce_fails(): ...
def test_check_reaches_compare_when_reproduce_succeeds(): ...
```

- [x] **Step 2: confirmar RED**

Run: `.venv/bin/python -m pytest -q tests/test_publish.py -k "check_stops or check_reaches"`

Expected: primeiro caso FAIL porque a receita atual usa linhas shell separadas.

- [x] **Step 3: aplicar correção mínima e documentar o resultado efetivo**

Encadear a reprodução e o compare na mesma receita fail-fast, preservando trap/limpeza. Atualizar README a partir do `ceo_answer.json` validado, sem fixar números exploratórios divergentes.

- [x] **Step 4: executar o gate final no diff exato** — `make reproduce` + `make check` concluídos no Codespace: duas suítes com `80 passed`, Ruff verde, `18 files already formatted` e `artifact_sets=equal`.

Run no ambiente autorizado: `make check`

Run: `git diff --check`

Expected: lint, formato, suíte, reprodução e comparação verdes; 14 payloads + manifesto coerentes.

- [x] **Step 5: entregar o diff; o orquestrador fecha a Fase 2** — resposta canônica revisada contra a pergunta do CEO, dashboard desktop/mobile inspecionado e branch remota atualizada. PR/merge ficam fora deste gate até decisão explícita de entrega.

```bash
git add app.py README.md Makefile tests/test_app.py tests/test_publish.py
git commit -m "feat(churn): deliver canonical CEO answer"
```

Somente o orquestrador executa esses comandos depois que Steps 6/7 terminarem, `make check` passar e relatório/dashboard forem revisados contra CK-1–CK-12/HR-1–HR-3. Registrar no diário decisões, deltas, comandos, resultados e limites remanescentes.
