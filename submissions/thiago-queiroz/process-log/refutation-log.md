# Refutation Log: Prototype Scope

## Generation 1

- Review: `deleg_129bf6b9`
- Manifest SHA-256: `f5167b81c0392f67392a7c84983c9733aa3381c9accfcbf672e3150b87393a6a`
- Schema Gate: `WARN`
- Semantic Score: `7.86/10`
- Decision: `REVISE`
- Severities: `C0/H2/M4`
- Safe to build: `false`

## Refutations accepted

### H-01: claim-to-evidence was conceptual, not executable

Accepted. A concrete `evidence/claim-evidence-map.json` now binds every planned UI claim to allowed text, forbidden interpretations, source, hash, method, limitations and test ID. Build must reject unresolved hash markers before freeze.

### H-02: decision matrix was not unambiguous

Accepted. `evidence/decision-map.json` now defines exactly one primary state, reason, claim IDs, allowed CTA and forbidden CTA for each of the five questions.

### M-01: evidence plan lacked canonical commands and run identity

Accepted. Harness Brief now defines canonical commands, deterministic run ID, environment fields, input/output hashes, test counts, browser/console/network evidence, screenshots and criterion-to-artifact mapping.

### M-02: state machine lacked entry/evidence/next/rollback

Accepted. Harness Brief now contains an operational transition table and a policy for rejected generations, refutation and archive.

### M-03: MVP lacked timebox and cut line

Accepted. Timebox is one challenge day with explicit allocations. Extra dimensions, export and animation are cut before safeguards, tests or the decision flow.

### M-04: five AI Master fronts lacked visible acceptance evidence

Accepted. Harness Brief now maps each front to one visible component, one artifact and one acceptance criterion. AI process evidence is included as a sixth evaluation row.

## New generation

Generation 2 includes:

- updated Harness Brief;
- `evidence/claim-evidence-map.json`;
- `evidence/decision-map.json`;
- `evidence/process-timeline.json`;
- this refutation log;
- updated prototype scope.

Generation 1 remains rejected and must not be relabeled. Generation 2 was reviewed separately and also remains rejected.

## Generation 2

- Review: `deleg_bf81cf78`
- Manifest SHA-256: `9d45858f47101b78ad1448d68ba7c71ee0b222dd59dc32d33f7101e1dab59daf`
- Schema Gate: `FAIL`
- Semantic Score: `8.8/10`
- Decision: `REVISE`
- Severities: `C0/H1/M3`
- Safe to build: `false`

## Refutations accepted for generation 3

### H-01: metric claim used a non-canonical Markdown anchor

Accepted. `CLM-METRIC-001` now references `docs/prototype-scope.md#4-metric-contract`, and the source hash was recalculated after the scope update.

### M-01: failure states lacked operational contracts

Accepted. All six fail-closed states now define entry condition, mandatory evidence, allowed next action and rollback.

### M-02: sponsorship claim implied a composite engagement metric

Accepted. The claim now names the four component metrics actually audited: views, likes, shares and comments_count. It does not state that composite ER was tested.

### M-03: sustainability promised one command without an entrypoint

Accepted. `scripts/build_all.py` is now the specified single fail-closed rebuild command; the test command remains separate verification evidence.

Generation 3 was reviewed and remains rejected. Neither previous verdict may be reused.

## Generation 3

- Review: `deleg_589bfc1c`
- Manifest SHA-256: `47031c5f8cfeaabeda17862a3857c0818e6525aaed3a2f839bcbcdc1795b5684`
- Schema Gate: `FAIL`
- Semantic Score: `9.0/10`
- Decision: `REVISE`
- Severities: `C0/H1/M0`
- Safe to build: `false`

## Refutation accepted for generation 4

### H-01: experiment rules were left as a placeholder

Accepted. The two MVP experiments now define hypothesis, unit/randomization, primary metric, explicit provisional SESOI, required fields, success, inconclusive and no-go conditions, guardrails and the only action allowed after each outcome. The thresholds are explicitly not business-validated; a live run remains `NOT_AUTHORIZED` until human confirmation and a power/sample-size plan.

The prototype-scope hash and its claim-map reference were recalculated. Generation 4 was reviewed and remains rejected.

## Generation 4

- Review: `deleg_b34cd0d8`
- Manifest SHA-256: `5dcd48ce54ecd72aedd37e5df6ed954b47bdb63f28b12931eecb3eb253a1c305`
- Schema Gate: `PASS`
- Semantic Score: `9.1/10`
- Decision: `REVISE`
- Severities: `C0/H1/M0`
- Safe to build: `false`

## Refutation accepted for generation 5

### H-01: experiment rules did not partition every possible confidence interval

Accepted. Both experiment contracts now apply an explicit priority order: guardrail failure or `upper <= 0` returns `NO_GO`; with guardrails clear, `lower > SESOI` returns `SUCCESS`; every remaining finite interval returns `INCONCLUSIVE`. This covers intervals below zero, crossing zero, wholly between zero and SESOI, touching SESOI and above SESOI. Guardrails are evaluated conservatively by 95% confidence bounds.

The rules were also encoded in `evidence/experiment-contracts.json` with seven boundary cases. Live use remains blocked pending human threshold confirmation and a power/sample-size plan. Generation 5 requires a new manifest and review.

## Advisory pre-freeze review of the first MVP candidate

- Review: `deleg_ea4ed372`
- Schema Gate: `FAIL`
- Semantic Score: `6.8/10`
- Decision: `BLOCK`
- Severities: `C3/H4/M0`
- Safe to freeze: `false`

This verdict remains rejected and cannot be relabeled after remediation.

### C-01: screenshot hashes were not authenticated

Accepted. The QA validator now requires the exact six-file inventory, opens each screenshot, rejects missing/non-regular/multi-link files and recomputes every SHA-256. Regression probes cover forged and missing captures.

### C-02: navigated bytes were not bound to the reviewed HTML

Accepted. The QA runner no longer accepts an arbitrary URL. It navigates the local `dist/index.html` via `file://`, hashes each browser response body and rejects any mismatch against the exact on-disk artifact.

### C-03: completed stages remained pending

Accepted. The canonical timeline now records scope approval, prototype build, QA and the blocked advisory review. Only the final authoritative Cético and the human publication decision remain pending.

### H-01: build manifest was incomplete

Accepted. The manifest now records deterministic `run_id`, Python/OS, canonical commands, test result/count, browser/console/network fields, exact screenshot inventory and all ten success-criterion mappings.

### H-02: visual coverage did not match the Harness Brief

Accepted. The six canonical captures now cover desktop cockpit, desktop diagnostic, desktop decision matrix, mobile cockpit, mobile decision matrix and the complete mobile experiment backlog.

### H-03: ER per audience was absent

Accepted. The aggregate payload and dashboard now include ER per visualization and ER per audience for platform and content type, with exact fixture tests and a prominent `follower_count` instability warning.

### H-04: canonical state diverged

Accepted. README, timeline and Harness Brief were reconciled to `FINAL_REVIEW_PENDING`. The previous advisory verdict remains preserved as a failed generation; a fresh immutable generation requires a new authoritative review.

## Final review generation 1

- Review: `deleg_ba01b645`
- Immutable manifest SHA-256: `94b56f8d18ebf99f21b719cd03b410352ff9b54919660d53bd9122fbb2a11301`
- Schema Gate: `FAIL`
- Semantic Score: `8.8/10`
- Decision: `BLOCK`
- Severities: `C0/H1/M0`
- Safe to freeze: `false`

All seven technical remediation checks passed except canonical status alignment.

### H-01: stale next step in the Harness Brief

Accepted. The Harness Brief correctly declared `FINAL_REVIEW_PENDING` in its frontmatter and current-state section, but its final `Next minimum step` still instructed approval of the brief followed by future implementation. The next step now requires a replacement immutable review, then a local Git checkpoint only after `C0/H0`, score `>=8` and `safe_to_freeze=true`. External publication and live experiments remain separately blocked.

Final review generation 1 remains rejected and must not be relabeled. Generation 2 requires rebuilt outputs, refreshed QA, a new immutable manifest and a new authoritative review.

## Final review generation 2

- Review: `deleg_af62736a`
- Immutable manifest SHA-256: `46d91c19590b954dacdc0f873e9250dd44e7a087f4cecbc2451d400766d444b5`
- Schema Gate: `FAIL`
- Semantic Score: `8.8/10`
- Decision: `BLOCK`
- Severities: `C0/H2/M0`
- Safe to freeze: `false`

Every technical requirement passed again. The generation was blocked only because two canonical next-step sections remained behind the actual workflow state.

### H-01: stale next step in the prototype scope

Accepted. `docs/prototype-scope.md` no longer instructs scope review followed by implementation. It now directs the immutable candidate to authoritative final review and conditions the local checkpoint on `C0/H0`, score `>=8` and `safe_to_freeze=true`.

### H-02: Harness next step described completed remediation as future work

Accepted. The Harness Brief now uses the same stable current action as the prototype scope: submit the current immutable candidate to authoritative review, then checkpoint only after approval. It no longer names correction or rebuild as future work.

Final review generation 2 remains rejected and must not be relabeled. Generation 3 requires a new build, refreshed QA, immutable manifest and authoritative review.

## V2 authoritative review — blocked generation `9181a874…`

- HTML SHA-256: `9181a8741e926ee03ef421fef924deac547d057e2e7fa25712ff8b39160ddda7`
- Schema Gate: `FAIL`
- Semantic Score: `7,4/10`
- Decision: `BLOCK`
- Severities: `C0/H4/M2/L1`
- Submission: `blocked`

This verdict remains historical and rejected. It is not relabeled after remediation.

### H-01: six strategic answers and decision coverage were incomplete

Accepted. A six-row `item → response → evidence/limitation` matrix now explicitly answers effort, posting frequency, sponsorship policy, influencer profile/threshold, what to stop and this week's quick wins. The decision map contains the four analytical decisions plus a matrix decision linked to `CLM-STRATEGY-MATRIX-001`; the HTML renders all six rows.

### H-02: hashtag significance was hardcoded

Accepted. `scripts/build_all.py` now computes, for each eligible term, present/absent publication-rate means, effect per 1,000 views, Welch standard error, two-sided normal `erfc` p-value, Holm-adjusted p-value and significance at alpha 0.05. The structured payload stores all 970 term records and the summary. The method is explicitly normal-approximate and exploratory.

### H-03: the thesis exceeded descriptive evidence

Accepted. The generation no longer claims the absence of a material, consistent and replicable association. It states only that observed descriptive differences are small and do not support operational decisions, while preserving that this does not prove absence of real, nonlinear or conditional effects.

### H-04: adjusted sponsorship language exceeded the audit

Accepted. The exact raw composite comparison remains 19.9048% sponsored versus 19.9059% organic, difference -0.0011 percentage point. Adjusted evidence is restricted to views, likes, shares and comments; neither payload nor HTML claims an adjusted composite rate.

### M-01: baseline and cuts used different estimands

Accepted. Engagement baseline and every cut now use the ratio of summed actions to summed views per 1,000. Sponsorship explicitly retains its required distinct estimand, the mean of publication-level rates, and labels it as raw.

### M-02: evidence maps were declarative rather than binding

Accepted. The builder now fails closed unless every claim's `allowed_text`, `method`, `limitations` and approved `method_id` are executed in the visible HTML; forbidden interpretations are absent; HTML and claim coverage are exact; all decision references resolve; and all six strategy rows are rendered with answer and evidence/limitation. Mutation regressions prove rejection of absent allowed text and unknown methods.

### L-01: residual English business terms in canonical docs

Accepted. README and scope now use pt-BR business language, while internal status enums and literal artifact paths remain unchanged where required for reproducibility.

## TDD evidence for the remediation generation

The focused RED run executed seven regressions before production changes and observed the expected causal failures: missing strategy matrix, missing hashtag method/results, overbroad thesis, unsupported sponsorship adjustment, missing common estimand, missing semantic validator and residual anglicisms. The concise record is `evidence/test-results-red-v2-remediation.txt`. GREEN and full-suite evidence are regenerated in `evidence/test-results.txt` before the new candidate is frozen.

## V2 authoritative review — blocked generation `c46cf0a…`

- Commit: `c46cf0a286f39c02831ca01d13ca461c032ea7b9`
- Tree: `0be79ec871bbc3192c689af7cd9259ebe1e39de0`
- Schema Gate: `FAIL`
- Semantic Score: `8,7/10`
- Decision: `BLOCK`
- Severities: `C0/H1/M0/L1`
- Safe to checkpoint: `false`

This verdict remains historical and rejected. It is not relabeled after remediation.

### H-01: frozen generation omitted the source dataset

Accepted. The next generation tracks both frozen source inputs, `data/raw/social-media-sponsorship-and-engagement-dataset.zip` and `data/extracted/social_media_dataset.csv`, and binds both hashes in the build manifest. A clean archive checkout must run the canonical 43-test suite and deterministic build without relying on files outside the generation.

### L-01: scope reported 18 states instead of 20 captures

Accepted. The scope now reports 20 authenticated captures, matching the QA contract, README, QA evidence and manifest.

## V2 authoritative review — approved checkpoint `687ca17…`

- Commit: `687ca17a82c4232b9b4dafdc906475734d068591`
- Tree: `e118fd5343010a0127cd6c7623dab4660da823b1`
- Schema Gate: `PASS`
- Semantic Score: `10,0/10` (`9,96` weighted)
- Decision: `PASS`
- Severities: `C0/H0/M0/L0`
- Safe to checkpoint: `true`

This checkpoint remains immutable. It reproduced 43 tests, two identical builds, the frozen ZIP/CSV audit, 970 hashtag analyses and 20 authenticated screenshots from a self-contained checkout. Publication and submission were not authorized.

## Human visual review — refinement generation

Thiago approved the direction of V2 and requested six presentation refinements: complete process history, separation of zero-event labels and values, spacing before the distribution and audience reading panels, sponsorship summary cards, and multiple-comparison summary cards. These requests were converted into a focused RED regression and a new generation. The replacement candidate expands QA to 26 authenticated screenshots, including dedicated desktop and mobile captures for distribution, hashtags and the full process timeline. It must receive a fresh authoritative review before replacing checkpoint `687ca17`.

## Executive refinement review — blocked generation `90c3a5b`

- Schema Gate: `PASS` (36/36)
- Semantic Score: `8,27/10`
- Decision: `BLOCK`
- Severities: `C0/H2/M3/L0`
- Safe to checkpoint: `false`

Mandatory remediation: avoid treating chance candidates as proven false positives; make standard unittest evidence set `tests.status=passed`; qualify the UTM/SESOI goal with outcome, sample, power and attribution; remove unauthenticated legacy screenshots; and authenticate the decision matrix at 125% and 150% zoom. The rejected commit remains preserved and cannot replace `687ca17`.
