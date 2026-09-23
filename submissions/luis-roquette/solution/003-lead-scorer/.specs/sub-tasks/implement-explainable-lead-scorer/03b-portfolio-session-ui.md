# Step 03b: Native seller/manager portfolios with cache and session overlays

**Task File:** `.specs/tasks/todo/implement-explainable-lead-scorer.feature.md`

> The task file moves between `.specs/tasks/{draft,todo,in-progress,done}/` as work progresses; if it is not at this path, resolve it by its filename under `.specs/tasks/`.

**Phase:** Phase 2
**Model:** sonnet
**Agent:** sdd:developer
**Depends on:** `02b-temporal-evaluation`
**Parallel with:** `03a-explainable-priorities`
**Note:** MUST run in parallel with 03a-explainable-priorities after the Phase 1 review. Own app.py and tests/test_app.py only. Develop against 02b's exact C3 synthetic contract fixtures, then exercise real build_scoring_bundle once 03a finishes; never alter scoring.py contracts.

**Goal:** Provide the approved single-screen seller/manager experience while keeping cached computations immutable and pins session-local.

Implement app.cached_bundle(snapshot, config), render_portfolio(bundle, session), set_temporary_priority and recalculate from C4. Reuse data.read_snapshot/load_dataset/fingerprint and scoring.build_scoring_bundle; the interface performs filtering and display only. Native st.tabs, selectable dataframe and st.columns provide comparisons/details. Config/result schema and algorithms are already fixed; this is ordinary single-presentation-module work with local UI choices, so sonnet applies rather than a new subsystem trigger.

All paths are relative to `submissions/luis-roquette/solution/003-lead-scorer/` unless explicitly identified as repository paths. Read `.claude/skills/explainable-crm-prioritization/SKILL.md` and task contracts before edits. Keep writes within the participant submission, preserve unrelated work, and make no paid AI API calls.

#### Expected Output

- app.py with native labeled controls, two stage tabs, sectioned rows/details, input-quality and route diagnostics, cache identity and session pins
- tests/test_app.py with AppTest state checks and Playwright seller/manager journeys using synthetic contract bundles/temp app copies

#### Success Criteria

- [x] TC-33 through TC-41 pass first against frozen C3 contract fixtures; the completed real `build_scoring_bundle` integration is owned by 04 after 03a is available. TC-40 also proves data/config/source changes cause a new cache identity and unchanged filters do not refit.
- [x] Seller starts at own portfolio; manager starts at only the selected manager's team, supports exact regional-office and seller filtering and shows prototype/no-auth context; unassigned seller rows stay in data-quality view.
- [x] Selection always resolves an ID from the exact displayed table; stage/role/filter/order changes cannot leave stale details; empty portfolios have explicit message and no pin action.
- [x] Only manager callback can pin a current portfolio deal, one per stage, with manager/time; scores remain byte-equivalent; filtering retains valid hidden state, recalculation/new browser session/new fingerprint clears overrides.
- [x] Failed-route rows/details/hover/totals expose no probability or expected revenue; calibrated-only totals show coverage; insufficient rows keep named corrections, even when pinned.

#### Subtasks

- [x] Implement app.py snapshot verification/cache entry and source identity (read-only HEAD when available plus required three-source/requirements SHA-256) without sending filters or pins into the cache key.
- [x] Implement role/identity/region/team/seller controls, st.tabs and stage-specific calibrated/relative/insufficient sections plus unassigned-row quality diagnostics in app.py; do not invent currency.
- [x] Implement native row selection/adjacent details with stage-context-ID keys, strongest two factors per direction, origin/support/actions, empty-state handling and visible version/fingerprint diagnostics.
- [x] Implement st.session_state generation, selection and one pin per stage in app.py; recheck manager/portfolio in callback and clear session state without global cache clear.
- [x] Write tests/test_app.py TC-33–41 with AppTest and Playwright, using isolated browser contexts and temporary fixture copies for insufficient/failed-route/empty states; keep this step fixture-only so parallel work does not depend on unfinished 03a.

#### Implementation Evidence

- Fixture-first Codespace gate: 8/8 tests passed on CPython 3.11.16; TC-33 through TC-41 are mapped explicitly in `tests/test_app.py`.
- Expanded Streamlit gate: 9/10 passed; the remaining Playwright journey stopped during browser setup because the bare Codespace lacked `libatk-1.0.so.0`, before any product assertion. `playwright install --with-deps chromium` installed the missing OS dependencies, but the manager left the environment active and safely refused a second session. The canonical rendered-browser rerun remains required in step 04.
- `python3.11 -m py_compile app.py tests/test_app.py` passes locally. No real 03a implementation was consumed; step 04 owns real bundle integration.

#### Blockers & Risks

| Type | Item | Impact | Likelihood | Mitigation / Resolution |
|------|------|--------|------------|-------------------------|
| Blocker | Native dataframe selection differs from pinned Streamlit/Playwright behavior | Medium | Medium | Use the pinned native API and accessible labels; prove exact ID mapping through browser tests instead of adding a custom grid. |
| Risk | Shared cached results are mutated by a manager or stale row positions | High | Medium | Copy presentation overlays only, assert immutable scores and reset selection keys on context/order changes. |
| Risk | Synthetic UI success hides real result-contract mismatch | High | Medium | Use 02b's concrete C3 fixtures and run the same journeys on the completed real bundle in 04 before phase review. |
