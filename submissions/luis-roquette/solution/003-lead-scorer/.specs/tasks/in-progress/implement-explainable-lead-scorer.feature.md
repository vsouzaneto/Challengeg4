---
title: Implement explainable lead prioritization tool
---

## Initial User Prompt

Challenge 3 pra vc - Me confirme que absorveu as regras pré-estabelecidas no briefing:

https://github.com/luisroquette/ai-master-challenge/tree/main/challenges/build-003-lead-scorer

agora, antes de seguirmos, registre tambem no nosso diário a decisao de seguir com a metodologia SDD {Spec-Driven} e,
para isso, usaremos uma skillq ue gosto muito. Instale e use: https://claudecowork.im/resources/sdd npx skills add
NeoLabHQ/context-engineering-kit --skill sdd --agent claude-code

### Requirements

#### Objective and users

- Build a functional lead-prioritization application that uses the four real CRM CSV files from Challenge 003.
- Optimize the seller's decision about where to focus while giving managers a team view, region and seller filters, and a temporary manual-priority control.
- Treat expected revenue per seller as the business north star, while ordering `Engaging` deals primarily by validated closing-probability bands.
- Keep the product useful to non-technical sellers: every priority must be understandable and lead to a concrete next action when supported by data.

#### Operational experience

- Implement one Streamlit screen with separate `Engaging` and `Prospecting` tabs; never create a synthetic common score across the stages.
- Default sellers to their own portfolio. Default managers to the team view with region and seller filters.
- Render compact rows for comparison and a side panel with favorable and unfavorable factors, score origin, evidence strength and next action.
- Let managers temporarily pin a deal to the top without changing its score. Show manager and timestamp; keep this state only in `st.session_state` and expire it on a new session or recalculation.
- Keep unsupported deals visible as `Dados insuficientes`, without an invented score, and name the field or condition that needs correction.

#### Data contracts

- Version the four real CC0 CSVs under `data/raw/` with source, license and checksums.
- Provide an explicit external recovery command pinned to Kaggle dataset version 1 (`datasetVersionNumber=1`) that verifies checksums before replacing any file; it must not run silently when the app starts.
- Validate required files, columns, keys, data types and prices. Normalize the known `GTXPro` product key to `GTX Pro` before joining.
- Never discard invalid rows silently. Fail globally when the dataset cannot support the pipeline; isolate row-level problems when the remaining data is usable.
- Fingerprint data and scoring configuration so cached results invalidate when either changes.

#### Leakage and temporal truth

- Train and evaluate only on closed `Won` and `Lost` deals; score only active `Prospecting` and `Engaging` deals.
- Split closed history chronologically into train, calibration and untouched final-test periods.
- Prohibit `close_value`, `close_date`, final `deal_stage` and every derivative of those fields from model features. Use `Won/Lost` only as the label, `close_date` only for temporal splitting/evaluation and `close_value` only for financial evaluation.
- Use only features available at the scoring decision. Do not infer elapsed-to-close or another future-derived feature.

#### Engaging scoring

- Compare a regularized logistic-regression baseline with a gradient-boosting candidate.
- For each candidate, train and validate a full route with account attributes and an intentional fallback route without account attributes. Never use average-account imputation.
- Exclude `sales_agent` from direct `Engaging` prediction. Use seller, manager and region only for filtering and segmented diagnostics so seller history is not presented as deal quality.
- Calibrate candidate probabilities on the intermediate temporal period. Publish a probability only when the untouched test beats the historical-rate baseline on Brier score and log loss and validated bands show coherent predicted versus observed frequencies.
- Among candidates that pass calibration, compare ranking quality and concentration of realized financial value at the top. Prefer logistic regression when gains from boosting are not consistent.
- Order by validated probability band first. Within the same validated band, break ties using expected revenue (`probability × product price`).
- If no candidate passes, remove probability and probabilistic expected revenue and expose only clearly labeled relative-priority bands plus the failure diagnostics.

#### Prospecting priority

- Do not present `Prospecting` as a calibrated closing probability because the dataset lacks outcomes for opportunities that never reached engagement.
- Derive relative priority from smoothed historical evidence across product, seller and account.
- Back off sparse combinations progressively to broader groups and ultimately the global base; expose effective sample size and evidence strength.
- Show priority band and potential product revenue, not probabilistic expected revenue.

#### Explainability and actions

- Derive explanations from the actual score: coefficient contributions for logistic regression and a faithful local tree-contribution method if boosting wins.
- Show the strongest favorable and unfavorable factors with observed value and direction in plain Portuguese. Describe association, never unsupported causality.
- Generate next actions through a deterministic, versioned and tested playbook based on stage and the strongest actionable factor. Use `Sem ação recomendada com os dados atuais` when evidence is insufficient.
- Do not call paid or generative AI APIs at runtime.

#### Minimal architecture

- Use Python 3.11 and Streamlit with three application units: `app.py` for presentation/session state, `data.py` for data contracts and joins, and `scoring.py` for modeling, prioritization, explanations and playbook.
- Train deterministically on first load per data/configuration fingerprint and cache the result for filters and navigation.
- Pin runtime and test dependencies in `requirements.txt`, including a Streamlit Community Cloud-compatible `protobuf<6`; local `venv` execution is the source of truth.
- Do not add a separate API, frontend, database, authentication layer or CRM writeback.

#### Verification and evidence

- Test schema/joins, `GTXPro` normalization, leakage prohibition, chronological splitting, full/fallback feature contracts, routing, ordering, expected revenue, explanations, playbook, temporary priority and probability suppression.
- Use small synthetic fixtures for edge cases and at least one integration test over all four real CSVs.
- Provide a canonical preflight that runs tests, import checks, the complete training/evaluation pipeline and a Streamlit startup smoke test.
- Inspect the rendered seller and manager journeys in a browser, including tabs, filters, side panel, insufficient-data state and temporary priority.
- Record real counts, model metrics, chosen routes, screenshots and validation evidence in the submission documentation and process log.
- Block push, deployment and completion claims while any deterministic gate fails.

#### Delivery and documented limits

- Keep every changed or created project file under `submissions/luis-roquette/`.
- Provide copyable setup, test and run commands; document scoring logic, limitations and scaling path.
- Guarantee reproducible local execution. After all gates pass, publish the same revision to Streamlit Community Cloud and verify the live URL before documenting it.
- Explicitly document that the dataset is static, `Prospecting` lacks complete outcome labels, associations are not causal, session overrides are not persistent, and the prototype has no authentication, CRM writeback, drift monitoring or scheduled retraining.
- Recommend a controlled seller pilot, capture of interventions/outcomes, segmented performance audit and periodic recalibration before scaled operational use.

# Description

> **Required Skill**: You MUST use and analyse `explainable-crm-prioritization` skill before doing any modification to task file or starting implementation of it!
>
> Skill location: `.claude/skills/explainable-crm-prioritization/SKILL.md`

Build a working lead-prioritization tool for sellers and managers using the four real CRM tables from Challenge 003. Help sellers decide which active opportunities deserve attention and understand why, with expected revenue per seller as the business north star. Keep Engaging and Prospecting separate because their historical outcome evidence supports different claims.

For Engaging, expose closing probabilities only when chronological evaluation supports their reliability, order by validated probability band, then use expected revenue within a band. Otherwise show explicitly relative priority with validation diagnostics. For Prospecting, show relative historical priority, evidence strength and potential product revenue. Every supported priority must have faithful plain-Portuguese factors and an evidence-grounded next action; unsupported deals remain visible with the missing condition named.

Provide seller-own and manager-team views, compact comparison rows, deal details and attributable temporary manager priority that expires on recalculation or a new session. Deliver reproducible execution, honest evaluation records and a verified live version of the validated revision. This is a static-data decision-support prototype, not authenticated CRM automation or evidence of causal revenue uplift.

**Scope**:

- Included: four-table data integrity, both stage priorities, full/fallback routes, explanations/actions, role-filtered inspection, temporary overrides, reproducible verification and live delivery evidence.
- Excluded: authentication, separate services/frontend/database, CRM writeback, persistent overrides, paid/generative runtime AI, drift monitoring and scheduled retraining.

**User Scenarios**:

1. **Primary**: A seller selects their identity, opens their own Engaging portfolio, compares priorities and inspects evidence plus a next action.
2. **Alternative**: A seller opens Prospecting and sees relative priority, potential revenue, sample support and the reason for backoff.
3. **Manager**: A manager starts with the team, filters to one seller and temporarily pins a deal with visible attribution.
4. **Data error**: Missing account data selects fallback; an unsupported deal stays visible with a correction; globally unusable data blocks scoring with diagnostics.
5. **Degraded/session**: Failed validation suppresses probabilities; recalculation or a new session clears pins, while filtering preserves them.

---

## Acceptance Criteria

**Checklist:**

| ID | Question | Category | Importance |
|----|----------|----------|------------|
| CK-1 | Are all four real CC0 CSVs versioned under data/raw/ with source, license and checksums? | hard_rule | essential |
| CK-2 | Does the explicit external recovery operation verify downloaded checksums before replacing any raw file, without running on app startup? | hard_rule | essential |
| CK-3 | Does ingestion validate required files, columns, keys, types and product prices before scoring? | hard_rule | essential |
| CK-4 | Is GTXPro normalized to GTX Pro before the product join? | hard_rule | essential |
| CK-5 | Are invalid rows explicitly accounted for, isolating usable remainder while blocking a globally unusable dataset? | hard_rule | essential |
| CK-6 | Are only Won/Lost deals used for training/evaluation in disjoint chronological train, calibration and untouched final-test periods? | hard_rule | essential |
| CK-7 | Are close_value, close_date, final deal_stage and every derivative absent from prediction features, with their use limited respectively to financial evaluation, temporal evaluation and labels? | hard_rule | essential |
| CK-8 | Can every model feature be established at the scoring decision without future-derived elapsed-to-close information? | hard_rule | essential |
| CK-9 | Are regularized logistic regression and gradient boosting each trained/evaluated through full-account and intentionally account-free routes? | hard_rule | essential |
| CK-10 | Do missing-account deals use an account-free route without average-account imputation? | hard_rule | essential |
| CK-11 | Are sales_agent, manager and region excluded from direct Engaging prediction and reserved for filtering or segmented diagnostics? | hard_rule | essential |
| CK-12 | Is each candidate-route calibrator fitted only on the intermediate calibration period? | hard_rule | essential |
| CK-13 | Is every published Engaging probability backed by a held-out route result beating the historical-rate baseline on both Brier score and log loss with coherent predicted/observed bands under predeclared rules? | hard_rule | essential |
| CK-14 | Does candidate selection compare ranking and realized-value concentration only among validated candidates, preferring logistic regression when boosting gains are inconsistent under a documented rule? | hard_rule | essential |
| CK-15 | Are unpinned Engaging deals ordered first by validated probability band, then by probability times product price within the band? | hard_rule | essential |
| CK-16 | When no candidate for a route validates, are probability and probabilistic expected revenue suppressed in every visible result while relative bands and failure diagnostics are explicit? | hard_rule | essential |
| CK-17 | Is Prospecting priority based on smoothed historical product, seller and account evidence rather than presented as calibrated closing probability? | hard_rule | essential |
| CK-18 | Do sparse Prospecting combinations back off progressively to broader groups and ultimately the global base? | hard_rule | essential |
| CK-19 | Does each supported Prospecting result expose a relative band, potential product revenue, effective sample size and evidence strength without probabilistic expected revenue? | hard_rule | essential |
| CK-20 | Do explanations derive from actual logistic coefficient contributions or a faithful local tree-contribution method when boosting is selected? | hard_rule | essential |
| CK-21 | Do details identify the strongest favorable/unfavorable factors with observed values and direction in plain Portuguese, explicitly indicating when a direction has no supported factor? | hard_rule | essential |
| CK-22 | Does the deterministic versioned playbook use stage plus the strongest actionable factor, returning exactly Sem ação recomendada com os dados atuais when evidence is insufficient? | hard_rule | essential |
| CK-23 | Do unsupported active deals remain visible as Dados insuficientes with no invented score and the field or condition requiring correction named? | hard_rule | essential |
| CK-24 | Does one Streamlit screen provide distinct Engaging and Prospecting tabs without a synthetic shared score? | hard_rule | essential |
| CK-25 | Do selectable seller and manager contexts default respectively to own portfolio and the team view without implying authentication? | hard_rule | essential |
| CK-26 | Do the manager, region and seller filters produce the exact selected portfolio without changing underlying scores? | hard_rule | essential |
| CK-27 | Do compact comparison rows open a side panel containing factors, score origin, evidence strength and the next action? | hard_rule | important |
| CK-28 | Can only the manager context temporarily pin a deal above the normal order without changing its score? | hard_rule | essential |
| CK-29 | Does each temporary pin show its manager and timestamp? | hard_rule | important |
| CK-30 | Are pins held only in st.session_state, retained for navigation/filtering, and cleared by recalculation or a new session? | hard_rule | essential |
| CK-31 | Does changing either data or scoring configuration invalidate cached scoring through a fingerprint? | hard_rule | essential |
| CK-32 | Are repeated runs deterministic, with first-load training reused across filters and navigation for an unchanged fingerprint? | hard_rule | essential |
| CK-33 | Does runtime scoring and explanation make zero paid or generative AI API calls? | hard_rule | essential |
| CK-34 | Are application responsibilities confined to the approved app.py, data.py and scoring.py units without a separate API, frontend, database, authentication layer or CRM writeback? | hard_rule | essential |
| CK-35 | Does a fresh local Python 3.11 venv reproduce the application using pinned runtime/test dependencies in requirements.txt? | hard_rule | essential |
| CK-36 | Do small synthetic fixtures cover the specified edge cases and does an integration test exercise all four real CSVs? | hard_rule | essential |
| CK-37 | Does one documented canonical preflight fail on any failed test, import, complete training/evaluation or Streamlit startup smoke gate? | hard_rule | essential |
| CK-38 | Does recorded browser verification exercise rendered seller and manager journeys including both tabs, filtering, details, insufficient data and temporary priority? | hard_rule | essential |
| CK-39 | Do submission documentation and the process log record measured counts, route/model metrics, chosen routes, screenshots and revision-specific validation evidence? | hard_rule | essential |
| CK-40 | Are copyable setup/test/run instructions, scoring rationale, limitations and a scaling path documented? | hard_rule | important |
| CK-41 | After all gates pass, does the documented Streamlit Community Cloud URL render the same validated revision with recorded live verification? | hard_rule | essential |
| CK-42 | Are all changed or created project files confined to submissions/luis-roquette/? | hard_rule | essential |
| CK-43 | Do documented limits state static data, incomplete Prospecting labels, noncausal associations, session-only overrides and missing auth/writeback/drift monitoring/scheduled retraining, with a controlled pilot, intervention/outcome capture, segmented audit and recalibration recommended? | hard_rule | important |
| CK-44 | Is new code free of duplicated functions, scoring rules or concepts already provided by another application unit? | principle | important |
| CK-45 | Where touched code permits it, are small meaningful cleanup improvements made without expanding task scope? | principle | optional |
| CK-46 | Does every selected Test Matrix type have at least one corresponding implemented test? | hard_rule | essential |
| CK-47 | Does every main, edge and error case specified in the scratchpad test matrix have a corresponding implemented test? | hard_rule | essential |
| CK-48 | Does every behavior-testable checklist item resolve through the coverage map to at least one real passing test? | hard_rule | essential |
| CK-49 | Does every Test Cases to Cover entry have a corresponding implemented test? | hard_rule | essential |
| CK-50 | Does any explanation or documented conclusion claim that a model association causes closure or revenue uplift? | principle | pitfall |

CK-50 is an explicit pitfall: YES identifies a prohibited causal claim; compliant output answers NO. Other items use YES for compliance. CK-45 is optional and cannot require unrelated cleanup.

**Regular Checks:**

- [ ] The documented canonical preflight passes tests, import checks, complete training/evaluation and Streamlit startup; any failed gate blocks push, deployment and completion claims. No existing project gate command was available when this specification was written.
- [ ] No code duplication: new code does not duplicate functions, scoring rules or concepts provided by another application unit.
- [ ] Where applicable, small cleanup improvements remain within touched scope; this optional quality item does not require unrelated refactoring.
- [ ] Every test type selected in the Test Matrix has at least one corresponding implemented test.
- [ ] Every main, edge and error case specified below has a corresponding implemented test.
- [ ] Every behavior-testable checklist item resolves to a real passing test; structural/documentary/meta items are verified from source or captured evidence.
- [ ] Every Test Cases to Cover entry is implemented and passing; repeated TC IDs across groups may share one test.

**Rubric:**

| Criterion | Weight |
|-----------|--------|
| Probability Evidence Traceability | 0.25 |
| Correction Specificity | 0.15 |
| Explanation Fidelity | 0.25 |
| Ranking Test Discrimination | 0.15 |
| Project Guidelines Alignment | 0.20 |

**Rubric Score Definitions:**

Scale: 1–5 integers, anchor-relative. Each dimension pins score_2 and score_4; other scores describe evidence on that same axis. Anchor metrics and dates are illustrative excerpts, not expected measured results or required cutoffs.

### Probability Evidence Traceability

A reader can trace a published probability, or its suppression, to the exact evaluated route and held-out evidence.

Collect route-specific split identities, baseline losses, calibrated losses, band support and the publication decision. Compare the linkage between the displayed claim and the recorded evidence against the anchors; do not reward a higher probability or invented successful metric.

#### Anchors

**contrast**: The same validation claim gains identifiable route and held-out metric provenance.

**score_2**:

```text
evidence: "Validated"
```

**score_4**:

```text
evidence: "full route; held-out period 2017-10..12; Brier 0.18 versus baseline 0.24; log loss 0.53 versus 0.66; band observed 7/10"
```

### Correction Specificity

A diagnosed unsupported deal gives the user a concrete field or condition they can correct.

Collect invalid-input and unsupported-row messages across file, join and pricing failures. Compare their specificity against the anchors, holding the underlying failure fixed; extra prose does not improve the score.

#### Anchors

**contrast**: The same invalid-data outcome identifies the affected record, field and correction.

**score_2**:

```text
invalid_row: "Invalid data"
```

**score_4**:

```text
invalid_row: "opportunity 17: product price missing; correct product catalog price"
```

### Explanation Fidelity

The displayed contribution values agree numerically with the actual selected model output on its documented scale.

Trace the displayed factors to logistic coefficients or the selected tree contribution output; independently reconstruct the explained result using its base value and contributions. Compare against the anchors on reconstruction fidelity, not explanation length. Calibrated probability and pre-calibration explanation scale must be distinguished.

#### Anchors

**contrast**: Contribution values reconstruct the same displayed model output.

**score_2**:

```text
explanation: base_log_odds=-0.40; contributions=[+0.20]; explained_log_odds=0.8473
```

**score_4**:

```text
explanation: base_log_odds=-0.40; contributions=[+1.2473]; explained_log_odds=0.8473
```

### Ranking Test Discrimination

The ranking verification catches the realistic error of putting product value ahead of probability-band priority.

Inspect the ranking test inputs and asserted order. Determine whether replacing band-first sorting with value-first sorting makes the check fail. Compare that falsifiability against the anchors; test count or framework choice receives no credit.

#### Anchors

**contrast**: The assertion distinguishes the required ordering from the plausible value-first defect.

**score_2**:

```text
assert sorted_scores[0] is not None
```

**score_4**:

```text
assert rank([lower_band_expensive, higher_band_cheap])[0] == higher_band_cheap
```

### Project Guidelines Alignment

Reproduction and submission evidence identifies the actual validated delivery, consistent with the discovered project rules.

Use the repository submission-folder restriction, working-software requirement and required process/setup evidence as binding reference patterns. Inspect the delivered file scope, documented commands and captured validation identity. Treat user AGENTS constraints and contribution rules as stronger evidence than presentation choices. Place the evidence against the anchors on reproducibility identity; no credit for merely claiming compliance.

#### Anchors

**contrast**: The same preflight success is linked to the revision, data and supported environment.

**score_2**:

```text
preflight: PASS; revision: unknown
```

**score_4**:

```text
preflight: PASS; revision: 0123456; data_fingerprint: abc123; environment: Python 3.11 pinned
```

**Test Strategy:**

**Criticality:** MEDIUM-HIGH

**Test Matrix:**

| Type | Size | Framework | Dependencies | Gate |
|------|------|-----------|--------------|------|
| unit | small | Python unittest | None | Gate 1 |
| integration | medium | Python unittest | temporary filesystem; local HTTP fixture for recovery; four versioned real CSVs | Gate 2 |
| e2e | large | Playwright | local Streamlit server; isolated browser contexts; synthetic unsupported-row fixture | Gate 3 |
| smoke | large | Python unittest / Playwright | local Streamlit process; published Streamlit URL | Gate 5 |
| property-based | small | Python unittest with seeded stdlib generators | None | Gate 6 |

**Test Cases to Cover**

Case IDs identify distinct behaviors; a single implemented test can satisfy the same TC ID referenced under multiple checklist headings. Table-driven cases must have individual names. Fix and version all modeling, band/support and numerical-tolerance rules before inspecting final-test results. Expand every chosen cutoff into its stated boundary neighbors.

#### CK-1: Are all four real CC0 CSVs versioned under data/raw/ with source, license and checksums?

- [integration] TC-01: Real-data provenance: verify the four versioned CSV checksums against their recorded source/license metadata.

#### CK-2: Does the explicit external recovery operation verify downloaded checksums before replacing any raw file, without running on app startup?

- [integration] TC-02: Verified recovery: a matching local HTTP fixture replaces a raw file only after digest verification.
- [integration] TC-03: Recovery integrity failure: a mismatching download leaves the original raw file byte-identical; startup performs no recovery request.

#### CK-3: Does ingestion validate required files, columns, keys, types and product prices before scoring?

- [unit] TC-04: Input contract partitions: missing file/column, duplicate primary key, malformed type/date, unknown join key or unusable price produces the declared global/row-level diagnostic.
- [unit] TC-05: Price lower bound B=0: -1, 0, 1 exercise invalid, invalid, valid price partitions; nonfinite values are rejected.

#### CK-4: Is GTXPro normalized to GTX Pro before the product join?

- [integration] TC-06: Known product spelling: GTXPro joins exactly one GTX Pro catalog row without changing opportunity cardinality.

#### CK-5: Are invalid rows explicitly accounted for, isolating usable remainder while blocking a globally unusable dataset?

- [unit] TC-04: Input contract partitions: missing file/column, duplicate primary key, malformed type/date, unknown join key or unusable price produces the declared global/row-level diagnostic.
- [integration] TC-07: Row accounting: a mixed-validity fixture preserves the supported rows plus visible excluded-row reasons; an unusable fixture blocks the pipeline.

#### CK-6: Are only Won/Lost deals used for training/evaluation in disjoint chronological train, calibration and untouched final-test periods?

- [unit] TC-08: Temporal membership: only closed outcomes enter three disjoint chronological periods, with equal-date groups kept together; only active opportunities are scored.
- [unit] TC-09: Temporal cutoff boundaries: for each predeclared cutoff B, dates B-1 day, B, B+1 day match the documented interval rule without overlap.
- [unit] TC-10: Insufficient temporal evidence: empty or single-class required periods prevent unsupported probability publication with named diagnostics.

#### CK-7: Are close_value, close_date, final deal_stage and every derivative absent from prediction features, with their use limited respectively to financial evaluation, temporal evaluation and labels?

- [unit] TC-11: Feature prohibition: fitted full/fallback feature names contain no close value/date, final stage or derivatives, seller, manager or region; preprocessing is fitted only on training rows.
- [unit] TC-12: Forbidden-field mutation: changing close outcome fields on an otherwise identical active input cannot change its feature vector.

#### CK-8: Can every model feature be established at the scoring decision without future-derived elapsed-to-close information?

- [unit] TC-12: Forbidden-field mutation: changing close outcome fields on an otherwise identical active input cannot change its feature vector.
- [unit] TC-13: Decision-time feature provenance: every derived feature uses only an explicitly permitted input available at the scoring decision.

#### CK-9: Are regularized logistic regression and gradient boosting each trained/evaluated through full-account and intentionally account-free routes?

- [integration] TC-14: Four candidate routes: the full real-data evaluation records logistic/full, logistic/fallback, boosting/full, boosting/fallback outcomes.

#### CK-10: Do missing-account deals use an account-free route without average-account imputation?

- [unit] TC-15: Missing-account routing: absent account selects the account-free route; populated supported account selects the full route without averaged attributes.

#### CK-11: Are sales_agent, manager and region excluded from direct Engaging prediction and reserved for filtering or segmented diagnostics?

- [unit] TC-11: Feature prohibition: fitted full/fallback feature names contain no close value/date, final stage or derivatives, seller, manager or region; preprocessing is fitted only on training rows.
- [unit] TC-16: Engaging seller invariance: seller/manager/region changes alone do not change prediction inputs or scores.

#### CK-12: Is each candidate-route calibrator fitted only on the intermediate calibration period?

- [unit] TC-17: Calibration isolation: training, calibration fitting and final evaluation consume only their respective predeclared temporal row sets.

#### CK-13: Is every published Engaging probability backed by a held-out route result beating the historical-rate baseline on both Brier score and log loss with coherent predicted/observed bands under predeclared rules?

- [unit] TC-10: Insufficient temporal evidence: empty or single-class required periods prevent unsupported probability publication with named diagnostics.
- [unit] TC-18: Probability-publication decision table: publish only when both losses improve over the training-history baseline and the fixed band-coherence rule passes.
- [unit] TC-19: Publication metric equality: baseline difference -epsilon, 0, +epsilon distinguishes strictly better from equal/worse for each loss; exercise both losses separately.
- [unit] TC-20: Band-rule boundaries: for each fixed probability/support cutoff B, exercise B-epsilon/B/B+epsilon or B-1/B/B+1 as appropriate using the documented rule.
- [unit] TC-43: Probability bounds B=0 and B=1: -epsilon, 0, +epsilon plus 1-epsilon, 1, 1+epsilon verify supported bounds and reject/suppress invalid exposed values.

#### CK-14: Does candidate selection compare ranking and realized-value concentration only among validated candidates, preferring logistic regression when boosting gains are inconsistent under a documented rule?

- [unit] TC-21: Candidate choice: validated logistic wins inconsistent boosting gains; validated boosting wins consistent gains; invalid candidates cannot win.

#### CK-15: Are unpinned Engaging deals ordered first by validated probability band, then by probability times product price within the band?

- [unit] TC-20: Band-rule boundaries: for each fixed probability/support cutoff B, exercise B-epsilon/B/B+epsilon or B-1/B/B+1 as appropriate using the documented rule.
- [unit] TC-22: Band-first ranking: a lower-band expensive deal cannot outrank a higher-band deal; equal-band ordering follows probability multiplied by product price.
- [unit] TC-23: Equal-priority ties: tied band/revenue outputs use opportunity ID as the deterministic final tie-break.
- [property-based] TC-42: Deterministic priority invariants: seeded generated supported deals produce finite bounded probabilities when enabled, stable repeat results and band-first order; Prospecting never acquires probability fields.

#### CK-16: When no candidate for a route validates, are probability and probabilistic expected revenue suppressed in every visible result while relative bands and failure diagnostics are explicit?

- [unit] TC-10: Insufficient temporal evidence: empty or single-class required periods prevent unsupported probability publication with named diagnostics.
- [unit] TC-24: Failed-route output suppression: no passing route removes probability plus expected-revenue fields from the returned presentation data.

#### CK-17: Is Prospecting priority based on smoothed historical product, seller and account evidence rather than presented as calibrated closing probability?

- [unit] TC-25: Prospecting smoothing: hand-computed product/seller/account evidence matches relative priority for a small known history.
- [property-based] TC-42: Deterministic priority invariants: seeded generated supported deals produce finite bounded probabilities when enabled, stable repeat results and band-first order; Prospecting never acquires probability fields.

#### CK-18: Do sparse Prospecting combinations back off progressively to broader groups and ultimately the global base?

- [unit] TC-20: Band-rule boundaries: for each fixed probability/support cutoff B, exercise B-epsilon/B/B+epsilon or B-1/B/B+1 as appropriate using the documented rule.
- [unit] TC-26: Sparse backoff: decreasing support traverses broader groups to global evidence; support counts -1, 0, 1 reject negative counts and distinguish no/one observation; prior strength must be positive and labeled separately from observed support.

#### CK-19: Does each supported Prospecting result expose a relative band, potential product revenue, effective sample size and evidence strength without probabilistic expected revenue?

- [unit] TC-27: Prospecting display contract: output includes potential revenue, relative band, effective sample size and evidence strength, but no calibrated probability or expected revenue.
- [property-based] TC-42: Deterministic priority invariants: seeded generated supported deals produce finite bounded probabilities when enabled, stable repeat results and band-first order; Prospecting never acquires probability fields.

#### CK-20: Do explanations derive from actual logistic coefficient contributions or a faithful local tree-contribution method when boosting is selected?

- [unit] TC-28: Logistic fidelity: contributions plus intercept reconstruct the actual model output on the labeled scale; calibration zero/reversed slope is handled without falsely claiming probability-point contributions.
- [unit] TC-29: Tree fidelity: the selected local explanation method reconstructs the explained tree output on its documented scale within numerical tolerance.

#### CK-21: Do details identify the strongest favorable/unfavorable factors with observed values and direction in plain Portuguese, explicitly indicating when a direction has no supported factor?

- [unit] TC-30: Portuguese factor rendering: strongest positive/negative contributions retain observed values and signs; absent supported direction is explicit.

#### CK-22: Does the deterministic versioned playbook use stage plus the strongest actionable factor, returning exactly Sem ação recomendada com os dados atuais when evidence is insufficient?

- [unit] TC-31: Playbook decision table: each versioned stage/actionable-factor rule maps to its declared action.
- [unit] TC-32: No actionable evidence: missing or nonactionable support returns exactly Sem ação recomendada com os dados atuais.

#### CK-23: Do unsupported active deals remain visible as Dados insuficientes with no invented score and the field or condition requiring correction named?

- [integration] TC-07: Row accounting: a mixed-validity fixture preserves the supported rows plus visible excluded-row reasons; an unusable fixture blocks the pipeline.
- [e2e] TC-33: Unsupported row visibility: a synthetic unsupported active opportunity renders Dados insuficientes, its correction reason and no score.

#### CK-24: Does one Streamlit screen provide distinct Engaging and Prospecting tabs without a synthetic shared score?

- [e2e] TC-34: Seller journey: selected seller starts with own active portfolio; both separate tabs show their stage-specific output without a common score.

#### CK-25: Do selectable seller and manager contexts default respectively to own portfolio and the team view without implying authentication?

- [e2e] TC-34: Seller journey: selected seller starts with own active portfolio; both separate tabs show their stage-specific output without a common score.
- [e2e] TC-35: Manager journey: manager starts at team scope; choosing a regional office and seller updates exact visible opportunity membership without changing scores.

#### CK-26: Do the manager, region and seller filters produce the exact selected portfolio without changing underlying scores?

- [e2e] TC-35: Manager journey: manager starts at team scope; choosing a regional office and seller updates exact visible opportunity membership without changing scores.

#### CK-27: Do compact comparison rows open a side panel containing factors, score origin, evidence strength and the next action?

- [e2e] TC-36: Deal details: opening a compact row reveals its factors, origin, evidence strength and next action; changing filter/tab cannot display a stale or different row's details.

#### CK-28: Can only the manager context temporarily pin a deal above the normal order without changing its score?

- [e2e] TC-37: Manager pin: a manager pin moves the deal to the top with unchanged score plus manager/timestamp attribution.
- [e2e] TC-38: Seller pin restriction: the seller context cannot invoke the manager-only priority control.

#### CK-29: Does each temporary pin show its manager and timestamp?

- [e2e] TC-37: Manager pin: a manager pin moves the deal to the top with unchanged score plus manager/timestamp attribution.

#### CK-30: Are pins held only in st.session_state, retained for navigation/filtering, and cleared by recalculation or a new session?

- [e2e] TC-39: Pin lifetime: filtering/navigation retain the override; explicit recalculation clears it even for unchanged data; data/config generation changes clear it; a new browser session has no prior override.

#### CK-31: Does changing either data or scoring configuration invalidate cached scoring through a fingerprint?

- [integration] TC-40: Cache invalidation: data-content mutation changes the fingerprint; configuration mutation changes it independently.

#### CK-32: Are repeated runs deterministic, with first-load training reused across filters and navigation for an unchanged fingerprint?

- [unit] TC-23: Equal-priority ties: tied band/revenue outputs use opportunity ID as the deterministic final tie-break.
- [integration] TC-41: Cache reuse: an unchanged fingerprint reuses fitted results across filtering/navigation without another training invocation.
- [property-based] TC-42: Deterministic priority invariants: seeded generated supported deals produce finite bounded probabilities when enabled, stable repeat results and band-first order; Prospecting never acquires probability fields.

#### CK-33: Does runtime scoring and explanation make zero paid or generative AI API calls?

- [integration] TC-44: Offline runtime: load, train and score with external network blocked after dependency installation; no paid/generative requests are attempted.

#### CK-35: Does a fresh local Python 3.11 venv reproduce the application using pinned runtime/test dependencies in requirements.txt?

- [smoke] TC-46: Local startup: the canonical preflight starts Streamlit from the pinned environment, verifies readiness, then shuts down the spawned process cleanly.

#### CK-36: Do small synthetic fixtures cover the specified edge cases and does an integration test exercise all four real CSVs?

- [integration] TC-01: Real-data provenance: verify the four versioned CSV checksums against their recorded source/license metadata.
- [integration] TC-14: Four candidate routes: the full real-data evaluation records logistic/full, logistic/fallback, boosting/full, boosting/fallback outcomes.

#### CK-37: Does one documented canonical preflight fail on any failed test, import, complete training/evaluation or Streamlit startup smoke gate?

- [integration] TC-45: Preflight failure propagation: a failing required gate returns nonzero rather than reporting successful verification.
- [smoke] TC-46: Local startup: the canonical preflight starts Streamlit from the pinned environment, verifies readiness, then shuts down the spawned process cleanly.

#### CK-38: Does recorded browser verification exercise rendered seller and manager journeys including both tabs, filtering, details, insufficient data and temporary priority?

- [e2e] TC-34: Seller journey: selected seller starts with own active portfolio; both separate tabs show their stage-specific output without a common score.
- [e2e] TC-35: Manager journey: manager starts at team scope; choosing a regional office and seller updates exact visible opportunity membership without changing scores.
- [e2e] TC-36: Deal details: opening a compact row reveals its factors, origin, evidence strength and next action; changing filter/tab cannot display a stale or different row's details.
- [e2e] TC-37: Manager pin: a manager pin moves the deal to the top with unchanged score plus manager/timestamp attribution.
- [e2e] TC-39: Pin lifetime: filtering/navigation retain the override; explicit recalculation clears it even for unchanged data; data/config generation changes clear it; a new browser session has no prior override.

#### CK-41: After all gates pass, does the documented Streamlit Community Cloud URL render the same validated revision with recorded live verification?

- [smoke] TC-47: Live revision: the published URL loads its active-stage view with revision/data fingerprint evidence matching the locally validated delivery.

#### CK-50: Does any explanation or documented conclusion claim that a model association causes closure or revenue uplift?

- [unit] TC-30: Portuguese factor rendering: strongest positive/negative contributions retain observed values and signs; absent supported direction is explicit.

Structural/documentary/meta checks CK-34, CK-39, CK-40, CK-42–49 are verified through source, documentation, revision evidence and test-result inspection, not recursive tests of tests. CK-50 additionally requires inspection of explanations and conclusions for unsupported causal claims. Real-data evaluation may legitimately suppress all probabilities; passing requires honest gating and diagnostics, not fabricated successful models.

**Definition of Done:**

- [ ] Every essential checklist item is satisfied, the causal-claim pitfall is absent, and applicable Regular Checks pass without bypasses.
- [ ] Every distinct Test Cases to Cover case is implemented and passing, including the integration over all four real CSVs and the rendered seller/manager journeys.
- [ ] Both stage portfolios provide supported priorities or explicit insufficient-data/degraded states; faithful explanations, grounded actions and temporary manager pins match their contracts.
- [ ] Fresh local execution reproduces measured counts, route choices and evaluation evidence; submission documentation/process log contains copyable commands, screenshots, limitations and pilot/scaling recommendations.
- [ ] After all gates pass, the same validated revision is published to Streamlit Community Cloud and its rendered live URL is verified before being documented as delivered.

## Architecture References

- Required [research skill](../../../.claude/skills/explainable-crm-prioritization/SKILL.md), [impact analysis](../../analysis/analysis-explainable-lead-scorer.md) and [architecture scratchpad](../../scratchpad/c7c4ed72.md).
- Approved design: [process log, sections 1–5](../../../../../process-log/003-lead-scorer.md#design-consolidado); scope and ownership: [pre-start log](../../../../../process-log/000-pre-inicio.md#o-briefing-pré-início). [Business test matrix and coverage map](../../scratchpad/4002b33e.md#test-strategy--stage-6) is the specific scratchpad referenced by CK-47.
- Architecture-relevant corrections from [research review](../../scratchpad/fd28a1a9.md), [impact review](../../scratchpad/9e67a0d5.md) and [business review](../../scratchpad/6e45e9b8.md) are incorporated below. Existing Description, checklist IDs, rubric and test cases remain unchanged.
- Version-specific method references: [scikit-learn 1.9 calibration](https://scikit-learn.org/1.9/modules/generated/sklearn.calibration.CalibratedClassifierCV.html), [logistic regression](https://scikit-learn.org/1.9/modules/generated/sklearn.linear_model.LogisticRegression.html), [gradient boosting](https://scikit-learn.org/1.9/modules/generated/sklearn.ensemble.GradientBoostingClassifier.html), [pinned calibration source](https://raw.githubusercontent.com/scikit-learn/scikit-learn/1.9.1/sklearn/calibration.py). Native UI contracts: [dataframe](https://docs.streamlit.io/develop/api-reference/data/st.dataframe), [cache](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_resource), [session state](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state). These support API selection; runtime compatibility remains an implementation gate.

## Solution Strategy

**Architecture Pattern: Layered modular monolith, with a functional core and imperative boundaries.** Preserve the approved three-file structure. Plain records and pure policy functions live in `scoring.py`; local tabular/model adapters also live there as explicitly separate functions. `data.py` owns file I/O and normalized input, and `app.py` owns Streamlit and session state. No service, repository, provider interface, fourth application module or persistent model store is needed. This is proportional separation, not a claim of physically separated Clean Architecture packages.

**Key decisions (5):**

| ID | Decision | Reason and accepted trade-off |
|---|---|---|
| AD-1 | Keep three units and one Lead Prioritization bounded context, with named Data Integrity, Engaging Evidence, Prospecting Evidence and Portfolio Presentation responsibilities. | Reuses the approved design at process-log lines 906–912; zero executable code exists to extend. Co-location is accepted at this prototype size; domain policy remains independent of Streamlit, filesystem, HTTP and estimator objects. |
| AD-2 | Validate one immutable four-file snapshot, preserve every input row in accounting, and recover only through a staged, locked directory replacement with rollback. | Prevents silent drops, join multiplication, stale cache and partially replaced datasets. Recovery briefly blocks reads and leaves a recoverable backup on interruption. |
| AD-3 | Fix all features, cutoffs, candidate settings and publication rules before final-test inspection; choose candidates separately for account-supported and account-free routes. | Probability is conditional on route and validated band. Conservative gates may suppress every probability, which is an acceptable documented result. |
| AD-4 | Keep Prospecting relative; explain the actual score and its scale; use a small deterministic Portuguese playbook. | Avoids unsupported probability, causal or action-effect claims. Tree path attribution is additive and order-dependent, not SHAP. No generative runtime dependency. |
| AD-5 | Cache only immutable computation by snapshot/config identity; keep intervention and selection in the current browser session; verify clean installation, offline execution and rendered journeys. | Filtering is cheap, pins cannot mutate shared scores, and proof identifies the exact revision. The selectable role is demonstration context, not identity verification. |

The probability estimand is **Won versus Lost among historically engaged opportunities that eventually resolved in this static extract**, with no promised days-to-close horizon. Applying it to still-open opportunities assumes transportability; delayed outcomes/right censoring, static catalog/account metadata and the lack of naturally missing-account closed cases limit that assumption. Show a concise version of this qualification beside probability diagnostics, and document mature cohorts plus future outcome collection before operational expansion. Do not label the result “chance de fechar em 30 dias”, causal uplift, or expected negotiated revenue.

## Architecture Decomposition

Source: scratchpad Steps 3.2–3.6. Paths below are proposed, not existing symbols.

| Component and file | Layer / single responsibility | Dependencies and public boundary | Reuses from |
|---|---|---|---|
| Data Integrity — `data.py` | Adapter: acquire a trustworthy normalized snapshot or explicit diagnostics | pandas plus stdlib paths/JSON/hash/temporary files/HTTP/archive handling. `read_snapshot(raw_dir, manifest_path, verify_checksums=True)`, `load_dataset(snapshot)`, `fingerprint(snapshot, config)`, `recover_dataset(manifest_path, raw_dir)`. Returns plain records; imports neither `app` nor `scoring`. | Challenge table/key contract; pandas validated left joins; hashlib, tempfile, urllib, zipfile and os. New orchestration because no application code exists. |
| Lead Prioritization — `scoring.py` | Domain + application functions: turn normalized opportunities into stage-specific priorities and evidence | Stdlib-only domain records/policies; pandas/NumPy/sklearn imported inside named fitting/attribution adapters. `build_scoring_bundle(dataset, config)` composes `split_closed_history`, `fit_candidate`, `evaluate_candidate`, `select_route`, `score_active`, `explain_score`, `recommend_action` and `rank_stage`. Does not import `data` or `app`; callers inject records. | Research calibration, coefficient/path reconstruction and nested smoothing patterns; sklearn estimators/preprocessing. New domain rules because none exist. |
| Portfolio Presentation — `app.py` | Presentation/framework: render the current portfolio and session overlay | Streamlit, `data` and `scoring`; `cached_bundle(snapshot, config)`, `render_portfolio(bundle, session)`, `set_temporary_priority`, `recalculate`. No training rules or probability reconstruction in UI. | Native dataframe selection, columns, cache_resource and session_state; approved seller/manager interaction. |

Imports at the new entry point are `import data` and `import scoring`. `app.cached_bundle` calls `data.load_dataset` then `scoring.build_scoring_bundle`; the same functions are called by integration tests. Data records are dictionaries/tuples; scoring-owned stdlib dataclasses describe result contracts. Do not create a generic `utils`, `helpers`, `common` or `shared` module. Each public use case is one named function within its approved unit, not a new class/file.

**Implementation dependency order (architecture only, not Phase 4 decomposition):**

1. Establish provenance, headers, snapshot validation and recovery. Reuse the challenge contract and stdlib/pandas mechanisms; exercise `tests/test_data.py`.
2. Freeze `ScoringConfig`, feature allowlists, temporal partition and four-candidate evaluation. Reuse the research sklearn routes; exercise `tests/test_scoring.py`.
3. Complete score unions, sparse evidence, explanations, ordering and actions. Reuse the same candidate outputs and aggregate calculation; no parallel scoring formula in UI.
4. Connect native Streamlit views, generation-aware pins and browser journeys. Reuse the immutable bundle and result-state discriminant; implement `tests/test_app.py`.
5. Run the canonical verification, capture real evidence and coordinate same-revision delivery. Reuse the submission template and existing process log; shared submission README remains orchestrator-owned.

## Building Block View

```text
                    app.py  [Streamlit + current session]
                    |                            |
          read/validate snapshot        filter, select, pin overlay
                    |                            ^
                    v                            |
data.py [files -> plain records] -> scoring.py [immutable result bundle]
                                    |          |           |
                             temporal models  relative    explanations
                             + route gates    evidence    + playbook

Explicit operator recovery -> data.py -> staged snapshot -> raw/
Tests and canonical preflight call these same three units.
```

Bounded-context vocabulary: opportunity, closed outcome, active stage, account route, validated band, relative priority, observed support, prior strength, local contribution, next action, temporary pin and calculation generation. A route is an account-feature contract; a candidate is a model family evaluated under that contract. Neither role nor seller is a predictor for Engaging, including degraded Engaging priorities.

## Contracts

### C1 — Dataset, diagnostics and snapshot identity

`Dataset` contains `opportunities` (all normalized rows), `accounts`, `products`, `sales_teams`, `diagnostics`, per-file counts and `data_fingerprint`. Preserve `opportunity_id` as a nonempty string, including leading zeroes. Required pipeline columns: `opportunity_id, sales_agent, product, account, deal_stage, engage_date, close_date, close_value`; product columns: `product, series, sales_price`; team columns: `sales_agent, manager, regional_office`; account columns: `account, year_established`. Read remaining supplied account fields for inspection but never silently substitute one header for another. Confirm these proposed physical names against the actual acquired CSV headers before freezing the manifest; an incompatible source stops acquisition with a named schema discrepancy.

Strip incidental outer whitespace, convert empty cells to missing, and apply only `GTXPro -> GTX Pro` as a product alias. Keys in dimensions and opportunity IDs must be unique and non-null; normalize before checking duplicates. Use many-to-one left joins and assert unchanged opportunity cardinality. Dates use explicit ISO parsing; numeric values must be finite. Product price must be strictly positive. Catalog currency is shown only if established by provenance; otherwise use “valor do catálogo”, never invent BRL or USD.

`Diagnostic` has `code: str`, `scope: global|row|route`, `file: str|None`, `opportunity_id: str|None`, `field: str|None`, `reason: str` and `correction: str`. Global errors include missing files/columns, unreadable CSVs, manifest mismatch, duplicate/null primary keys, recovery in progress, and no usable history/three nonempty time periods. Malformed row values, unknown product/seller keys, unusable prices and invalid stages are counted with record-specific diagnostics. Valid active rows with missing/unmatched/invalid account attributes use the account-free route with a reason. Unsupported active rows remain visible; unsupported stages appear in an input-error summary rather than being silently assigned to a stage. Bad closed records remain in accounting and are excluded from fitting with explicit reasons. A missing/negative/nonfinite Won `close_value`, or nonzero Lost value, blocks that record's financial evaluation, not its valid label/features; candidate financial comparison must report this reduced cohort and cannot silently count the value as zero.

`read_snapshot` reads the four byte buffers once, checks the recovery marker before and after, verifies their manifest SHA-256, and supplies exactly those bytes to parsing and hashing. Hash sorted filenames, content digests, manifest schema/provenance metadata and canonical JSON configuration; never hash mtimes alone. Include all feature/threshold/seed/playbook versions and the pinned runtime dependency digest in the combined fingerprint. Production checksum verification is mandatory; synthetic tests may supply their own matching manifests.

### C2 — Frozen model/evaluation policy

`ScoringConfig` is one versioned immutable value in `scoring.py`, not a settings UI. The policy below is predeclared, not a claim of measured adequacy. Altering it after final-test inspection creates a new exploratory model, not a newly untouched holdout; no test-driven threshold tuning is permitted.

| Policy | Exact decision |
|---|---|
| Label and features | `Won=1, Lost=0`. Account-free predictors: normalized `product` and `series`. Account-supported predictors add only positive integer `year_established`, a fixed historical attribute. Account identity, sector/location, revenue, employee counts and parent company are omitted as predictors because their historical point-in-time values are unverified. Price is a current catalog value for revenue/ties, not a historical predictor. No dates, stage, outcomes, seller/team fields or their derivatives enter either feature matrix. |
| Routing/support | Base row needs matched product, positive price and matched seller for portfolio ownership. Full route requires a matched account and valid founding year; otherwise use fallback with diagnosis. Training-seen product/series categories are required; unseen base categories give `insufficient_data`. If an account year falls outside full training support, use the account-free route and identify the unsupported field. Prediction and retrospective evaluation apply the same eligibility rules. |
| Time split | On valid dated closed history, group by close date and order dates ascending. First boundary is the earliest date whose cumulative count reaches `ceil(0.60*N)`; second is the earliest later date reaching `ceil(0.80*N)`. Train `date <= b1`; calibration `b1 < date <= b2`; test `date > b2`. Empty intervals or inability to choose strictly increasing boundaries block the dataset. Record exact dates/ID hashes; never split equal dates. Full/fallback use these same global boundaries, then apply route eligibility. Training-derived category/range support is frozen from each route's training rows and applied unchanged to calibration/test; report excluded IDs/reasons and period coverage rather than silently shrinking the test population. |
| Minimum evidence | Per candidate-route: at least 200 eligible train, 100 calibration and 100 test rows, with at least 20 of each label in each period. Failure is a route-level publication rejection, not a reason to reshuffle dates. Fitting may still produce a relative-only raw model if its training rows contain both labels; one-class or empty training cannot fit either classifier and uses the historical safety fallback. Full trains on complete account-supported history; fallback intentionally removes account fields from all eligible history. Report naturally missing-account subset size separately; absence is a transportability limitation, not fabricated subgroup validation. |
| Preprocessing/candidates | Train-only one-hot encoding of product/series (`drop=None`, dense output, unknown categories rejected by the support check); train-only standard scaling of founding year for full route, no imputation. Both candidates use the same transformed schema. Logistic: L2 via `l1_ratio=0`, `C=1`, `solver=lbfgs`, `max_iter=1000`. Boosting: binary `log_loss`, 100 estimators, learning rate 0.05, depth 2, minimum leaf 20, subsample 1, constant default initial prior, no early stopping. Seed 42; no hyperparameter search or refit after test. Convergence failure is a controlled failed candidate. |
| Calibration/baseline | Frozen fitted pipeline plus sigmoid `CalibratedClassifierCV` fitted only on the intermediate period, `ensemble=False`. The route baseline is its training Won prevalence, scored on the exact same test rows. All probability values must be finite in [0,1]; numerical clipping to [1e-15,1-1e-15] is only for log-loss computation, never for concealing invalid predictions. Both test losses must improve by more than 1e-12; equality fails. |
| Probability bands | Fixed bands: baixa [0,0.40), média [0.40,0.70), alta [0.70,1]. A populated test band requires at least 30 rows and absolute mean-predicted minus observed-Won rate <=0.10. At least two populated supported bands are required, with nondecreasing observed rates. Any populated failing band rejects the route candidate. Empty test bands have no validation: an active deal landing there receives relative priority with `unvalidated_band`, never a probability. |
| Candidate choice | Decide separately per route after all four outcomes are recorded. On the same eligible test IDs, rank by validated band descending, expected catalog revenue descending, ID ascending. At K=ceil(10%*N) and ceil(20%*N), compare precision@K and share of total realized Won value@K; each candidate's ranking uses its own output. Boosting wins only if all four metrics exceed logistic by >1e-12 and neither probability loss worsens by >1e-12. Otherwise choose validated logistic. If only one validates, select it. If financial comparison is undefined (no positive total or incomplete common financial labels), prefer logistic when both validate, and record why. Never compare different route populations as one candidate contest. |
| Evaluation output | Exactly four `CandidateEvaluation` records keyed `logistic/full, logistic/fallback, boosting/full, boosting/fallback`. Each has `status: passed|rejected|failed`, sample/class counts, split/feature fingerprints, losses and baseline losses, band diagnostics, top-K metrics or explicit unavailable reasons, segmented seller/team summaries and rejection reasons. No metric is invented for an unfit candidate. Bundle publication waits for every record. |

The immutable `ScoringBundle` contains `fingerprint, config_version, candidate_evaluations, selected_routes, scores, input_diagnostics, source_identity`. `source_identity` records the read-only Git HEAD when available and SHA-256 over the three application files plus requirements; the source digest is mandatory even in a Cloud checkout without Git metadata, and is included in the cache identity. The verification record links that displayed digest to the exact reviewed Git revision/diff; an unavailable HEAD is not replaced with a guessed value. It is not refitted on all closed data after choosing a model: active probabilities use exactly the training/calibration estimator that was evaluated. Fixed final-test candidate selection still creates post-selection optimism; report it and require new prospective evidence for an unbiased selected-system estimate.

### C3 — Score states, explanations, relative evidence and ordering

`ScoreResult` is a discriminated record, never a dataframe with ambiguous NaN meanings.

| Field | Contract |
|---|---|
| Identity/context | `opportunity_id: str`, `stage: Engaging|Prospecting`, `sales_agent: str|None`, `manager: str|None`, `product: str|None`, `account: str|None`. Context preserves the input identity even when invalid. |
| Claim state | `state: calibrated|relative|insufficient_data`; `route: full|fallback|prospecting|None`; `origin: logistic|boosting|historical_evidence|None`; `band: alta|media|baixa|None`; `band_kind: probability|relative|None`. `calibrated` is legal only for Engaging and a passed route plus supported band. |
| Monetary/numeric fields | `potential_revenue: positive float|None` is catalog price. Only the `calibrated` variant owns `probability: float` and `expected_revenue: float` (probability × price). Those two keys are absent, not zero, in relative/insufficient records and their UI views. `relative_index: float` exists only for relative state; no score/band exists for insufficient state. |
| Evidence/provenance | `evaluation_id: str|None`, `fingerprint: str`, `observed_n: int`, `prior_strength: float`, `effective_support: float`, `evidence_strength: forte|moderada|fraca|indisponivel`, `backoff_path: tuple[str,...]`, `diagnostics: tuple[Diagnostic,...]`. For calibrated scores, observed_n is its held-out band count; prior=0. Strong >=100, moderate 30–99, weak 1–29, unavailable 0; use observed counts, never n+alpha, for the label. |
| Explanation/action | `explanation_scale: calibrated_log_odds|raw_margin|relative_index|None`, `base_value: float|None`, all grouped `factors`, `next_action: str`. Each factor has `field, observed_value, contribution, direction, reference, actionable`. UI displays at most the top two per direction and an explicit “Sem fator favorável/desfavorável sustentado” when absent; the full vector remains available for reconstruction. |

**Relative evidence.** Use the approved nested hierarchy `product+seller+account -> product+seller -> product -> global` for Prospecting. The account-free Engaging historical safety fallback uses `product -> global`; it never uses seller/account identity. Build counts only from valid closed outcomes: train-only when evaluating a historical period, all dated closed history when producing current explicitly relative queues. Never include an active or retrospectively evaluated row's own outcome. Missing keys skip their specific groups.

Global rate is total wins/observations; if history is empty, return insufficient data. Prior strength alpha=20; group posterior is `(wins + 20*parent_rate)/(n+20)`. Compute parent-to-child; skip groups with observed n<20 and choose the deepest remaining eligible group, with global terminal regardless of size. Record every skipped group/reason. At a non-global selected group, `effective_support=n+20` is labeled “observações + peso do prior”, not independent observations; global has alpha=0 and support=N. Relative bands use posterior minus global rate: baixa below -0.05, média from -0.05 inclusive to +0.05 exclusive, alta at >=+0.05. Explain the global baseline plus selected hierarchy deltas; telescoping deltas reconstruct the final index and expose each group's observed count. Do not sum overlapping counts or represent this index as a prospect closing probability.

**Degraded Engaging.** If no calibrated candidate/active band is eligible, use the fitted logistic raw margin for that route; use fitted boosting only when logistic cannot produce a valid finite reconstructable margin. Define relative bands by the route's training-margin 1/3 and 2/3 quantiles (linear quantile method), with equality assigned to the upper interval; if the cutoffs coincide, use only “média” to avoid artificial separation. The underlying margin stays explicitly nonprobabilistic. If neither estimator is usable, reuse the seller-free product/global historical evidence above. If even that evidence is unavailable, show insufficient data. Record why probability was suppressed and which source actually supplies the relative priority.

**Faithful model explanations.** Logistic transformed-value × coefficient plus intercept reconstructs raw margin. Boosting uses initial constant log-odds plus learning-rate-weighted tree roots as base; child-minus-parent values along each reached path are assigned to the split feature and grouped back to original columns. No global feature importance masquerades as a local contribution. For a selected sigmoid calibrator, map base and contributions by its actual affine log-odds transform, including zero/reversed slopes; test both raw margin and final predict_proba reconstruction at absolute/relative tolerance 1e-8. Isolate version-sensitive calibration coefficient access in one scoring function. Do not describe contributions as probability percentage points. Attribution-shape/additivity failures are correctness failures that block delivery, not tolerated model underperformance.

**Versioned playbook v1.** Among supported actual factors, choose the largest absolute actionable contribution, ties by field name. Product or series evidence in Engaging maps to “Confirmar com a conta se o produto atende à necessidade e combinar o próximo passo comercial”; in Prospecting, to “Validar a necessidade para este produto antes de avançar para engajamento”. These are verification actions, not claimed interventions that increase closure. Founding year, seller and account identity are not actionable factors. A hierarchical factor involving several keys is actionable only as evidence for verifying the observed product, never for changing seller/account. Zero contribution (absolute value <=1e-12), insufficient state or no actionable factor returns exactly `Sem ação recomendada com os dados atuais`.

**Ordering.** Within a stage, render separate labeled calibrated, relative and insufficient sections; their numeric priorities are not interchangeable. The calibrated Engaging section sorts band descending, unrounded expected revenue descending, then opportunity ID lexicographically ascending. Relative sections are partitioned by route, origin and explanation scale so margins from different fitted models are never compared as one numeric score; within each partition sort band descending, relative index descending, potential revenue descending, then ID ascending; insufficient rows sort by ID. Preserve original scores when pinning. A manager pin appears in a distinct top strip inside its stage, once, and is removed from its normal section while pinned; an unsupported pinned row still has no score. Seller/team expected-revenue totals sum calibrated Engaging rows only and state coverage (scored/total), so missing values never masquerade as zero.

### C4 — Streamlit and session lifecycle

Use `st.tabs` for the two stages, a native single-row-select dataframe and adjacent `st.columns` details. Provide explicit accessible labels for role, identity, regional office, manager seller filter, recalculation and temporary priority. Seller defaults to selected seller; manager defaults to sellers mapped to the selected manager, with “Todas as regiões”, “Todos da equipe” and exact-membership region/seller filters. Display the prototype/no-auth context. Unassigned/invalid seller rows remain visible in a separate data-quality area, since they cannot safely be assigned to a seller.

Store `fingerprint`, `calculation_generation: int`, `selection_by_stage` and `pins_by_stage` in `st.session_state`. Each stage allows one `TemporaryPin(opportunity_id, manager, created_at_utc, fingerprint, generation)`; choosing another replaces only that stage's pin. The callback rechecks current manager context and portfolio membership. Display manager and localized timestamp. Pins survive ordinary stage/filter changes, are visible only if they still match the current portfolio, and clear on explicit recalculation, new session or changed fingerprint. A role/identity change clears selections; hidden pins remain session-local and cannot give a seller pin controls.

Each rerun verifies the actual snapshot fingerprint before cache lookup. Cache the immutable bundle by exact bytes/combined fingerprint and canonical config; filters/role/pins are not arguments. Recalculation increments the session generation and clears that session's pins/selections, even if the immutable cached computation can be reused for unchanged data/config. Never call a global cache clear merely to expire one user's pins.

Resolve selected positions against the exact displayed section's ID list; key/reset each table by stage, role, filters and ordered ID fingerprint. Changing context cannot keep a stale deal panel. If the selected portfolio is empty, show “Nenhuma oportunidade neste filtro” and no selected panel or pin action. For a failed route, probability and expected-revenue fields/metrics are absent from rows, details, hover text and totals for those rows; a separate diagnostic panel may display validation losses, never a rejected deal probability.

### C5 — Recovery, reproducibility and evidence boundaries

The proposed explicit command is `.venv/bin/python data.py recover --manifest data/manifest.json --raw-dir data/raw`. It is never reachable from app initialization. Manifest entries identify source/license URL, exact CSV name, SHA-256, acquisition date, source download URL and optional archive member; the production URL is the public Kaggle endpoint pinned with `datasetVersionNumber=1`, because the unversioned API path returns 404. Recovery supports direct CSV or exact allowlisted ZIP members, rejects traversal/symlinks and never extracts arbitrary archive paths. Sources use HTTPS; local HTTP is allowed only by test fixtures. Changed upstream bytes cause a failure, not an automatic checksum update.

Before any replacement, acquire an exclusive `data/.recovery.lock` directory, download all four files into a temporary sibling directory, validate all checksums and schemas, then rename existing `raw` to a unique backup and promote the complete staged directory to `raw` on the same filesystem. Readers fail closed while the marker exists and recheck it after reading. If promotion or final verification fails, restore the original directory and verify original digests. On rollback failure/crash, retain marker, backup and staging with exact recovery instructions; never remove the only original. A `recover --resume` command reads the transaction record, restores the recorded original snapshot first and verifies it before clearing the marker. Lock/transaction paths and expected digests are validated against the solution data directory. This is a guarded transaction with recoverable interruption, not a claim that two renames are one atomic operation. The replacement strategy follows [Python filesystem rename guarantees](https://docs.python.org/3.11/library/os.html#os.replace).

`requirements.txt` pins the complete resolved Python 3.11 runtime and test set. Start from the research candidates for Streamlit/pandas/NumPy/SciPy/sklearn; use stdlib `unittest`, not the optional research pytest dependency. Add and pin Playwright for its already-approved browser tests, with matching Chromium installed explicitly during setup, and constrain `protobuf<6` for Streamlit Community Cloud compatibility. A fresh disposable Python 3.11 venv must install solely that file, pass `pip check` and execute the same canonical preflight. Freeze the proven versions; candidate pins are not claimed as installed. Missing interpreter/browser/dependency is a blocking gate, never an optional skip.

Canonical command: `bash scripts/preflight.sh`. It creates an isolated temporary Python 3.11 venv, installs only the pinned requirements and matching Playwright Chromium, then checks dependencies/imports, runs `unittest` discovery over the three test files (including seeded property cases and the local recovery server), completes the four-route real-data evaluation, and runs Streamlit startup plus Playwright journeys. On the managed Codespace, where the base image currently exposes Python 3.14 rather than 3.11, the gate bootstraps pinned `uv` in a disposable bootstrap venv, installs CPython 3.11 and creates the test venv with `uv venv --seed --python 3.11`; local execution uses the already-required Python 3.11 directly. The shell command owns clean-environment setup exactly once; TC-46 verifies startup inside that environment and never recursively invokes preflight. Cleanup touches only the temporary environment and child processes created by that invocation. A statistically rejected route is a valid evaluated outcome; incomplete evaluation, invalid output, exceptions, missing tests or failed assertions return nonzero. Test methods have stable TC IDs; existing 47 distinct TC contracts remain mapped to the business matrix. `tests/test_app.py` owns both AppTest lifecycle checks and Playwright journeys; no fourth test file or separate frontend suite is required. Local discovery contains only local checks. TC-47 is a separate explicit post-deploy `verify_live_revision(url, expected_revision, expected_source_digest, expected_fingerprint)` verifier in that same file, invoked through its `live` CLI mode with those four required arguments. It is not a discovered local TestCase that skips when a URL is missing; its nonzero result blocks delivery after deployment, avoiding a preflight/deploy dependency cycle.

Extend the existing verification obligations without rewriting Acceptance Criteria: TC-03 injects second-rename and rollback failures; TC-34/35 include empty portfolios and a fixture forcing a failed probability route; TC-36 checks absent probability/revenue in that fixture's detail panel; TC-44 denies external networking after installation during load/train/score; TC-46 includes clean-venv installation and teardown of only the spawned server. Use a temporary copied app plus fixture data/config in tests, never a production “test mode” or edits to real CSVs. Disable Streamlit usage telemetry on the spawned command. Offline denial permits loopback for local browser/recovery fixtures and fails attempted external traffic; no network prohibition is bypassed by stubbing a successful external response.

Resolve the Python/package/browser versions in a clean environment before the real final evaluation, record the complete lock digest and then freeze them with the scoring policy. Source-compatibility fixes remain possible, but reusing a revealed test after changed model policy must be labeled exploratory rather than new validation.

The full automated gate follows the approved managed-Codespace execution policy via `codespace-manager list` / `codespace-manager run`, at the exact intended source/diff and data fingerprint. Fresh local Python 3.11 reproduction remains separately required evidence; remote success cannot be described as a local run. Both use the same portable command, no Node build is introduced, and no secrets are copied. These gates run during implementation, not this architecture phase.

Capture evidence by separate fields in `docs/evaluation.md`: actual dataset/join counts, four route records, selected route/source, baseline/model metrics, temporal/feature/config identities, environment/dependency digest, verified source revision, commands/status, seller screenshot and manager screenshot. List each CK-43 limitation and pilot recommendation separately so bundled checklist failures stay diagnosable. Screenshots over synthetic error fixtures are labeled as such. Record those findings in the challenge process log; hand its concise section to the shared-README owner. After all local/managed gates and browser inspection pass, configure Community Cloud for Python 3.11 with the nested app entrypoint and repository root as working directory. Verify the same source revision, fingerprint and rendered journey at the Community Cloud URL; HTTP readiness alone is insufficient. Delivery remains blocked if that external proof is unavailable.

## Runtime Scenarios

Source: scratchpad Step 3.7.

| Scenario | Observable flow |
|---|---|
| First load / supported seller | Verify snapshot -> fit/cache all four route outcomes -> choose stage-specific result state -> seller portfolio -> select exact opportunity -> show true factors and action. Subsequent filters reuse fitted computation. |
| Missing account / rejected probability | Missing/unusable account -> account-free pipeline; rejected route or unsupported probability band -> explicit relative section with actual-score explanation and validation reason. No deal probability or expected revenue survives in any UI surface. |
| Invalid row / empty portfolio / global failure | Unsupported active row -> visible “Dados insuficientes” with field/correction; empty selection -> empty-state message; global corruption or impossible temporal split -> stop scoring with actionable diagnostics. |
| Manager intervention | Manager team -> optional region/seller filters -> temporary pin with author/time -> unchanged result moved to stage top; filtering retains state -> recalculation/new session/fingerprint change expires it. |
| Recovery failure | Explicit CLI -> acquire marker -> stage/verify whole snapshot -> replace -> verify; write failure -> restore and verify original; failed rollback -> keep backup and marker, block app, explicit resume recovers. |

```text
loaded -> validated -> four outcomes complete -> calibrated / relative / insufficient
   |          |
   +--error---+-------------------------------> blocked with correction

session generation N -> pin -> filtered view (pin retained)
                     -> recalculate / new fingerprint -> generation N+1 (pins cleared)
```

## Expected Changes

All paths are under `submissions/luis-roquette/`; architecture artifacts are excluded from this future implementation footprint.

```text
README.md                                      NEW; orchestrator-owned integration
process-log/003-lead-scorer.md                   UPDATE; decisions and verified evidence
process-log/screenshots/003-lead-scorer-seller.png   NEW; real browser evidence
process-log/screenshots/003-lead-scorer-manager.png  NEW; real browser evidence
solution/003-lead-scorer/
  .gitignore                                   UPDATE; venv/cache/recovery generated paths
  app.py                                       NEW; native UI/cache/session overlay
  data.py                                      NEW; snapshot/joins/recovery CLI
  scoring.py                                   NEW; all scoring/evaluation/explanations/actions
  requirements.txt                             NEW; complete pinned Python 3.11 environment
  README.md                                    NEW; setup/run/gates/policy/limits
  data/manifest.json                           NEW; real source/license/checksums
  data/raw/accounts.csv                        NEW; verified real data
  data/raw/products.csv                        NEW; verified real data
  data/raw/sales_teams.csv                      NEW; verified real data
  data/raw/sales_pipeline.csv                   NEW; verified real data
  scripts/preflight.sh                          NEW; portable canonical failing gate
  tests/test_data.py                           NEW; schema/recovery/real-data checks
  tests/test_scoring.py                        NEW; policy/fidelity/determinism checks
  tests/test_app.py                            NEW; AppTest + Playwright + startup
  docs/evaluation.md                           NEW; measured outcomes and proof identity
```

Minimum footprint remains 20 paths: 2 existing updates, 17 Lead Scorer-owned creations and 1 shared README integration; zero deletions. Recovery locks/backups, environments and browser outputs are generated artifacts, not application modules or versioned datasets. The repository root currently ignores `submissions/`; preserve root rules and intentionally include only approved submission deliverables when the later authorized Git stage occurs.

---

## Implementation Process

You MUST launch for each step a separate agent, instead of performing all steps yourself. And for each step marked as parallel, you MUST launch separate agents in parallel.

**CRITICAL:** For each agent you MUST:

1. Use the **Model** and **Agent** type specified in the step's sub-task file.
2. Provide the path to THIS task file AND the path to that step's sub-task file.
3. Require agent to implement exactly that step, not more, not less, not other steps.

**CRITICAL:** Verification is done at PHASE level, not per step. When every step of a phase is complete, you MUST launch `sdd:code-reviewer` ONCE for that phase, at the **Reviewer model** named in the Phase Overview. Individual step tests still run before the step reports completion. Phase review does not replace those tests or the canonical preflight.

The maximum concurrent implementation width is 3; this dependency graph reaches 2. Do not add nested fanout. Parallel pairs MUST be done in parallel with their stated exclusive file ownership. Complete each phase review before starting the next phase. Artifact dependencies in the table are distinct from that phase-review barrier. The implementation orchestrator owns shared `submissions/luis-roquette/README.md` integration using the exact Lead Scorer section supplied by step `06-delivery-documentation`; it MUST finish that integration before Phase 3 review. Git/provider operations remain subject to the established authorization and integrity rules.

### Parallelization Overview

```text
Phase 1
01-validated-snapshot [sdd:developer / opus]
    |
    +-------------------------------+
    v                               v
02a-verified-recovery            02b-temporal-evaluation
[sdd:developer / opus]           [sdd:developer / opus]
(data + test_data only)          (scoring + test_scoring only)
    |                               |
    +---------------+---------------+
            Phase 1 review [opus]
          (both branches required)
                        |
Phase 2 (artifact prerequisite for both lanes: 02b)
    +-------------------+-------------------+
    v                                       v
03a-explainable-priorities             03b-portfolio-session-ui
[sdd:developer / opus]                [sdd:developer / sonnet]
(scoring + test_scoring only)         (app + test_app only)
    |                                       |
    +-------------------+-------------------+
                        v
             04-canonical-verification
                [general sonnet / sonnet]
                        |
              Phase 2 review [opus]
                        |
Phase 3                 v
             05-verified-cloud-delivery
                [general sonnet / sonnet]
                        |
                        v
             06-delivery-documentation
                [sdd:tech-writer / sonnet]
                        |
              Phase 3 review [opus]
```

| Step | Phase | Model | Agent | Depends on | Parallel with | Sub-Task File |
|------|-------|-------|-------|------------|---------------|---------------|
| `01-validated-snapshot` [DONE] | Phase 1 | opus | sdd:developer | None | None | `.specs/sub-tasks/implement-explainable-lead-scorer/01-validated-snapshot.md` |
| `02a-verified-recovery` [DONE] | Phase 1 | opus | sdd:developer | `01-validated-snapshot` | `02b-temporal-evaluation` | `.specs/sub-tasks/implement-explainable-lead-scorer/02a-verified-recovery.md` |
| `02b-temporal-evaluation` [DONE] | Phase 1 | opus | sdd:developer | `01-validated-snapshot` | `02a-verified-recovery` | `.specs/sub-tasks/implement-explainable-lead-scorer/02b-temporal-evaluation.md` |
| `03a-explainable-priorities` [DONE] | Phase 2 | opus | sdd:developer | `02b-temporal-evaluation` | `03b-portfolio-session-ui` | `.specs/sub-tasks/implement-explainable-lead-scorer/03a-explainable-priorities.md` |
| `03b-portfolio-session-ui` [DONE] | Phase 2 | sonnet | sdd:developer | `02b-temporal-evaluation` | `03a-explainable-priorities` | `.specs/sub-tasks/implement-explainable-lead-scorer/03b-portfolio-session-ui.md` |
| `04-canonical-verification` [DONE] | Phase 2 | sonnet | general sonnet | `03a-explainable-priorities`, `03b-portfolio-session-ui` | None | `.specs/sub-tasks/implement-explainable-lead-scorer/04-canonical-verification.md` |
| `05-verified-cloud-delivery` | Phase 3 | sonnet | general sonnet | `04-canonical-verification` | None | `.specs/sub-tasks/implement-explainable-lead-scorer/05-verified-cloud-delivery.md` |
| `06-delivery-documentation` | Phase 3 | sonnet | sdd:tech-writer | `05-verified-cloud-delivery` | None | `.specs/sub-tasks/implement-explainable-lead-scorer/06-delivery-documentation.md` |

### Phase Overview

#### Phase 1: Trustworthy data and callable temporal evidence [REVIEWED]

Steps: `01-validated-snapshot`, `02a-verified-recovery`, `02b-temporal-evaluation`
Reviewer model: `opus`

The real dataset can be loaded, diagnosed and explicitly recovered; all four candidate-route evaluations are callable and tested. This is a working data/evidence solution, not yet a claim that the seller UI exists.

Acceptance Criteria that should be fulfiled:

Checklist items:

- `CK-1` — Four real CC0 CSVs with source, license and checksums.
- `CK-2` — Explicit recovery verifies bytes before replacement.
- `CK-3` — Required files, schemas, keys, types and prices validated.
- `CK-4` — GTXPro normalized before product join.
- `CK-5` — Invalid rows accounted for and global failures diagnosed.
- `CK-7` — Outcome/date/stage values and derivatives absent from features.
- `CK-8` — All features available at scoring decision.
- `CK-9` — Both model families evaluated on both account routes.
- `CK-12` — Calibration uses only intermediate temporal period.
- `CK-14` — Candidate selection compares validated ranking/value evidence.

Rubrics:

- `Correction Specificity`

#### Phase 2: Working explainable seller and manager application [REVIEWED]

Steps: `03a-explainable-priorities`, `03b-portfolio-session-ui`, `04-canonical-verification`
Reviewer model: `opus`

The complete Streamlit application works on real data or explicit degraded/insufficient states. The canonical clean-environment gate, real evaluation, offline execution and rendered local journeys pass with TC-01 through TC-46. The live verifier exists but TC-47 is not claimed until Phase 3.

Acceptance Criteria that should be fulfiled:

Checklist items:

- `CK-6` — Closed-only disjoint chronological training; active-only scoring.
- `CK-10` — Missing account uses deliberate account-free route.
- `CK-11` — Seller/team excluded from direct Engaging prediction.
- `CK-13` — Published probabilities have route-specific held-out evidence.
- `CK-15` — Probability band precedes expected-revenue tie-break.
- `CK-16` — Rejected probabilities/revenue absent from every visible result.
- `CK-17` — Prospecting is smoothed relative historical evidence.
- `CK-18` — Sparse evidence backs off to the global base.
- `CK-19` — Prospecting shows support/potential revenue, never expected revenue.
- `CK-20` — Actual selected-model contributions reconstruct scores.
- `CK-21` — Portuguese favorable/unfavorable factors carry values/direction.
- `CK-22` — Versioned deterministic grounded next action or exact no-action.
- `CK-23` — Unsupported active deals remain visible with correction.
- `CK-24` — Separate Engaging and Prospecting tabs.
- `CK-25` — Seller-own and manager-team defaults without auth claim.
- `CK-26` — Manager filter changes membership, not scores.
- `CK-27` — Compact rows open complete side details.
- `CK-28` — Manager-only pins change display order, not scores.
- `CK-29` — Pins show manager and timestamp.
- `CK-30` — Pins stay session-only and expire on new calculation/session.
- `CK-31` — Data/config fingerprint invalidates cached computation.
- `CK-32` — Deterministic results and reuse across filters/navigation.
- `CK-33` — Zero paid or generative runtime calls.
- `CK-34` — Only three approved application units.
- `CK-35` — Fresh Python 3.11 reproduction with pinned dependencies.
- `CK-36` — Synthetic cases and real-four-CSV integration.
- `CK-37` — One canonical preflight fails on every failed required gate.
- `CK-38` — Rendered seller/manager journeys recorded.
- `CK-50` — No unsupported causal claim; compliance is NO.

Rubrics:

- `Probability Evidence Traceability`
- `Correction Specificity`
- `Explanation Fidelity`
- `Ranking Test Discrimination`

#### Phase 3: Verified live delivery and submission evidence

Steps: `05-verified-cloud-delivery`, `06-delivery-documentation`
Reviewer model: `opus`

The validated source revision is published and rendered live, TC-47 passes, all evidence/limitations are documented and the shared submission owner has integrated the Lead Scorer section. Completion requires actual external proof; a missing deployment/access outcome remains a blocker.

Acceptance Criteria that should be fulfiled:

Checklist items:

- `CK-39` — Measured counts, metrics, routes, screenshots and revision proof.
- `CK-40` — Copyable commands, scoring rationale, limits and scaling.
- `CK-41` — Rendered Community Cloud URL matches validated revision.
- `CK-42` — All changed files inside submissions/luis-roquette/.
- `CK-43` — All stated limits and pilot/audit/recalibration recommendations.
- `CK-44` — No duplicated functions/scoring rules/concepts.
- `CK-45` — Only applicable touched-scope cleanup; optional.
- `CK-46` — Every selected test type implemented.
- `CK-47` — Every scratchpad matrix main/edge/error case implemented.
- `CK-48` — Behavior checklist resolves to real passing tests.
- `CK-49` — Every Test Cases to Cover entry implemented and passing.
- `CK-50` — No unsupported causal claim; compliance is NO.

Rubrics:

- `Probability Evidence Traceability`
- `Explanation Fidelity`
- `Project Guidelines Alignment`
