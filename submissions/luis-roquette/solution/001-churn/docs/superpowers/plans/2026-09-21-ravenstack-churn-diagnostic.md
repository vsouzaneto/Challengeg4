# RavenStack Churn Diagnostic Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar um diagnóstico reproduzível que explique o churn da RavenStack, priorize causas e segmentos pelo MRR exposto e gere uma fila operacional de contas para Customer Success.

**Architecture:** Um pacote Python transforma cinco CSVs imutáveis em um painel temporal de conta por data de corte, executa diagnóstico controlado e, condicionalmente, valida um modelo de risco. Um publicador grava artefatos canônicos consumidos pelo relatório Markdown e por uma aplicação Streamlit de três visões; nenhuma interface recalcula métricas.

**Tech Stack:** Python 3.12, pandas 3.0.6, NumPy 2.5.3, SciPy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1, Streamlit 1.64.0, pytest 9.1.1 e Ruff 0.16.8.

**Spec:** `submissions/luis-roquette/solution/001-churn/.specs/tasks/in-progress/implement-churn-diagnostic.feature.md`

## Global Constraints

- Alterar somente `submissions/luis-roquette/`.
- Não usar APIs pagas, banco, autenticação, CRM, contato automático ou serviço de modelo.
- Tratar os cinco CSVs como entradas imutáveis e creditar River @ Rivalytics.
- Usar o primeiro evento com `is_reactivation=False` como rótulo temporal primário; flags de churn são fontes de reconciliação.
- Calcular atributos apenas com eventos em `event_time <= cutoff` e alvo em `(cutoff, cutoff + 30 dias]`; cutoffs rotulados terminam em `2024-11-30` e a fila operacional usa o snapshot sem rótulo de `2024-12-31`.
- Produzir visões `observed` e `strict`; rebaixar findings materialmente instáveis entre elas.
- Rotular receita como `MRR exposto — oportunidade máxima`, nunca como recuperação prevista.
- Publicar o modelo somente se ele superar o baseline fora do tempo e passar todos os gates definidos na Task 5.
- `make reproduce` deve falhar diante de contrato crítico, teste vermelho ou artefato inconsistente.
- A demonstração pública é somente leitura e não bloqueia a reprodução local.
- Executar o preflight final no Codespace gerenciado e provar o mesmo commit e diff antes do Pull Request.

## Review Focus

- `usage_id` repetido com conteúdo conflitante deve preservar todas as linhas e sinalizar a anomalia — `test_conflicting_usage_ids_are_preserved_and_flagged` na Task 2.
- flags de churn, evento terminal e reativação divergentes devem ser reconciliados sem trocar o rótulo primário — `test_churn_label_disagreement_is_reported` na Task 2.
- eventos anteriores ao ciclo de vida devem permanecer em `observed` e desaparecer de `strict` — `test_strict_panel_excludes_pre_lifecycle_events` na Task 3.
- assinaturas simultâneas com plano e frequência diferentes devem preservar receita e produzir dimensões `mixed` — `test_concurrent_subscriptions_preserve_revenue_and_mixed_dimensions` na Task 3.
- zero findings aprovados deve gerar relatório honesto e fila vazia, não causa inventada — `test_no_accepted_finding_publishes_honest_empty_queue` na Task 6.

---

## Execution Convention

- Execute comandos Python/Make a partir de `submissions/luis-roquette/solution/001-churn/`.
- Execute comandos `git` a partir da raiz do repositório.
- Durante a implementação automatizada, execute todos os blocos de instalação, pytest, reprodução e Streamlit dentro do Codespace obtido por `codespace-manager`; os blocos omitem esse invólucro apenas para manter cada passo legível. No Mac, limite-se a inspeção de arquivos e Git.
- Fixtures citadas por um teste são criadas na mesma task, em `tests/conftest.py`; nenhuma task depende de fixture implícita.
- O primeiro churn não reativação encerra conservadoramente a observação daquela conta; reativações posteriores aparecem apenas na reconciliação e nas limitações, sem fabricar uma segunda jornada.

## Timebox

| Task | Budget |
|---|---:|
| 1–2 — foundation and contracts | 55 min |
| 3 — temporal panel | 55 min |
| 4 — diagnosis | 75 min |
| 5 — optional model gate | 35 min; skip publication when the budget expires |
| 6–7 — artifacts, report and dashboard | 80 min |
| 8–9 — documentation and clean preflight | 35 min |

Core implementation budget: `5 h 35 min`, inside the official 4–6 hour window. Public deployment is attempted only after the local submission is complete and is outside the critical path.

## File Structure

```text
submissions/luis-roquette/solution/001-churn/
├── Makefile
├── README.md
├── pyproject.toml
├── requirements.txt
├── app.py
├── data/
│   ├── README.md
│   └── raw/
│       ├── ravenstack_accounts.csv
│       ├── ravenstack_subscriptions.csv
│       ├── ravenstack_feature_usage.csv
│       ├── ravenstack_support_tickets.csv
│       └── ravenstack_churn_events.csv
├── artifacts/
│   ├── account_panel.csv
│   ├── account_queue.csv
│   ├── account_watchlist.csv
│   ├── claim_checks.csv
│   ├── findings.csv
│   ├── segment_metrics.csv
│   ├── quality_report.json
│   ├── model_evaluation.json
│   ├── report.md
│   └── run_manifest.json
├── src/ravenstack_churn/
│   ├── __init__.py
│   ├── config.py
│   ├── contracts.py
│   ├── quality.py
│   ├── panel.py
│   ├── diagnosis.py
│   ├── modeling.py
│   ├── publish.py
│   └── cli.py
└── tests/
    ├── conftest.py
    ├── test_contracts.py
    ├── test_quality.py
    ├── test_panel.py
    ├── test_diagnosis.py
    ├── test_modeling.py
    ├── test_publish.py
    └── test_app.py
```

---

### Task 1: Bootstrap reproducible project and verified raw data

**Files:**
- Create: `submissions/luis-roquette/solution/001-churn/pyproject.toml`
- Create: `submissions/luis-roquette/solution/001-churn/src/ravenstack_churn/__init__.py`
- Create: `submissions/luis-roquette/solution/001-churn/src/ravenstack_churn/config.py`
- Create: `submissions/luis-roquette/solution/001-churn/data/README.md`
- Create: `submissions/luis-roquette/solution/001-churn/data/raw/*.csv`
- Test: `submissions/luis-roquette/solution/001-churn/tests/test_contracts.py`

**Interfaces:**
- Produces: `RAW_FILE_SHA256: dict[str, str]`, `RAW_TABLE_NAMES: tuple[str, ...]`, `DEFAULT_WINDOWS: tuple[int, ...]`, `DEFAULT_CUTOFFS: pandas.DatetimeIndex`.
- Produces: `SCORING_CUTOFF = pandas.Timestamp("2024-12-31")` para a fila corrente sem alvo futuro.
- Produces: um ambiente instalável sem compilação nativa com `python -m pip install --only-binary=:all: -e '.[dev]'`.

- [x] **Step 1: Write the failing raw-file checksum test**

```python
from pathlib import Path

from ravenstack_churn.config import RAW_FILE_SHA256, sha256_file


def test_raw_files_match_published_checksums() -> None:
    raw_dir = Path("data/raw")
    actual = {name: sha256_file(raw_dir / name) for name in RAW_FILE_SHA256}
    assert actual == RAW_FILE_SHA256
```

- [x] **Step 2: Run the checksum test and verify the import fails**

Run from `submissions/luis-roquette/solution/001-churn`:

```bash
python -m pytest tests/test_contracts.py::test_raw_files_match_published_checksums -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'ravenstack_churn'`.

- [x] **Step 3: Create the pinned Python project**

Create `pyproject.toml` with Python `==3.12.*`, package directory `src`, and these exact dependencies:

```toml
[project]
name = "ravenstack-churn-diagnostic"
version = "0.1.0"
requires-python = "==3.12.*"
dependencies = [
  "numpy==2.5.3",
  "pandas==3.0.6",
  "scikit-learn==1.9.1",
  "scipy==1.18.1",
  "statsmodels==0.15.0",
  "streamlit==1.64.0",
]

[project.optional-dependencies]
dev = ["pytest==9.1.1", "ruff==0.16.8"]

[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py312"
```

- [x] **Step 4: Add immutable input constants and checksum helper**

```python
from hashlib import sha256
from pathlib import Path
import pandas as pd

RAW_FILE_SHA256 = {
    "ravenstack_accounts.csv": "348d8ba906b7776894b5236b2e7aa91a503d41670dbc9aad30c37b503c9abef5",
    "ravenstack_churn_events.csv": "6391c41d8291b7b4845ec9a84d3837c2ed230a33a32a854ec33d4e66dc150940",
    "ravenstack_feature_usage.csv": "c081da2be8caf987d07f0f79ceb0619aba523d819529230ed6df77984fa21d4e",
    "ravenstack_subscriptions.csv": "dcf1d93ca9a35e0dcba0ab686d255f0e9ec26512970bbf0944cf19cbef2d751a",
    "ravenstack_support_tickets.csv": "ba0006951479771ee9f93c98789c96bc5fec892cf11f867afb28194f0b76d220",
}
RAW_TABLE_NAMES = tuple(name.removeprefix("ravenstack_").removesuffix(".csv") for name in RAW_FILE_SHA256)
DEFAULT_WINDOWS = (7, 30, 90)
DEFAULT_CUTOFFS = pd.date_range("2023-04-30", "2024-11-30", freq="ME")
SCORING_CUTOFF = pd.Timestamp("2024-12-31")
MIN_SEGMENT_ACCOUNTS = 30
MIN_SEGMENT_CHURNS = 10
MIN_COVERAGE = 0.70
RANDOM_SEED = 42


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()
```

- [x] **Step 5: Download and vendor the five public CSVs**

```bash
work_dir=$(mktemp -d /tmp/ravenstack-data.XXXXXX)
curl -fsSL 'https://www.kaggle.com/api/v1/datasets/download/rivalytics/saas-subscription-and-churn-analytics-dataset' -o "$work_dir/data.zip"
unzip -q "$work_dir/data.zip" -d "$work_dir/data"
cp "$work_dir"/data/ravenstack_*.csv data/raw/
```

Do not commit the downloaded archive. Add `data/README.md` with source URL, retrieval date `2026-09-21`, synthetic/no-PII status, credit `River @ Rivalytics`, license wording, five SHA-256 values, and the exact download command above.

- [x] **Step 6: Install and run the checksum test**

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --only-binary=:all: -e '.[dev]'
.venv/bin/python -m pytest tests/test_contracts.py::test_raw_files_match_published_checksums -v
```

Expected: PASS.

- [x] **Step 7: Commit the reproducible foundation**

```bash
git add -f \
  submissions/luis-roquette/solution/001-churn/pyproject.toml \
  submissions/luis-roquette/solution/001-churn/src/ravenstack_churn/__init__.py \
  submissions/luis-roquette/solution/001-churn/src/ravenstack_churn/config.py \
  submissions/luis-roquette/solution/001-churn/data/README.md \
  submissions/luis-roquette/solution/001-churn/data/raw/ravenstack_*.csv \
  submissions/luis-roquette/solution/001-churn/tests/test_contracts.py
git commit -m "feat(churn): add reproducible project and verified data"
```

---

### Task 2: Enforce data contracts and publish quality evidence

**Files:**
- Create: `submissions/luis-roquette/solution/001-churn/src/ravenstack_churn/contracts.py`
- Create: `submissions/luis-roquette/solution/001-churn/src/ravenstack_churn/quality.py`
- Create: `submissions/luis-roquette/solution/001-churn/tests/conftest.py`
- Modify: `submissions/luis-roquette/solution/001-churn/tests/test_contracts.py`
- Test: `submissions/luis-roquette/solution/001-churn/tests/test_quality.py`

**Interfaces:**
- Produces: `load_raw_tables(raw_dir: Path) -> dict[str, pd.DataFrame]`.
- Produces: `validate_contracts(tables: dict[str, pd.DataFrame]) -> pd.DataFrame`; raises `DataContractError` only for missing schema, parse failure, primary-key failure outside documented usage duplicates, or orphan foreign keys.
- Produces: `build_quality_report(tables: dict[str, pd.DataFrame]) -> dict[str, object]` with row counts, nulls, duplicate IDs, orphan counts, chronology contradictions and churn-label reconciliation.
- Produces: `add_usage_row_key(usage: pd.DataFrame) -> pd.DataFrame` using `f"{usage_id}#{occurrence}"`, where `occurrence` starts at zero, without dropping rows.

- [x] **Step 1: Create minimal synthetic tables in `tests/conftest.py`**

Define a `mini_tables()` fixture returning all five DataFrames with accounts `A-1` and `A-2`; set their signup dates to `2023-01-01` and `2024-05-20`, with account churn flags `False` and `True` respectively. Give `A-1` an annual Enterprise `S-1` from `2023-06-15` to `2024-06-15` at MRR `1000`, plus monthly Pro `S-2` from `2024-04-01` onward at MRR `200`; give `A-2` monthly Basic `S-3` from `2024-05-20` onward at MRR `300`. Add usage before and after the `2024-05-31` cutoff, one conflicting duplicated `usage_id`, one `A-1` ticket before signup, one future ticket, terminal churn for `A-1` on `2024-06-15`, and a later reactivation. Copy the exact column lists from `SCHEMAS`, assert `set(mini_tables) == set(RAW_TABLE_NAMES)`, and fill non-tested required fields with fixed valid values.

- [x] **Step 2: Write failing contract and quality tests**

```python
import pytest

from ravenstack_churn.contracts import DataContractError, add_usage_row_key, validate_contracts
from ravenstack_churn.quality import build_quality_report


def test_orphan_subscription_blocks_execution(mini_tables):
    mini_tables["subscriptions"].loc[0, "account_id"] = "A-missing"
    with pytest.raises(DataContractError, match="subscriptions.account_id.*1 orphan"):
        validate_contracts(mini_tables)


def test_conflicting_usage_ids_are_preserved_and_flagged(mini_tables):
    validated = add_usage_row_key(mini_tables["feature_usage"])
    assert validated["usage_row_id"].is_unique
    assert len(validated) == len(mini_tables["feature_usage"])
    report = build_quality_report({**mini_tables, "feature_usage": validated})
    assert report["contradictions"]["duplicate_usage_id_groups"] == 1


def test_churn_label_disagreement_is_reported(mini_tables):
    report = build_quality_report(mini_tables)
    assert report["contradictions"]["accounts_flag_vs_terminal_event"] == 2
    assert report["label_policy"] == "first_non_reactivation_event"
```

- [x] **Step 3: Verify both tests fail**

```bash
.venv/bin/python -m pytest tests/test_contracts.py tests/test_quality.py -v
```

Expected: FAIL because `contracts.py` and `quality.py` do not exist.

- [x] **Step 4: Implement explicit schemas and date parsing**

In `contracts.py`, define a `SCHEMAS` mapping for all columns and parse only these date fields: `signup_date`, `start_date`, `end_date`, `usage_date`, `submitted_at`, `closed_at`, `churn_date`. Parse booleans from `True` and `False`; reject any third value. Validate `arr_amount == 12 * mrr_amount` with exact integer arithmetic.

- [x] **Step 5: Implement critical-vs-warning validation**

Critical failures: missing file/column, unparseable value, duplicate primary key except `usage_id`, orphan foreign key, negative `mrr_amount`, `arr_amount`, counts or durations. Warning evidence: conflicting `usage_id`, event before signup, usage before subscription start, usage after subscription end, closed ticket before submission, and churn-label disagreement.

- [x] **Step 6: Encode the known-data assertions**

Add a test that loads the vendored data and asserts these observed counts so a dataset refresh cannot silently change conclusions:

```python
assert report["rows"] == {
    "accounts": 500,
    "subscriptions": 5000,
    "feature_usage": 25000,
    "support_tickets": 2000,
    "churn_events": 600,
}
assert report["contradictions"]["duplicate_usage_id_groups"] == 21
assert report["contradictions"]["usage_before_subscription"] == 19142
assert report["contradictions"]["usage_before_signup"] == 13198
assert report["contradictions"]["tickets_before_signup"] == 1077
```

- [x] **Step 7: Run the quality suite**

```bash
.venv/bin/python -m pytest tests/test_contracts.py tests/test_quality.py -v
```

Expected: PASS.

- [x] **Step 8: Commit contracts and quality evidence**

```bash
git add -f submissions/luis-roquette/solution/001-churn/src/ravenstack_churn submissions/luis-roquette/solution/001-churn/tests
git commit -m "feat(churn): validate inputs and expose data contradictions"
```

---

### Task 3: Build leak-free observed and strict account panels

**Files:**
- Create: `submissions/luis-roquette/solution/001-churn/src/ravenstack_churn/panel.py`
- Modify: `submissions/luis-roquette/solution/001-churn/tests/conftest.py`
- Test: `submissions/luis-roquette/solution/001-churn/tests/test_panel.py`

**Interfaces:**
- Consumes: parsed tables from `load_raw_tables` and constants from `config.py`.
- Produces: `first_terminal_churn(churn_events: pd.DataFrame) -> pd.Series` indexed by `account_id`.
- Produces: `mrr_lost_at_churn(subscriptions: pd.DataFrame, terminal_churn: pd.Series) -> pd.Series`, using each account's active subscriptions on the day before terminal churn.
- Produces: `build_account_panel(tables: dict[str, pd.DataFrame], cutoffs: pd.DatetimeIndex, chronology: Literal["observed", "strict"]) -> pd.DataFrame`.
- Produces columns: `account_id`, `cutoff`, `chronology`, `churn_next_30d`, `first_terminal_churn_date`, `mrr_active`, `billing_frequency`, `days_to_annual_renewal`, static account fields, and 7/30/90-day usage/support features.

- [x] **Step 1: Write the terminal-churn and future-leakage tests**

```python
import pandas as pd

from ravenstack_churn.panel import build_account_panel, first_terminal_churn


def test_first_terminal_churn_ignores_reactivation(mini_tables):
    result = first_terminal_churn(mini_tables["churn_events"])
    assert result["A-1"] == pd.Timestamp("2024-06-15")


def test_panel_excludes_events_after_cutoff(mini_tables):
    panel = build_account_panel(
        mini_tables, pd.DatetimeIndex(["2024-05-31"]), chronology="observed"
    )
    row = panel.loc[panel.account_id.eq("A-1")].iloc[0]
    assert row["tickets_30d"] == 1
    assert row["usage_count_30d"] == 4
    assert row["churn_next_30d"] == 1
```

- [x] **Step 2: Write the strict chronology sensitivity test**

```python
from ravenstack_churn.panel import build_account_panel, mrr_lost_at_churn


def test_strict_panel_excludes_pre_lifecycle_events(mini_tables):
    observed = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "observed")
    strict = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "strict")
    assert strict.loc[0, "usage_count_90d"] < observed.loc[0, "usage_count_90d"]
    assert strict.loc[0, "tickets_90d"] < observed.loc[0, "tickets_90d"]


def test_annual_renewal_uses_next_start_anniversary(mini_tables):
    panel = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "strict")
    annual = panel.loc[panel.account_id.eq("A-1")].iloc[0]
    assert annual["next_annual_renewal"] == pd.Timestamp("2024-06-15")
    assert annual["days_to_annual_renewal"] == 15


def test_mrr_lost_is_active_revenue_immediately_before_churn(mini_tables):
    terminal = first_terminal_churn(mini_tables["churn_events"])
    lost = mrr_lost_at_churn(mini_tables["subscriptions"], terminal)
    assert lost["A-1"] == 1200


def test_concurrent_subscriptions_preserve_revenue_and_mixed_dimensions(mini_tables):
    panel = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "strict")
    account = panel.loc[panel.account_id.eq("A-1")].iloc[0]
    assert account["mrr_active"] == 1200
    assert account["plan_tier"] == "mixed"
    assert account["billing_frequency"] == "mixed"


def test_incomplete_observation_window_is_null_not_zero(mini_tables):
    panel = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "strict")
    recent = panel.loc[panel.account_id.eq("A-2")].iloc[0]
    assert pd.isna(recent["usage_count_30d"])
    assert not bool(recent["usage_coverage_30d"])
```

- [x] **Step 3: Run the panel tests and verify failure**

```bash
.venv/bin/python -m pytest tests/test_panel.py -v
```

Expected: FAIL because `panel.py` does not exist.

- [x] **Step 4: Add derived panel fixtures**

Extend `tests/conftest.py` with `observed_panel` and `strict_panel`, both built from `mini_tables` at fixed cutoffs. These are the only panel fixtures used by later tests.

- [x] **Step 5: Implement account and subscription state at cutoff**

Include accounts with `signup_date <= cutoff` and no terminal churn on or before cutoff. Define active subscriptions as `start_date <= cutoff` and `end_date` null or `end_date > cutoff`; sum MRR and seats once per `subscription_id`. If no active subscription exists, set MRR to zero and emit `has_active_subscription=False`; do not backfill from a future subscription. Derive `plan_tier` and `billing_frequency` as the sole active value or `mixed` when active subscriptions disagree. For every active annual subscription, compute the smallest anniversary `start_date + DateOffset(years=n)` strictly after cutoff; account-level renewal is the minimum such date. Accounts with no annual subscription receive null renewal fields.

- [x] **Step 6: Implement time-window aggregation**

For each window `w`, select events in `(cutoff - w days, cutoff]`. Map usage to account through `subscription_id`. A support window is covered only when `signup_date <= cutoff - w days`; a usage window is covered only when that condition holds and at least one mapped subscription spans the full window. For covered windows, captured-event counts may be zero. For uncovered windows, count and aggregate metrics are null and their coverage flags are false. Response, resolution and satisfaction means are additionally null when no ticket carries the measured field; record the non-null response count and field coverage as `non_null_measured_tickets / tickets_in_window`, with null when there are no tickets. Create `usage_count_{w}d`, `usage_duration_{w}d`, `errors_{w}d`, `feature_breadth_{w}d`, `beta_share_{w}d`, `tickets_{w}d`, `escalations_{w}d`, `mean_first_response_{w}d`, `mean_resolution_{w}d`, `mean_satisfaction_{w}d`, `satisfaction_responses_{w}d`, structural coverage flags and measured-field coverage. In `strict`, also require event time on or after account signup and usage time on or after subscription start.

- [x] **Step 7: Implement trends and labels**

Add `usage_change_7_vs_30`, `usage_change_30_vs_90`, `error_rate_30d`, `ticket_change_30_vs_90`, `downgrade_90d`, `upgrade_90d`, `auto_renew_off`, `tenure_days`, and `churn_next_30d`. Compare non-overlapping daily rates: last 7 days versus the preceding 23, and last 30 versus the preceding 60; calculate change as `recent_rate / prior_rate - 1`. Use the same last-30-versus-prior-60 rule for ticket change. Define `error_rate_30d = errors_30d / usage_count_30d`; define `auto_renew_off=True` when any active annual subscription has auto-renew disabled. Safe division returns null when the prior denominator is zero, with a companion availability flag instead of coercing null to zero. At `SCORING_CUTOFF`, force `churn_next_30d` to null and `is_scoring_row=True`; never infer a December outcome not present in the data.

- [x] **Step 8: Verify panel shape, uniqueness and leakage**

```bash
.venv/bin/python -m pytest tests/test_panel.py -v
```

Expected: PASS, with unique `(account_id, cutoff, chronology)`.

- [x] **Step 9: Commit the temporal panel**

```bash
git add -f submissions/luis-roquette/solution/001-churn/src/ravenstack_churn/panel.py submissions/luis-roquette/solution/001-churn/tests/test_panel.py submissions/luis-roquette/solution/001-churn/tests/conftest.py
git commit -m "feat(churn): build leak-free temporal account panel"
```

---

### Task 4: Produce traceable diagnosis, segments and action ranking

**Files:**
- Create: `submissions/luis-roquette/solution/001-churn/src/ravenstack_churn/diagnosis.py`
- Modify: `submissions/luis-roquette/solution/001-churn/tests/conftest.py`
- Test: `submissions/luis-roquette/solution/001-churn/tests/test_diagnosis.py`

**Interfaces:**
- Consumes: observed and strict account panels plus churn feedback.
- Produces: `build_diagnostic_snapshot(panel: pd.DataFrame) -> pd.DataFrame`, one active row per account no último cutoff rotulado comum; o cutoff `2024-12-31` nunca entra na estimação e o outcome não escolhe uma data diferente por conta.
- Produces: `evaluate_candidates(observed: pd.DataFrame, strict: pd.DataFrame, churn_events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]` returning `findings` and `segment_metrics`.
- Produces: `build_claim_checks(strict_panel: pd.DataFrame) -> pd.DataFrame`, an auditable six-month reconciliation of overall versus next-30-day-churn usage and satisfaction.
- Produces finding columns: `finding_id`, `driver_group`, `claim`, `evidence_level`, `adjusted_odds_ratio`, `ci_low`, `ci_high`, `observed_effect`, `strict_effect`, `sensitivity_delta`, `source_tables`, `affected_accounts`, `mrr_exposed_max`, `confidence`, `counterevidence`, `limitation`, `immediate_action`, `structural_action`, `priority_rank`.

- [x] **Step 1: Add deterministic diagnosis fixtures**

Extend `tests/conftest.py` with `candidate_frames`, a tuple of observed panel, strict panel and churn events containing one stable and one direction-reversing candidate; `accepted_findings`, two fully populated passing rows whose MRR/reach order is unambiguous; and `claim_panel`, six monthly cutoffs where overall usage rises while the next-30-day-churn cohort falls and overall satisfaction is at least `4.0` while that cohort remains below `4.0`. Tests must not refer to production artifacts.

- [x] **Step 2: Write failing finding-gate tests**

```python
import pandas as pd

from ravenstack_churn.diagnosis import build_claim_checks, evaluate_candidates, rank_findings


def test_unstable_candidate_is_not_ranked(candidate_frames):
    findings, _ = evaluate_candidates(*candidate_frames)
    unstable = findings.loc[findings.finding_id.eq("F-product-usage-drop")].iloc[0]
    assert unstable["confidence"] == "inconclusive"
    assert pd.isna(unstable["priority_rank"])


def test_rank_uses_mrr_then_reach_then_actionability(accepted_findings):
    ranked = rank_findings(accepted_findings)
    assert ranked.finding_id.tolist() == ["F-support-escalation", "F-commercial-renewal"]


def test_zero_variance_candidate_is_inconclusive(candidate_frames):
    observed, strict, churn_events = candidate_frames
    observed = observed.assign(error_rate_30d=0.0)
    strict = strict.assign(error_rate_30d=0.0)
    findings, _ = evaluate_candidates(observed, strict, churn_events)
    row = findings.loc[findings.finding_id.eq("F-product-errors")].iloc[0]
    assert row["confidence"] == "inconclusive"
    assert row["failure_reason"] == "zero_variance"


def test_claim_checks_expose_aggregate_contradictions(claim_panel):
    checks = build_claim_checks(claim_panel).set_index(["claim_id", "cohort"])
    assert checks.loc[("C-usage-growth", "overall"), "status"] == "up"
    assert checks.loc[("C-usage-growth", "churn_next_30d"), "status"] == "down"
    assert checks.loc[("C-satisfaction-ok", "overall"), "status"] == "ok"
    assert checks.loc[("C-satisfaction-ok", "churn_next_30d"), "status"] == "concern"
```

- [x] **Step 3: Verify diagnosis tests fail**

```bash
.venv/bin/python -m pytest tests/test_diagnosis.py -v
```

Expected: FAIL because the diagnosis interfaces do not exist.

- [x] **Step 4: Define the candidate registry**

Use these auditable candidates and source groups:

```python
CANDIDATES = {
    "F-product-usage-drop": ("usage_change_30_vs_90", "lower", "product", "le", -0.30),
    "F-product-errors": ("error_rate_30d", "higher", "product", "ge", 0.10),
    "F-support-escalation": ("escalations_90d", "higher", "support", "ge", 1),
    "F-support-satisfaction": ("mean_satisfaction_90d", "lower", "support", "le", 3.0),
    "F-commercial-downgrade": ("downgrade_90d", "higher", "commercial", "eq", True),
    "F-commercial-renewal": ("auto_renew_off", "higher", "commercial", "eq", True),
}
```

Tuple fields are `(feature, expected_direction, driver_group, exposure_operator, exposure_threshold)`. GLMs use the measured feature; the final queue uses the declared operator and threshold. Thresholds are fixed before inspecting outcomes and may produce an inconclusive finding when reach is insufficient.

Controls: `industry`, `country`, `referral_source`, `plan_tier`, `billing_frequency`, `is_trial`, `log1p(mrr_active)`, `seats`, `tenure_days`, and cutoff calendar quarter.

- [x] **Step 5: Fit adjusted association models**

Fit one statsmodels binomial GLM per candidate on the diagnostic snapshot with HC3 robust covariance. Record odds ratio and 95% confidence interval. Do not call the coefficient causal. Mark association evidence as passing only when the expected direction holds and the interval excludes `1.0`. Before fitting, require two outcome classes and nonzero candidate variance. Convert perfect separation, singular matrix, non-convergence or non-finite coefficient/interval into `confidence=inconclusive` with a stable `failure_reason`; never abort the remaining candidates.

- [x] **Step 6: Add temporal and cross-table gates**

Require the candidate value to precede churn by construction. Corroborate product candidates with product `reason_code` or a separately passing pre-churn support signal; support candidates with support `reason_code` or a separately passing pre-churn product signal; commercial candidates with price/competitor `reason_code` or a separately passing pre-churn subscription change. A reason code corroborates only with at least `10` terminal churn events and prevalence ratio `>= 1.25` among exposed versus all terminal churn events. Require at least `30` exposed accounts, `10` churn outcomes and candidate coverage `>= 70%`, defined as non-null candidate values divided by eligible diagnostic-snapshot rows. Compare observed and strict effect direction and compute `abs(strict_effect - observed_effect) / max(abs(observed_effect), 1e-9)`; mark inconclusive if directions differ or this delta exceeds `0.25`.

- [x] **Step 7: Calculate opportunity and priority**

For each accepted finding, identify accounts exposed at `SCORING_CUTOFF`, sum `mrr_active` once per account as `mrr_exposed_max`, count reach, and rank by descending MRR, then descending reach, then actionability order `immediate > structural-only`. Findings may select only from this reviewed mapping, never generate free text:

```python
ACTIONS = {
    "product": {
        "immediate_action": "CS revisa em 7 dias as contas expostas e confirma o fluxo que perdeu uso.",
        "structural_action": "Produto e Engenharia corrigem em 30–90 dias o fluxo corroborado e medem a coorte.",
        "owner": "Head de Produto",
        "success_metric": "MRR perdido e uso de 30 dias da coorte exposta",
    },
    "support": {
        "immediate_action": "Suporte revisa em 7 dias escaladas abertas das contas expostas e define responsável.",
        "structural_action": "Support Ops ajusta em 30–90 dias triagem e SLA da causa corroborada.",
        "owner": "Head de Suporte",
        "success_metric": "MRR perdido, taxa de escalada e satisfação da coorte exposta",
    },
    "commercial": {
        "immediate_action": "CS revisa em 7 dias renovações próximas e mudanças contratuais das contas expostas.",
        "structural_action": "RevOps testa em 30–90 dias o playbook comercial na coorte exposta.",
        "owner": "Head de Receita",
        "success_metric": "MRR perdido e renovação da coorte exposta",
    },
}
```

- [x] **Step 8: Reconcile the CEO's two aggregate claims**

Use the last six labeled monthly cutoffs. Define `retained` as `churn_next_30d == 0`, `churn_next_30d` as `churn_next_30d == 1`, and `overall` as both cohorts. For `C-usage-growth`, calculate covered-account daily usage (`usage_count_30d / 30`), preserve the ordinary least-squares slope as context and classify `up`, `down` or `flat` by the endpoint change with tolerance `1e-9`; the executive wording must agree with the displayed start and end. For `C-satisfaction-ok`, calculate the ticket-response-weighted mean from `mean_satisfaction_90d` and `satisfaction_responses_90d`; status is `ok` only when mean is at least `4.0` and response coverage is at least `70%`, otherwise `concern`, with `insufficient` when either value is unavailable. Emit `claim_id`, `cohort`, `start_value`, `end_value`, `slope`, `status`, `coverage`, `cutoff_start`, `cutoff_end` and `limitation`. These are observed facts, not causal findings.

- [x] **Step 9: Produce segment metrics**

Generate churn count, churn rate, MRR lost, MRR exposed, sample size and coverage by `industry`, `country`, `referral_source`, derived `plan_tier`, derived `billing_frequency`, `is_trial`, and MRR band. Define MRR lost as `mrr_lost_at_churn`; never use refund or current MRR as a substitute. Suppress executive ranking for groups below the sample gates but retain them with `confidence=inconclusive`.

- [x] **Step 10: Run diagnosis tests**

```bash
.venv/bin/python -m pytest tests/test_diagnosis.py -v
```

Expected: PASS.

- [x] **Step 11: Commit traceable diagnosis**

```bash
git add -f submissions/luis-roquette/solution/001-churn/src/ravenstack_churn/diagnosis.py submissions/luis-roquette/solution/001-churn/tests/test_diagnosis.py submissions/luis-roquette/solution/001-churn/tests/conftest.py
git commit -m "feat(churn): rank traceable causes and segments"
```

---

### Task 5: Gate the optional predictive model outside time

**Files:**
- Create: `submissions/luis-roquette/solution/001-churn/src/ravenstack_churn/modeling.py`
- Modify: `submissions/luis-roquette/solution/001-churn/tests/conftest.py`
- Test: `submissions/luis-roquette/solution/001-churn/tests/test_modeling.py`

**Interfaces:**
- Consumes: strict-chronology panel and a fixed list of pre-cutoff features; never consumes churn flags, churn reasons, feedback, temporally invalid events or post-cutoff fields. The observed panel is diagnostic sensitivity evidence, not model input.
- Constant: `MODEL_FEATURES = ("mrr_active", "seats", "tenure_days", "days_to_annual_renewal", "usage_count_30d", "usage_change_30_vs_90", "error_rate_30d", "feature_breadth_30d", "tickets_30d", "ticket_change_30_vs_90", "escalations_90d", "mean_satisfaction_90d", "downgrade_90d", "auto_renew_off", "industry", "country", "referral_source", "plan_tier", "billing_frequency", "is_trial")`.
- Produces: `stable_account_split(account_ids: pd.Series) -> pd.Series`; bucket is `int(sha256(f"42:{account_id}".encode()).hexdigest()[:8], 16) % 100`, with `0–79` train and `80–99` test.
- Produces: `apply_model_gate(average_precision_gain: float, lift_at_20pct: float, brier_score: float, baseline_brier_score: float, segment_metrics_complete: bool = True) -> tuple[dict[str, object], None]`.
- Produces: `evaluate_model(panel: pd.DataFrame) -> tuple[dict[str, object], pd.DataFrame | None]` returning evaluation and optional current scores.
- Gate: publish only if `average_precision_gain >= 0.05`, `lift_at_20pct >= 1.25`, `brier_score <= baseline_brier_score`, and all eligible segments report metrics.

- [x] **Step 1: Add a deterministic model fixture**

Extend `tests/conftest.py` with `model_panel`: at least ten accounts, repeated monthly rows, both outcomes, known account hashes on both sides of the split and only the approved pre-cutoff feature columns. Assert the fixture itself has disjoint expected train/test account IDs.

- [x] **Step 2: Write failing split and gate tests**

```python
import pandas as pd

from ravenstack_churn.modeling import MODEL_FEATURES, apply_model_gate, stable_account_split


def test_accounts_never_cross_train_and_test(model_panel):
    split = stable_account_split(model_panel["account_id"])
    grouped = (
        pd.DataFrame({"account_id": model_panel.account_id, "split": split})
        .groupby("account_id")
        .split.nunique()
    )
    assert grouped.max() == 1


def test_failed_model_gate_returns_no_scores():
    evaluation, scores = apply_model_gate(
        average_precision_gain=0.01,
        lift_at_20pct=1.10,
        brier_score=0.20,
        baseline_brier_score=0.22,
    )
    assert evaluation["publish_model"] is False
    assert scores is None


def test_model_features_exclude_post_churn_sources():
    forbidden = {"churn_flag", "churn_date", "reason_code", "feedback_text", "refund_amount_usd"}
    assert forbidden.isdisjoint(MODEL_FEATURES)
```

- [x] **Step 3: Verify model tests fail**

```bash
.venv/bin/python -m pytest tests/test_modeling.py -v
```

Expected: FAIL because `modeling.py` does not exist.

- [x] **Step 4: Implement deterministic grouped, out-of-time evaluation**

Assign accounts with the exact SHA-256 formula declared in the interface. Train only on train-account cutoffs through `2024-08-31`. Test only on test-account cutoffs from `2024-09-30` through `2024-11-30`. Assert account sets are disjoint and every feature timestamp is at or before cutoff.

- [x] **Step 5: Fit baseline and interpretable candidate**

Use `DummyClassifier(strategy="prior")` as baseline and a pipeline of median imputation, one-hot encoding and `LogisticRegression(class_weight="balanced", max_iter=2000, random_state=42)` as candidate. Fit preprocessing only on training rows.

Select exactly `MODEL_FEATURES`; do not add IDs, names, raw dates, churn flags, reason codes, feedback, refunds or fields discovered after the cutoff.

- [x] **Step 6: Calculate operational metrics and gate**

Calculate average precision, Brier score, recall in the top 20% of ranked accounts and lift at 20%. Report the same metrics for eligible `plan_tier`, `billing_frequency` and MRR-band segments. Write `publish_model`, every threshold, observed metric and failure reason to the evaluation dictionary.

If train or test has a single outcome class, or an eligible segment cannot produce the required metric, set `publish_model=False`, record `single_class_split` or `incomplete_segment_metrics`, and return no scores instead of raising or weakening the gate.

- [x] **Step 7: Generate current scores only after passing**

When all gates pass, refit on strict labeled rows through `2024-11-30` and score active accounts from the strict feature-only `SCORING_CUTOFF` snapshot. Return `account_id`, `risk_probability`, `risk_rank`, and signed per-feature logistic contributions. When any gate fails, return `None`; downstream code must omit predictive claims.

- [x] **Step 8: Run model tests**

```bash
.venv/bin/python -m pytest tests/test_modeling.py -v
```

Expected: PASS.

- [x] **Step 9: Commit the optional model gate**

```bash
git add -f submissions/luis-roquette/solution/001-churn/src/ravenstack_churn/modeling.py submissions/luis-roquette/solution/001-churn/tests/test_modeling.py submissions/luis-roquette/solution/001-churn/tests/conftest.py
git commit -m "feat(churn): gate predictive risk outside time"
```

---

### Task 6: Publish canonical artifacts and executive report

**Files:**
- Create: `submissions/luis-roquette/solution/001-churn/src/ravenstack_churn/publish.py`
- Create: `submissions/luis-roquette/solution/001-churn/src/ravenstack_churn/cli.py`
- Modify: `submissions/luis-roquette/solution/001-churn/tests/conftest.py`
- Test: `submissions/luis-roquette/solution/001-churn/tests/test_publish.py`
- Create at runtime: `submissions/luis-roquette/solution/001-churn/artifacts/*`

**Interfaces:**
- Consumes: quality report, both panels, claim checks, findings, segment metrics, model evaluation and optional scores.
- Produces: `publish_artifacts(result: AnalysisResult, output_dir: Path) -> dict[str, Path]`.
- Produces: `validate_artifact_set(output_dir: Path) -> dict[str, object]`; raises `ArtifactConsistencyError` on mixed or incomplete runs.
- Produces: `compare_artifact_sets(reference_dir: Path, candidate_dir: Path) -> None`; compares canonical CSV/report checksums and manifest parameters while ignoring only run timestamp and source Git SHA.
- CLI: `python -m ravenstack_churn.cli reproduce --raw-dir data/raw --output-dir artifacts`.

- [x] **Step 1: Add the publication fixture**

Extend `tests/conftest.py` with `analysis_result`, built only from small in-memory DataFrames matching the `AnalysisResult` fields. After `publish.py` exists, add `generated_artifacts(tmp_path, analysis_result)` that calls `publish_artifacts` and returns the output directory for the app smoke test.

- [x] **Step 2: Write failing consistency tests**

```python
from dataclasses import replace

import pandas as pd
import pytest

from ravenstack_churn.publish import (
    ArtifactConsistencyError,
    publish_artifacts,
    validate_artifact_set,
)


def test_queue_and_report_use_same_finding_ids(analysis_result, tmp_path):
    paths = publish_artifacts(analysis_result, tmp_path)
    findings = pd.read_csv(paths["findings"])
    claim_checks = pd.read_csv(paths["claim_checks"])
    queue = pd.read_csv(paths["account_queue"])
    report = paths["report"].read_text()
    assert set(queue.finding_id).issubset(set(findings.finding_id))
    assert all(fid in report for fid in findings.query("confidence != 'inconclusive'").finding_id)
    assert set(claim_checks.claim_id) == {"C-usage-growth", "C-satisfaction-ok"}
    assert all(claim_id in report for claim_id in claim_checks.claim_id.unique())


def test_manifest_rejects_modified_artifact(analysis_result, tmp_path):
    publish_artifacts(analysis_result, tmp_path)
    (tmp_path / "findings.csv").write_text("changed")
    with pytest.raises(ArtifactConsistencyError, match="findings.csv checksum mismatch"):
        validate_artifact_set(tmp_path)


def test_no_accepted_finding_publishes_honest_empty_queue(analysis_result, tmp_path):
    result = replace(
        analysis_result,
        findings=analysis_result.findings.assign(confidence="inconclusive"),
    )
    paths = publish_artifacts(result, tmp_path)
    assert pd.read_csv(paths["account_queue"]).empty
    assert "Evidência insuficiente para priorizar uma causa" in paths["report"].read_text()
```

- [x] **Step 3: Verify publication tests fail**

```bash
.venv/bin/python -m pytest tests/test_publish.py -v
```

Expected: FAIL because publication interfaces do not exist.

- [x] **Step 4: Define the `AnalysisResult` data contract**

Use a frozen dataclass with `quality_report`, `panel`, `claim_checks`, `findings`, `segment_metrics`, `model_evaluation`, and optional `model_scores`. Keep DataFrames in memory; serialize only in `publish_artifacts`.

- [x] **Step 5: Build the operational queue**

Create one row per active account exposed to an accepted finding. Columns: `account_id`, `priority`, `finding_id`, `mrr_exposed_max`, `plan_tier`, `mrr_band`, `risk_probability`, `signals`, `immediate_action`, `structural_action`, `owner`, `status`. Copy the reviewed owner into `owner` and leave `status` empty. If the model is unpublished, leave `risk_probability` empty and rank by finding priority, MRR and reach. If no finding passes, write an empty CSV with these headers; do not promote model scores into an action queue without an accepted driver. Gere separadamente `account_watchlist.csv` com contas expostas a sinais descritivos, ordenadas por quantidade de sinais e MRR, sempre com `status=validation_only` e sem autorização de intervenção.

- [x] **Step 6: Generate the executive report from data**

Write `artifacts/report.md` with: executive decision; section `O que não bate` showing `C-usage-growth` and `C-satisfaction-ok` overall versus the next-30-day-churn cohort; top accepted cause; counterevidence; segment table; named priority accounts; one-week containment; 30–90-day correction; expected measurement; methodology and limitations. Insert metrics from DataFrames; do not hard-code numbers into prose. If no finding passes, replace the decision and action ranking with `Evidência insuficiente para priorizar uma causa`, list the failed gates, preserve the two claim checks and descriptive facts, keep the operational queue empty and name only validation accounts from the separate watchlist, explicitly without intervention authorization.

- [x] **Step 7: Write the run manifest last**

Include UTC generation timestamp, source git SHA, Python and dependency versions, input checksums, chronology modes, cutoffs, thresholds, artifact checksums, test status from `RAVENSTACK_TEST_STATUS`, and `publish_model`. `make reproduce` sets the status only after tests pass; a direct CLI run records `unknown`, never `passed`. Write other artifacts to temporary sibling paths and rename them before the manifest; the manifest marks a complete run. `compare_artifact_sets` ignores only metadata that must change between executions and fails on any changed data, report content, parameters or artifact checksums.

- [x] **Step 8: Implement the reproduce CLI**

The CLI loads, validates, profiles, builds both panels, reconciles the two aggregate CEO claims, evaluates findings, evaluates the optional model, publishes artifacts, validates the artifact set and exits non-zero on any critical failure. Print only paths and a compact gate summary; no secret or raw feedback text in logs.

- [x] **Step 9: Run publication tests**

```bash
.venv/bin/python -m pytest tests/test_publish.py -v
```

Expected: PASS.

- [x] **Step 10: Commit canonical publication**

```bash
git add -f submissions/luis-roquette/solution/001-churn/src/ravenstack_churn submissions/luis-roquette/solution/001-churn/tests/test_publish.py submissions/luis-roquette/solution/001-churn/tests/conftest.py
git commit -m "feat(churn): publish consistent diagnostic artifacts"
```

---

### Task 7: Build the three-view read-only Streamlit dashboard

**Files:**
- Create: `submissions/luis-roquette/solution/001-churn/app.py`
- Create: `submissions/luis-roquette/solution/001-churn/requirements.txt`
- Test: `submissions/luis-roquette/solution/001-churn/tests/test_app.py`

**Interfaces:**
- Consumes: only validated files under `artifacts/`.
- Produces: tabs named `Decisão executiva`, `Evidências`, and `Fila operacional` plus expander `Metodologia e limitações`.
- Produces: CSV download with the currently filtered queue.
- Runs from the solution directory and from the repository root used by Streamlit Community Cloud.

- [x] **Step 1: Write the failing Streamlit smoke test**

```python
from pathlib import Path
import tomllib

import pandas as pd
from streamlit.testing.v1 import AppTest


def test_dashboard_has_three_decision_views(generated_artifacts, monkeypatch):
    monkeypatch.setenv("RAVENSTACK_ARTIFACT_DIR", str(generated_artifacts))
    app = AppTest.from_file("app.py").run(timeout=20)
    assert not app.exception
    assert [tab.label for tab in app.tabs] == [
        "Decisão executiva", "Evidências", "Fila operacional"
    ]
    assert len(app.get("download_button")) == 1


def test_queue_filter_and_download_match_canonical_artifact(generated_artifacts, monkeypatch):
    monkeypatch.setenv("RAVENSTACK_ARTIFACT_DIR", str(generated_artifacts))
    app = AppTest.from_file("app.py").run(timeout=20)
    selected = app.selectbox(key="finding_filter").select("F-support-escalation").run()
    canonical = pd.read_csv(generated_artifacts / "account_queue.csv")
    expected = canonical.query("finding_id == 'F-support-escalation'")
    assert selected.dataframe[0].value["account_id"].tolist() == expected["account_id"].tolist()
    assert len(selected.download_button) == 1


def test_dashboard_runs_from_repository_root(generated_artifacts, monkeypatch):
    repo_root = next(
        parent
        for parent in Path(__file__).resolve().parents
        if (parent / "CONTRIBUTING.md").exists()
    )
    monkeypatch.chdir(repo_root)
    monkeypatch.setenv("RAVENSTACK_ARTIFACT_DIR", str(generated_artifacts))
    app_path = "submissions/luis-roquette/solution/001-churn/app.py"
    app = AppTest.from_file(app_path).run(timeout=20)
    assert not app.exception


def test_cloud_requirements_match_runtime_dependencies():
    project = tomllib.loads(Path("pyproject.toml").read_text())
    expected = set(project["project"]["dependencies"])
    actual = {line for line in Path("requirements.txt").read_text().splitlines() if line}
    assert actual == expected
```

- [x] **Step 2: Verify the smoke test fails**

```bash
.venv/bin/python -m pytest tests/test_app.py -v
```

Expected: FAIL because `app.py` does not exist.

- [x] **Step 3: Bootstrap paths and validate artifacts before rendering**

Set `SOLUTION_ROOT = Path(__file__).resolve().parent`, prepend `SOLUTION_ROOT / "src"` to `sys.path` before importing `ravenstack_churn`, and read `RAVENSTACK_ARTIFACT_DIR`, defaulting to `SOLUTION_ROOT / "artifacts"`. Call `validate_artifact_set` before any chart. On failure, call `st.error` with the exact reason and `st.stop()` with instruction to run `make reproduce`; never recalculate data in the app.

- [x] **Step 4: Implement executive view**

Show `O que não bate` from `claim_checks.csv`, then the top accepted finding, confidence, MRR exposed maximum, account reach, counterevidence, immediate action and structural action. Use a maximum of three charts: MRR/count churn trend, top causes, and segment exposure. Label every metric with its definition.

When no finding passes, render the same explicit inconclusive message and failed gates, hide cause ranking and action cards, and keep descriptive trend and quality evidence available.

- [x] **Step 5: Implement evidence view**

Add filters for finding, segment dimension and chronology. Display adjusted effect with interval, observed-vs-strict sensitivity, sample/coverage, source tables and limitations. Distinguish fact, association and hypothesis visually and textually.

- [x] **Step 6: Implement operational queue**

Filter by priority, finding, plan and MRR band. Display account ID, MRR exposed, signals and actions. Use `st.download_button` with the filtered DataFrame encoded as UTF-8 CSV. Keep `owner` and `status` editable only after download; the web app remains read-only. Quando a fila estiver vazia, mostrar e exportar a watchlist separada com aviso explícito de validação sem contato.

- [x] **Step 7: Add the Cloud runtime dependency file**

Create `requirements.txt` beside `app.py` with exactly:

```text
numpy==2.5.3
pandas==3.0.6
scikit-learn==1.9.1
scipy==1.18.1
statsmodels==0.15.0
streamlit==1.64.0
```

Do not add `packages.txt`; every dependency has a Python 3.12 Linux wheel and the app requires no apt package.

- [x] **Step 8: Add accessible, restrained theme**

Call `st.set_page_config(layout="wide")` before rendering. Add minimal in-app CSS for high-contrast text and visible focus states, plus color-independent status labels. Avoid custom JavaScript and ornamental animation. Do not create a nested `.streamlit/config.toml`: Community Cloud reads configuration only from the repository root, which is outside the allowed submission scope.

- [x] **Step 9: Run the dashboard test**

```bash
.venv/bin/python -m pytest tests/test_app.py -v
```

Expected: PASS.

- [x] **Step 10: Commit the dashboard**

```bash
git add -f submissions/luis-roquette/solution/001-churn/app.py submissions/luis-roquette/solution/001-churn/requirements.txt submissions/luis-roquette/solution/001-churn/tests/test_app.py
git commit -m "feat(churn): add decision-focused Streamlit dashboard"
```

---

### Task 8: Wire one-command reproduction and submission documentation

**Files:**
- Create: `submissions/luis-roquette/solution/001-churn/Makefile`
- Create: `submissions/luis-roquette/solution/001-churn/README.md`
- Modify: `submissions/luis-roquette/process-log/002-otimizacao-plano-loop.md`
- Modify: `submissions/luis-roquette/README.md`

**Interfaces:**
- Produces commands: `make setup`, `make test`, `make reproduce`, `make app`, and `make check`.
- `make reproduce` runs tests before generating and validating artifacts.
- `make check` runs Ruff, the full pytest suite, reproduction and artifact validation.

- [x] **Step 1: Write the Makefile with explicit targets**

```makefile
PYTHON := .venv/bin/python

.PHONY: setup test reproduce app check

setup:
	python3.12 -m venv .venv
	$(PYTHON) -m pip install --only-binary=:all: -e '.[dev]'

test:
	$(PYTHON) -m pytest -q

reproduce: test
	RAVENSTACK_TEST_STATUS=passed $(PYTHON) -m ravenstack_churn.cli reproduce --raw-dir data/raw --output-dir artifacts

app:
	RAVENSTACK_ARTIFACT_DIR=artifacts $(PYTHON) -m streamlit run app.py

check:
	$(PYTHON) -m ruff check src tests app.py
	$(PYTHON) -m pytest -q
	run_dir=$$(mktemp -d /tmp/ravenstack-check.XXXXXX); \
	RAVENSTACK_TEST_STATUS=passed $(PYTHON) -m ravenstack_churn.cli reproduce --raw-dir data/raw --output-dir "$$run_dir"; \
	$(PYTHON) -m ravenstack_churn.cli compare --reference-dir artifacts --candidate-dir "$$run_dir"
```

- [x] **Step 2: Run the full clean-environment contract**

```bash
make setup
make reproduce
make check
```

Expected: all commands exit `0`; `artifacts/run_manifest.json` reports a complete consistent run; `make check` reproduces into a temporary directory and proves substantive equality without modifying committed artifacts.

Run this block through the managed Codespace described in the execution convention; it documents what an evaluator can reproduce locally, not permission to install or run the full suite on the Mac host.

- [x] **Step 3: Write the solution README**

Document purpose, executive output, architecture, exact setup commands, file structure, data source and credit, artifact definitions, model gate, known contradictions, limitations, troubleshooting and local dashboard command. State that public hosting is optional and local reproduction is authoritative.

- [x] **Step 4: Complete the submission README**

Fill every field from `templates/submission-template.md`: name, LinkedIn, chosen challenge, 3–5 sentence executive summary, approach, findings, recommendations, limitations, AI-tools table, numbered workflow, where AI erred, human additions, evidence checklist and submission date. Link the report, dashboard instructions, CSV, Git history and all process logs (`000`, `001`, `002`); leave no bracketed template placeholder.

- [x] **Step 5: Record actual findings and corrections in the process log**

Append the commands executed, tool/version choices, dataset contradictions, failed hypotheses, model gate result, changes caused by human judgment and exact validation evidence. Preserve outputs and numbers; do not reconstruct the story after completion.

- [x] **Step 6: Commit documentation and generated artifacts**

```bash
git add -f \
  submissions/luis-roquette/README.md \
  submissions/luis-roquette/process-log/002-otimizacao-plano-loop.md \
  submissions/luis-roquette/solution/001-churn/Makefile \
  submissions/luis-roquette/solution/001-churn/README.md \
  submissions/luis-roquette/solution/001-churn/artifacts/account_panel.csv \
  submissions/luis-roquette/solution/001-churn/artifacts/account_queue.csv \
  submissions/luis-roquette/solution/001-churn/artifacts/account_watchlist.csv \
  submissions/luis-roquette/solution/001-churn/artifacts/claim_checks.csv \
  submissions/luis-roquette/solution/001-churn/artifacts/findings.csv \
  submissions/luis-roquette/solution/001-churn/artifacts/segment_metrics.csv \
  submissions/luis-roquette/solution/001-churn/artifacts/quality_report.json \
  submissions/luis-roquette/solution/001-churn/artifacts/model_evaluation.json \
  submissions/luis-roquette/solution/001-churn/artifacts/report.md \
  submissions/luis-roquette/solution/001-churn/artifacts/run_manifest.json
git commit -m "docs(churn): complete reproducible diagnostic submission"
```

---

### Task 9: Run clean preflight and publish the non-blocking demo

**Files:**
- Modify only if deployment succeeds: `submissions/luis-roquette/solution/001-churn/README.md`
- Modify only if deployment succeeds: `submissions/luis-roquette/README.md`
- Modify: `submissions/luis-roquette/process-log/002-otimizacao-plano-loop.md`

**Interfaces:**
- Consumes: committed solution and artifacts from Task 8.
- Produces: clean Codespace proof for the exact commit and, when available, a read-only Streamlit URL.

- [x] **Step 1: Inspect the global Codespace semaphore** — dispensado por instrução explícita do proprietário nesta execução.

```bash
codespace-manager list
```

Reuse only a stopped, clean Codespace for this repository. Do not start or delete one outside `codespace-manager`.

- [x] **Step 2: Prove the remote workspace contains the intended commit** — substituído por preflight local do SHA exato após bypass explícito.

```bash
: "${RAVENSTACK_CODESPACE:?export the clean stopped name returned by codespace-manager list}"
codespace-manager run "$RAVENSTACK_CODESPACE" -- 'git rev-parse HEAD && git status --short && cd submissions/luis-roquette/solution/001-churn && make setup && make check && cd ../../../.. && test -z "$(git status --porcelain)"'
```

Expected: reported SHA equals the local intended SHA, status is clean before and after the gate, every check exits `0`, and the committed artifacts match the fresh temporary reproduction. The shell variable contains external state selected from `codespace-manager list`, not a repository constant.

- [x] **Step 3: Verify the dashboard behavior against generated artifacts**

```bash
cd submissions/luis-roquette/solution/001-churn
.venv/bin/python -m pytest tests/test_app.py -v
```

Expected: the AppTest suite opens all three views, exercises the finding filter, creates the download payload and confirms displayed account IDs against the canonical queue. Visual browser review happens only on the optional public deployment; it is not a hidden local gate.

- [ ] **Step 4: Run the five-minute executive comprehension gate**

Give a nontechnical reviewer only `artifacts/report.md` and start a five-minute timer. Without coaching, ask them to state: the prioritized cause or the explicit inconclusive decision; the meaning of `MRR exposto — oportunidade máxima`; the one-week action; the 30–90-day action; and the main limitation. Pass only when all five are correct. Record elapsed time, answers and any wording correction in the process log; rerun after a material correction.

- [ ] **Step 5: Deploy the optional read-only app**

Pause here and request explicit current authorization to push the branch and create a public deployment. After approval, configure Streamlit Community Cloud with repository branch `submission/luis-roquette`, main file path `submissions/luis-roquette/solution/001-churn/app.py`, and Python 3.12. Add no secrets. If approval is absent or deployment fails, record that status and retain local reproduction as the authoritative deliverable.

- [ ] **Step 6: Verify persisted deployment before linking it**

Open the returned public URL, confirm all three views render from the committed artifacts, download the CSV and compare its SHA-256 with the repository artifact. Only then add the URL to both READMEs and commit:

```bash
git add -f submissions/luis-roquette/README.md submissions/luis-roquette/solution/001-churn/README.md submissions/luis-roquette/process-log/002-otimizacao-plano-loop.md
git commit -m "docs(churn): link verified public dashboard"
```

- [x] **Step 7: Prepare the Pull Request evidence**

Run from the repository root:

```bash
git fetch upstream main
test "$(git merge-base HEAD upstream/main)" = "$(git rev-parse upstream/main)"
test -z "$(git diff --name-only upstream/main...HEAD | rg -v '^submissions/luis-roquette/')"
test "$(git branch --show-current)" = "submission/luis-roquette"
```

Confirm that process logs `000`, `001` and `002` plus setup evidence are present, and use the single PR title `[Submission] Luis Roquette — Challenge 001`. Do not push, deploy or open the PR until the canonical preflight is green for the exact final SHA and the user has explicitly authorized those external actions in the current conversation.

---

## Requirements Traceability

| Requirement | Implementation | Executable evidence |
|---|---|---|
| Cross all five tables | Tasks 1–4 | contract, orphan, panel and corroboration tests |
| Explain churn without claiming proven causality | Task 4 | direction, confidence interval, chronology and sensitivity gates |
| Reconcile “usage grew” and “satisfaction is okay” | Tasks 4, 6 and 7 | six-month claim checks, canonical artifact and executive section |
| Identify risky segments and named accounts | Tasks 4 and 6 | segment thresholds plus action queue or validation-only watchlist |
| Prioritize concrete action by MRR | Tasks 3, 4 and 6 | MRR-at-churn test, deterministic ranking and shared finding IDs |
| Prevent leakage and expose contradictory dates | Tasks 2 and 3 | known-data assertions and observed-versus-strict panel tests |
| Keep model optional and useful outside time | Task 5 | grouped temporal split and fail-closed model gate |
| Keep report, dashboard and CSV consistent | Tasks 6 and 7 | manifest tamper test and AppTest-to-CSV comparison |
| Prove reproducibility and AI process | Tasks 8 and 9 | `make check`, clean-SHA Codespace proof and process logs |
| Let a nontechnical CEO decide in five minutes | Task 9 | timed five-answer comprehension gate recorded in the process log |

---

## Final Self-Review Checklist

- [x] Every requirement in the SPEC maps to at least one task and executable check.
- [x] The five CSVs are credited, checksummed and never silently mutated.
- [x] Observed and strict chronology variants are both produced and compared.
- [x] Findings that fail coverage, stability or evidence gates are visibly inconclusive and unranked.
- [x] The model can fail closed without breaking diagnosis, report, queue or dashboard.
- [x] Report, dashboard and CSV read the same canonical artifacts and manifest.
- [x] `claim_checks.csv`, report and dashboard answer the two contradictory executive claims with the same numbers.
- [x] No paid API, secret, external database or production-only dependency exists.
- [x] `make reproduce` and `make check` are sufficient from a clean Python 3.12 environment.
- [x] The dashboard starts from the repository root with the exact runtime pins in `requirements.txt` and no apt package.
- [x] Process logs contain actual prompts, mistakes, corrections, commands and validation evidence.
- [x] Only files under `submissions/luis-roquette/` are changed.
