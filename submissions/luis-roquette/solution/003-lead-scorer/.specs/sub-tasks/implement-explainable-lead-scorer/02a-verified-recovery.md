# Step 02a: Explicit snapshot recovery with rollback and resume

**Task File:** `.specs/tasks/todo/implement-explainable-lead-scorer.feature.md`

> The task file moves between `.specs/tasks/{draft,todo,in-progress,done}/` as work progresses; if it is not at this path, resolve it by its filename under `.specs/tasks/`.

**Phase:** Phase 1
**Model:** opus
**Agent:** sdd:developer
**Depends on:** `01-validated-snapshot`
**Parallel with:** `02b-temporal-evaluation`
**Note:** MUST run in parallel with 02b-temporal-evaluation. Own only recovery/read-guard additions in data.py and recovery cases in tests/test_data.py; do not edit scoring.py, requirements.txt or tests/test_scoring.py.

**Goal:** Make operator-requested recovery preserve the original four-file dataset through download, promotion and interrupted rollback failures.

Use data.py read_snapshot/load_dataset and the exact manifest produced by 01-validated-snapshot. Pin the public Kaggle archive source to dataset version 1 with `datasetVersionNumber=1`; the unversioned endpoint is invalid. Implement recover_dataset(manifest_path, raw_dir) plus the recover and recover --resume CLI from C5. Recovery acquires data/.recovery.lock, stages all four downloads, verifies complete digests/schema, renames original raw to a unique backup and promotes the staged snapshot on the same filesystem. On any failure restore and verify the original; failed restoration retains marker/backup/transaction metadata and tells the operator how to resume. Never treat two renames as one atomic operation or reach recovery from app startup. Data integrity and destructive-replacement error handling earn opus.

All paths are relative to `submissions/luis-roquette/solution/003-lead-scorer/` unless explicitly identified as repository paths. Read `.claude/skills/explainable-crm-prioritization/SKILL.md` and task contracts before edits. Keep writes within the participant submission, preserve unrelated work, and make no paid AI API calls.

#### Expected Output

- data.py recovery functions, validated transaction/resume record and explicit CLI
- tests/test_data.py local HTTP/archive fixtures and rollback fault-injection cases

#### Success Criteria

- [x] TC-02 and TC-03 pass: valid staged data promotes; digest/schema mismatch leaves every original byte unchanged; failure on second rename restores original digests.
- [x] Injected rollback failure keeps the only original and lock intact; recover --resume validates in-scope transaction paths and restores the original before clearing the marker.
- [x] ZIP traversal/symlinks/unlisted members and unexpected external plain HTTP sources are rejected; only exact listed CSV members are consumed; readers fail closed while recovery is active.
- [x] .venv/bin/python data.py recover --manifest data/manifest.json --raw-dir data/raw is documented in CLI help and never runs implicitly.

#### Subtasks

- [x] Implement C5 explicit data.py argparse recovery entrypoint using stdlib HTTPS/download/archive handling, with allowlisted exact members and verified staging.
- [x] Implement exclusive lock, bounded transaction record, original/staging path validation and guarded two-rename promotion in data.py; retain recoverable backup on failure.
- [x] Implement data.py recover --resume and restoration verification; share read_snapshot/load_dataset validation rather than duplicating schemas.
- [x] Write tests/test_data.py TC-02/03 cases using temporary directories and loopback HTTP, inject promotion/rollback/interruption failures, check startup/import makes no recovery request, and run the whole data test file.

#### Feedback loop and validation evidence — 2026-09-21

1. **Planning/review:** read the step, C1/C5 and the required CRM skill. Inspection found that the official ZIP also contains `metadata.csv`. The step-01 owner changed the manifest to four direct, version-pinned Kaggle CSV URLs; archive recovery retains the strict exact-member allowlist.
2. **Execution:** added explicit recovery/`--resume`, an exclusive directory marker plus POSIX advisory owner lock, an 8-KiB bounded scoped transaction record, checksum/schema-verified staging and guarded promotion/rollback. Interrupted readers fail closed. Successful backups and completed transaction records are retained; clearing the marker is one rename, avoiding a record-less cleanup interruption window. No runtime/startup call initiates recovery.
3. **Test:** fresh environment through `codespace-manager run codex-preflight-657v7q4ggx7f5557` after observing `Shutdown/clean`; CPython 3.11.16, `uv==0.10.12`, pinned `requirements.txt`, `pip check` → `No broken requirements found`. `.venv/bin/python -m unittest discover -s tests -p test_data.py -v` → **23/23 passed in 11.416 s**, including all 14 step-01 tests against the direct-URL manifest and nine TC-02/03 recovery test methods with fault-injection subcases. Exec session **14275**, terminal **exit 0**; manager confirmed completion and automatic stop. Log: `/tmp/lead-step02a-gate.log` (local transient evidence).
4. **Identity:** transported archive SHA-256 `678c2cfdb6216efe614b164d9f172514c8ebd549dc009718a0900207587eb819`; remote/local hashes matched: `data.py` `793b03a5177a7c01062901e76818f2635e2bf1a13ce2e33bb2d8b707e8a57386`; `tests/test_data.py` `d70261a71582061899c37bd4f93b2430f643eca7c5aefc0e6eda6b27e5884c5e`; manifest `b79e8d484d66dfa7c39bc7fe138169da84150548d8ec858aae18aad613abc5e2`; dependency lock `43a420f22b5e31ceadf0946434689dca39359c7a69d358e4636ee6c0fb344843`. Local checks were AST parsing and `git diff --check`; no heavy local gate ran.

**Self-critique / handoff:** POSIX file locking deliberately targets the approved macOS/Linux environments. Backups are preserved rather than auto-pruned. `--resume` restores actual original bytes, even when originally damaged; a subsequent explicit fresh recovery repairs them. The app does not yet exist, so absence of implicit recovery is proven for module import and dataset initialization; later application integration must keep it unreachable. The phase gate must rerun data and scoring tests together because step 02b previously tested the pre-recovery data module. No failed code-test iteration occurred in this step; the archive/source incompatibility was corrected during review before the green gate.

#### Review feedback loop 1 — 2026-09-21

The phase review found an initialization interruption not covered by the first green gate. The previous 23-test result remains historical evidence, not proof of the corrected revision.

- **High, resolved:** initialization now prepares the complete, flushed/fsynced record in a unique private `data/.recovery-<id>-init/` directory, then publishes that directory as `.recovery.lock` with one rename. A stable advisory owner lock under `.recovery-owner/` serializes initialization, publication and resume. A visible marker therefore always carries a complete record. Before publication, raw remains unchanged and readable; explicit resume returns `no_published_transaction`. After publication, resume verifies/restores the recorded original and clears the guard. Private aborted initialization records are retained, not silently deleted.
- **Medium, resolved:** extracted scoped-path resolution, owner locking, transaction publication, resume and verified promotion/rollback into cohesive helpers inside `data.py`. `recover_dataset` is 14 physical lines; the module has no function above 80 lines. Existing step-01 parsing/normalization helpers are preserved. No new application unit or dependency was added; broad contextual rollback coverage remains deliberately intact.
- **Medium, resolved:** removed internal `data.load_dataset`/`data._download` mocks. Final-validation failure now comes from actual CSV corruption immediately after filesystem promotion; staging interruption comes from `Path.mkdir`; concurrency observations happen while the real loopback HTTP server blocks on events. The new initialization regression injects interruption after private-directory creation, during an actual partial record write and immediately after marker publication, verifying exact original bytes, reader state, successful resume and subsequent fresh recovery. An actual duplicate ZIP member also joins the archive rejection cases.
- **Test, passed:** fresh managed Codespace run from `Shutdown/clean`, exec session **20962**, terminal **exit 0**. CPython **3.11.16**, pinned requirements, `pip check` → `No broken requirements found`; the entire `test_data.py` suite passed **24/24 tests in 13.561 s** (all 14 step-01 methods plus ten recovery methods). Log: `/tmp/lead-step02a-review1-gate.log`; manager confirmed automatic stop. AST, `git diff --check` and ignore rules for generated owner/init paths passed locally.
- **Identity:** transported archive `5a8b0831d31196fe1adbe4ae0f7cc741c76792b2517228e9a667334a7dd8487c`; matching local/remote `data.py` SHA-256 `617c115c4941e665491506d573dc9ca0faef73e0fe170c1614c6bb9b36f42fb4`, `tests/test_data.py` `e19c9d8ec1c36163bdc1b89c570a64f15926a851e0aeab2db3ebdbc35f6ed408`. Manifest and dependency-lock hashes remain those recorded above. The combined phase review must now test these artifacts with current scoring before advancing.

#### Blockers & Risks

| Type | Item | Impact | Likelihood | Mitigation / Resolution |
|------|------|--------|------------|-------------------------|
| Blocker | Existing recovery marker refers to an unresolved interrupted transaction | High | Low | Refuse fresh recovery; validate recorded in-scope paths and execute explicit resume, never auto-delete the original backup. |
| Risk | Failure between the two renames or during rollback loses the original | High | Medium | Fault-inject both failures; keep marker and unique backup until original or new snapshot is fully verified. |
| Risk | Archive or transaction path escapes the solution data directory | High | Low | Resolve and validate every path; reject traversal and symlinks; extract only expected bytes into controlled staging. |
