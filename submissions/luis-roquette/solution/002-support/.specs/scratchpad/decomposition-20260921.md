# Phase 4 decomposition

The task architecture is the contract authority; earlier plan signatures are superseded. No implementation, training, download, paid call, publication or gate execution was performed by this planning step.

Ten steps, three runnable milestones. Environment/proof and packaging are combined; all data contracts/splits/manifest are combined; model selection/calibration and risk policy stay together to avoid circular implementation ownership. Store owns transactional integrity. Retrieval owns review packet/lock semantics. The integration owner alone edits final UI/pipeline entrypoints. Documentation and real human evaluation can proceed independently after integration.

Phase 1: 01 -> 02 -> 03. A runnable local diagnostic application uses sanitized real data, exposes valid denominators and clearly reports missing decision capabilities. Phase 2: 04 and 05 parallel; 06 after 04; 07 joins 03/04/05/06. A working complete application exercises pending-review/abstention and persistence; synthetic fixtures exercise approved drafts, without masquerading as real human evidence. No real frozen-test data opens here. Phase 3: 08 and 09 parallel after 07; 10 joins them. Human calibration/test evidence and final demo become real artifacts, or the exact blocking dependency remains visible.

Dependency graph: 01:none; 02:01; 03:02; 04:02; 05:02; 06:02,04; 07:03,04,05,06; 08:07; 09:07; 10:08,09. Phase review barriers additionally apply; no artifact dependencies are invented to encode those barriers. Critical scheduling chain with barriers: 01 -> 02 -> 03 -> phase-1-review -> 04 -> 06 -> 07 -> phase-2-review -> 08 -> 10 -> phase-3-review. Longest artifact-only chain: 01 -> 02 -> 04 -> 06 -> 07 -> 08 -> 10. Human review wait can dominate 08. Peak implementation concurrency 2 (04/05, then 05/06 if 05 still running; 08/09).

Model triggers: 01 sonnet ordinary bounded framework proof; 02 opus shared ingestion/manifest contract and split integrity; 03 sonnet fixed analytics in one module plus thin presentation; 04 opus cross-model/routing shared contract and nontrivial calibration; 05 opus data integrity; 06 opus nontrivial threshold/packet integrity across evaluation lifecycle; 07 opus breadth across UI/pipeline/components; 08 opus test independence/data integrity; 09 sonnet multi-document editorial work with established template; 10 sonnet established end-to-end verification/evidence capture. No mechanical single-file task warrants haiku. Reviewer opus for each phase, capped at highest available tier.

Distribution: developer 3 (01,05,07); data-engineer 2 (02,03); ml-engineer 3 (04,06,08); tech-writer 1 (09); test-engineer 1 (10). Models: opus 6, sonnet 4, haiku 0. Ten steps each carry five actionable subtasks (50 total); three conceptual merges above prevent unnecessary agent churn.

High-priority risk families (7): privacy/quarantine; leakage/frozen-test lifecycle; model/risk and retrieval bypass; SQLite/export integrity; artifact trust/partial publication; genuine human review or insufficient eligible sample; final real approval evidence impossible when all safe drafts are disabled. Each is assigned a mitigation in its owning step. External blockers never become synthetic results or implicit approval.

Checklist mapping: phase1 CK-2/3/4/5/6; phase2 CK-7/9/10/11/13/14/15/17; phase3 CK-1/8/12/16/18/19/20. Earlier criteria are rechecked at final evidence capture; phase2 CK-7 refers to development isolation/freeze enforcement, and CK-15 to the working UI with test fixtures, not delivery proof. Full real-data outcome is only claimed at phase3.

## Iteration 2 — Judge 4 findings

1. Step 07 now explicitly creates `test_reproduce_twice_same_inputs`, comparing canonical logical outputs from two identical pipeline runs, with only `manifest.generated_at` excluded. Binary hashes verify each instance; logical hashes compare serializations. The deterministic fixture has no generic numeric tolerance; real-data numerical comparisons still follow the unchanged architecture.
2. Step 07 seals snapshot S07 after the phase-2 review. Step 08 runs only its named reproduction test from the immutable, hashed copy, never the workflow file edited by step 09 or whole-suite collection during the parallel window. Snapshot/code/config/lock fingerprints are checked; step 10 runs final consolidated gates after both steps. Diagram/table interpretation and steps 07–10 now name the same ownership and snapshot contract. Graph and concurrency remain unchanged.
3. Step 06 owns protocol documentation exclusively in `src/support_copilot/retrieval.py` module docstring/CLI help. Step 05 owns its README changes in the parallel window; step 09 consolidates the protocol into delivery docs later. No new architecture component or public file added.

Pre-edit SHA-256 of all task content before `## Implementation Process`: `9d0acd739559858b9cef54ad3fb2c5f870aaa535026a40e59844dc2fe081d8e3`; validation must confirm unchanged after this iteration.
