# Step 06: Measured submission evidence, limitations and shared README handoff

**Task File:** `.specs/tasks/todo/implement-explainable-lead-scorer.feature.md`

> The task file moves between `.specs/tasks/{draft,todo,in-progress,done}/` as work progresses; if it is not at this path, resolve it by its filename under `.specs/tasks/`.

**Phase:** Phase 3
**Model:** sonnet
**Agent:** sdd:tech-writer
**Depends on:** `05-verified-cloud-delivery`
**Parallel with:** None
**Note:** Documentation only: own solution README.md/docs/evaluation.md and ../../process-log/003-lead-scorer.md. The shared ../../README.md remains implementation-orchestrator-owned; provide and integrate its exact Lead Scorer section through that owner before Phase 3 review.

**Goal:** Make the delivered app reproducible and reviewable without overstating probability, business impact or execution evidence.

Read the official submission template and consume the actual verified evidence from docs/evaluation.md and screenshots from 05-verified-cloud-delivery. Finish solution README.md and append the measured decision/error/validation account to ../../process-log/003-lead-scorer.md without rewriting prior history. Provide the ready-to-integrate Lead Scorer section to the owner of ../../README.md; the orchestration directive requires that integration before completion. Documentation references the immutable validated source/deployment revision; a documentation-only later commit is not misrepresented as the runtime revision. Sonnet applies because this synthesizes several evidence files and local narrative decisions, not one mechanical README edit.

All paths are relative to `submissions/luis-roquette/solution/003-lead-scorer/` unless explicitly identified as repository paths. Read `.claude/skills/explainable-crm-prioritization/SKILL.md` and task contracts before edits. Keep writes within the participant submission, preserve unrelated work, and make no paid AI API calls.

#### Expected Output

- README.md with copyable Python 3.11 setup, requirements/browser install, preflight, run, recovery and live-verifier commands; scoring rationale and limits
- docs/evaluation.md complete measured counts/four outcomes/cohort identities/selected routes/metrics/coverage/source/dependency/live evidence ledger
- ../../process-log/003-lead-scorer.md appended process/evidence account and exact shared ../../README.md section handed to and integrated by its owner

#### Success Criteria

- [ ] CK-39/40/43 evidence is individually traceable: every actual count/route metric/screenshots link has provenance and local/managed/live execution are clearly distinguished.
- [ ] All 47 TC IDs, every selected type and all main/edge/error partitions in .specs/scratchpad/4002b33e.md resolve to real passing tests/live result; structural/documentary checks and CK-50 NO are explicit.
- [ ] Each documented command/link is exercised or resolved, not merely copied; a clean setup run reproduces the recorded source/data identity; no invented successful calibration metric is introduced.
- [ ] Limits individually cover static data, incomplete Prospecting labels, noncausal associations, session-only pins, absent auth/writeback/drift/retraining, post-selection/transportability/censoring limits and controlled pilot/outcome capture/audit/recalibration.
- [ ] The shared submission owner has integrated the reviewed Lead Scorer section and links without overwriting other challenges; final source/doc scope remains under submissions/luis-roquette/.

#### Subtasks

- [ ] Finish README.md command recipes and explain stage/route/state semantics, expected catalog versus realized revenue, actual explanations/actions and each limit/pilot recommendation using measured evidence.
- [ ] Complete docs/evaluation.md with separate CK-39 evidence fields and CK-43 limitation clauses, TC-01..47 test method/live-result mapping, environment/dependency/source identities and actual rendered URL/screenshots.
- [ ] Append the real process, human decisions, discovered errors/corrections and validation in ../../process-log/003-lead-scorer.md; hand the exact template-compatible Lead Scorer section to the shared ../../README.md owner and verify its integration before review.
- [ ] Write and execute documentation acceptance test cases in docs/evaluation.md for each setup/run/preflight/recovery/live command and local evidence link; use disposable recovery fixtures and existing checks, verify no causal claims, and record results without adding a redundant test framework.

#### Blockers & Risks

| Type | Item | Impact | Likelihood | Mitigation / Resolution |
|------|------|--------|------------|-------------------------|
| Blocker | Shared README owner has not integrated the agreed Lead Scorer section | Medium | Medium | Deliver exact ready-to-paste section and links to the implementation orchestrator; final review waits for scoped integration, never replace the cross-challenge README independently. |
| Risk | Documentation reports different source/deploy identity or claims a rejected model succeeded | High | Medium | Use the immutable evidence ledger and cite verified source revision separately from later documentation commits; show rejection honestly. |
| Risk | Bundled limits or test coverage hide one missing obligation | Medium | Medium | List CK-39 fields, CK-43 clauses and TC IDs individually; inspect matrix partitions and execute documented acceptance cases. |
