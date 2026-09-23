# Architecture record — Support Decision Copilot

Role: `sdd:software-architect`; Phase 3; 2026-09-21. Planning only.

## Inputs and scope

Read the full task, research skill, impact analysis, research/business scratchpads and relevant prior implementation-plan interfaces. The plan-task auxiliary scripts/prompts are absent; this file is the explicit fallback scratchpad. No code, dependency installation, dataset processing or runtime verification occurred. No existing runtime helpers exist to reuse.

## Decisions carried into Architecture Overview

1. One offline Python process, native Streamlit, stdlib SQLite/CSV and separate per-domain sklearn pipelines; exact library lock remains contingent on the complete framework proof.
2. Preserve 60/20/20 on eligible deduplicated records; quarantine conflicting canonical-text labels; use independent calibration-fit and policy-selection halves within calibration. Report infeasible class support rather than borrowing test examples.
3. Explicit unsupported/disabled/unavailable states and nullable predictions replace fabricated probabilities and the unsafe threshold=1.0 disable sentinel.
4. Version observable input/risk signals and deterministic priority ordering. OOD heuristics describe limited detection, not universal safety. Rules can only block automation.
5. Human retrieval review has a binding packet identity, calibration lock and separate final review. Fewer than 30 distinct eligible queries means insufficient evidence, never duplication or a weaker gate.
6. Privacy boundaries include input, edits, notes and exports. Known-name/regex masking is limited; unresolved free text is quarantined, and reviewed public evidence requires manual inspection.
7. One SQLite event table with unique submission ID, transaction/readback, factual nulls and authoritative decision snapshots. Export is a persistent file plus bytes from committed rows, and a separately reviewed public evidence copy.
8. A typed JSON manifest ties sources/splits/configuration/lock/policies/model versions/artifact hashes to feature availability; hashes are integrity checks only within a trusted local root.
9. Reproduction is resumable with frozen locks, immutable final-evaluation settings and logical determinism; missing human review permits only explicitly incomplete source-only mode.

## Resolved review gaps

The added section specifies TicketSignals, scalar/batch Prediction, ModelTrainingResult, RoutingPolicy, RouteDecision, RetrievalResult, DecisionEvent/StoredDecision, ExportResult, Manifest and their function returns. It resolves runtime and evidence export paths; accessibility remains in native UI requirements. The source analysis inventory gains one reviewed CSV evidence artifact and a generated review lock; no service or generic abstraction is introduced.

## Deliberate limits and evidence not yet available

No data count, benchmark, library version compatibility, PII completeness, stratification feasibility, model skill or human retrieval result is asserted as measured. Two retrieval samples and real persisted approval evidence remain hard gates; insufficient data or invalid assistance can leave final acceptance unmet while still yielding a safe partial demo. The phase does not change acceptance criteria to manufacture completion.

Only `## Architecture Overview` was appended to the task. Description and Acceptance Criteria remain untouched; decomposition belongs to Phase 4. Later subtask contracts must follow this section where the earlier plan's signatures, threshold sentinel, export omissions and calibration protocol conflict.

## Judge 3 — iteration 2 corrections

P1 OOD propagation: `DomainModel` owns the fitted TF-IDF transform and row-level `nnz == 0` measurement. `Prediction.zero_vector: bool | None` carries measured false/true or unavailable; `derive_signals` copies it, and true/null explicitly invalidate the input and block routing. Scalar/batch and adversarial high-confidence checks are specified. The gate no longer depends on an unprovided vector signal.

P1 draft safety: `TicketRetriever.suggest(..., *, signals: TicketSignals)` now requires the same derived signals in both reproduction and UI. Its internal guard runs before draft creation, blocking Critical, sensitive, failed privacy/input/artifact and unknown/unsafe vector signals regardless of score. Failed privacy/input also blocks lookup; safe sources may remain source-only for Critical/sensitive cases. Callers cannot create drafts directly from returned sources. Retrieval/workflow regression obligations name both pipeline and UI paths.

Only these Phase 3 contracts and this scratchpad were revised; all other decisions and task sections are preserved. `git diff --check` is the formatting verification; no implementation or runtime pass is claimed.
