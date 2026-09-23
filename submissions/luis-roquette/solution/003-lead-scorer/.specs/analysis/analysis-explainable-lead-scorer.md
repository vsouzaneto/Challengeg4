---
title: Codebase Impact Analysis - Implement explainable lead prioritization tool
task_file: .specs/tasks/todo/implement-explainable-lead-scorer.feature.md
scratchpad: .specs/scratchpad/942449e2.md
created: 2026-09-21
status: complete
---

# Codebase Impact Analysis: Implement explainable lead prioritization tool

## Summary

This is a greenfield application inside an existing challenge submission. The complete repository inventory contains no Python implementation, CSV data, dependency manifest, tests or CI workflows. The solution currently contains only `.gitignore` and SDD scaffolding. Consequently there are no existing executable entry points, signatures or callers to modify; future interfaces below are requirements, not discovered code.

- Files to modify: **2** existing Lead Scorer files.
- Files to create: **17** Lead Scorer-owned files plus **1** shared README integration owned by the orchestrator; minimum **20 affected paths** total.
- Files to delete: **0**. New test files: **3**.
- Risk: **High**, driven by statistical validity, data integrity, and unimplemented delivery gates, not legacy migration.

Counts exclude this phase's two analysis artifacts and later SDD plan artifacts. Evidence screenshot count can increase. In references below, `S/` means `submissions/luis-roquette/solution/003-lead-scorer/`; `P/` means `submissions/luis-roquette/process-log/`. `TASK` means `S/.specs/tasks/todo/implement-explainable-lead-scorer.feature.md`.

## Files to be Modified/Created

```text
submissions/luis-roquette/
├── README.md                           NEW; shared, orchestrator-owned integration
├── process-log/
│   ├── 003-lead-scorer.md               UPDATE; decisions and verified delivery evidence
│   └── screenshots/
│       ├── 003-lead-scorer-seller.png   NEW; browser evidence, proposed filename
│       └── 003-lead-scorer-manager.png  NEW; browser evidence, proposed filename
└── solution/003-lead-scorer/
    ├── .gitignore                      UPDATE; Python env/cache/generated local files
    ├── app.py                          NEW; Streamlit presentation and session state
    ├── data.py                         NEW; validation, joins, fingerprint, recovery CLI
    ├── scoring.py                      NEW; fitting, evaluation, ranking, explanation, actions
    ├── requirements.txt                NEW; pinned runtime/test requirements
    ├── README.md                       NEW; copyable setup/run/preflight, logic and limits
    ├── data/
    │   ├── manifest.json               NEW; source, CC0, expected checksums
    │   └── raw/
    │       ├── accounts.csv            NEW; real source data
    │       ├── products.csv            NEW; real source data
    │       ├── sales_teams.csv         NEW; real source data
    │       └── sales_pipeline.csv      NEW; real source data
    ├── scripts/preflight.sh            NEW; canonical gate, proposed filename
    ├── tests/
    │   ├── test_data.py                NEW; ingestion/recovery and real-data integration
    │   ├── test_scoring.py             NEW; modeling/priority/explanation contracts
    │   └── test_app.py                 NEW; role/navigation/session behaviors
    └── docs/evaluation.md              NEW; counts, route metrics, failures, validation revision
```

These are proposed minimal implementation locations, not pre-existing files. Test fixtures can remain in test modules. Recovery can be an explicit `data.py` CLI mode; a fourth application module is unnecessary. Keep versioned scoring/playbook configuration in `scoring.py` and include it in the fingerprint.

`P/000-pre-inicio.md:25` reserves the shared submission README for the orchestrator. Prepare the Lead Scorer section and evidence links for integration; do not independently replace the cross-challenge README. `CONTRIBUTING.md:41` forbids edits outside the participant folder.

## Useful Resources and Reuse

| Existing resource | Exact reference | Reuse |
|---|---|---|
| Challenge data contract | `challenges/build-003-lead-scorer/README.md:25` | Dataset source/license; table/key inventory at lines 27-45 |
| Official submission structure | `CONTRIBUTING.md:15` | Solution, process-log and docs placement |
| Submission narrative template | `templates/submission-template.md:19` | Approach, findings, recommendations, limits; process/evidence at lines 49-93 |
| Approved three-module design | `P/003-lead-scorer.md:906` | Boundaries and end-to-end behavior, not executable reuse |
| Existing versioning workaround | `P/000-pre-inicio.md:84` | Explicit scoped inclusion of ignored submission files |

Executable reusable utilities: **0**. Implemented similar scoring features: **0**. Shared executable abstractions/domain models: **0**. No installed dependency set exists to reuse. Standard-library hashing, JSON, paths, temporary files and download handling are appropriate prospective reuse; dependency/API choices and pins require validation during implementation.

## Key Interfaces & Contracts

No existing functions, classes or type signatures exist. Do not manufacture line numbers for proposed code. Required interface boundaries are sourced from approved design and task lines:

| Boundary | Required data/behavior | Evidence |
|---|---|---|
| `data.py` → `scoring.py` | Normalized opportunity records plus product/account/team attributes, row diagnostics and dataset fingerprint; preserve IDs and invalid active rows | `P/003-lead-scorer.md:908`; `TASK:34` |
| Historical records → four candidate routes | Won/Lost label only; chronological train/calibration/test; full and intentional no-account feature sets for each candidate; no final-stage/date/value derivatives or seller/team predictors | `TASK:42`; `TASK:49`; `P/003-lead-scorer.md:922` |
| `scoring.py` → `app.py` | Stage, route/origin, band, optional approved probability, optional expected revenue, potential price, factors, evidence size/strength, next action, insufficiency reason and diagnostics | `P/003-lead-scorer.md:912`; `TASK:59` |
| Session state → presentation | Temporary deal ID, manager, timestamp and recalculation association; never change model score | `TASK:29`; `P/003-lead-scorer.md:898` |
| Explicit recovery command → raw files | Verify all expected downloaded contents before replacement; preserve existing data on download/checksum failure; never invoked by app startup | `TASK:35`; `P/003-lead-scorer.md:726` |

The score result must make calibrated probability, relative priority and insufficient data distinguishable. All downstream displays, tie-breakers and totals must respect that distinction. Data/configuration fingerprint changes invalidate both training cache and stale temporary priorities; navigation/filter reruns must retain them within the same calculation.

## Planned Execution Flow, Not Existing Runtime

1. `app.py` obtains data/configuration identity and calls the cached pipeline. `data.py` reads four files, validates columns/types/keys/prices, normalizes `GTXPro` to `GTX Pro`, and performs validated many-to-one joins. Example: a valid active opportunity lacking account attributes remains present and is routed to fallback; an unknown product remains visible without a score. Global schema/critical-key/historical-split failures halt with file, cause and correction (`P/003-lead-scorer.md:934`).
2. `scoring.py` separates closed history from active rows, orders history by `close_date`, fits preprocessing and the two model families on training data, calibrates on the middle period, and evaluates predetermined full/fallback routes on the untouched final period. `close_value` serves financial evaluation only. Preprocessing learned from calibration/test rows would violate the temporal contract (`TASK:40`).
3. Each candidate/route records completion or controlled failure. Publication waits for all four outcomes. Passing routes provide probability bands; a failed publication gate suppresses probability and probabilistic revenue. Candidate selection compares Brier/log-loss baseline performance, band coherence, ranking and realized-value concentration, preferring logistic regression without consistent boosting gain (`TASK:49`; `P/003-lead-scorer.md:936`).
4. Active `Engaging` rows use their validated route; band precedes expected-revenue tie-breaking. Active `Prospecting` rows use smoothed closed-history aggregates over product/seller/account with backoff and evidence count, never a closing-probability label. Coefficient/local-tree contributions explain the actual Engaging score; a versioned deterministic playbook maps supported actionable factors to Portuguese recommendations (`TASK:54`; `TASK:60`; `TASK:66`).
5. `app.py` selects demonstrated role/identity, defaults seller to own portfolio and manager to team, filters independently of fitting, renders separate stage tabs and selected-deal details, and applies temporary manager pinning only to displayed order. New session/recalculation expires pins (`P/003-lead-scorer.md:892`).

Future architecture is a small modular application with a pure data/model boundary and presentation-owned session state. There is no evidence of Repository, Factory, API-service, persistent DB, authentication or event-bus patterns. Do not add them. No runtime generative/API provider is needed (`TASK:69`, `TASK:76`).

## Integration Points

| Point | Impact and necessary action |
|---|---|
| Dataset/license/schema | Four named CSVs and primary keys come from challenge README lines 25-45. CSV bytes are absent; verify actual schema, source, checksums, counts and join cardinality before implementation assumptions become assertions. |
| Module contracts | Data diagnostics and feature availability determine full/fallback/insufficient routing; model output controls UI language and numerical columns. |
| Cache/session boundary | Share computation across filters without persisting intervention state across sessions; data/configuration changes and explicit recalculation expire pins. |
| Verification/deployment | No existing workflow or gate exists. Add one canonical preflight, then browser evidence and Cloud verification of the same revision (`TASK:82`, `TASK:91`). |
| Versioning/submission | Root `.gitignore:16` ignores `submissions/`; confirmed by `git check-ignore`. New files can be omitted from normal status/add. Preserve root configuration; explicitly include only intended deliverables later. Coordinate README with orchestrator. |

External dependencies currently present in code: **none**. Required future runtime: Python 3.11, Streamlit, tabular processing and ML functionality. Exact libraries/transitive versions are not yet pinned; faithful tree attribution must be available if boosting wins. External services: explicit source recovery and post-gate Streamlit Community Cloud/GitHub delivery only, no application startup download or paid runtime AI call.

## Test Coverage and Verification Surface

There are no existing tests to update.

| New test location | Required coverage |
|---|---|
| `S/tests/test_data.py` | Missing/schema-invalid files, duplicate keys, typed values/prices, left-row preservation, GTXPro normalization, unknown products, missing accounts, checksum recovery failure preserving originals, fingerprint changes; one real-four-CSV integration. |
| `S/tests/test_scoring.py` | Allowed feature sets and forbidden derivatives; chronological isolation and tied dates; four routes and controlled candidate failures; sparse/single-class periods; Brier/log-loss and band gates; probability/revenue suppression; stable ordering and prices; faithful contributions; deterministic playbook; Prospecting smoothing/backoff/evidence. |
| `S/tests/test_app.py` | Seller/manager defaults, manager seller filtering, stage separation, row-detail selection, visible insufficiency, manager-only pin, author/time, score invariance and reset on new session/recalculation. |
| `S/scripts/preflight.sh` | Tests, import checks, complete real-data fitting/evaluation and Streamlit startup smoke; every failure returns nonzero. |
| Browser and evidence artifacts | Rendered seller/manager journeys including filters, tabs, details, insufficient data and temporary priority; screenshots plus actual revision/metrics. Startup alone is insufficient. |

The task makes local Python/venv reproduction authoritative (`TASK:75`); an earlier design paragraph describes running preflight in managed Codespaces (`P/003-lead-scorer.md:940`). Preserve a portable canonical command and document both execution location and exact verified revision; this analysis ran no tests/training and does not resolve infrastructure by silently running a gate.

## Algorithms, Performance and Risks

Prospective bounds, not measured implementation claims: hashing O(input bytes); expected hash joins O(opportunities + dimension rows), with O(joined cells) memory; temporal and final sorting O(n log n); logistic prediction O(n·features); tree prediction O(n·trees·depth); fixed-depth aggregate/backoff O(n·levels). Training complexity depends on chosen solver/estimator. Cache the deterministic trained result by data plus complete scoring configuration; do not retrain for filters. Dataset sizes in the README/log remain source statements until real CSV integration verifies them.

| Risk | Mitigation required before delivery |
|---|---|
| Leakage or test-set reuse falsely validates probability | Explicit feature allowlists and derivative checks; fit preprocessing only on train; set candidate/calibration/band decisions without iterative final-test tuning. |
| Full-route success incorrectly blesses fallback or weak bands | Route-specific diagnostics/gates and explicit safe routing; evaluate intentionally omitted account features on labeled history; explain that historical omission is not proof of representativeness for genuinely missing-account active rows. |
| Score/explanation mismatch after calibration | State contribution scale; verify contributions reconstruct the modeled score, distinguish calibration transformation, never present arbitrary reasons as local contributions. |
| Silent data loss, inflated joins or failed recovery overwrites | Validate unique dimension keys and row conservation, retain insufficiency diagnostics, validate complete recovery contents before replacing originals. |
| Delivery evidence and scope drift | Keep all changes within submission, include ignored intended files explicitly, preserve unrelated root changes, coordinate shared README, verify gates and rendered/live revision before completion claims. |

Remaining design details for the planning phase: temporal cutoff policy/tied-date handling, minimum classes/sample sizes, band coherence thresholds, candidate-selection rule, smoothing/backoff order, effective sample size definition, safe unknown-category behavior, calibrated-explanation scale and deterministic tie-breaker. These are specification decisions, not missing code paths that can be explored today.

## Essential Reading

- `S/.specs/tasks/todo/implement-explainable-lead-scorer.feature.md:15`: authoritative current requirements and scope.
- `P/003-lead-scorer.md:888`: approved design, failure behavior and delivery constraints.
- `challenges/build-003-lead-scorer/README.md:21`: real data contract and functional scoring requirement.
- `P/000-pre-inicio.md:25`: ownership of shared submission integration; line 84 explains ignored-file handling.
- `templates/submission-template.md:19`: required reviewable narrative and evidence structure.

## Verification Summary

| Check | Status | Evidence/limit |
|---|---|---|
| Affected existing files and proposed additions identified | Complete | Full no-ignore inventory; future filenames explicitly proposed |
| Entry points/call chains/type signatures | Not yet implemented | No Python source exists; approved future flow mapped without invented symbols |
| Integration points mapped | Complete | Data, modules, cache/session, verification/deployment, submission ownership |
| Similar patterns/reuse searched | Complete | Zero executable assets; documentation/approved contracts reused |
| Tests and risk assessed | Complete | No present tests; new coverage allocated to three modules plus gates/browser evidence |
| Self-critique | Complete | Six questions and findings recorded in scratchpad |

Limitations: repository inspection only. CSVs were not downloaded, metrics were not recomputed, dependencies were not installed, runtime/deployment was not exercised, and no implementation or Git mutation was performed. This Phase 2b report is not a judge verdict or a completed specification.
