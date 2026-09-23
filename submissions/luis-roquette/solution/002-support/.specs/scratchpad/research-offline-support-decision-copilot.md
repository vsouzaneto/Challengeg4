# Phase 2a research — Support Decision Copilot

Date: 2026-09-21. Scope: research only; no business analysis, architecture, task decomposition, dependency installation, model training or runtime proof.

Input task: `.specs/tasks/draft/implement-support-decision-copilot.feature.md`.
Output skill: `.claude/skills/offline-support-decision-copilot/SKILL.md`.

## Existing evidence reused

Read `../../research/002-support.md` and `docs/superpowers/plans/2026-09-21-support-decision-copilot.md` from the solution root. The former records the three UI candidates and previous dataset inspection. The latter is prior planning input, not proof of implemented or approved behavior.

Dataset 1's 8,469 rows, 5,700 missing resolutions and missing creation timestamp, and Dataset 2's 47,837 rows/eight labels are inherited observations from that research. This phase did not redownload or recompute these counts. Preserve their status as prior observations until an implementation manifest reproduces them. Never derive first-response latency or total resolution time from the available endpoint timestamps.

## Resources inspected

16 successful external resources; technical recommendations rely on primary sources. Reddit is discovery/context only.

| ID | Resource | Reusable evidence |
|---|---|---|
| R1 | https://github.com/streamlit/streamlit | Python data-app candidate; official source and examples |
| R2 | https://github.com/gradio-app/gradio | Inference-oriented Python UI candidate; repository inspected when website docs failed |
| R3 | https://github.com/plotly/dash | Dashboard UI candidate; official repository |
| R4 | https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest | v1.64.0 reference supports entrypoint-based multipage tests and explicit run after switch |
| R5 | https://docs.streamlit.io/develop/concepts/architecture/forms | Form submission groups user edits across reruns |
| R6 | https://dash.plotly.com/basic-callbacks | Explicit input/output callback wiring for dashboard comparison |
| R7 | https://scikit-learn.org/stable/modules/calibration.html | Calibration must be disjoint from base fitting; sigmoid/isotonic tradeoffs |
| R8 | https://scikit-learn.org/stable/modules/generated/sklearn.frozen.FrozenEstimator.html | Freeze already-fitted estimator rather than silently retraining it |
| R9 | https://scikit-learn.org/stable/common_pitfalls.html | Fit preprocessing only inside training folds; avoid leakage |
| R10 | https://scikit-learn.org/stable/auto_examples/model_selection/plot_grid_search_text_feature_extraction.html | Text pipeline and model-selection baseline |
| R11 | https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html | Local lexical similarity baseline, distinct from probability |
| R12 | https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html | Group isolation with approximate class preservation when duplicates/templates demand it |
| R13 | https://scikit-learn.org/stable/model_persistence.html | Trusted-source restriction and environment compatibility for joblib/pickle |
| R14 | https://docs.python.org/3.12/library/sqlite3.html | Parameterized SQL, explicit commit/rollback, connection lifecycle |
| R15 | https://community.owasp.org/attacks/CSV_Injection | Export is a formula-injection boundary as well as a privacy boundary |
| R16 | https://www.reddit.com/r/ExperiencedDevs/comments/16k3x6e/streamlit_instead_of_real_frontend/ | Anecdotal discovery of state/UX limits, not technical proof |

Failed fetches, excluded from resource count: `https://www.gradio.app/docs/gradio/blocks` and `/guides/blocks-and-event-listeners` returned tool fetch errors; the official Gradio repository supplied the candidate inspection. `https://microsoft.github.io/presidio/limitations/` failed; the root redirected to `https://data-privacy-stack.github.io/presidio/`, which was inaccessible through the tool. No Presidio capability claim or dependency recommendation was inferred from these failures.

## Candidate findings and recommendation

| Candidate | Why it remains viable | Fit judgment for this task |
|---|---|---|
| Streamlit | Native data display/forms plus documented multipage AppTest | First candidate for minimum reproduction of queue and scorecard |
| Gradio | Official Python demo framework and custom Blocks composition | Alternative if the validated workflow becomes primarily inference |
| Dash | Official callback-driven dashboard framework | Alternative if explicit interaction/state control outweighs added wiring |

Recommend reproducing Streamlit + SQLite, then independent scikit-learn text pipelines and TF-IDF retrieval. This is provisional tool guidance, not an architectural decision. No benchmark or runtime result was produced by this phase. Do not add BM25, embeddings, a vector service, agent framework or cloud LLM without a measured shortfall and a new candidate/reproduction check.

## Consequential pitfalls to carry into synthesis

The documentation distinguishes AppTest simulation from browser rendering. A healthy server cannot prove edited response persistence or downloaded CSV contents; the first proof must perform those actions and read the persisted result.

Known-name replacement plus email/phone regexes does not establish full free-text anonymization. Human-entered final responses require the same boundary checks as dataset text. Failed sanitizer assurance means quarantine, reduced visible content or blocked export, not a claim of zero PII.

Random stratification with unique row IDs cannot prevent duplicate/template leakage. Inspect normalized sanitized text duplicates before splitting; use grouping where necessary. Keep preprocessing fit inside CV and prevent held-out resolutions from entering retrieval references.

The previous 60/20/20 outline does not by itself specify unbiased threshold estimation. Ensure calibration fitting and policy selection/estimation use disjoint development subsets or out-of-fold predictions; then evaluate the locked system on the frozen test. Calibrated confidence does not establish out-of-domain safety.

SQLite writes must survive a fresh connection and UI reruns without duplicate submissions. CSV quoting is insufficient protection against formula injection. Model artifact hashes are not authenticity checks when both artifact and manifest are untrusted.

## Open evidence gates

Framework reproduction, exact dependency compatibility and lock, sanitizer adequacy, group-aware split feasibility, risk thresholds, retrieval relevance/safety and end-to-end rendering remain unmeasured. These are future implementation gates after human SPEC approval. Do not mark them passed in planning or replace missing dataset signal with fabricated evidence.

Skill reference belongs in the task Description so implementers read these research findings before finalizing dependencies, validation or exports. No other SPEC content is changed by this phase.
