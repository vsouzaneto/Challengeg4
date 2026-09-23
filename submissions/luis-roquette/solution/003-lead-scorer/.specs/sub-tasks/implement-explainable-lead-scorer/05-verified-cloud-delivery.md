# Step 05: Same-revision Cloud publication and rendered live proof

**Task File:** `.specs/tasks/todo/implement-explainable-lead-scorer.feature.md`

> The task file moves between `.specs/tasks/{draft,todo,in-progress,done}/` as work progresses; if it is not at this path, resolve it by its filename under `.specs/tasks/`.

**Phase:** Phase 3
**Model:** sonnet
**Agent:** general sonnet
**Depends on:** `04-canonical-verification`
**Parallel with:** None
**Note:** Uses existing verified code and live verifier; no new runtime policy or dependency. Coordinate Git/Cloud writes with the implementation orchestrator under the user's authorization and shared submission ownership. Do not auto-delete any Codespace.

**Goal:** Publish only the verified source revision and prove the live app renders the same data/config/source identity and core journeys.

Use the complete green evidence from 04-canonical-verification, exact source/diff and the tests/test_app.py live verifier already written there. Before any push/deploy, inspect actual workflows/provider configuration and required checks; follow branch+PR policy and the single shared submission PR. Existing authorized publication does not permit paid AI APIs or provider/model changes. Configure the approved Streamlit Community Cloud Python 3.11 entrypoint and locked dependencies. Keep docs/evaluation.md as the evidence ledger, and capture actual seller/manager screenshots under ../../process-log/screenshots/. This step is release/tooling work with settled behavior, not auth/payments implementation.

All paths are relative to `submissions/luis-roquette/solution/003-lead-scorer/` unless explicitly identified as repository paths. Read `.claude/skills/explainable-crm-prioritization/SKILL.md` and task contracts before edits. Keep writes within the participant submission, preserve unrelated work, and make no paid AI API calls.

#### Expected Output

- Streamlit Community Cloud deployment of the validated source identity with rendered public URL proof
- docs/evaluation.md local/managed/live gate identity, URL/revision/source digest/fingerprint and TC-47 result
- ../../process-log/screenshots/003-lead-scorer-seller.png and ../../process-log/screenshots/003-lead-scorer-manager.png captured from actual browser journeys

#### Success Criteria

- [ ] No push/deploy occurs with known deterministic gate failure; all applicable actual CI/provider checks reach terminal green at the latest delivery SHA.
- [ ] The single submission PR targets upstream `main` and uses the exact required title `[Submission] Luis Roquette — Challenge 003`; subsequent changes update that same PR.
- [ ] Run .venv/bin/python tests/test_app.py live --url <actual-url> --expected-revision <verified-sha> --expected-source-digest <verified-digest> --expected-fingerprint <verified-fingerprint>; TC-47 succeeds against rendered active-stage UI.
- [ ] The Cloud source digest is linked to the exact reviewed revision even when runtime Git HEAD is unavailable; no guessed revision or HTTP-only success is accepted.
- [ ] Seller and manager browser journeys at the published URL, identity evidence and actual screenshots are recorded; lack of access or final provider proof remains a concrete delivery blocker.

#### Subtasks

- [x] Revalidate intended diff/revision, source and data/config fingerprints plus actual workflow/branch-check/provider requirements, then coordinate scoped Git inclusion and the single `[Submission] Luis Roquette — Challenge 003` PR targeting upstream `main` with the orchestrator.
- [ ] Publish the gated source to Streamlit Community Cloud with Python 3.11, repository root as working directory, the actual nested solution `app.py` entrypoint and requirements.txt containing `protobuf<6`; follow provider runs to terminal result without bypassing checks.
- [ ] Write the concrete live browser verification cases/results in docs/evaluation.md, execute TC-47 and seller/manager journeys, include wrong-identity rejection evidence from the existing verifier tests, and capture the two required screenshots.
- [ ] Record actual URL, revision/digest/fingerprint, commands/status and deployment identity in docs/evaluation.md; if runtime source changes, return to canonical verification and repeat live proof before delivery.

#### Implementation evidence — 2026-09-22

- Git: branch `submission/luis-roquette-003-lead-scorer` publicada no fork na revisão `aa70dc6435e9df85c512007e3d1c008e4cf78876`; PR upstream [#140](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/pull/140), base `main`, título exato e estado inicial mergeable.
- Checks: não há workflow versionado, ruleset ou check pendente; a exceção explícita do owner ao preflight integral repetido está registrada no corpo do PR e em `docs/evaluation.md`.
- Provider: tentativa no Streamlit Community Cloud chegou ao consentimento OAuth do GitHub. Nenhum deploy foi submetido porque essa autorização interativa exige confirmação do owner no momento do clique.
- Correção pré-deploy: `14d0296` corrige `source_identity(ROOT)`, que resolvia o diretório pai e produzia digest de arquivos ausentes. A regressão TC-40 reconstrói o digest real. A asserção focal direta passou com fonte `7e25ba0ecbda9e3e06e89141182dc538e8407af543adca676ad23632f345d311`; `py_compile`, `bash -n` e `git diff --check` também passaram. O `unittest` focal versionado não iniciou no Mac por ausência de `streamlit`; não se reivindica teste executado nem preflight pós-correção.
- Pendente sem falsa reivindicação: URL, estado terminal do deploy, TC-47, jornadas seller/manager e duas capturas reais.

#### Blockers & Risks

| Type | Item | Impact | Likelihood | Mitigation / Resolution |
|------|------|--------|------------|-------------------------|
| Blocker | Cloud/GitHub access or provider completion is unavailable | High | Medium | Finish independent local evidence; report only the indispensable access/provider blocker without inventing a URL or claiming delivery. |
| Risk | Ignored submission files or another challenge's edits contaminate delivered revision | High | Medium | Inspect exact scoped diff and root ignore behavior, explicitly include only owned deliverables via orchestrator, and compare deployed source digest. |
| Risk | HTTP readiness is mistaken for same-revision user-journey proof | High | Medium | Require TC-47 rendered identity plus actual seller/manager interactions and screenshots. |
