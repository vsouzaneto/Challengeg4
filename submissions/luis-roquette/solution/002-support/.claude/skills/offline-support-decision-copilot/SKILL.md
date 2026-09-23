---
name: offline-support-decision-copilot
description: Research and validate local support decision prototypes with calibrated text classification, evidence-only retrieval, human review and auditable offline persistence. Use when implementing or reviewing these capabilities without external AI APIs.
---

# Offline support decision copilot

Use this skill for research-backed implementation and review of small, local support workspaces. It supplies reusable engineering guidance; the task specification owns scope, thresholds and acceptance criteria.

## Start with evidence

Read the task, dataset manifests, existing research and dependency lock before selecting tools. Separate documented API support, reproduced behavior, measured dataset results and hypotheses. A library's health endpoint does not demonstrate its decision workflow.

For a new framework, inspect three viable candidates and reproduce the smallest complete interaction before committing to the choice. Prefer an existing implementation, standard library or installed dependency. Do not add an orchestration framework, vector database, remote model or separate frontend for this prototype pattern.

The current research recommends Streamlit for an operational queue plus analytics, Gradio when inference is the primary interaction, and Dash when explicit callback-driven dashboard behavior justifies more wiring. These are fit judgments, not measured performance comparisons. Official repositories: [Streamlit](https://github.com/streamlit/streamlit), [Gradio](https://github.com/gradio-app/gradio), [Dash](https://github.com/plotly/dash).

## Local UI and persisted decisions

Use native forms to submit a coherent human decision in one interaction; bind editor state to a stable ticket key. Streamlit reruns must not create duplicate records or apply one ticket's draft to another. Keep suggestion and final response separate. After saving, read the record back through a new connection and exercise a fresh UI session. [Forms documentation](https://docs.streamlit.io/develop/concepts/architecture/forms).

Use `sqlite3` with parameterized SQL, explicit transaction handling, and a database uniqueness constraint for a submission identifier. A connection context manager handles transaction outcome but does not close the connection; close it explicitly. For Python 3.12, set transaction behavior explicitly rather than depending on a changing default. [Python SQLite documentation](https://docs.python.org/3.12/library/sqlite3.html).

Test a multipage Streamlit app from its entrypoint, then call `switch_page(...).run()` for file-based pages. `AppTest` simulates app execution; separately inspect rendered UI and an actual downloaded file. Pin and reproduce the exact version: the reference inspected on 2026-09-21 documents v1.64.0 behavior. [AppTest reference](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest).

## Data privacy and honest analytics

Treat ingestion, human edits, export and logs as privacy boundaries. Remove direct identifier columns and sanitize free text before training or writing derived artifacts. Email/phone regexes and known-name replacement are a baseline, not proof that arbitrary names, addresses or account identifiers are absent. Use adversarial examples and manually inspect a sanitized sample; quarantine uncertain text instead of declaring perfect anonymization. Never place raw examples in a public regression fixture.

Report each metric's eligible count, missing count and exclusion rule. Validate timestamp parsing and ordering; absent start events cannot be reconstructed from an endpoint timestamp. Distinguish observed intervals, associations and editable cost scenarios. Zero eligible rows means unavailable, not zero duration or zero risk.

CSV exports need both PII controls and spreadsheet-formula controls. Quoting alone does not neutralize formula-like cell values; test dangerous leading characters and whitespace/control-character variants in the target spreadsheet workflow. Preserve the sanitized stored value while applying the documented export policy. [OWASP CSV injection](https://community.owasp.org/attacks/CSV_Injection).

## Classification, calibration and abstention

Compare a dummy baseline with TF-IDF plus MultinomialNB, LogisticRegression and LinearSVC. Put vectorization inside each cross-validation pipeline so vocabulary and IDF are fitted only on its training fold. Select on development folds, record variance and class support, then freeze the selection before looking at final test results. [Official text example](https://scikit-learn.org/stable/auto_examples/model_selection/plot_grid_search_text_feature_extraction.html), [leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html).

Keep distinct domains' rows, labels, fitted vectorizers, models, calibration data and metrics separate. Deduplicate or group repeated/template text before splitting; different row IDs alone do not establish independent examples. Where grouping is necessary, inspect class balance and use a group-aware split, documenting any infeasible stratification. [StratifiedGroupKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html).

Fit calibration on examples disjoint from base-model fitting. An already-fitted model can be wrapped with `FrozenEstimator` and calibrated with `CalibratedClassifierCV`; ensure the wrapper includes fitted preprocessing. Start with sigmoid, compare native probabilities where available, and use isotonic only with enough data and measured benefit. Choose gate thresholds on held-out development predictions; never fit a calibrator and report its training predictions as unbiased policy performance. The final test remains untouched until model, calibration and thresholds are locked. [Calibration guide](https://scikit-learn.org/stable/modules/calibration.html), [FrozenEstimator](https://scikit-learn.org/stable/modules/generated/sklearn.frozen.FrozenEstimator.html).

Calibration is not an out-of-distribution detector or a safety guarantee. Invalid, empty, zero-vector, unsupported-domain, ambiguous or risk-flagged input must reach human review even when the model emits high confidence. Treat numerical values outside their valid ranges as invalid. Risk rules take precedence over model confidence.

Publish macro-F1, per-class metrics/support, confusion matrix, calibration diagnostics, and risk versus coverage. Define coverage as eligible automatic decisions divided by the stated evaluated population; selective error uses accepted decisions as denominator. An empty accepted set has undefined risk, not perfect safety. Show the number of accepted examples so tiny samples cannot masquerade as reliable evidence.

## Retrieval with evidence-only drafts

Start with TF-IDF and cosine similarity over sanitized, allowed historical examples. The score is normalized vector similarity, not a probability of correctness. Keep held-out query tickets, their resolutions and duplicate groups out of the reference index. Retrieve on issue text; return provenance, score, safe resolution excerpt and eligibility reasons. [Cosine similarity reference](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html).

Evaluate unseen queries with human relevance, correctness, safety and editing-effort judgments before selecting a threshold. Also inspect missing, generic, contradictory and unsafe resolutions. When there is no safe precedent, explicitly abstain; do not invent a response, call an LLM, or lower a threshold to force a demonstration. Benchmark BM25 or local embeddings only if lexical retrieval fails in a measured, relevant way and the added dependency has its own reproduced evidence.

## Reproducibility and small checks

Persist source fingerprints, split IDs, sanitizer version, labels, chosen model, calibration/policy settings and exact package versions. Refuse mismatched artifacts with an actionable regeneration command. `joblib` and pickle-based formats can execute code when loaded: accept only artifacts produced by the trusted local reproduction pipeline, never uploaded or arbitrary downloaded model files. Matching hashes establish consistency only when the manifest itself is trusted. [Model persistence](https://scikit-learn.org/stable/model_persistence.html).

Keep the smallest checks that would fail for real regressions: split/group disjointness, PII boundary examples, risk-over-confidence precedence, retrieval abstention, duplicate submission prevention, persisted reload and safe export. The first framework proof must exercise navigation → edited form → SQLite save → fresh read → CSV download. Record command, dependency versions, exit status and actual persisted/rendered evidence. Do not label the proof complete from source review or an HTTP health check alone.

## Reference freshness and scope

Technical references were inspected on 2026-09-21. Recheck API compatibility against the actual lock when implementing. A [Reddit discussion](https://www.reddit.com/r/ExperiencedDevs/comments/16k3x6e/streamlit_instead_of_real_frontend/) was consulted for discovery of possible UX/state limits only; it is not evidence of current library behavior. [Dash callbacks](https://dash.plotly.com/basic-callbacks) provides the official comparison point for explicit callback wiring.

Project-specific facts, resource provenance, failed fetches and still-open reproduction gates belong in the task research scratchpad, not in this reusable skill.
