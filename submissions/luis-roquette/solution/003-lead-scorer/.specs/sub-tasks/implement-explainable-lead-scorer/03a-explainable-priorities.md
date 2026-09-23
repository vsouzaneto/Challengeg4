# Step 03a: Complete stage scores, faithful factors and deterministic actions

**Task File:** `.specs/tasks/todo/implement-explainable-lead-scorer.feature.md`

> The task file moves between `.specs/tasks/{draft,todo,in-progress,done}/` as work progresses; if it is not at this path, resolve it by its filename under `.specs/tasks/`.

**Phase:** Phase 2
**Model:** opus
**Agent:** sdd:developer
**Depends on:** `02b-temporal-evaluation`
**Parallel with:** `03b-portfolio-session-ui`
**Note:** MUST run in parallel with 03b-portfolio-session-ui after the Phase 1 review. Own scoring.py and tests/test_scoring.py only. Preserve the C3 contracts already frozen by 02b; no app.py or tests/test_app.py edits.

**Goal:** Turn evaluated models and historical evidence into truthful, reconstructable active-deal priorities for both stages.

Implement build_scoring_bundle, score_active, explain_score, recommend_action and rank_stage in scoring.py using the exact C2 model artifacts and C3 records from 02b-temporal-evaluation. No full-history probability refit occurs. Implement calibrated, relative and insufficient states, honest empty-band suppression, full-to-fallback support routing, nested Prospecting evidence, raw-model degraded Engaging and seller-free historical safety fallback. All local contributions reconstruct their actual score on the labeled scale; no surrogate explanations or UI scoring rules. Non-trivial attribution/smoothing algorithms earn opus.

All paths are relative to `submissions/luis-roquette/solution/003-lead-scorer/` unless explicitly identified as repository paths. Read `.claude/skills/explainable-crm-prioritization/SKILL.md` and task contracts before edits. Keep writes within the participant submission, preserve unrelated work, and make no paid AI API calls.

#### Expected Output

- scoring.py complete immutable ScoringBundle with all active results, evidence, grouped contributions, stage ordering and v1 playbook
- tests/test_scoring.py routing, score-state, additive reconstruction, smoothing, action, ranking and seeded invariant cases

#### Success Criteria

- [X] TC-15, TC-22 through TC-32 and TC-42 pass; complete active-scoring aspects of TC-08/12/16/20/43 and retain TC-14 real integration.
- [X] Logistic intercept+grouped contributions and tree initial/root/path contributions reconstruct margins; calibrated affine transformation handles zero/reversed slope and reconstructs predict_proba within C3 tolerance.
- [X] Prospecting follows product+seller+account -> product+seller -> product -> global with alpha=20, observed-support >=20, explicit skipped levels and prior labeling; it never owns probability/expected_revenue keys.
- [X] Rejected routes/unvalidated active bands remove probability and expected revenue entirely, prefer reconstructable logistic relative margins, then boosting, then seller-free product/global evidence; empty support yields correction-specific insufficient data.
- [X] rank_stage catches lower-band-expensive versus higher-band-cheap reversal, separates incomparable relative origins/routes/scales and preserves lexical ID ties; actions use the exact C3 Portuguese messages without causal claims.

#### Subtasks

- [X] Implement build_scoring_bundle/score_active routing and variant serialization in scoring.py, preserving every active input identity and using only evaluated probability models.
- [X] Implement nested relative evidence and observed/prior support in scoring.py; add degraded-model training-quantile bands and seller-free historical fallback without duplicating Prospecting aggregation logic.
- [X] Implement explain_score for logistic and exact tree path decomposition; isolate sigmoid coefficient access and group transformed features back to observed fields with explicit scale.
- [X] Implement recommend_action v1 and rank_stage from C3, including no-action/absent-direction messages, stage/route/origin partitions, expected-product-revenue semantics and deterministic ties.
- [X] Write and run tests/test_scoring.py TC-15/22–32/42 plus complete shared TC-08/12/16/20/43; use hand-computed smoothing, raw/calibrated additivity, unseen support, equal-quantile and seeded ordering/state invariants.

#### Blockers & Risks

| Type | Item | Impact | Likelihood | Mitigation / Resolution |
|------|------|--------|------------|-------------------------|
| Blocker | Pinned sigmoid internals or tree shape cannot reconstruct actual output | High | Medium | Isolate adapter and fix against pinned synthetic estimator outputs; treat failed additivity as a correctness blocker, not acceptable statistical degradation. |
| Risk | Degraded states leak rejected probabilities or introduce seller-based Engaging ranking | High | Medium | Variant serialization excludes forbidden keys; test seller invariance across every fallback and validate all origin/scale partitions. |
| Risk | Prior support or associations are presented as observations/causal actions | High | Medium | Expose observed n separately from alpha and use telescoping true contributions plus verification-only playbook wording. |
