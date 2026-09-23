# Business analysis record — Support Decision Copilot

Role: `sdd:business-analyst`; planning only; 2026-09-21.

## 1. Evidence and authority

Sources: draft, decision ledger I06–I37, approved implementation plan, compliance audit, research note, Challenge 002, submission guide and CONTRIBUTING. The installed plan-task skill supplies artifact/judge contracts; auxiliary role prompts are absent. No product execution or implementation is claimed.

## 2. Actors and outcome

Support agents need a prioritized queue, explainable routing, safe historical drafts and durable human decisions. The Operations director needs quantified bottlenecks, credible automation boundaries and working evidence. The evaluator needs reproducibility, the submission-root README and a contemporaneous process log.

## 3. Scope authority

I06 records 24 decisions; I07 approves six synthesis sections. I37 authorizes faithful SDD adaptation and validated feedback loops. The local demonstration uses both domains without merging records/categories. Paid APIs, external responses, helpdesk integration, authentication, tenancy, deployment and online learning remain excluded.

## 4. Data constraints

Recorded source inspection: 8,469 customer rows; 47,837 IT rows; eight IT classes; customer creation timestamp absent; 5,700 resolutions/ratings missing; 1,365 negative intervals among 2,769 timestamp pairs. These are source-version observations, not universal invariants. Reproduction must report actual counts/hashes. `post_response_hours` is the only supported elapsed-time measure.

## 5. Scenario coverage

Five scenario families: startup/daily queue; historical suggestion plus approval/edit; rejection/escalation/failure; executive diagnostic and scenario decisions; independent IT free-text classification. Normal, alternative and error expectations are mapped to checklist/test IDs.

## 6. Business policies

Unsafe automation is costlier than fallback. Risk overrides confidence. Weak classification, absent evidence and invalid artifacts disable affected automation. Human review validates historical drafts. Test results cannot tune a model or threshold. Save confirmation means a committed local event; exports are sanitized/versioned.

## 7. Numerical decisions preserved

Independent stratified 60/20/20 splits; seed 42; five-fold training CV; minimum 0.02 macro-F1 improvement versus dummy; 0.01 tie margin favors simplicity. Routing grid 0.50–0.95 by 0.05, maximum 10% selective calibration error; no qualifying nonempty selection means disabled even at confidence 1.0. Current plan/audit prescribe 30 calibration and 30 independent test queries for retrieval, superseding older ledger references to 50. Retrieval grid 0.20–0.90 by 0.10 requires mean correctness/safety at least 4/5 and no safety below 3. No qualifying evidence means no drafts.

## 8. Trust-boundary coverage

Cover PII reintroduced in edits, invalid probabilities, unknown domain/class, empty/OOD input, stale/corrupt artifacts, transaction rollback and spreadsheet-formula export payloads. This enforces existing privacy and safe-persistence commitments. Audit duplicate text leakage; record exact policy/model/data versions used at decision time.

## 9. Verification and project guidelines

No runnable Makefile, application, tests or CI workflow yet exists. The approved plan defines `make doctor`, `make test`, `make lint`, `make reproduce`, `make demo`, focused pytest and Ruff commands; these remain planned gates, not passing evidence. Heavy gates use codespace-manager and exact intended SHA. Public diff stays under submissions/luis-roquette; root README follows the official template; process entries accompany checkpoints. Current user/global instructions override conflicting historical command examples.

## 10. Output contract and remaining evidence

One `# Description`, one `## Acceptance Criteria`, six ordered blocks; 20 boolean criteria (18 essential, 2 important), five checks, five weighted rubric dimensions totaling 1.0, five test types, 20 checklist-linked test groups. No architecture/decomposition/scoring configuration written. Actual code, gates, human ratings and SPEC review remain future evidence; nothing fabricated.
