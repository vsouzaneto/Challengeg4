# Step 04: Portable canonical preflight and complete local evidence

**Task File:** `.specs/tasks/todo/implement-explainable-lead-scorer.feature.md`

> The task file moves between `.specs/tasks/{draft,todo,in-progress,done}/` as work progresses; if it is not at this path, resolve it by its filename under `.specs/tasks/`.

**Phase:** Phase 2
**Model:** sonnet
**Agent:** general sonnet
**Depends on:** `03a-explainable-priorities`, `03b-portfolio-session-ui`
**Parallel with:** None
**Note:** Own scripts/preflight.sh, gate/startup/live-verifier additions in tests/test_app.py, and initial README.md/docs/evaluation.md. Existing score/data tests may only receive missing integration assertions; logic fixes go to their owning functions and rerun all gates.

**Goal:** Make one failing canonical command prove clean installation, full offline pipeline and rendered journeys at the exact intended source identity.

Apply C5 to the complete app from 03a/03b. Create bash scripts/preflight.sh to provision one disposable Python 3.11 venv, install locked requirements and matching Chromium, verify imports/pip check, discover local unittest tests, evaluate all four real routes, then start/stop only its own Streamlit process and execute Playwright journeys. In the managed Codespace, bootstrap pinned `uv` from the base interpreter, install CPython 3.11 and create the venv with `uv venv --seed --python 3.11`; this preserves `python -m pip check` even though the base image currently has Python 3.14. Reuse the same production data/scoring functions; no second evaluator or fourth test/application module. Add the explicit post-deploy verifier now so later deployment does not change tested runtime/test code. This is a bounded verification/tooling integration with settled contracts; source inspection across three files is not a three-module rewrite.

All paths are relative to `submissions/luis-roquette/solution/003-lead-scorer/` unless explicitly identified as repository paths. Read `.claude/skills/explainable-crm-prioritization/SKILL.md` and task contracts before edits. Keep writes within the participant submission, preserve unrelated work, and make no paid AI API calls.

#### Expected Output

- scripts/preflight.sh canonical gate with nonzero failure propagation and bounded child/temporary cleanup
- tests/test_app.py TC-44/45/46 checks and explicit live CLI verify_live_revision(url, expected_revision, expected_source_digest, expected_fingerprint) for TC-47
- README.md copyable initial setup/test/run/recovery instructions; docs/evaluation.md measured local/managed evidence, coverage map and revision/digest fields

#### Success Criteria

- [x] bash scripts/preflight.sh passed in managed Codespace at `e052e4e` (74/74); after the review fixes, the exact SHA `9228ffd` passed 6/6 focused regressions and the owner explicitly waived the new integral repetition. The duplicate heavy Mac execution remains prohibited by AGENTS.md.
- [x] TC-44 blocks outbound runtime networking but permits loopback fixtures; TC-45 injects a failing required gate and observes nonzero; TC-46 proves clean setup/startup and child-only teardown without recursive preflight.
- [x] Every TC-01..TC-46 resolves to real passing stable named tests, including all business matrix partitions; TC-47 is an explicit separate required live gate, never a silently skipped discovered test.
- [x] Complete pipeline records four actual outcomes and rejects invalid/incomplete outputs; legitimately rejected probability candidates do not fail solely for underperformance.
- [x] The live verifier requires all four explicit arguments and rejects a mismatched rendered source identity/fingerprint or missing active-stage view; invocation behavior has synthetic/local negative tests.

#### Subtasks

- [x] Implement scripts/preflight.sh with strict failure propagation, one disposable environment owner, locked install/browser setup, imports/tests/full real evaluation and local rendered journeys; disable spawned Streamlit telemetry.
- [x] Add tests/test_app.py TC-44/45/46 for external-network denial, gate failure injection and safe server teardown; reuse tests/test_data.py loopback fixtures and avoid hidden installed dependencies.
- [x] Implement tests/test_app.py live CLI and verify_live_revision with explicit URL/revision/source-digest/fingerprint arguments; write local positive/negative verifier tests without pretending they satisfy actual TC-47.
- [x] Run the canonical gate via codespace-manager at `e052e4e` with pinned `uv`/Python 3.11 (74/74), then run the six post-review AppTest/Playwright and contract regressions at exact SHA `9228ffd` (6/6 in 26.818 s). The owner explicitly waived the post-review integral repetition and the duplicate heavy Mac reproduction; no full post-fix result is claimed.
- [x] Write README.md setup/run/test/recovery commands and docs/evaluation.md TC/CK coverage map with actual test method names and statuses; resolve every local deterministic failure, re-run the canonical gate and retain honest global/route rejection diagnostics.

#### Post-review evidence (2026-09-22)

- RED at `7d023604c318264d2e85005652c65c49c7a5620a`: 6 tests, 2 failures and 4 errors, exposing all five review gaps.
- GREEN at `9228ffdf3ff760efe0ecfb9b107d9a537c26789b`: 6 focused tests in 26.818 s, all passing, including rendered AppTest and Playwright journeys.
- The last completed full preflight remains 74/74 at `e052e4e226a8962fc338380e6cebb2e6446dc86b`. A post-fix full run was started but interrupted by explicit owner order and is not evidence of an integral pass. TC-47 remains out of scope.
- Residual review 2: tests were committed at `2dbc3e561b845bc11c8b54ce25219209da4b4669` and implementation at `af046c4a4d9c90f4c3e3968260b3306e794659bc` for one active grid selection and CK-19 Prospecting support/pin details. The owner extended the bypass to Codespace waiting and local AppTest/Playwright, so these tests are written but unexecuted; `py_compile`, `bash -n` and `git diff --check` passed. No executed GREEN is claimed.

#### Blockers & Risks

| Type | Item | Impact | Likelihood | Mitigation / Resolution |
|------|------|--------|------------|-------------------------|
| Blocker | Python 3.11, matching Chromium or an exact-diff managed environment is unavailable | High | Medium | Treat missing runtime as blocker; use the shared codespace-manager, preserve dirty/active workspaces, never substitute a different SHA or skip a gate. |
| Risk | Preflight recursively creates environments or kills unrelated sessions | High | Low | Single shell owner tracks its exact temporary path and child PID; TC-46 proves bounded cleanup and no recursion. |
| Risk | Live verification is accidentally part of pre-deploy discovery | Medium | Medium | Keep TC-47 in explicit live CLI only; test verifier locally, then require actual live invocation in 05. |
