# Step 01: Validated real-data snapshot and reproducible test foundation

**Task File:** `.specs/tasks/todo/implement-explainable-lead-scorer.feature.md`

> The task file moves between `.specs/tasks/{draft,todo,in-progress,done}/` as work progresses; if it is not at this path, resolve it by its filename under `.specs/tasks/`.

**Phase:** Phase 1
**Model:** opus
**Agent:** sdd:developer
**Depends on:** None
**Parallel with:** None
**Note:** Own data.py, requirements.txt, .gitignore, data/ and tests/test_data.py in this step. No final-test evaluation occurs until the dependency lock and C2 policy are frozen.

**Goal:** Load the four real CRM files as one trustworthy snapshot while preserving every opportunity and establishing the pinned test environment.

Apply architecture C1 and the acquisition/dependency parts of C5. Read the required research skill before edits. Acquire the actual four CC0 CSVs from the documented source, inspect their real headers, and freeze provenance and SHA-256 values rather than assuming illustrative counts. Implement read_snapshot(raw_dir, manifest_path, verify_checksums=True), load_dataset(snapshot) and fingerprint(snapshot, config) in data.py using immutable input byte buffers, pandas validated left joins and stdlib hashing. No scoring or automatic recovery runs here. This is data-integrity work and establishes the Dataset/Diagnostic boundary, so the complex tier overrides ordinary file count.

All paths are relative to `submissions/luis-roquette/solution/003-lead-scorer/` unless explicitly identified as repository paths. Read `.claude/skills/explainable-crm-prioritization/SKILL.md` and task contracts before edits. Keep writes within the participant submission, preserve unrelated work, and make no paid AI API calls.

#### Expected Output

- data.py with read_snapshot, load_dataset, fingerprint and C1 diagnostics; data/manifest.json; data/raw/{accounts,products,sales_teams,sales_pipeline}.csv
- requirements.txt with the complete compatible Python 3.11 dependency lock, including Streamlit, pandas, NumPy, SciPy, sklearn, Playwright and a `protobuf<6` pin compatible with Community Cloud; .gitignore for generated local/recovery artifacts
- tests/test_data.py with unittest fixture builders and the real-four-file integration harness, reused by later tests without a new helpers module

#### Success Criteria

- [x] TC-01, TC-04, TC-05, TC-06 and TC-07 pass via .venv/bin/python -m unittest discover -s tests -p test_data.py; TC-40 checks the generic snapshot/config digest contract.
- [x] IDs retain leading zeroes; normalization precedes uniqueness checks; GTXPro joins exactly one GTX Pro; opportunity counts reconcile across supported/unsupported/excluded rows.
- [x] Missing files/headers/checksum violations/critical duplicate keys block globally; row errors name record, field and correction; missing account permits later fallback; bad financial labels exclude financial evaluation only.
- [x] A fresh Python 3.11 venv installs requirements.txt, passes pip check and imports the required estimator, calibration, Streamlit AppTest and Playwright APIs; the managed Codespace bootstrap uses pinned `uv`, `uv python install 3.11` and `uv venv --seed --python 3.11`; candidate pins are corrected only from actual compatibility evidence before modeling policy freeze.

#### Subtasks

- [x] Acquire and verify the four real CSVs into data/raw/, recording exact headers, source/license/download or archive-member metadata and checksums in data/manifest.json.
- [x] Resolve and pin the complete Python 3.11 runtime/test dependency set in requirements.txt, including `protobuf<6`; use unittest rather than adding pytest/SHAP; add generated-path ignores to .gitignore without changing repository-root rules.
- [x] Implement data.py snapshot-byte reads with recovery-marker checks before/after; validate C1 schema, keys, finite numerics/dates/prices, normalize only approved aliases, perform cardinality-preserving joins and retain diagnostic accounting.
- [x] Implement data.py fingerprint over actual bytes, provenance/schema metadata, canonical supplied config and dependency digest; source identity will be added by the app caller without importing scoring into data.
- [x] Write tests/test_data.py fixtures and TC-01/04/05/06/07/40 tests, including financial-label isolation and exact boundary/error partitions; run them in the resolved environment and preserve measured acquisition evidence for docs/evaluation.md.

#### Blockers & Risks

| Type | Item | Impact | Likelihood | Mitigation / Resolution |
|------|------|--------|------------|-------------------------|
| Blocker | Upstream acquisition or actual CSV headers differ from the challenge contract | High | Medium | Stop with exact source/header discrepancy; do not fabricate rows, checksums, license or silently substitute a mirror. |
| Risk | Normalization/null joins multiply or silently discard opportunities | High | Medium | Normalize before unique-key validation; reject null dimension keys; validate many-to-one and reconcile every input row. |
| Risk | Research candidate versions do not install on Python 3.11 | High | Medium | Resolve in a clean disposable environment and test imports/fitting APIs before locking dependencies and examining final outcomes. |

#### Execution evidence — 2026-09-21

- Acquisition: versioned public Kaggle endpoint returned the ZIP; only the four named CSV members were extracted. Archive SHA-256: `74d535826330b616758ebb6bb393abf701a5126364a72fbe71003cb6a7a87a9c`.
- Stdlib verification passed all four SHA-256 values, exact headers, row counts and unique raw identities against `data/manifest.json`: 85 accounts, 7 products, 35 sellers and 8,800 opportunities.
- Descriptive source counts: Won 4,238; Lost 2,473; Engaging 1,589; Prospecting 500. There are 1,480 `GTXPro` aliases and 1,425 blank account cells. No final-test model evaluation was run.
- `python3.11 -m py_compile data.py tests/test_data.py` passed. Thirteen unittest methods cover TC-01/04/05/06/07/40; their runtime gate is pending the managed Python 3.11 environment. Compilation is not claimed as test execution.
- Dependency pins remain candidates until the fresh managed environment resolves the complete lock and passes imports plus `pip check`. Bootstrap candidate `uv==0.10.12` exists on PyPI and supports Python >=3.8.
- Feedback loop status: **BLOCKED**, not validated. Attempts 1 and 2 ended with manager exit 73 (`ShuttingDown`); between them the same Codespace was actively validating the separate `002-support` branch. Attempt 3 started through the manager but the long inline archive payload hit an apparent PTY input limit, leaving the remote shell at a continuation prompt before any Python gate ran. The doubtful assumption is that the manager's `ssh -tt` transport accepts one long base64 command line. A future retry must use bounded lines or another manager-mediated transfer and independently verify the transported source digest.
- Only this step's manager/SSH child processes were terminated. The manager returned 143 and its cleanup moved `codex-preflight-657v7q4ggx7f5557` to `ShuttingDown`; no other session/process was stopped. No fourth attempt was made. The complete dependency lock, `pip check`, import gate and thirteen runtime tests remain unverified; all corresponding checkboxes stay open.

#### Resumed feedback loop — 2026-09-21

- Transport repaired by carrying only code/manifest/tests with base64 folded into 1,000-character lines; real data is fetched separately from the pinned URL. The remotely checked source-archive digest was `6051eaa7416c96ace43c8d7d236290e6ff1d86dcedd4695b325a931e47fa8ea5`.
- Managed bootstrap `uv==0.10.12` selected CPython 3.11.16. Forty-four runtime/test packages were resolved and frozen, including `protobuf==5.29.5`. A second fresh seeded venv installed solely the resulting `requirements.txt`; `pip check` returned `No broken requirements found` and estimator/calibration/Streamlit AppTest/Playwright API imports passed. Local and remote lock SHA-256 both equal `43a420f22b5e31ceadf0946434689dca39359c7a69d358e4636ee6c0fb344843`.
- First runtime pass: 13 tests in 1.187 seconds, with one failure in TC-07. Root cause: pandas 3 represents empty normalized string cells as NaN; `raw is not None` incorrectly treated blank optional Prospecting dates as malformed. Replaced the missing-value guard with `pd.isna` and added a dedicated regression case. Fourteen tests now await the repeat gate; no assertion was weakened.
- Corrected repeat gate: **14/14 tests passed in 1.198 seconds**, including the new optional-date regression. A new clean seeded Python 3.11.16 venv installed the exact 44-package lock; `pip check` and every required API import passed again. These are managed Linux results, not a claim of local macOS installation or browser execution.
- The corrected source archive SHA-256 was verified before execution: `2c60c8d3e396b0b734d57c6a2a7209d6a6387e2a5a492ef4391121a4ba5b8609`. Remote source hashes match the local files: `data.py=a2f50da877e95e7f9b9a9ea7e3065abca85a99ccc6e556e8398991ba7e031609`; `tests/test_data.py=87e539decd6801acc3cee42bd6cdedf8aa9efec7ce34d5e2a45cf07eca186073`; requirements hash remains `43a420f22b5e31ceadf0946434689dca39359c7a69d358e4636ee6c0fb344843`.
- Real normalized accounting: 6,711 supported closed rows + 2,089 supported active rows = 8,800; all 6,711 financial labels are eligible. The 1,425 diagnostics identify account-free fallback, not discarded rows. Engaging: 501 full / 1,088 fallback; Prospecting: 163 full / 337 fallback. No naturally missing-account closed row exists. Data fingerprint with empty scoring config and the frozen lock: `a54b24cc98d69ab6976db2d97a3f63895bdc68a3dc81d2f1ea3f7c6f37aa0536`.
- Step status: **VALIDATED**. Only step 01 was executed; recovery, model-policy implementation, training/calibration/holdout evaluation, application UI and browser/live gates remain later steps.

#### Phase 1 review correction — iteration 1

- Reviewer finding: `load_dataset` mixed parsing, joins and row validation in 116 lines. Extracted cohesive private helpers in the same `data.py`: `_parse_table`, `_join_opportunities`, `_normalize_context`, `_normalize_dates` and `_normalize_opportunity`. The public coordinator now has 22 lines; all six functions have fewer than 50 lines. No fourth application module was introduced.
- Public contracts, diagnostic ordering, financial-label isolation and row-accounting rules remain unchanged. The recovery region beginning at `class RecoveryError` is byte-identical to the pre-refactor HEAD; manifest, raw CSVs, dependency lock and scoring policy were not edited. Local `py_compile` and `git diff --check` passed.
- Managed clean-environment gate: Python 3.11.16, pinned `uv==0.10.12`, seeded venv and exact 44-package lock; `pip check` passed. Complete `test_data.py`: **23/23 tests passed in 11.377 seconds**, including the existing 14 data tests and 9 recovery tests. This is managed Linux evidence, not a local macOS test claim.
- Transport archive SHA-256 verified before execution: `4d20d7934770f9f3b73fb7cb479a3ee12a390b2187a8741de80dcdac13305517`. Local/remote hashes match: `data.py=7e54969d5713a760d7cd0d5315185033c30de9b508538cdae64bc72ed6f7cccf`; `tests/test_data.py=d70261a71582061899c37bd4f93b2430f643eca7c5aefc0e6eda6b27e5884c5e`; manifest `b79e8d484d66dfa7c39bc7fe138169da84150548d8ec858aae18aad613abc5e2`; lock `43a420f22b5e31ceadf0946434689dca39359c7a69d358e4636ee6c0fb344843`.
- Feedback loop: plan/extract by responsibility → review unchanged contracts and recovery boundary → execute same-file refactor → full data gate green on its first run. Generic file-size guidance does not override the approved three-unit architecture. The separate recovery-review defect remains owned by step 02a; this passing regression suite does not claim that finding is resolved.
