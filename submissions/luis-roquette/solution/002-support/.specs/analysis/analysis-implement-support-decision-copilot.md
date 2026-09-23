# Codebase impact — Implement Support Decision Copilot

Date: 2026-09-21. Scope: codebase impact only; no implementation or task-section edits.

> **Estado histórico/superseded em 2026-09-22:** este documento retrata a análise
> pré-implementação. A autoridade atual é a task concluída em
> `.specs/tasks/done/implement-support-decision-copilot.feature.md`. Claims conflitantes
> sobre rubricas humanas obrigatórias, approve/edit real e preflight terminal verde foram
> superseded pelas emendas canônicas I61/I62, pela decisão de bypass do owner registrada
> em I64/I66 e pelo DoD 5/5. O PR não foi superseded: é o canal obrigatório de envio,
> ainda não executado nem presumido durante a construção. Consulte task, READMEs e diário.

## Inspected state and authority

- Workspace: `/Users/luisroquette/Projects/ai-master-challenge-worktrees/002-support`.
- Branch: `submission/luis-roquette-002-support`; inspected HEAD: `05f83d1be27c1b93c58e3eadd7a7b2b8279e723f`. Tracked worktree was clean at inspection; concurrent planning agents may add their own files later.
- Repository is documentation plus submission planning. There is no application code, dependency manifest, lockfile, test suite, Makefile, deployment configuration, or `.github/workflows` in the inspected tree. Existing public function definitions/callers: none. All signatures below come from the earlier implementation plan and remain proposed contracts, not verified implementations.
- Sources: `challenges/process-002-support/README.md`, `CONTRIBUTING.md`, `submission-guide.md`, `templates/submission-template.md`; submission research, process log, draft task, prior implementation plan and coverage audit.
- Canonical scope is the completed task at `.specs/tasks/done/implement-support-decision-copilot.feature.md`. The earlier plan at `docs/superpowers/plans/2026-09-21-support-decision-copilot.md` supplies historical candidate file locations and contracts; it is not current proof that any module or command works. Execution evidence and limitations live in the task, READMEs and process log.

Root `.gitignore` ignores `submissions/`. Existing submission documents are tracked through explicit additions; new descendants can be invisible to ordinary `git status` and `rg --files`. Inspection used `rg --files --hidden --no-ignore -g '!.git'` and `git ls-files`. Use explicit scoped additions when implementation is authorized; do not change root ignore rules or add the entire ignored tree. Local solution `.gitignore` currently contains only `.specs/scratchpad/`.

## File impact inventory

Paths in this section are relative to `submissions/luis-roquette/`. The estimated implementation inventory is **28 creates, 3 modifications, 0 deletions**. It follows the existing plan, including its two retrieval rubrics omitted from its overview tree. Counts exclude generated/ignored runtime artifacts and the current SDD planning outputs. Architecture synthesis may consolidate files; there is no legacy migration.

| Action | Exact path | Impact |
|---|---|---|
| Create | `README.md` | Official evaluator template, findings, evidence and process links |
| Create | `solution/002-support/README.md` | Prerequisites, commands, limitations, artifacts, reproduction |
| Create | `solution/002-support/pyproject.toml` | Python package, dependencies, pytest import path, Ruff configuration |
| Create | `solution/002-support/requirements.lock` | Exact tested dependency environment |
| Create | `solution/002-support/Makefile` | Doctor, setup, data, reproduction, app and validation commands |
| Create | `solution/002-support/.streamlit/config.toml` | Local Streamlit configuration |
| Create | `solution/002-support/app.py` | Framework proof followed by final four-page entrypoint |
| Create | `solution/002-support/scripts/reproduce.py` | Deterministic artifact pipeline and CLI |
| Create | `solution/002-support/src/support_copilot/__init__.py` | Package import boundary |
| Create | `solution/002-support/src/support_copilot/data.py` | Schemas, sanitization, stable IDs, splits, source manifest |
| Create | `solution/002-support/src/support_copilot/analytics.py` | Valid durations, denominators, associations, scenarios |
| Create | `solution/002-support/src/support_copilot/modeling.py` | Separate domain models, validation, calibration, metrics |
| Create | `solution/002-support/src/support_copilot/decision.py` | Deterministic risk gate and queue ordering |
| Create | `solution/002-support/src/support_copilot/retrieval.py` | Training-only search, sources, rubric workflow, abstention |
| Create | `solution/002-support/src/support_copilot/store.py` | SQLite transactions, action records, CSV export |
| Create | `solution/002-support/src/support_copilot/ui.py` | Queue, scorecard, IT lab, evidence, validated loading |
| Create | `solution/002-support/tests/test_data.py` | Schemas, PII, invalid input, disjoint and stable splits |
| Create | `solution/002-support/tests/test_analytics.py` | Interval quarantine, denominators, honest scenarios |
| Create | `solution/002-support/tests/test_modeling.py` | Domain isolation, baseline fallback, test exclusion |
| Create | `solution/002-support/tests/test_decision.py` | Risk precedence, all confidence and validity boundaries |
| Create | `solution/002-support/tests/test_retrieval.py` | Safe index, source provenance, rubric locking, abstention |
| Create | `solution/002-support/tests/test_store.py` | Atomicity, action validation, sanitization, safe export |
| Create | `solution/002-support/tests/test_workflow.py` | Pipeline reproducibility, artifact failures, UI persistence |
| Create | `solution/002-support/evidence/metrics.json` | Reviewed measured model and retrieval evidence |
| Create | `solution/002-support/evidence/operational-summary.json` | Reviewed aggregate operational evidence |
| Create | `solution/002-support/evidence/screenshot.png` | Real rendered app evidence after privacy review |
| Create | `solution/002-support/evidence/retrieval-calibration-rubric.csv` | Human scores used to lock retrieval threshold |
| Create | `solution/002-support/evidence/retrieval-test-rubric.csv` | Separate unseen final human evaluation |
| Modify | `solution/002-support/.gitignore` | Exclude raw inputs, model artifacts, environments, SQLite runtime and caches |
| Modify | `research/002-support.md` | Record actual framework reproduction and resulting exact dependency decisions |
| Modify | `process-log/002-support.md` | Contemporaneous decisions, failed checks, corrections and proof |

No change is needed to repository README, challenge descriptions, templates, LICENSE, CONTRIBUTING, sibling challenges, production services, or deployment workflows. The prior plan/audit are reference documents; this analysis does not rewrite them. If architecture changes a decision, reconcile derived planning references explicitly during the responsible planning phase.

## Planned interfaces and consumers

These signatures are transcribed from the earlier plan. Types and return shapes not specified there are explicitly unresolved; do not treat illustrative fixture functions as existing helpers.

| File | Planned public interface | Consumers / integration obligations |
|---|---|---|
| `data.py` | `DatasetSplit(train, calibration, test)`; `load_customer_tickets(path)`; `load_it_tickets(path)`; `sanitize_text(value, names=())`; `sanitize_customer_frame(frame)`; `make_split(frame, target, random_state=42)`; `write_manifest(paths, destination)` | Analytics, models, retriever, pipeline. Validate raw inputs and sanitize both domains before downstream text consumption. Manifest must carry source hashes, stable split IDs and versions; the proposed `write_manifest` signature does not yet explain how split/model metadata reaches it. |
| `analytics.py` | `add_operational_fields(frame)`; `grouped_bottlenecks(frame)`; `recoverable_excess_hours(frame)`; `satisfaction_associations(frame)`; `operational_summary(frame)`; `scenario_projection(summary, assumptions)` | Pipeline and scorecard. Return serializable counts/denominators and clearly typed scenario assumptions; exact return schemas remain to be fixed in architecture. |
| `modeling.py` | `Prediction(label, confidence, probabilities, model_version)`; `candidate_pipelines()`; `select_candidate(train, text, target)`; `train_domain_model(domain, split)`; `evaluate_frozen_test(model, test)`; `DomainModel.predict(text)` | Routing, pipeline, IT lab. Plan prose shows scalar predict while its example passes a list: choose one explicit scalar/batch contract. `classification_unsupported` state must be representable without fabricating calibrated probabilities. |
| `decision.py` | `RouteDecision(action, reason_codes)`; `priority_score(priority, confidence, risk_count)`; `decide_route(prediction, signals, threshold)` | Queue, IT lab, audit. `TicketSignals` appears in an example but its fields/type are unspecified. Domain, invalid/OOD status, known priority and sensitive rules must be explicit inputs. |
| `retrieval.py` | `fit_retriever(train_closed)`; `TicketRetriever.suggest(text, threshold=...)`; `evaluate_retriever(retriever, unseen, rubric_path)`; `python -m support_copilot.retrieval prepare-review` | Queue and reproduction. Return source IDs/scores, status and nullable draft. CLI flags, rubric state/version contract and return schema remain unresolved. |
| `store.py` | `initialize_store(path)`; `record_decision(connection, event)`; `list_decisions(connection)`; `export_decisions_csv(connection)` | UI form and evidence download. `DecisionEvent` mentioned without fields/type; proposed SQL schema supplies fields but not validation rules or unavailable-model null semantics. |
| `ui.py` | `load_artifacts(root)`; `render_queue()`; `render_scorecard()`; `render_it_lab()`; `render_evidence()` | `app.py` registers page callables; UI tests use AppTest. Validate before deserialization and isolate failed features. Do not train, mutate thresholds, send externally or learn from decisions. |
| `scripts/reproduce.py` | `python scripts/reproduce.py --customer data/raw/customer_support_tickets.csv --it data/raw/all_tickets_processed_improved_v3.csv --output artifacts` | Makefile. Produce source/split/model/policy metadata and separately addressable feature artifacts; missing human rubrics must permit source-only operation. |

The proposed audit table has `id`, `created_at`, `ticket_id`, `domain`, `data_version`, `model_version`, `rules_version`, `threshold`, `suggested_label`, `confidence`, `gate_action`, `reason_codes`, `human_action`, `human_reason`, `suggestion_text`, `final_text`, `edit_ratio`. Several prediction fields are `NOT NULL` in the prior plan, conflicting with required review/audit when a model is absent or unsupported. Resolve this in the contract rather than inserting fictitious labels/confidence. Sanitize edited responses and human notes at the persistence boundary; sanitizing only imported data is insufficient.

## Integration map and reusable assets

No code can currently be reused from this repository. Reuse the official README template, research comparisons, approved requirements and process-log pattern. The selected plan already favors native Streamlit UI and Python stdlib `sqlite3`, `csv`, `json`, `hashlib`, `difflib`; do not introduce helpdesk clients, cloud services, provider keys or additional infrastructure.

The proposed integration chain is raw CSV → per-domain schema validation and sanitization → independent split manifests → analytics/models/retriever → versioned artifacts and deterministic gate → UI → sanitized SQLite audit → CSV export. Analytics is Dataset 1 only; classification shares code but not rows, target labels or models. Retrieval indexes only sanitized closed Dataset 1 training resolutions; customer frozen-test rows supply demonstration queries. The bridge between domains is an explanatory automation-opportunities report, never a record-level join or one taxonomy predicting the other.

Runtime artifact paths under `solution/002-support/artifacts/`: `manifest.json`, `risk-policy.json`, `analytics/operational-summary.json`, `analytics/bottlenecks.csv`, `analytics/waste-opportunities.csv`, `analytics/satisfaction-associations.csv`, `analytics/satisfaction-model.json`, `analytics/automation-opportunities.csv`, `models/customer.joblib`, `models/it.joblib`, `models/metrics.json`, `retrieval/customer.joblib`, `retrieval/metrics.json`, `review/retrieval-calibration-template.csv`, `review/retrieval-test-template.csv`, `queue/customer-test.csv`. These are regenerated, ignored outputs, not 16 additional public implementation files. SQLite path is not specified by existing documents and must be resolved within an ignored local runtime location.

External setup integration is limited to public Kaggle download and dependency installation; inference and interaction must work offline after setup. Thus “no external service” must not be confused with “fresh setup without internet.” Raw source CSVs are absent from the inspected workspace. Row counts and invalid-interval counts in existing research are prior observations, not newly verified dataset facts. The implementation must recompute them and fail visibly on schema/hash drift.

## Risk and unresolved contract assessment

Overall implementation risk: **High**, driven by data privacy, statistical validity, fail-closed safety and unproven first-run setup; existing-code regression risk is low because there is no runtime code.

| Severity | Evidence / location | Required resolution or verification |
|---|---|---|
| High | `data.py` proposed sanitization; IT has no customer-name column; freeform UI edits and rubric notes add new text | Explicitly handle known names, emails/phones and unsupported name detection; test both domains plus edited responses/reasons. Do not claim universal PII removal from a known-name test. No raw text in screenshots or public artifacts until reviewed. |
| High | Prior plan Task 4 sets threshold `1.0` to mean disable, while Task 5 blocks only confidence below threshold | Probability exactly `1.0`, NaN, infinity, malformed distributions and unsupported status need explicit rejection/disabled semantics. Test boundaries; threshold alone cannot encode disabled automation safely. |
| High | Row-number-based IDs distinguish duplicated content; only ID non-overlap is proposed in Task 2 | Audit normalized duplicate/near-template text before splitting; independent IDs do not prove content independence. Record a defensible grouping policy or demonstrate absence; never fit preprocessing before CV splits. |
| High | Calibration rows used both to fit calibration and select policy threshold in Task 4 | Distinguish fitted-set policy selection from independent error estimates; keep final test untouched and report uncertainty/support. Resolve calibration protocol before fitting; do not relabel selection-set error as test performance. |
| High | Task 7 emits frozen-test queue/metrics while retrieval threshold awaits human rubric | Enforce phase ordering: seal test access until model, calibration, risk policy and retrieval decision are locked. Missing rubric means disabled drafts/source-only, not premature tuning from test. Subsequent reproduction must not retune from final evidence. |
| High | Task 5 gate names OOD/ambiguous/sensitive detection without operational input or algorithm | Define observable invalid/OOD/risk signals and regression cases; calibrated confidence alone cannot establish OOD safety. Risk must override confidence and fail closed on missing artifacts. |
| High | Proposed audit schema demands nonnull prediction values despite missing-model review mode | Resolve unavailable fields and action validation; preserve factual missingness. Require reasons for reject/escalate, transactional writes, safe free-text handling and recovery after failed save. |
| High | `joblib` artifacts loaded by UI; CSV exported to user | Validate trusted local artifact paths/version/hash before deserialization; never accept arbitrary uploaded pickle/joblib. Test spreadsheet formula-like text in CSV without losing audit meaning. |
| Medium | Dataset 1 interval assumptions differ from approximate challenge brief | Recompute denominators, negative interval quarantine and eligible-row counts. Label interval after first response only; observed associations/opportunity proxies are not causal savings or measured costs. |
| Medium | Task 1 proposed installable `src` package has no package files until Task 2 | Reproduce package discovery and bootstrap from a clean checkpoint; empty package layout may break editable installation. Framework proof must include actual navigation/form/SQLite/download, not only health HTTP. |
| Medium | Task 1/8 shell smoke uses semicolon-separated curl, kill, wait | Preserve startup/curl exit status and cleanup independently: a later successful kill-status assertion must not mask failed health validation. No existing command is implemented or validated. |
| Medium | `make demo` always calls setup/data/reproduction; planned second artifact run compares hashes | Verify idempotency, legitimate offline reruns and logical determinism; `generated_at` must be documented and volatile storage/compression fields must not be mistaken for model changes. |
| Medium | Root ignore excludes new submission files; full-tree staging suggested by some previous task steps | Stage exact public paths; verify raw files, runtime databases, model binaries and ignored scratchpads stay out of commits. Final diff must stay under `submissions/luis-roquette/`. |
| Medium | Prior plan assumes approved Codespace lifecycle and framework compatibility | Follow current user authority: managed execution, never active/dirty reuse, no automatic deletion under latest global instruction. Inspect actual provider/runtime availability when implementation starts; no paid model API fallback. |

## Verification implications

There are **no runnable project gates today**. `make doctor`, `make test`, `make lint`, `make reproduce`, `make demo`, pytest and Ruff are intended outputs, not current commands. No dependency installation, data download, training, Codespace execution, push, PR or service change was performed for this analysis.

Implementation verification must cover schema and privacy boundaries; valid/invalid interval reconciliation; separate CV/calibration/frozen-test lifecycle; explicit unsupported-model/disabled states; high-confidence risky input; training-only retrieval provenance; missing/stale human rubrics; safe transaction/export; feature-specific unavailable artifacts; real rendered UI action → committed audit ID → reload → export. Prefer focused tests in the listed files rather than a new test framework or service. Heavy installation, complete tests and reproduction use the managed Codespace on the exact intended SHA/diff. Verify final screenshot/export and metric evidence, not merely server health.

The next planning phase must resolve the named contract gaps while preserving approved scope. This analysis neither approves implementation nor supplies business acceptance criteria or phase decomposition.
