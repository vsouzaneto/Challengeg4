---
name: explainable-crm-prioritization
description: Research-backed guidance for stage-separated CRM priorities, temporal probability validation, faithful explanations and Streamlit session behavior.
topics: Python, Streamlit, scikit-learn, calibration, leakage, explainability, sparse evidence
created: 2026-09-21
updated: 2026-09-21
scratchpad: .specs/scratchpad/b84f29c1.md
---

# Explainable CRM Prioritization

## Overview

Use this skill when a CRM prioritizer must distinguish validated closing probabilities from relative historical evidence. Prefer a small deterministic pipeline with explicit data contracts, independent chronological evaluation and explanations that reconstruct the actual model output. Associations are not causal effects or evidence that an intervention will improve conversion.

## Key concepts

- **Different populations:** outcomes among engaged opportunities do not establish closing probabilities for prospects that never engaged.
- **Different routes:** full-account and account-free pipelines require their own calibration, eligibility and validation evidence.
- **Different score spaces:** additive raw-margin contributions are not probability percentage points; calibration is another transformation.
- **Different states:** immutable fitted models may be cached globally; user priority overrides belong only to the session.

## Documentation and verified references

All references verified 2026-09-21. The scratchpad records release dates, maintenance snapshots and 36 resources. Online documentation may change; API examples below target scikit-learn 1.9.1.

| Resource | Purpose |
|---|---|
| [Calibration](https://scikit-learn.org/stable/modules/calibration.html), [CalibratedClassifierCV](https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV) | Reliability and separate calibration data |
| [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html), [GradientBoostingClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingClassifier.html) | Minimal candidate comparison |
| [Pipeline pitfalls](https://scikit-learn.org/1.7/common_pitfalls.html), [pandas merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html) | Prevent leakage and silent join errors |
| [TargetEncoder](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.TargetEncoder.html) | Shrinkage concepts and target leakage |
| [Tree structure](https://scikit-learn.org/stable/auto_examples/tree/plot_unveil_tree_structure.html), [boosting source](https://github.com/scikit-learn/scikit-learn/blob/1.9.1/sklearn/ensemble/_gb.py), [calibration source](https://raw.githubusercontent.com/scikit-learn/scikit-learn/1.9.1/sklearn/calibration.py) | Verify additive reconstruction and sigmoid mapping |
| [TreeSHAP](https://shap.readthedocs.io/en/stable/generated/shap.TreeExplainer.html) | Optional local attribution; output-space and shape caveats |
| [Resource cache](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_resource), [session state](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state), [dataframe](https://docs.streamlit.io/develop/api-reference/data/st.dataframe) | Cache and native interface contracts |
| [AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest), [Cloud dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies) | Testing and matching deployment environments |
| [Model persistence](https://scikit-learn.org/stable/model_persistence.html), [Streamlit advisories](https://streamlit.io/advisories), [hashlib](https://docs.python.org/3.11/library/hashlib.html) | Security and checksums |

## Recommended libraries and alternatives

| Tool or approach | Recommendation and tradeoff |
|---|---|
| scikit-learn logistic regression | Default candidate: regularized, coefficient-based explanations; can miss interactions. In 1.9.1 use `l1_ratio=0` for L2; `penalty` is deprecated. |
| scikit-learn ordinary gradient boosting | Comparison candidate; nonlinear, slower and more explanation work. Its public regression-tree arrays permit exact path decomposition. |
| SHAP TreeExplainer | Optional alternative attribution; latest SHAP 0.52.0 requires Python 3.12. Older 0.49.1 supports 3.11 but requires an actual sklearn compatibility check. Do not install automatically. |
| pandas + stdlib | Validation, joins, smoothed evidence, SHA-256, deterministic playbook; no schema framework or extra backend needed. |
| Streamlit native dataframe/columns/state | Compact rows and side details without a custom grid; role selection demonstrates a view, not access control. |

These projects are maintained upstream, but popularity does not prove package security or runtime compatibility. Metadata-compatible **candidate pins for Python 3.11**, not an already-tested environment:

```sh
python3.11 -m venv .venv
.venv/bin/python -m pip install streamlit==1.64.0 pandas==3.0.6 numpy==2.4.6 scipy==1.17.1 scikit-learn==1.9.1 pytest==9.1.1
.venv/bin/python -m pip check
```

Sources: PyPI JSON for [Streamlit](https://pypi.org/pypi/streamlit/json), [pandas](https://pypi.org/pypi/pandas/json), [NumPy](https://pypi.org/pypi/numpy/json), [SciPy](https://pypi.org/pypi/scipy/1.17.1/json), [sklearn](https://pypi.org/pypi/scikit-learn/json), [pytest](https://pypi.org/pypi/pytest/json). Latest NumPy 2.5.3 and SciPy 1.18.1 require Python 3.12. Resolve and lock transitives, then verify imports and fitting on the actual Python 3.11 environment. No installation was performed during this research.

## Patterns and best practices

### Data contracts before modeling

Check required files/columns, unique non-null dimension keys, opportunity identity, stage vocabulary, dates and finite positive product prices. Normalize only explicitly known aliases. Use left joins with `validate="many_to_one"` and join indicators; assert that opportunity count is unchanged. pandas matches null join keys to null keys, so reject null dimension keys first.

Separate global pipeline blockers from row-level eligibility problems. Preserve unsupported rows with a reason. Missing account data uses a deliberate account-free route, not average-account imputation. Unknown categories should follow an explicit support policy; `handle_unknown="ignore"` prevents a crash but does not by itself prove prediction validity.

Hash actual CSV bytes plus canonical configuration, including feature lists, thresholds, random seed and playbook version. Keep downloaded bytes in staging until checksums pass; recovery must be explicit, not an app-start side effect. Do not load models from untrusted pickle/joblib artifacts.

### Temporal probability contract

Select positive/negative labels from resolved outcomes only. Outcome values, close timestamps, final stages and derived proxies must never enter the feature matrix. Fit transformations and estimators only on training rows; fit calibrators on later rows; reserve the latest period for one fixed evaluation. Keep equal-date groups together and verify disjoint opportunity IDs and ordered date boundaries.

Generic calibration example:

```python
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator

base.fit(X_train, y_train)
calibrated = CalibratedClassifierCV(FrozenEstimator(base), method="sigmoid")
calibrated.fit(X_calibration, y_calibration)
```

Do not use default stratified calibration CV as a chronological split. Require adequate samples and both labels in applicable periods. Validate full and account-free routes separately, including natural missing-account subsets where possible; a passed full route cannot validate fallback. Historical account snapshots may not represent information available at past decisions: document that uncertainty and omit features without a defensible availability claim.

Predeclare baseline prevalence source, Brier/log-loss comparison, band boundaries, band support/tolerance, top-K ranking/financial metrics and candidate-choice rule. Baseline prevalence comes from prior history, never final-test labels. Lower losses alone do not establish reliable bands. Do not adjust bands after inspecting test results. If final-test comparisons select a winner, acknowledge post-selection optimism; future independent data is needed for an unbiased estimate of that selected system.

Publish probabilities only for validated routes/support. Otherwise expose relative priority with failure diagnostics and suppress probabilistic expected revenue. Within validated bands, probability times list price is an expected product-revenue proxy, not expected realized negotiated revenue. Evaluate actual financial concentration with held-out realized amounts only. Freeze deterministic final tie-breaking by opportunity ID.

### Faithful local explanations

For logistic regression, transformed feature value times coefficient contributes to its raw margin; sum with intercept to reconstruct `decision_function`. For one-hot or scaled inputs, group contributions back to original fields and display the observed value and reference. Do not present global feature importance as a local reason.

For ordinary binary gradient boosting, a path decomposition assigns child-minus-parent tree values to the split feature. The sum telescopes to the leaf value; multiply by learning rate and include the initial margin plus root baselines. This is a derived, testable application of the public tree structure and boosting source. It is **not SHAP**: split order changes attribution and no causal or fairness guarantee follows. Fix the supported model/loss/init contract and require reconstruction tests before use.

Sigmoid calibration in sklearn applies `expit(-(a * margin + b))`. Thus raw contributions can be multiplied by `-a`, and the baseline transformed accordingly, to explain calibrated **log-odds**, not probability points. Verify the reconstructed probability equals `predict_proba`; handle zero/reversed slope rather than assuming direction. Calibration coefficients are internal API: isolate access and protect with the pinned-version regression check. An alternative is to label base-score explanations explicitly and display the calibration transformation separately. TreeSHAP must also identify the exact output and calibration boundary.

### Sparse relative evidence

When prospect outcomes are unobserved, do not call a historical engaged-deal rate a prospect closing probability. Use a versioned nested backoff hierarchy and a smoothed relative index:

```python
relative_evidence = (wins + alpha * parent_rate) / (n + alpha)
```

Require positive prior strength and valid counts; use global history as the terminal parent. Display the selected group, observed count, prior strength and evidence level. If presenting `n + alpha` as effective support, label its prior component; it is not an independent observed sample size. Never sum overlapping group counts. Use earlier history only for retrospective evaluation; do not target-encode a row using its own outcome.

Actions come from a small versioned deterministic playbook tied to actual actionable factors. A statistical association with sector or seller is not a recommendation to change it. If no supported action exists, use an explicit no-action message.

### Streamlit lifecycle

Cache fitting by data/config fingerprint and treat the returned model bundle as immutable. Keep manager pins, timestamp and identity in `st.session_state`; never mutate shared cached scores. Reset pins on explicit recalculation, including identical-data recalculations, and when data/config generation changes. New sessions naturally reset state.

Map selected row positions to IDs from the exact displayed table; clear stale selection when filters or tabs change. Use a native table plus columns for details. AppTest checks widget flows, while browser inspection checks actual rendering; neither startup HTTP success nor import success proves the user journey.

## Similar implementations

- [Mixed-type pipeline example](https://scikit-learn.org/1.7/auto_examples/compose/plot_column_transformer_mixed_types.html): reuse separation of transforms, not prohibited account imputation.
- [Frozen estimator example](https://scikit-learn.org/stable/auto_examples/frozen/plot_frozen_examples.html): reuse calibration mechanism with temporal partitions.
- [Streamlit row selection](https://docs.streamlit.io/develop/tutorials/elements/dataframe-row-selections): reuse native selection to populate details.
- [Treeinterpreter](https://github.com/andosa/treeinterpreter): primary illustration of bias-plus-path-contributions; no dependency recommended.

## Verification and limitations

Require checks for leakage, chronological splits, route eligibility, bad keys/prices, unknown categories, probability suppression, explanation reconstruction, stable sorting, session resets and playbook behavior. Include real-data integration and full training diagnostics, but never report unmeasured counts or metrics. Research establishes API/metadata compatibility only; installation, transitive vulnerability audit, real-data calibration, browser proof and deployment remain unexecuted.

Context7 was unavailable; authoritative web documentation and versioned source were used. Dataset license/contents need provenance evidence at acquisition. Static CRM extracts cannot establish causal sales uplift or solve missing-outcome selection bias; controlled pilots and future outcome capture are necessary before broad operational claims.

## Changelog

| Date | Change |
|---|---|
| 2026-09-21 | Created during Phase 2a research for explainable lead prioritization; includes Python 3.11 version constraints and calibrated-score explanation semantics. |
