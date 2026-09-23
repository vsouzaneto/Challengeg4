# Step 02b: Frozen contracts and four-route temporal evaluation

**Task File:** `.specs/tasks/todo/implement-explainable-lead-scorer.feature.md`

> The task file moves between `.specs/tasks/{draft,todo,in-progress,done}/` as work progresses; if it is not at this path, resolve it by its filename under `.specs/tasks/`.

**Phase:** Phase 1
**Model:** opus
**Agent:** sdd:developer
**Depends on:** `01-validated-snapshot`
**Parallel with:** `02a-verified-recovery`
**Note:** MUST run in parallel with 02a-verified-recovery. Own scoring.py and tests/test_scoring.py. Freeze the complete C2/C3 result/config contract before the Phase 2 parallel agents start; no edits to data.py or the dependency lock.

**Goal:** Produce four independently auditable candidate-route outcomes without leakage or test-driven policy changes.

Consume the C1 Dataset from data.load_dataset, injected as plain records; scoring.py must not import data or app. Define immutable ScoringConfig, CandidateEvaluation, ScoringBundle and the C3 ScoreResult variants/factor fields before implementation consumers. Implement split_closed_history, fit_candidate, evaluate_candidate and select_route according to every fixed C2 row. Establish the build_scoring_bundle(dataset, config) callable signature and result serialization contract for Phase 2 without publishing fabricated/placeholder active scores. Synthetic example bundles are test-only. Use the pinned dependency set from 01; freeze policy/config digest before the first real final evaluation. Non-trivial statistical algorithms and the shared result contract earn opus.

All paths are relative to `submissions/luis-roquette/solution/003-lead-scorer/` unless explicitly identified as repository paths. Read `.claude/skills/explainable-crm-prioritization/SKILL.md` and task contracts before edits. Keep writes within the participant submission, preserve unrelated work, and make no paid AI API calls.

#### Expected Output

- scoring.py immutable records/config, chronological partitions, train-only feature adapters, full/fallback logistic and boosting candidates, intermediate calibrators and four CandidateEvaluation records
- tests/test_scoring.py fixture builders, contract examples for all C3 states, synthetic policy cases and real-data four-route integration

#### Success Criteria

- [x] TC-08 through TC-14, TC-16 through TC-21 and TC-43 pass for this step's temporal/features/evaluation scope; active-routing assertions of TC-08/12/16/20 are completed by 03a.
- [x] Every real evaluation returns exactly logistic/full, logistic/fallback, boosting/full, boosting/fallback passed/rejected/failed records with exact split IDs/counts, feature identities, losses/baseline, band coverage and unavailable reasons.
- [x] Training transformations/estimators, intermediate calibrators and final evaluation use disjoint global date groups; unseen product/series and unsupported full-route year values are excluded with exact reasons under train-frozen support.
- [x] Selection compares identical route test IDs using declared K values and valid financial labels; invalid or inconsistent boosting cannot win; no eligible candidate is an explicit supported outcome.
- [x] C3 serializers omit probability/expected_revenue keys from relative and insufficient variants; concrete test fixtures make app/scoring parallel work independent of unfinished model implementation.

#### Subtasks

- [x] Define all C2 config values and C3 immutable record/serialization fields in scoring.py and tests/test_scoring.py fixtures; freeze feature, cutoff, seed, playbook and dependency identities before real holdout use.
- [x] Implement split_closed_history with global tied-date 60/80 cumulative cutoffs and route-specific train-frozen support; implement allowlists and provenance checks excluding dates/stage/outcomes/seller/team/price from predictors.
- [x] Implement train-only full/fallback preprocessors and logistic/boosting fit_candidate adapters, controlled convergence/fitting failures and intermediate-only frozen sigmoid calibration.
- [x] Implement evaluate_candidate and select_route for exact losses/support/bands, ranking and financial concentration comparisons, segmented diagnostics, common cohort checks and four completed outcomes; record fixed holdout reuse/transportability limitations.
- [x] Write tests/test_scoring.py TC-08–14/16–21/43 with named boundary neighbors, forbidden-field mutations, synthetic loss/selection decision tables and one real four-CSV evaluation; run all currently implemented scoring tests.

#### Blockers & Risks

| Type | Item | Impact | Likelihood | Mitigation / Resolution |
|------|------|--------|------------|-------------------------|
| Blocker | The real dataset cannot form three nonempty global date periods | High | Low | Return a global named diagnostic; do not alter cutoffs or invent a holdout to manufacture probability. |
| Risk | Inspecting the final set leads to tuning thresholds or comparing different populations | High | Medium | Freeze C2/config before real evaluation; compare common route IDs, record all exclusions and label any later changed policy exploratory. |
| Risk | Calibration API or model failure is confused with statistical rejection | High | Medium | Test pinned APIs on synthetic data first; distinguish failed/rejected/passed and prevent incomplete four-route publication. |
