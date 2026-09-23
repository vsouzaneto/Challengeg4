# Social Media Decision Cockpit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Elevar para pelo menos `9,5/10` a capacidade média do cockpit de responder às três perguntas do Head de Marketing e à pergunta obrigatória sobre audiência, acrescentando profundidade multivariada, decisão financeira condicional e estratégia executável de 30 dias sem inventar causalidade ou ROI.

**Architecture:** O processo local existente continua com Streamlit, funções puras Pandas e SQLite padrão. `analysis.py` recebe ranking contextual, cenário financeiro puro e estratégia relativa de 30 dias; o mesmo resultado determinístico alimenta UI e exports. Nenhum serviço, dependência ou segundo motor é criado.

**Tech Stack:** Python 3.14.2, Streamlit 1.64.0, Pandas 2.3.3, stdlib `sqlite3`, `csv`, `hashlib`, `html`, `json`, `unittest`.

**Spec:** [`SPEC.md`](./SPEC.md)

## Adendo de status da implementação — 22/09/2026

- Tasks 1–10 e a execução técnica da Task 11 foram implementadas e validadas; os checkboxes abaixo registram o estado executado sem apagar o plano original. A nota humana final e HR-01 permanecem pendentes.
- A comparação de patrocínio controla também `calendar_month`; a frequência usa somente semanas ISO completas dentro do mesmo mês/contexto. O histórico CSV conserva proveniência por evento; a barreira final `export_field` cobre qualquer célula extensa antes de `analysis_field` e `history_field`.
- Refinamento publicado localmente em `METHOD_VERSION = "2.5.0"`: 146 testes catalogados, gate focal anterior **45/45** e matriz executiva ampliada para **20/20** na auditoria final. O CSV contém seis recomendações e 6.830 registros. Artefatos correntes: `evidence.csv` SHA-256 `e982cd2fcc346951d4c6ab5d9a3af4443858548a1786fe0424d4f71d84c2f30a` e `analysis.md` SHA-256 `f2e8f4929bf1bbe9e8e7395f9ab5e7b09f093919a6cfe0af364710fb0b65db54`.
- A avaliação preliminar da IA é `9,62/10`, sem dimensão abaixo de `9,5`; a nota final permanece `PENDING` até leitura humana, sem transformar 20/20 técnico em aprovação subjetiva automática.
- **HR-01 continua pendente**; push, PR, merge e deploy continuam não autorizados. A branch atual difere da branch exigida e só será reconciliada no gate de publicação.

## Global Constraints

- All deliverables live under `submissions/luis-roquette/`; `.specs/`, `.claude/`, datasets, virtual environments and SQLite files stay local.
- Use exactly `streamlit==1.64.0` and `pandas==2.3.3`; add no runtime dependency unless a measured blocker is recorded in the diary.
- Derive `ERv = 100 × (likes + shares + comments_count) / views`; never treat `engagement_rate` as a source column.
- Keep sponsorship claims observational; never invent ROI, unique reach, causality, audience percentages or content-duration units.
- Keep observed evidence and manually entered financial scenarios separate in data structures, labels, exports and persistence; a scenario never becomes historical evidence.
- A contextual winner requires the exact sample, stability, materiality and strength gates in the SPEC; absence of a winner is a valid definitive answer.
- Preserve the current mix outside explicit tests; the 30-day strategy is a decision program and never schedules, publishes, hires or spends automatically.
- Bind Streamlit to `127.0.0.1`; use no account, cloud service, external API, LLM call, automatic publication or investment action.
- Persist metadata, baselines, decisions and outcomes only; never persist raw CSV rows, descriptions, comments, URLs or secrets.
- An invalid import fails atomically with `{row, column, problem, expected}` diagnostics and leaves the previous valid analysis active.
- Gate histórico satisfeito: a revisão humana da SPEC foi registrada antes da implementação. O plano nunca autorizou, e ainda não autoriza, push, PR ou deployment.

## Review Focus

- CSV with valid schema but a single platform must load and report actual coverage instead of requiring the canonical five platforms; pinned in Task 1.
- Repeated posts from one creator must not manufacture benchmark confidence or false post outliers; pinned in Task 2.
- Sponsored and organic cohorts with different composition must remain stratified and show uncovered groups; pinned in Task 2.
- Streamlit reruns must not duplicate a decision or display success after a failed transaction; pinned in Tasks 4 and 5.
- A later 30-day snapshot must not look better than a 7-day baseline because of raw volume alone; pinned in Task 4.
- A large but unstable multivariate delta must not become a winner; pinned in Task 7 with alternating monthly signs and concentrated creators.
- A tiny stable delta below practical materiality must remain “sem vencedor sustentado”; pinned in Task 7.
- Financial inputs with missing/negative values, zero conversion value or rates outside `[0,1]` must abstain without mutating evidence; pinned in Task 8.
- Filters and Streamlit reruns must not change the full-history executive ranking or duplicate its 30-day plan; pinned in Task 10.
- HTML/Markdown/CSV must agree on verdict, strength, coverage and decision-change trigger while escaping adversarial labels; pinned in Tasks 9–10.

## File Map

| Path | Responsibility |
|---|---|
| `analysis.py` | CSV boundary, formulas, cohorts, multivariate driver ranking, sponsorship/scenario math, 30-day strategy, recommendations, exports and CLI. No Streamlit or SQLite imports. |
| `storage.py` | SQLite schema, idempotent import/decision/outcome writes and durable reads. No Pandas or Streamlit imports. |
| `app.py` | Streamlit composition only: upload, filters, drill-down, decision forms, history and downloads. |
| `requirements.txt` | Two direct runtime pins: Streamlit and Pandas. |
| `tests/helpers.py` | Small deterministic DataFrame/CSV builders shared by tests. |
| `tests/test_analysis.py` | Validation, metrics, benchmarks, contextual drivers, sponsorship/scenario math, 30-day strategy, recommendation and priority contracts. |
| `tests/test_exports.py` | HTML/CSV safety, consistency and CLI contracts. |
| `tests/test_storage.py` | Schema, transactions, idempotency, revisions and temporal comparison contracts. |
| `tests/test_app.py` | Streamlit `AppTest` smoke and state/error behavior. |
| `analysis.md` | Standalone findings and strategy backed by evidence IDs. |
| `evidence.csv` | Generated evidence/decision export, not the raw dataset. |
| `solution/004-social/README.md` | Technical setup, commands, data acquisition, five-minute demo and limitations. |
| `submissions/luis-roquette/README.md` | Submission entrypoint following the repository template: summary, findings, recommendations, limitations and process evidence. |

## Acceptance Coverage

| SPEC criteria | Owning task | Primary proof |
|---|---|---|
| CK-01–02 | Task 1 | Parser/metric unit tests plus canonical-file reconciliation. |
| CK-03–07 | Task 2 | Cohort, sponsorship, priority and action regression tests. |
| CK-10 analytical/export portion; HR-02 | Task 3 | Safe export tests, deterministic CLI, `analysis.md` and `evidence.csv`. |
| CK-08–09 | Task 4 | SQLite transaction, idempotency, revision and temporal-comparison tests. |
| CK-10 UI portion; CK-11 | Task 5 | Streamlit `AppTest` plus real-browser state and download flow. |
| HR-01, HR-03–04; all final CK/HR | Task 6 | Timed human scenario, evidence matrix, clean setup and Git-scope audit. |
| Refinamento: driver multivariado e estabilidade | Task 7 | Contextos orgânicos, pares mensais, materialidade, força e abstenção determinística. |
| Refinamento: decisão financeira condicional | Task 8 | Fórmulas puras, validação de premissas e prova de não persistência. |
| Refinamento: respostas e estratégia executiva | Tasks 9–10 | Três respostas completas, quatro semanas e paridade entre UI/HTML/Markdown/CSV. |
| Refinamento: gate interno ≥9,5 | Task 11 | Matriz 15/15, reconciliação independente, medição e nota humana documentada. |

## Evaluator Coverage

| Repository requirement | Plan coverage | Final evidence |
|---|---|---|
| Performance analysis: engagement by platform, content, category and creator size; sponsorship; audience; failures | Tasks 1–3 | `analysis.md` claims linked to generated `evidence.csv`; unavailable financial cost is stated, never fabricated. |
| Recommended strategy: effort, frequency hypothesis, creator band, sponsorship policy, stop list and quick wins | Tasks 2–3 | Deterministic, prioritized actions with owner, window, metric and review criterion. |
| Differentiator that supports recurring decisions | Tasks 4–5 | Local cockpit, evidence drill-down, durable human decision and later comparable outcome. |
| Fair organic-versus-sponsored comparison and non-superficial analysis | Task 2 | Controlled strata, overlap/coverage, creator-aware evidence strength and abstention regressions. |
| Executive clarity and action within five minutes | Tasks 3, 5–6 | Priorities-first report/UI, one-page summary and timed human scenario. |
| Mandatory process log showing tools, decomposition, AI errors, human judgment and iterations | Every task; final assembly in Task 6 | Narrative diary, framework spike, Git history and linked visual evidence. |
| Submission format and PR rules | Task 6 | Root template README, technical README, setup, allowed paths, target branch and exact PR title. |

## Verified Stack Baseline

Pre-plan verification on 21/09/2026 used the reproduced isolated environment:

- Python 3.14.2, Streamlit 1.64.0, Pandas 2.3.3 and SQLite 3.50.4 imported together; `python -m pip check` returned no broken requirements.
- `streamlit.testing.v1.AppTest` and `FileUploader.set_value` exist in the pinned Streamlit installation.
- The 52,214-row CSV loaded with Pandas in 0.17 s; derivation plus a representative four-key groupby took 0.01 s.
- The probe completed in 0.65 s wall time, about 218 MB maximum resident set size and zero swap.
- This proves stack compatibility and baseline capacity, not final-engine performance. Tasks 1, 3 and 6 still measure the exact validation, cohort, export and UI paths before acceptance.

---

### Task 1: Establish the CSV boundary and metric contract

**Estimated active time:** 45 minutes.

**Files:**
- Create: `submissions/luis-roquette/solution/004-social/requirements.txt`
- Create: `submissions/luis-roquette/solution/004-social/analysis.py`
- Create: `submissions/luis-roquette/solution/004-social/tests/__init__.py`
- Create: `submissions/luis-roquette/solution/004-social/tests/helpers.py`
- Create: `submissions/luis-roquette/solution/004-social/tests/test_analysis.py`
- Modify: `submissions/luis-roquette/process-log/004-social.md`

**Interfaces:**
- Consumes: raw CSV `bytes` from an upload or CLI path.
- Produces: `load_csv(raw: bytes) -> tuple[pd.DataFrame | None, list[dict[str, object]]]`, `derive_metrics(df: pd.DataFrame) -> pd.DataFrame`, `follower_band(followers: int) -> str`.

- [x] **Step 1: Pin the reproduced direct dependencies**

Create `requirements.txt` exactly as:

```text
streamlit==1.64.0
pandas==2.3.3
```

- [x] **Step 2: Write fixture builders with canonical columns**

Create `tests/helpers.py` with `make_post(**overrides) -> dict[str, object]` and `csv_bytes(rows: list[dict[str, object]]) -> bytes`. `make_post` supplies all 16 required fields from the SPEC, uses ISO dates and defaults to one valid organic Instagram video row. `csv_bytes` uses `csv.DictWriter` and UTF-8.

- [x] **Step 3: Write failing boundary tests**

Create a `unittest.TestCase` class so stdlib discovery collects every test:

```python
class CsvBoundaryTests(unittest.TestCase):
    def test_load_csv_accepts_valid_single_platform_subset(self):
        frame, errors = load_csv(csv_bytes([make_post(platform="Instagram")]))
        self.assertEqual(errors, [])
        self.assertEqual(frame["platform"].unique().tolist(), ["Instagram"])

    def test_load_csv_reports_missing_required_column_without_partial_frame(self):
        row = make_post()
        del row["views"]
        frame, errors = load_csv(csv_bytes([row]))
        self.assertIsNone(frame)
        self.assertEqual(errors[0]["column"], "views")

    def test_load_csv_reports_negative_nonfinite_and_duplicate_identity(self):
        invalid = [make_post(id="1", content_id="a", views=-1), make_post(id="1", content_id="b", views="NaN")]
        frame, errors = load_csv(csv_bytes(invalid))
        self.assertIsNone(frame)
        self.assertEqual({error["column"] for error in errors}, {"id", "views"})

    def test_load_csv_accepts_zero_metrics_and_utf8_bom(self):
        raw = b"\xef\xbb\xbf" + csv_bytes([make_post(views=0, likes=0, shares=0, comments_count=0)])
        frame, errors = load_csv(raw)
        self.assertEqual(errors, [])
        self.assertEqual(int(frame.iloc[0]["views"]), 0)

    def test_load_csv_rejects_over_fifty_mib_before_parse(self):
        frame, errors = load_csv(b"x" * (50 * 1024 * 1024 + 1))
        self.assertIsNone(frame)
        self.assertEqual(errors[0]["problem"], "file_too_large")

    def test_load_csv_rejects_mixed_timezone_semantics(self):
        raw = csv_bytes([
            make_post(id="1", content_id="a", post_date="2025-01-01T00:00:00"),
            make_post(id="2", content_id="b", post_date="2025-01-02T00:00:00Z"),
        ])
        frame, errors = load_csv(raw)
        self.assertIsNone(frame)
        self.assertEqual(errors[0]["column"], "post_date")

    def test_load_csv_rejects_empty_and_malformed_bytes(self):
        for raw in (b"", b'"unterminated'):
            with self.subTest(raw=raw):
                frame, errors = load_csv(raw)
                self.assertIsNone(frame)
                self.assertTrue(errors)

    def test_load_csv_rejects_duplicate_headers_before_pandas_mangles_them(self):
        frame, errors = load_csv(b"id,id,platform\n1,2,Instagram\n")
        self.assertIsNone(frame)
        self.assertEqual(errors[0]["problem"], "duplicate_header")

    def test_derive_metrics_uses_views_denominator_and_preserves_undefined_rate(self):
        frame, _ = load_csv(csv_bytes([
            make_post(id="1", content_id="a", views=100, likes=5, shares=3, comments_count=2),
            make_post(id="2", content_id="b", views=0, likes=0, shares=0, comments_count=0),
        ]))
        result = derive_metrics(frame)
        self.assertEqual(int(result.iloc[0]["interactions"]), 10)
        self.assertEqual(float(result.iloc[0]["erv"]), 10.0)
        self.assertTrue(pd.isna(result.iloc[1]["erv"]))

    def test_follower_band_assigns_every_boundary_to_the_right_bucket(self):
        values = [0, 9_999, 10_000, 49_999, 50_000, 99_999, 100_000, 499_999, 500_000]
        actual = [follower_band(value) for value in values]
        self.assertEqual(actual, ["0–9,999", "0–9,999", "10,000–49,999", "10,000–49,999", "50,000–99,999", "50,000–99,999", "100,000–499,999", "100,000–499,999", "500,000+"])
```

- [x] **Step 4: Run the boundary tests and confirm red state**

Run:

```bash
python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_analysis.py' -v
```

Expected: import failure for `analysis`; no test may pass accidentally.

- [x] **Step 5: Implement strict parsing and diagnostics**

In `analysis.py`, define `REQUIRED_COLUMNS`, `OPTIONAL_COLUMNS`, `METRIC_COLUMNS` and `METHOD_VERSION = "2.4.0"`. `load_csv` must (o texto abaixo registra a intenção inicial; I38 substituiu `pandas.read_csv` por interpretação única com `csv.reader`, I42 tornou datas/números estritos e I45–I48 fecharam aritmética, fila, calendário e estados vazios):

```python
source_hash = hashlib.sha256(raw).hexdigest()
df = pd.read_csv(io.BytesIO(raw), encoding="utf-8-sig")
```

Then enforce unique headers, all required fields, integer/nonnegative metrics, `TRUE/FALSE` sponsorship, valid dates, unique `id` and unique `(platform, content_id)`. Return `(None, diagnostics)` if any row fails; otherwise return a normalized frame containing `source_hash` and `source_row_id`.

- [x] **Step 6: Implement formulas and creator bands**

`derive_metrics` copies the frame, sets `interactions`, `erv`, `erf` and never mutates the caller. Use these exact bands: `0–9,999`, `10,000–49,999`, `50,000–99,999`, `100,000–499,999`, `500,000+`.

- [x] **Step 7: Run Task 1 tests and full discovery**

Run:

```bash
python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_*.py' -v
git diff --check
```

Expected: all Task 1 tests pass; no whitespace errors.

- [x] **Step 8: Record evidence and commit**

Append the commands, results, elapsed time and any corrected assumption to the diary. Then:

```bash
git add -f submissions/luis-roquette/solution/004-social/requirements.txt submissions/luis-roquette/solution/004-social/analysis.py submissions/luis-roquette/solution/004-social/tests/__init__.py submissions/luis-roquette/solution/004-social/tests/helpers.py submissions/luis-roquette/solution/004-social/tests/test_analysis.py submissions/luis-roquette/process-log/004-social.md
git commit -m "feat(004): validate social dataset metrics"
```

---

### Task 2: Implement contextual evidence and deterministic actions

**Estimated active time:** 80 minutes.

**Files:**
- Modify: `submissions/luis-roquette/solution/004-social/analysis.py`
- Modify: `submissions/luis-roquette/solution/004-social/tests/helpers.py`
- Modify: `submissions/luis-roquette/solution/004-social/tests/test_analysis.py`
- Modify: `submissions/luis-roquette/process-log/004-social.md`

**Interfaces:**
- Consumes: the validated, type-normalized DataFrame returned by `load_csv` and `scope: dict[str, object]`; `analyze` calls `derive_metrics` exactly once internally.
- Produces: `analyze(df: pd.DataFrame, scope: dict[str, object], source_hash: str) -> dict[str, object]` with keys `source`, `scope`, `quality`, `metrics`, `cohorts`, `alerts`, `sponsorship`, `recommendations`, `row_references`.

- [x] **Step 1: Add deterministic cohort builders**

Extend `tests/helpers.py` with these exact helpers:

```python
make_cohort(creators=5, posts_per_creator=6, erv_values=None, **overrides) -> pd.DataFrame
frame_with_target(frame, erv: float) -> pd.DataFrame
default_scope() -> dict[str, object]
alert_for_target(result: dict[str, object]) -> dict[str, object]
make_audience_fallback_fixture() -> pd.DataFrame
expected_essential_context() -> dict[str, object]
make_unbalanced_sponsorship_fixture() -> pd.DataFrame
make_concentrated_cohort(total_posts: int) -> pd.DataFrame
first_strength(result: dict[str, object]) -> float
make_priority_fixture() -> pd.DataFrame
make_aggregate_effect_fixture() -> pd.DataFrame
make_conflicting_fixture() -> pd.DataFrame
make_strategy_fixture() -> pd.DataFrame
make_same_creator_leakage_fixture() -> pd.DataFrame
make_constant_iqr_fixture() -> pd.DataFrame
same_creator_source_ids(result: dict[str, object]) -> list[str]
```

Creator IDs, dates and metric values must be deterministic; never use random data. Define `ESSENTIAL_KEYS = ("platform", "content_type", "content_category", "follower_band", "is_sponsored")` in `test_analysis.py`.

- [x] **Step 2: Write failing benchmark and sponsorship tests**

Add `ContextEvidenceTests(unittest.TestCase)` with these executable assertions; helper arguments make every cohort deterministic:

```python
def test_post_alert_uses_post_distribution_not_creator_medians(self):
    frame = make_cohort(erv_values=[2, 4, 6, 8, 10, 12] * 5)
    ordinary = analyze(frame_with_target(frame, erv=8), default_scope(), "hash")
    extreme = analyze(frame_with_target(frame, erv=20), default_scope(), "hash")
    self.assertFalse(alert_for_target(ordinary)["is_outlier"])
    self.assertTrue(alert_for_target(extreme)["is_outlier"])

def test_benchmark_fallback_preserves_essential_controls(self):
    result = analyze(make_audience_fallback_fixture(), default_scope(), "hash")
    effective = alert_for_target(result)["benchmark"]["effective_context"]
    self.assertEqual({key: effective[key] for key in ESSENTIAL_KEYS}, expected_essential_context())
    self.assertIn("audience_location", alert_for_target(result)["benchmark"]["removed_controls"])

def test_benchmark_abstains_below_thirty_posts_or_five_creators(self):
    for frame in (make_cohort(creators=4, posts_per_creator=10), make_cohort(creators=5, posts_per_creator=5)):
        self.assertEqual(analyze(frame, default_scope(), "hash")["alerts"], [])

def test_sponsorship_reports_uncovered_strata(self):
    result = analyze(make_unbalanced_sponsorship_fixture(), default_scope(), "hash")
    self.assertGreater(len(result["sponsorship"]["uncovered_strata"]), 0)
    self.assertLess(result["sponsorship"]["coverage"], 1.0)

def test_evidence_strength_penalizes_creator_concentration(self):
    balanced = analyze(make_cohort(creators=10, posts_per_creator=10), default_scope(), "hash")
    concentrated = analyze(make_concentrated_cohort(total_posts=100), default_scope(), "hash")
    self.assertGreater(first_strength(balanced), first_strength(concentrated))

def test_benchmark_excludes_target_and_every_post_from_same_creator(self):
    result = analyze(make_same_creator_leakage_fixture(), default_scope(), "hash")
    refs = set(alert_for_target(result)["benchmark"]["source_row_ids"])
    self.assertTrue(refs.isdisjoint(same_creator_source_ids(result)))

def test_constant_iqr_reports_observation_without_strong_outlier(self):
    result = analyze(make_constant_iqr_fixture(), default_scope(), "hash")
    alert = alert_for_target(result)
    self.assertEqual(alert["benchmark"]["iqr"], 0)
    self.assertNotEqual(alert["strength_label"], "strong")
```

- [x] **Step 3: Run the new tests and confirm red state**

Run `python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_analysis.py' -v`. Expected: failure because `analyze` and cohort logic do not exist.

- [x] **Step 4: Implement benchmark ladders and evidence strength**

Implement the five fallback levels from the SPEC. Post alerts use post-level Q1/Q3/IQR after excluding the target and its creator. Use:

```python
strength = min(n_rate / 100, 1) * min(n_creators / 20, 1) * (1 - max_creator_post_share)
```

Return every attempted level, effective level, removed audience controls and abstention reason.

- [x] **Step 5: Implement sponsorship strata**

Group by platform, content type, category, follower band and selected period. Require 30 defined-rate posts and five creators per arm. Compute creator medians inside each arm, report overlap and coverage, and never discard an unmatched stratum silently.

- [x] **Step 6: Write failing priority and action tests**

Add these methods to the same `TestCase`:

```python
def test_priority_exposes_components_and_stable_tie_break(self):
    first = analyze(make_priority_fixture(), default_scope(), "hash")["recommendations"]
    second = analyze(make_priority_fixture(), default_scope(), "hash")["recommendations"]
    self.assertEqual(first, second)
    self.assertEqual(set(first[0]["priority_components"]), {"impact", "strength", "recency"})

def test_aggregate_recommendation_can_rank_without_post_outlier(self):
    result = analyze(make_aggregate_effect_fixture(), default_scope(), "hash")
    self.assertEqual(result["alerts"], [])
    self.assertEqual(result["recommendations"][0]["evidence_type"], "aggregate")

def test_weak_or_conflicting_evidence_yields_test_or_collect_action(self):
    result = analyze(make_conflicting_fixture(), default_scope(), "hash")
    self.assertIn(result["recommendations"][0]["action_type"], {"test", "collect"})

def test_recommendations_cover_topics_without_fabrication(self):
    result = analyze(make_strategy_fixture(), default_scope(), "hash")
    topics = {item["topic"] for item in result["recommendations"]}
    self.assertTrue(topics <= {"effort", "audience", "frequency", "sponsorship", "creator", "stop", "quick_win"})
    self.assertTrue(all(item["evidence_id"] for item in result["recommendations"]))
```

- [x] **Step 7: Implement priority and the action table**

Use platform-level P95 normalization, `impact = (N(views)+N(interactions)+N(followers))/3`, `recency = 2 ** (-age_days/7)` and `priority = 100 * impact * strength * recency`. Apply the SPEC's deterministic sign/eligibility-to-action mapping, deduplicate by context and return at most three context-distinct priorities.

- [x] **Step 8: Run Task 2 tests and commit**

Run full discovery and `git diff --check`; record actual results in the diary. Then:

```bash
git add -f submissions/luis-roquette/solution/004-social/analysis.py submissions/luis-roquette/solution/004-social/tests/helpers.py submissions/luis-roquette/solution/004-social/tests/test_analysis.py submissions/luis-roquette/process-log/004-social.md
git commit -m "feat(004): derive contextual social evidence"
```

---

### Task 3: Generate safe exports and the standalone analysis

**Estimated active time:** 55 minutes.

**Files:**
- Modify: `submissions/luis-roquette/solution/004-social/analysis.py`
- Create: `submissions/luis-roquette/solution/004-social/tests/test_exports.py`
- Create: `submissions/luis-roquette/solution/004-social/analysis.md`
- Create: `submissions/luis-roquette/solution/004-social/evidence.csv`
- Modify: `submissions/luis-roquette/process-log/004-social.md`

**Interfaces:**
- Consumes: final `AnalysisResult` dictionary and `list[dict[str, object]]` decisions.
- Produces: `export_evidence(result, decisions) -> bytes`, `executive_summary(result, decisions) -> str`, and CLI exit codes `0` success / `2` invalid input.

- [x] **Step 1: Write failing export and CLI tests**

At the top of `test_exports.py`, define deterministic test-only helpers `result_with_texts(texts)`, `parse_export(payload)`, `sample_result()`, `sample_decisions()` and `run_cli(path) -> tuple[int, bytes]`. `run_cli` uses `tempfile.TemporaryDirectory` and invokes `[sys.executable, str(APP_ROOT / "analysis.py"), str(path), "--evidence", str(output_csv), "--summary", str(output_html)]` through `subprocess.run(..., capture_output=True, check=False)`, returning `(returncode, output_csv.read_bytes())`. `valid_csv_path()` and `invalid_csv_path()` write fixtures inside the test's temporary directory. Then create `ExportTests(unittest.TestCase)`:

```python
def test_export_csv_keeps_numbers_numeric_and_neutralizes_formula_text(self):
    payload = export_evidence(result_with_texts(["=1+1", "+cmd", "-2+3", "@SUM(A1)", "\t=1"]), [])
    rows = list(csv.DictReader(io.StringIO(payload.decode("utf-8"))))
    self.assertTrue(all(row["text"].startswith("'") for row in rows if row["record_type"] == "evidence"))
    numeric = next(row for row in rows if row["record_type"] == "evidence" and row["metric_value"])
    self.assertEqual(float(numeric["metric_value"]), 10.0)

def test_export_rows_join_through_evidence_and_source_ids(self):
    rows = parse_export(export_evidence(sample_result(), sample_decisions()))
    evidence_ids = {row["evidence_id"] for row in rows if row["record_type"] == "evidence"}
    self.assertTrue(all(row["evidence_id"] in evidence_ids for row in rows if row["record_type"] in {"source_ref", "decision"}))

def test_executive_html_escapes_input_and_has_no_active_content(self):
    page = executive_summary(result_with_texts(["<script>alert(1)</script>"]), [])
    self.assertIn("&lt;script&gt;", page)
    self.assertNotIn("<script", page.lower())
    self.assertNotRegex(page, r"https?://")

def test_cli_is_deterministic_and_invalid_csv_returns_exit_two(self):
    first_code, first_bytes = run_cli(valid_csv_path())
    second_code, second_bytes = run_cli(valid_csv_path())
    invalid_code, _ = run_cli(invalid_csv_path())
    self.assertEqual((first_code, second_code), (0, 0))
    self.assertEqual(first_bytes, second_bytes)
    self.assertEqual(invalid_code, 2)
```

- [x] **Step 2: Run export tests and confirm red state**

Run `python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_exports.py' -v`. Expected: missing export functions.

- [x] **Step 3: Implement one shared export projection**

Create one internal `iter_export_rows(result, decisions)` generator. Both CSV and HTML read from the same result; neither recalculates analytics. HTML must use `html.escape`, inline print CSS and no JavaScript. CSV uses `record_type` values `summary`, `evidence`, `source_ref`, `decision`, `outcome`.

- [x] **Step 4: Implement the CLI contract**

Add `main(argv: list[str] | None = None) -> int` supporting:

```text
python3 submissions/luis-roquette/solution/004-social/analysis.py INPUT.csv --evidence evidence.csv --summary summary.html
```

Write through temporary files and `Path.replace` so a failed run cannot leave a half-written official export.

- [x] **Step 5: Run the real dataset and reconcile three numbers**

Execute the CLI against the downloaded Kaggle CSV outside the repository. Independently recompute one ERv aggregate, one eligible sponsorship comparison or documented insufficiency, and the top priority. Record source hash, method version, runtime and peak memory.

- [x] **Step 6: Write the standalone analysis and strategy**

Create `analysis.md` with priorities first, then platform/content/creator/audience/time findings, sponsorship, what underperforms, effort allocation, audience, frequency hypothesis, creator criteria, stop/review actions, quick wins and limitations. Every numerical claim cites an `evidence_id`; unavailable evidence yields a collection/test action.

- [x] **Step 7: Regenerate official evidence and commit**

Run export tests, full discovery and `git diff --check`. Regenerate `evidence.csv` from the final command, update the diary and commit:

```bash
git add -f submissions/luis-roquette/solution/004-social/analysis.py submissions/luis-roquette/solution/004-social/tests/test_exports.py submissions/luis-roquette/solution/004-social/analysis.md submissions/luis-roquette/solution/004-social/evidence.csv submissions/luis-roquette/process-log/004-social.md
git commit -m "feat(004): publish reproducible social analysis"
```

---

### Task 4: Persist decisions and comparable outcomes

**Estimated active time:** 50 minutes.

**Files:**
- Create: `submissions/luis-roquette/solution/004-social/storage.py`
- Create: `submissions/luis-roquette/solution/004-social/tests/test_storage.py`
- Modify: `submissions/luis-roquette/process-log/004-social.md`

**Interfaces:**
- Consumes: an open `sqlite3.Connection` and JSON-serializable event dictionaries.
- Produces: `initialize(conn)`, `record_import(conn, metadata) -> str`, `record_decision(conn, event) -> str`, `record_outcome(conn, event) -> str`, `list_decisions(conn) -> list[dict[str, object]]`.

- [x] **Step 1: Write failing schema and transaction tests**

In `test_storage.py`, define `import_event()`, `decision_event(**overrides)`, `revision_event(original_id)` and `expected_baseline()` as deterministic dictionary factories. Create `StorageTests(unittest.TestCase)` with `setUp` opening `sqlite3.connect(":memory:")`, calling `initialize`, then inserting the canonical import before decision tests:

```python
def test_initialize_enables_foreign_keys_and_creates_versioned_schema(self):
    initialize(self.conn)
    self.assertEqual(self.conn.execute("PRAGMA foreign_keys").fetchone()[0], 1)
    self.assertEqual(self.conn.execute("SELECT version FROM schema_version").fetchone()[0], 1)

def test_same_import_hash_and_event_id_are_idempotent(self):
    self.assertEqual(record_import(self.conn, import_event()), record_import(self.conn, import_event()))
    self.assertEqual(record_decision(self.conn, decision_event()), record_decision(self.conn, decision_event()))
    self.assertEqual(self.conn.execute("SELECT count(*) FROM decisions").fetchone()[0], 1)

def test_decision_revision_preserves_original_baseline(self):
    original = record_decision(self.conn, decision_event())
    revised = record_decision(self.conn, revision_event(original))
    self.assertNotEqual(original, revised)
    stored = next(item for item in list_decisions(self.conn) if item["decision_id"] == original)
    self.assertEqual(stored["baseline"], expected_baseline())

def test_failed_write_rolls_back_without_false_success(self):
    with self.assertRaises(sqlite3.IntegrityError):
        record_decision(self.conn, decision_event(source_hash="missing"))
    self.assertEqual(self.conn.execute("SELECT count(*) FROM decisions").fetchone()[0], 0)

def test_database_contains_no_raw_csv_or_source_text_fields(self):
    columns = {row[1] for table in ("imports", "decisions", "outcomes") for row in self.conn.execute(f"PRAGMA table_info({table})")}
    self.assertTrue({"csv_bytes", "content_description", "comments_text", "content_url"}.isdisjoint(columns))
```

- [x] **Step 2: Run storage tests and confirm red state**

Use an in-memory database and a temporary on-disk database. Expected: missing `storage` module.

- [x] **Step 3: Implement the minimal three-table schema**

Create `imports`, `decisions` and `outcomes` exactly as described in the SPEC. Enable foreign keys on every connection, use parameterized SQL and wrap each event in `with conn:`. Return the existing ID for repeated `source_hash` or `event_id`.

- [x] **Step 4: Write failing temporal-comparability tests**

Add cases for identical hash, overlapping dates, incompatible scope, method mismatch, insufficient samples, unknown execution date, equal 7-day windows and a 7-day versus 30-day comparison.

- [x] **Step 5: Implement outcome guards**

Only equal-duration/equal-coverage windows may compare raw volumes. For unequal windows, store rates/medians and per-day normalized volumes, label coverage mismatch and prohibit a `better/worse` status based only on raw volume. Acceptance remains distinct from execution.

- [x] **Step 6: Run storage/full tests and commit**

Run storage tests, full discovery and `git diff --check`; update the diary. Then:

```bash
git add -f submissions/luis-roquette/solution/004-social/storage.py submissions/luis-roquette/solution/004-social/tests/test_storage.py submissions/luis-roquette/process-log/004-social.md
git commit -m "feat(004): persist human social decisions"
```

---

### Task 5: Compose the Streamlit cockpit

**Estimated active time:** 80 minutes.

**Files:**
- Create: `submissions/luis-roquette/solution/004-social/app.py`
- Create: `submissions/luis-roquette/solution/004-social/tests/test_app.py`
- Modify: `submissions/luis-roquette/process-log/004-social.md`

**Interfaces:**
- Consumes: `load_csv`, `analyze`, export functions and storage functions from Tasks 1–4.
- Produces: `database_path() -> Path` plus one Streamlit page with upload, filters, priority overview, evidence drill-down, decision form, history and downloads. `database_path` reads `SOCIAL_COCKPIT_DB_PATH` only when explicitly set; otherwise it returns `~/.local/share/ai-master-challenge-004/cockpit.sqlite3`.

- [x] **Step 1: Write a failing import/smoke test**

Use `streamlit.testing.v1.AppTest`. In `setUp`, create a `TemporaryDirectory`, set `SOCIAL_COCKPIT_DB_PATH` to a file inside it and restore the environment in `tearDown`. Assert the initial render contains the product title, CSV uploader, source-state explanation and no exception.

- [x] **Step 2: Run the smoke test and confirm red state**

Run `python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_app.py' -v`. Expected: missing `app.py`.

- [x] **Step 3: Implement the no-data and valid-upload states**

Compose native Streamlit components only. Cache the active valid result in `st.session_state`; a rejected upload writes diagnostics but does not replace it. Show hash abbreviation, dataset reference date, selected period, coverage and limitation labels before charts.

- [x] **Step 4: Write failing interaction-state tests**

Add tests for invalid upload preserving the active analysis, empty filters, visible priority components, source-row drill-down and a decision form that emits one stable event UUID per submission.

- [x] **Step 5: Implement overview, drill-down and decisions**

Render at most three priorities, secondary rankings and tabular alternatives to every chart. Use one explicit `st.form` for decision writes. Show success only after `record_decision` returns and a read confirms the record. Preserve focusable labels and never rely on color alone.

- [x] **Step 6: Write and implement history/outcome/download tests**

Test history without a CSV, hash-required historical drill-down, pending outcome labels, weekly/monthly partial-window labels and matching download bytes. Then implement those UI states without a second calculation path.

- [x] **Step 7: Run app tests and a real browser flow**

Run:

```bash
python3 -m streamlit run submissions/luis-roquette/solution/004-social/app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

Verify upload, keyboard traversal, invalid-file recovery, filters, drill-down, accepted/edited/rejected decisions, rerun, restart, history and both downloads. Capture evidence only after the complete flow passes.

- [x] **Step 8: Run full tests and commit**

Update the diary with browser actions and effects. Run full discovery plus `git diff --check`, then:

```bash
git add -f submissions/luis-roquette/solution/004-social/app.py submissions/luis-roquette/solution/004-social/tests/test_app.py submissions/luis-roquette/process-log/004-social.md
git commit -m "feat(004): add local social decision cockpit"
```

---

### Task 6: Prove the acceptance contract and hand off

**Estimated active time:** 50 minutes. Total planned active time: 360 minutes; external waiting is recorded separately.

**Files:**
- Create: `submissions/luis-roquette/README.md`
- Create: `submissions/luis-roquette/solution/004-social/README.md`
- Create: `submissions/luis-roquette/process-log/evidence/004/cockpit-*-proof.png` (provas focais separadas)
- Modify: `submissions/luis-roquette/solution/004-social/analysis.md`
- Modify: `submissions/luis-roquette/solution/004-social/evidence.csv`
- Modify: `submissions/luis-roquette/process-log/004-social.md`

**Interfaces:**
- Consumes: the complete local application and every CK/HR from the SPEC.
- Produces: reproducible setup, final evidence, CK/HR matrix and explicit remaining human gate.

- [x] **Step 1: Write the technical README from commands already proven**

Document Python version, venv creation, pinned install, Kaggle source/license, test command, CLI command, app command, database location, five-minute demo and limitations. Do not describe an unexecuted command as passing.

- [x] **Step 2: Write the submission README from the official template**

Create `submissions/luis-roquette/README.md` with Luis Roquette, Challenge 004, executive summary, approach, actual findings, prioritized recommendations and limitations. Add the required process-log sections: tools and purposes, workflow, AI errors/corrections, human contribution, iterations and evidence links. Link the technical README, `analysis.md`, dashboard screenshot, research, diary and Git history. If LinkedIn is not confirmed by the user, write `Não informado` instead of inventing a URL.

- [x] **Step 3: Reproduce from a clean temporary environment**

Create a fresh venv outside the repository, install `requirements.txt`, run full test discovery, CLI against the real CSV and the Streamlit health/UI flow. Record exact commands, exit codes, runtime and peak memory.

- [x] **Step 4: Verify exports as artifacts**

Open the HTML, print/save it to A4 and confirm one page with essential limitations. Download the CSV through the UI, parse it, reconcile selected evidence IDs and confirm dangerous formula text is neutralized.

- [ ] **Step 5: Run the human five-minute scenario — pendente (HR-01)**

With installation and CSV ready, time: upload → identify deviation → explain benchmark/context → register action. Record duration and observer. If no human performs it, mark HR-01 pending and do not declare Definition of Done.

- [x] **Step 6: Fill the final CK/HR and rubric matrix**

For CK-01–11 and HR-01–04, record `pass/pending/fail`, command or visual evidence and file/line reference. Score R-01–R-05 with excerpts from the actual deliverable. A score never overrides a failed hard criterion.

- [x] **Step 7: Run final repository gates**

Run:

```bash
test -d submissions/luis-roquette/solution/004-social/tests
test -f submissions/luis-roquette/README.md
python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_*.py' -v
git diff --check
git diff --name-only main...HEAD
git status --short
git ls-files submissions/luis-roquette/solution/004-social
```

Expected: tests green; every intended commit path begins with `submissions/luis-roquette/`; `.claude/`, `.specs/`, `skills-lock.json`, CSV source, database and venv remain outside the commit.

Also record the submission metadata required by the repository: target branch `submission/luis-roquette`, one PR only, and PR title `[Submission] Luis Roquette — Challenge 004`. The current planning branch may differ; rename or create the target branch only when PR publication is explicitly authorized.

- [x] **Step 8: Commit the verified handoff**

```bash
git add -f submissions/luis-roquette/README.md submissions/luis-roquette/solution/004-social/README.md submissions/luis-roquette/solution/004-social/analysis.md submissions/luis-roquette/solution/004-social/evidence.csv submissions/luis-roquette/process-log/004-social.md submissions/luis-roquette/process-log/evidence/004/cockpit-*-proof.png
git commit -m "docs(004): prove cockpit acceptance"
```

Stop after the local handoff. Push, PR, merge and deployment require separate authorization and their own current gates.

---

## Refinamento executivo ≥9,5 — Tasks 7–11

As tarefas abaixo são incrementais e começam somente após as Tasks 1–6 já concluídas. Ordem obrigatória: `Task 7 → Task 8 → Task 9 → Task 10 → Task 11`. Cada task encerra com teste focal, atualização contemporânea do diário e commit próprio. O preflight pesado continua fora do Mac; antes de PR/merge, executar o gate canônico via `codespace-manager` conforme as regras globais.

Todos os comandos das Tasks 7–11 partem de `submissions/luis-roquette/solution/004-social`, salvo quando o próprio comando trouxer outro caminho explícito.

### Task 7: Rankear drivers multivariados estáveis

**Estimated active time:** 55 minutes.

**Files:**
- Modify: `submissions/luis-roquette/solution/004-social/analysis.py`
- Modify: `submissions/luis-roquette/solution/004-social/tests/helpers.py`
- Modify: `submissions/luis-roquette/solution/004-social/tests/test_analysis.py`
- Modify: `submissions/luis-roquette/process-log/004-social.md`

**Interfaces:**
- Consumes: o DataFrame derivado dentro de `analyze`, limitado a posts orgânicos com `erv` definida, mais `source_hash` e `scope_identity`.
- Produces: `_engagement_drivers(targets: pd.DataFrame, source_hash: str, scope: dict[str, object]) -> dict[str, object]` e `result["engagement_drivers"]` com `evidence_id`, `materiality_threshold_pp`, `contexts`, `leader`, `laggard`, `runner_up`, `verdict` e `change_trigger`.
- Preserves: `_dimensions`, alertas e fila existentes continuam disponíveis; nenhuma média marginal vira prova causal.

- [x] **Step 1: Criar fixtures mensais determinísticas**

Adicionar a `tests/helpers.py`:

```python
def driver_rows(month_deltas: list[float], *, concentrated: bool = False) -> list[dict[str, object]]:
    """Cria alvo texto/tech e pares vídeo/tech na mesma plataforma/faixa/mês."""
    # 30 posts e cinco creators por braço/mês; meses alternam dois grupos para somar dez creators.
    # views=10_000 permite deltas inteiros precisos.

def default_scope_all_history(rows: list[dict[str, object]]) -> dict[str, object]:
    dates = [str(row["post_date"]) for row in rows]
    return {"target_start": min(dates), "target_end": max(dates),
            "reference_date": max(dates), "filters": {}, "include_post_alerts": False}
```

A fixture usa creators `target-a-0..4`/`target-b-0..4` e `peer-a-0..4`/`peer-b-0..4`, alternando `a` e `b` por mês, para satisfazer cinco creators em cada braço mensal e dez no contexto completo. Ela deve permitir três casos: sinal positivo estável e material; sinais mensais alternados; sinal estável abaixo do limiar prático. Com `concentrated=True`, mantém pelo menos dez creators no conjunto e cinco por braço/mês, mas concentra pelo menos 78 dos 90 posts elegíveis em um creator para reduzir somente o fator de concentração.

- [x] **Step 2: Escrever os testes vermelhos do contrato**

Adicionar a `test_analysis.py`:

```python
def test_driver_ranking_requires_multivariate_peers_and_three_eligible_months(self):
    rows = driver_rows([1.0, 1.2, 0.8])
    result = analyze(frame_from_rows(rows), default_scope_all_history(rows), "hash")
    leader = result["engagement_drivers"]["leader"]
    self.assertEqual(leader["context"], {
        "platform": "Instagram", "content_type": "text",
        "content_category": "tech", "follower_band": "10,000–49,999",
    })
    self.assertEqual(leader["eligible_months"], 3)
    self.assertGreaterEqual(leader["stability"], 2 / 3)
    self.assertEqual(set(leader["volume_guard"]), {
        "target_median_views", "peer_median_views", "delta_views",
        "target_median_interactions", "peer_median_interactions", "delta_interactions",
        "status",
    })
    self.assertEqual(result["engagement_drivers"]["laggard"]["context"]["content_type"], "video")

def test_driver_ranking_abstains_for_unstable_or_immaterial_effect(self):
    for deltas in ([1.0, -1.0, 1.0, -1.0], [0.01, 0.02, 0.01]):
        rows = driver_rows(list(deltas))
        ranking = analyze(frame_from_rows(rows), default_scope_all_history(rows), "hash")["engagement_drivers"]
        self.assertIsNone(ranking["leader"])
        self.assertEqual(ranking["verdict"], "no_sustained_winner")

def test_driver_strength_penalizes_creator_concentration(self):
    balanced_rows = driver_rows([1, 1, 1])
    concentrated_rows = driver_rows([1, 1, 1], concentrated=True)
    balanced = analyze(frame_from_rows(balanced_rows), default_scope_all_history(balanced_rows), "hash")
    concentrated = analyze(frame_from_rows(concentrated_rows), default_scope_all_history(concentrated_rows), "hash")
    self.assertGreater(balanced["engagement_drivers"]["contexts"][0]["strength"],
                       concentrated["engagement_drivers"]["contexts"][0]["strength"])

def test_driver_ranking_is_stable_under_row_shuffle_and_exact_tie(self):
    rows = driver_rows([1, 1, 1])
    tied = duplicate_driver_context(rows, platform="TikTok")
    first = analyze(frame_from_rows(rows + tied), default_scope_all_history(rows + tied), "hash")
    shuffled = list(reversed(rows + tied))
    second = analyze(frame_from_rows(shuffled), default_scope_all_history(shuffled), "hash")
    self.assertEqual(first["engagement_drivers"], second["engagement_drivers"])
```

`duplicate_driver_context` copia alvo e par com IDs/creators exclusivos e troca a plataforma, preservando deltas, volumes e datas; assim, os conjuntos comparáveis permanecem isolados e o desempate final depende apenas de `context_signature`, não da ordem das linhas.

- [x] **Step 3: Executar os testes e confirmar o vermelho correto**

Run:

```bash
uv run --with-requirements requirements.txt python -m unittest \
  tests.test_analysis.ContextEvidenceTests.test_driver_ranking_requires_multivariate_peers_and_three_eligible_months \
  tests.test_analysis.ContextEvidenceTests.test_driver_ranking_abstains_for_unstable_or_immaterial_effect \
  tests.test_analysis.ContextEvidenceTests.test_driver_strength_penalizes_creator_concentration \
  tests.test_analysis.ContextEvidenceTests.test_driver_ranking_is_stable_under_row_shuffle_and_exact_tie
```

Expected: FAIL porque `engagement_drivers` e `driver_rows` ainda não existem; nenhuma falha de parsing da fixture.

- [x] **Step 4: Implementar o ranking mínimo no motor existente**

Implementar em `analysis.py` sem nova classe/dependência:

```python
DRIVER_KEYS = ("platform", "content_type", "content_category", "follower_band")
organic = targets.loc[(~targets["is_sponsored"]) & targets["erv"].notna()]
global_iqr = float(organic["erv"].quantile(.75) - organic["erv"].quantile(.25)) if len(organic) else 0.0
materiality = max(0.10, 0.25 * global_iqr)
monthly_delta = float(target_month["erv"].median() - peer_month["erv"].median())
median_delta = float(pd.Series(monthly_deltas).median())
same_sign_months = sum((value > 0) == (median_delta > 0) for value in monthly_deltas if value != 0)
stability = same_sign_months / len(monthly_deltas)
strength = min(_strength(context_rows)[0], _strength(peer_rows)[0])
eligible = len(monthly_deltas) >= 3 and len(context_rows) >= 90 and context_rows["creator_id"].nunique() >= 10
is_leader = eligible and median_delta >= materiality and stability >= 2 / 3 and strength >= 0.40
is_laggard = eligible and median_delta <= -materiality and stability >= 2 / 3 and strength >= 0.40
```

Para cada mês, `target_month` contém o contexto completo; `peer_month` contém outros formatos/categorias da mesma plataforma/faixa/mês e exclui os IDs do alvo. Cada braço precisa de 30 taxas e cinco creators. `context_rows` e `peer_rows` concatenam somente os braços dos meses elegíveis; a força reutiliza `_strength` e toma o menor braço, sem fórmula paralela. Ordenar candidatos positivos por `is_leader desc, stability desc, strength desc, median_delta desc, posts desc, context_signature asc`; ordenar negativos separadamente por `is_laggard desc, stability desc, strength desc, median_delta asc, posts desc, context_signature asc`. `runner_up` é o segundo positivo elegível, mesmo quando não há vencedor; `laggard` só existe quando passa os gates negativos. Guardar amostras, creators, meses, ERv/volumes de alvo e par, deltas mensais e referências. `volume_guard` compara medianas por post de views e interações: `aligned` quando ambos os deltas são não negativos; `tradeoff` caso contrário. O guard não altera o ranking por ERv, mas aparece obrigatoriamente no veredicto para impedir que taxa maior seja comunicada como maior alcance absoluto.

- [x] **Step 5: Integrar ao resultado e versionar o método**

Adicionar `"engagement_drivers": _engagement_drivers(...)` ao retorno de `analyze`. Alterar `METHOD_VERSION` para `2.5.0` e acrescentar `2.4.0` a `HISTORICAL_METHOD_VERSIONS`; comparações automáticas de outcomes entre 2.4.0 e 2.5.0 continuam bloqueadas.

- [x] **Step 6: Rodar regressões focais e commit**

Run:

```bash
uv run --with-requirements requirements.txt python -m unittest \
  tests.test_analysis.ContextEvidenceTests \
  tests.test_reconstruction.ReconstructionTests
python3 -m py_compile analysis.py
git diff --check
```

Expected: verde; resultados antigos continuam determinísticos sob 2.5.0 e os novos contextos não removem alertas/dimensões.

```bash
git add -u -- analysis.py tests/helpers.py tests/test_analysis.py ../../process-log/004-social.md
git commit -m "feat(004): rank stable engagement drivers"
```

### Task 8: Calcular decisão financeira condicional sem inventar ROI

**Estimated active time:** 35 minutes.

**Files:**
- Modify: `submissions/luis-roquette/solution/004-social/analysis.py`
- Modify: `submissions/luis-roquette/solution/004-social/tests/helpers.py`
- Modify: `submissions/luis-roquette/solution/004-social/tests/test_analysis.py`
- Modify: `submissions/luis-roquette/process-log/004-social.md`

**Interfaces:**
- Consumes: um estrato elegível escolhido explicitamente de `result["sponsorship"]["strata"]` e cinco entradas manuais não negativas.
- Produces: `sponsorship_break_even(evidence: dict[str, object], assumptions: dict[str, float]) -> dict[str, object]` com `status`, `incremental_conversion_rate`, `incremental_conversions`, `incremental_value`, `max_sponsorship_cost`, `required_uplift_pp`, `missing` e `limitations`.
- Does not: alterar `result`, persistir inputs ou chamar o cálculo de ROI observado.

- [x] **Step 1: Escrever os testes vermelhos de validação e fórmula**

Adicionar `monthly_sponsorship_rows(months=3)` a `tests/helpers.py`: gerar somente os dois braços do mesmo contexto `YouTube + mixed + finance + 10,000–49,999`, deslocar `post_date` por mês e usar IDs exclusivos. Cada braço/mês conserva 30 taxas e cinco creators; a união usa dez creators por braço para também testar estabilidade sem inflar força por repetição. O braço orgânico tem ERv `4%` e o patrocinado `5%`. Não criar outro formato/categoria orgânico nessa plataforma: a fixture comprova patrocínio sem entrar no universo de pares do ranking de drivers.

```python
def test_break_even_calculates_thresholds_from_manual_assumptions(self):
    evidence = {
        "evidence_id": "sponsorship-test",
        "context": {"platform": "YouTube", "content_type": "mixed",
                    "content_category": "finance", "follower_band": "10,000–49,999",
                    "period_month": "2025-01"},
        "sponsored": {"median_views_per_post": 10_000},
    }
    scenario = sponsorship_break_even(evidence, {
        "sponsorship_cost": 1_000, "incremental_production_cost": 200,
        "value_per_conversion": 100, "organic_conversion_rate": .01,
        "sponsored_conversion_rate": .013,
    })
    self.assertEqual(scenario["incremental_conversions"], 30)
    self.assertEqual(scenario["max_sponsorship_cost"], 2_800)
    self.assertEqual(scenario["required_uplift_pp"], 0.12)
    self.assertEqual(scenario["status"], "meets_break_even_scenario")

def test_break_even_abstains_on_missing_or_invalid_inputs(self):
    invalid = {"sponsorship_cost": -1, "value_per_conversion": 0,
               "organic_conversion_rate": 0, "sponsored_conversion_rate": 1.01}
    scenario = sponsorship_break_even({"sponsored": {"median_views_per_post": 0}}, invalid)
    self.assertEqual(scenario["status"], "invalid_or_missing_assumptions")
    self.assertTrue(scenario["missing"])

def test_sponsorship_answer_names_best_and_worst_comparable_contexts(self):
    rows = monthly_sponsorship_rows(3)
    result = analyze(frame_from_rows(rows), default_scope_all_history(rows), "hash")
    answer = executive_answers(result)[1]
    self.assertIn("melhor contexto comparável", answer["comparison"].lower())
    self.assertIn("pior contexto comparável", answer["comparison"].lower())
    self.assertIn("YouTube", answer["comparison"])
```

- [x] **Step 2: Confirmar o vermelho**

Run: `uv run --with-requirements requirements.txt python -m unittest tests.test_analysis.ContextEvidenceTests.test_break_even_calculates_thresholds_from_manual_assumptions tests.test_analysis.ContextEvidenceTests.test_break_even_abstains_on_missing_or_invalid_inputs tests.test_analysis.ContextEvidenceTests.test_sponsorship_answer_names_best_and_worst_comparable_contexts`

Expected: FAIL com import/função ausente.

- [x] **Step 3: Implementar validação e fórmulas puras**

Usar exatamente:

```python
incremental_rate = sponsored_conversion_rate - organic_conversion_rate
incremental_conversions = views_per_post * incremental_rate
incremental_value = incremental_conversions * value_per_conversion
max_sponsorship_cost = max(0.0, incremental_value - incremental_production_cost)
required_uplift_pp = 100 * (sponsorship_cost + incremental_production_cost) / (views_per_post * value_per_conversion)
```

Taxas pertencem a `[0,1]`; custos são `>=0`; `views_per_post` e `value_per_conversion` precisam ser positivos. Status é `meets_break_even_scenario` somente quando o custo informado não supera `max_sponsorship_cost`; caso contrário, `below_break_even_scenario`. Incluir sempre “cenário manual, não ROI observado nem efeito causal”.

Copiar para a saída o `evidence_id` e o contexto do estrato selecionado. Sem estrato elegível selecionado, retornar `invalid_or_missing_assumptions`; nunca misturar a mediana de views de um contexto com taxas digitadas para outro.

- [x] **Step 4: Provar imutabilidade e commit**

Adicionar asserção de que `deepcopy(evidence)` permanece idêntica e que nenhuma chave de cenário aparece em `export_evidence(result, [])` ou em `decision_baseline` sem ação explícita da UI.

```bash
uv run --with-requirements requirements.txt python -m unittest \
  tests.test_analysis.ContextEvidenceTests.test_break_even_calculates_thresholds_from_manual_assumptions \
  tests.test_analysis.ContextEvidenceTests.test_break_even_abstains_on_missing_or_invalid_inputs \
  tests.test_decision_evidence
git diff --check
git add -u -- analysis.py tests/helpers.py tests/test_analysis.py ../../process-log/004-social.md
git commit -m "feat(004): add sponsorship break-even scenario"
```

### Task 9: Produzir estratégia de 30 dias e respostas executivas completas

**Estimated active time:** 50 minutes.

**Files:**
- Modify: `submissions/luis-roquette/solution/004-social/analysis.py`
- Modify: `submissions/luis-roquette/solution/004-social/tests/test_analysis.py`
- Modify: `submissions/luis-roquette/solution/004-social/tests/test_exports.py`
- Modify: `submissions/luis-roquette/process-log/004-social.md`

**Interfaces:**
- Consumes: `result["engagement_drivers"]`, patrocínio, recomendações e hipótese de frequência.
- Produces: `content_strategy_30d(result: dict[str, object]) -> dict[str, object]` e `executive_answers(result, financial_scenario=None) -> list[dict[str, str]]`.
- Produces: `executive_summary(result, decisions, financial_scenario=None) -> str`; `analysis_report` continua canônico e não recebe cenário manual.
- Answer fields: `question`, `verdict`, `kpi`, `comparison`, `sample`, `action`, `strength`, `coverage`, `stability`, `evidence_id`, `change_trigger`.

- [x] **Step 1: Escrever testes vermelhos para as respostas e quatro semanas**

Em `test_analysis.py`, criar `ExecutiveAnswerTests` e dois helpers locais: `result_with_stable_driver()` analisa `driver_rows([1.0, 1.2, 0.8])`; `result_without_stable_driver()` analisa `driver_rows([1.0, -1.0, 1.0, -1.0])`. Ambos usam `default_scope_all_history` e `source_hash="hash"`.

```python
def test_executive_answers_use_driver_ranking_and_disclose_decision_trigger(self):
    answers = executive_answers(result_with_stable_driver())
    self.assertEqual(len(answers), 3)
    self.assertTrue(all(set(answer) == {
        "question", "verdict", "kpi", "comparison", "sample", "action",
        "strength", "coverage", "stability", "evidence_id", "change_trigger",
    } for answer in answers))
    self.assertIn("INSTAGRAM / TEXTO / TECH", answers[0]["verdict"])

def test_strategy_has_four_ordered_weeks_and_no_automatic_scale(self):
    strategy = content_strategy_30d(result_with_stable_driver())
    self.assertEqual([item["week"] for item in strategy["weeks"]], [1, 2, 3, 4])
    self.assertEqual([item["window"] for item in strategy["weeks"]], ["D1–D7", "D8–D14", "D15–D21", "D22–D30"])
    self.assertTrue(all("cadence" in item for item in strategy["weeks"]))
    self.assertEqual(strategy["mix_policy"], "preserve_current_mix_outside_tests")
    self.assertTrue(all(item["owner"] == "Gestor de Social Media" for item in strategy["weeks"]))
    self.assertFalse(strategy["automatic_publication_or_spend"])

def test_no_stable_driver_yields_explicit_collection_strategy(self):
    answers = executive_answers(result_without_stable_driver())
    self.assertIn("NÃO EXISTE VENCEDOR SUSTENTADO", answers[0]["verdict"])
    self.assertIn("mudaria", answers[0]["change_trigger"].lower())
```

- [x] **Step 2: Confirmar o vermelho**

Run: `uv run --with-requirements requirements.txt python -m unittest tests.test_analysis.ExecutiveAnswerTests`

Expected: FAIL porque os campos novos e `content_strategy_30d` ainda não existem.

- [x] **Step 3: Implementar o programa relativo de quatro semanas**

Retornar esta estrutura mínima:

```python
driver = result["engagement_drivers"].get("leader")
context = dict(driver["context"]) if driver else {}
{
    "mix_policy": "preserve_current_mix_outside_tests",
    "context": context,
    "weeks": [
        {"week": 1, "window": "D1–D7", "phase": "baseline", "owner": "Gestor de Social Media",
         "action": "Congelar o contexto e registrar o baseline orgânico comparável",
         "metric": "ERv mediano, visualizações e interações por post",
         "cadence": "manter o mix corrente fora do teste",
         "gate": "30 taxas definidas e cinco creators em alvo e comparador"},
        {"week": 2, "window": "D8–D14", "phase": "test", "owner": "Gestor de Social Media",
         "action": "Testar o contexto vencedor sem alterar o mix fora do experimento",
         "metric": "Delta de ERv contra pares da mesma plataforma e faixa",
         "cadence": "usar a hipótese observada somente quando seu status for test",
         "gate": "Efeito acima da materialidade e guards não negativos"},
        {"week": 3, "window": "D15–D21", "phase": "replicate_or_revise", "owner": "Gestor de Social Media",
         "action": "Replicar uma vez se o sinal persistir; revisar se divergir",
         "metric": "Concordância entre duas janelas e concentração por creator",
         "cadence": "repetir a cadência testada ou coletar sem número inventado",
         "gate": "Duas janelas concordantes e força sem queda"},
        {"week": 4, "window": "D22–D30", "phase": "decide", "owner": "Gestor de Social Media",
         "action": "Escalar como novo teste, manter, revisar ou coletar",
         "metric": "Confiança, materialidade, visualizações e interações",
         "cadence": "manter até decisão humana registrada",
         "gate": "C>=0,70, efeito material e duas janelas concordantes para propor escala"},
    ],
    "automatic_publication_or_spend": False,
}
```

Semana 4 só permite propor ampliação como novo teste se `C>=0,70`, efeito acima da materialidade, duas janelas concordantes e guards de views/interações não negativos. Caso contrário, manter/revisar/coletar. Usar cadência observada apenas quando seu status for `test`; `collect` não recebe número inventado.

- [x] **Step 4: Reescrever as três respostas a partir dos novos contratos**

Engajamento usa `engagement_drivers`, não a maior marginal de formato, e declara se views/interações estão alinhadas ou em trade-off. Patrocínio nomeia o melhor e o pior contexto comparável, com seus deltas, amostras e força; continua “não escalar” enquanto a cobertura/força forem insuficientes e, com cenário manual válido, acrescenta o ponto de equilíbrio sem mudar a classificação observacional. Estratégia resume as quatro semanas, incluindo janela e cadência. Cada resposta mostra força heurística, cobertura, estabilidade temporal, `evidence_id` e condição mensurável que mudaria o veredicto. Para patrocínio, agrupar os estratos por `platform + content_type + content_category + follower_band`, excluir `period_month` da chave e calcular, dentro de cada contexto, a mediana dos deltas e a proporção de meses com o mesmo sinal; somente contextos com pelo menos três meses elegíveis entram como estáveis. Melhor/pior contexto e `evidence_id` derivam desses agregados, sem misturar composição entre plataformas. Para estratégia, a estabilidade herda o driver que fundamenta o plano. Ausência de base produz “não mensurável”, nunca zero inventado.

- [x] **Step 5: Atualizar HTML e Markdown sem recalcular análise**

`executive_summary` e `analysis_report` iteram os onze campos de `executive_answers`; HTML aplica `html.escape` em todos. Inserir a estratégia de quatro semanas antes da fila legada. O relatório vazio mantém três abstenções completas.

Ampliar `_iter_export_rows` com registros `record_type="evidence"`: um por contexto de `engagement_drivers` (`metric_name="driver_context"`) e um por semana (`metric_name="strategy_week"`). Cada registro inclui `evidence_id`, método, fonte, escopo e payload JSON determinístico; nenhum campo do cenário manual entra no CSV.

- [x] **Step 6: Rodar regressões e commit**

```bash
uv run --with-requirements requirements.txt python -m unittest \
  tests.test_analysis.ExecutiveAnswerTests \
  tests.test_exports.ExportTests \
  tests.test_reconstruction.ReconstructionTests \
  tests.test_temporal_export.TemporalExportTests
python3 -m py_compile analysis.py
git diff --check
git add -u -- analysis.py tests/test_analysis.py tests/test_exports.py ../../process-log/004-social.md
git commit -m "feat(004): build thirty-day content strategy"
```

### Task 10: Integrar ranking, cenário e plano à dashboard

**Estimated active time:** 45 minutes.

**Files:**
- Modify: `submissions/luis-roquette/solution/004-social/app.py`
- Modify: `submissions/luis-roquette/solution/004-social/tests/test_app.py`
- Modify: `submissions/luis-roquette/solution/004-social/tests/test_exports.py`
- Modify: `submissions/luis-roquette/process-log/004-social.md`

**Interfaces:**
- Consumes: respostas/estratégia do histórico completo já cacheado por `(source_hash, METHOD_VERSION)` e inputs manuais do cenário.
- Produces: três cards ampliados, tabela “Drivers contextuais”, seção “Estratégia de 30 dias” e expander “Cenário financeiro manual”.
- Preserves: filtros operacionais não alteram a síntese histórica; input financeiro não entra em SQLite nem no CSV de evidências.

- [x] **Step 1: Escrever AppTests vermelhos**

Adicionar a `test_app.py` os helpers concretos abaixo. `driver_upload()` reutiliza `driver_rows`; `sponsorship_upload()` serializa `sponsorship_rows()` após remover apenas a coluna derivada que não pertence ao contrato de upload.

Importar `deepcopy` de `copy`; `driver_rows` e `sponsorship_rows` de `tests.helpers`; e `export_evidence` de `analysis`. Não criar wrapper genérico de upload.

```python
def driver_upload() -> bytes:
    return csv_bytes(driver_rows([1.0, 1.2, 0.8]))

def sponsorship_upload() -> bytes:
    rows = sponsorship_rows().drop(columns=["source_row_id"], errors="ignore")
    return csv_bytes(rows.to_dict(orient="records"))
```

```python
def test_dashboard_shows_multivariate_answers_and_four_week_strategy(self):
    app = self.app()
    app.file_uploader[0].set_value(("drivers.csv", driver_upload(), "text/csv")).run()
    text = "\n".join(item.value for item in app.markdown)
    for expected in ("Força", "Cobertura", "Estabilidade", "Evidência", "O que mudaria a decisão", "Semana 1", "Semana 4"):
        self.assertIn(expected, text)

def test_financial_scenario_is_manual_ephemeral_and_does_not_change_evidence(self):
    app = self.app()
    app.file_uploader[0].set_value(("sponsorship.csv", sponsorship_upload(), "text/csv")).run()
    before = deepcopy(app.session_state["active_result"])
    selected = before["sponsorship"]["strata"][0]["evidence_id"]
    app.selectbox(key="scenario_sponsorship_stratum").set_value(selected)
    for key, value in {
        "scenario_sponsorship_cost": 1_000.0,
        "scenario_production_cost": 200.0,
        "scenario_value_per_conversion": 100.0,
        "scenario_organic_rate": 0.01,
        "scenario_sponsored_rate": 0.013,
    }.items():
        app.number_input(key=key).set_value(value)
    app.button(key="calculate_sponsorship_scenario").click().run()
    self.assertIn("Cenário manual", "\n".join(item.value for item in app.markdown))
    self.assertEqual(app.session_state["active_result"], before)
    self.assertNotIn(b"value_per_conversion", export_evidence(before, []))

def test_operational_filters_do_not_recompute_full_history_answers(self):
    app = self.app()
    app.file_uploader[0].set_value(("drivers.csv", driver_upload(), "text/csv")).run()
    answers = deepcopy(app.session_state["head_answers"])
    app.multiselect(key="filter_content_category").set_value(["beauty"]).run()
    self.assertEqual(app.session_state["head_answers"], answers)
```

- [x] **Step 2: Confirmar o vermelho**

Run: `uv run --with-requirements requirements.txt python -m unittest tests.test_app.AppTests.test_dashboard_shows_multivariate_answers_and_four_week_strategy tests.test_app.AppTests.test_financial_scenario_is_manual_ephemeral_and_does_not_change_evidence tests.test_app.AppTests.test_operational_filters_do_not_recompute_full_history_answers`

Expected: FAIL somente pela UI/inputs ausentes.

- [x] **Step 3: Renderizar o ranking e a estratégia com componentes existentes**

Reutilizar CSS/cards, `st.dataframe`, `st.expander` e `st.number_input`; não criar componente ou dependência. A tabela mostra contexto, delta mediano mensal, estabilidade, força, meses, posts e creators. O plano mostra uma linha por semana, ação, métrica e gate.

- [x] **Step 4: Implementar o cenário manual isolado**

Dentro do expander, selecionar primeiro um estrato elegível pelo `evidence_id` e contexto legível; depois mostrar cinco `number_input` com as chaves usadas no teste (`scenario_sponsorship_cost`, `scenario_production_cost`, `scenario_value_per_conversion`, `scenario_organic_rate`, `scenario_sponsored_rate`) e ajuda explícita. O botão `calculate_sponsorship_scenario` chama `sponsorship_break_even`; assim, custo zero continua válido sem disparar cálculo antes da ação humana. Exibir resultado como “cenário” e passá-lo opcionalmente a `executive_summary`; nunca gravar em `record_decision`, `record_outcome`, cache analítico ou `evidence.csv`. Trocar a fonte, o estrato ou qualquer premissa invalida o cenário anterior na mesma sessão.

- [x] **Step 5: Validar desktop, 390×844 e acessibilidade básica**

Confirmar primeira viewport com os três veredictos, cards em uma coluna no mobile, foco visível, nenhuma dependência de cor e tabelas utilizáveis por teclado. Capturar somente estados reais e substituir evidência visual apenas se o novo estado for comprovado.

- [x] **Step 6: Rodar regressões e commit**

```bash
uv run --with-requirements requirements.txt python -m unittest \
  tests.test_app.AppTests.test_dashboard_shows_multivariate_answers_and_four_week_strategy \
  tests.test_app.AppTests.test_financial_scenario_is_manual_ephemeral_and_does_not_change_evidence \
  tests.test_app.AppTests.test_operational_filters_do_not_recompute_full_history_answers \
  tests.test_exports.ExportTests.test_executive_html_escapes_input_and_has_no_active_content
python3 -m py_compile app.py analysis.py
git diff --check
git add -u -- app.py tests/test_app.py tests/test_exports.py ../../process-log/004-social.md
git commit -m "feat(004): expose executive decision program"
```

### Task 11: Provar o gate global ≥9,5 e regenerar a entrega

**Estimated active time:** 50 minutes plus human evaluation.

**Files:**
- Modify: `submissions/luis-roquette/solution/004-social/tests/test_acceptance.py`
- Modify: `submissions/luis-roquette/solution/004-social/analysis.md`
- Modify: `submissions/luis-roquette/solution/004-social/evidence.csv`
- Modify: `submissions/luis-roquette/solution/004-social/README.md`
- Modify: `submissions/luis-roquette/solution/004-social/SPEC.md`
- Modify: `submissions/luis-roquette/solution/004-social/IMPLEMENTATION-PLAN.md`
- Modify: `submissions/luis-roquette/process-log/004-social.md`
- Modify only after real proof: `submissions/luis-roquette/process-log/evidence/004/cockpit-*-proof.png`

**Interfaces:**
- Consumes: método 2.5.0 completo, CSV real e matriz de avaliação abaixo.
- Produces: artefatos regenerados, hashes, tempo/memória, matriz 15/15, nota humana e decisão explícita sobre o goal `≥9,5`.

- [x] **Step 1: Criar a regressão da matriz executiva**

Em `test_acceptance.py`, exigir para cada pergunta os cinco critérios: resposta direta, sustentação multivariada, estabilidade temporal, decisão operacional e estratégia executável. O teste verifica presença/evidência; não atribui nota subjetiva sozinho.

```python
def test_three_executive_answers_cover_the_fifteen_item_matrix(self):
    result = result_with_full_executive_evidence()
    answers = executive_answers(result)
    self.assertEqual(len(answers), 3)
    for answer in answers:
        self.assertTrue(answer["verdict"])                       # resposta direta
        self.assertTrue(answer["comparison"] and answer["evidence_id"])  # sustentação
        self.assertTrue(answer["stability"])                     # estabilidade temporal
        self.assertTrue(answer["action"] and answer["change_trigger"])  # decisão
    strategy = content_strategy_30d(result)
    self.assertEqual(len(strategy["weeks"]), 4)                   # execução
    self.assertTrue(all(item["owner"] and item["gate"] for item in strategy["weeks"]))
```

`result_with_full_executive_evidence()` analisa a união de `driver_rows([1.0, 1.2, 0.8])` com `monthly_sponsorship_rows(3)`, após prefixar identidades para evitar colisões. Assim, patrocínio usa pelo menos três meses comparáveis e `stability` não passa apenas por texto fixo. Acrescentar também um caso sem meses comparáveis que exige `stability="não mensurável"` e veredicto de não escalar.

Atualizar no mesmo arquivo as provas publicadas existentes: `test_report_answers_the_heads_three_questions_with_kpis_and_actions` passa a exigir os veredictos, KPIs, estabilidade, evidência e ações realmente gerados pelo método 2.5; `test_every_evidence_id_cited_by_report_exists_in_export` amplia o padrão para IDs `driver-*` e `strategy-*`. Não apagar asserções para fazer a suíte passar: substituir apenas expectativas 2.4 comprovadamente obsoletas pelos valores reconciliados no Step 2.

- [x] **Step 2: Regenerar com o CSV real e reconciliar independentemente**

Run:

```bash
uv run --with-requirements requirements.txt python analysis.py \
  /tmp/social-dataset.tEuI48/social_media_dataset.csv \
  --evidence evidence.csv --summary /tmp/004-social-summary-2.5.html --report analysis.md
```

Recalcular fora das funções sob teste: líder/abstenção multivariada, limiar prático, meses/sinais, força, cobertura de patrocínio e quatro semanas. Nenhuma divergência numérica é aceita.

Expected: CLI retorna zero; `analysis.md`, `evidence.csv` e HTML compartilham método `2.5.0`, fonte, três veredictos e IDs; a reconciliação independente produz os mesmos deltas, gates e contextos.

- [x] **Step 3: Medir eficiência no caminho real**

Medir upload + histórico completo até os cards: alvo frio `≤30 s` no Mac de referência; rerun com mesma fonte `≤1 s`; pico de memória sem swap. Se ultrapassar, perfilar primeiro e otimizar somente a causa medida, sem mudar resultado.

Expected: os três limites são registrados com comando, máquina, horário e amostra no diário; qualquer limite excedido mantém a Task 11 aberta.

- [x] **Step 4: Aplicar a nota global sem autoengano**

Usar cinco dimensões com pesos iguais: clareza, objetividade, eficiência, profundidade e capacidade decisória. O goal só passa com média `≥9,5`, nenhuma dimensão `<9,0`, matriz técnica `15/15` e justificativa textual para cada nota. A IA pode produzir avaliação preliminar; a nota final precisa de leitura humana de Luis ou avaliador designado. Ausência dessa leitura fica `PENDING`, nunca arredondada para sucesso.

- [x] **Step 5: Executar gates focais locais e gate pesado remoto antes de PR**

No Mac: `py_compile`, `git diff --check` e testes focais afetados. Antes de abrir/atualizar PR, executar:

```bash
codespace-manager list
codespace-manager run <nome-parado-limpo-do-mesmo-repo> -- 'python -m pip install -r submissions/luis-roquette/solution/004-social/requirements.txt && PYTHONWARNINGS=error python -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p "test_*.py" -v'
```

Expected: instalação sem conflito e suíte completa verde no mesmo commit/diff pretendido. Se o semáforo estiver congestionado e Luis mantiver o bypass, registrar a exceção e deixar Actions/Vercel fecharem os gates; nunca alegar preflight local completo.

- [x] **Step 6: Atualizar documentação, provas e hashes**

Registrar resultados reais no diário, atualizar método/hashes/contagem de testes nos quatro documentos, substituir screenshots somente após inspeção real e verificar que `evidence.csv` não contém inputs manuais. Preservar HR-01 separadamente.

Expected: matriz técnica `15/15`; nota humana `≥9,5` sem dimensão `<9,0`, ou status honesto `PENDING`; hashes recalculados; nenhum segredo, dataset bruto ou premissa manual versionada.

- [x] **Step 7: Commitar o handoff local**

```bash
git add -u -- analysis.md evidence.csv README.md SPEC.md IMPLEMENTATION-PLAN.md \
  ../../process-log/004-social.md ../../process-log/evidence/004
git commit -m "docs(004): prove executive quality gate"
```

Stop local: não fazer push, abrir PR, mergear ou publicar sem autorização explícita.
