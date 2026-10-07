# Submission — Paulo Lanzilotti — Challenge 003

## About me

- **Name:** Paulo Lanzilotti
- **LinkedIn:** https://linkedin.com/in/paulo-guilherme-lanzilotti-a42373a9
- **Challenge chosen:** Challenge 003 — Lead Scorer

> **Full conversation walkthrough:** [ChatGPT conversation](https://chatgpt.com/s/cx_6ac68d1b75308191a97fc24164f07b5a)

---

## Executive Summary

I built Foco, a seller-facing priority queue for the open pipeline in the supplied CRM dataset. It calculates a Priority Score from pipeline momentum, commercial value, sector × product fit, and account history, then turns that score into a working queue with seller actions. Queue Mode gives one seller one opportunity at a time and records No Answer, Skip, Contacted, notes, sentiment, and follow-up dates. The solution is intentionally framed as sales prioritization rather than purchase probability because the dataset does not contain current interaction or intent signals.

---

## Solution

The runnable solution is in [`solution/`](./solution/). It is a dependency-free local web app using the real challenge data.

### Setup

```bash
cd solution
python3 server.py
```

Open `http://localhost:8765`.

The first run creates `solution/runtime/workflow.sqlite3` for local interaction history. No external CRM or API key is required.

### Approach

The data was inspected before choosing the scoring rules. The open pipeline has 2,089 opportunities, but only 664 have a linked account. Historical closed deals have a median cycle of 45 days, 90% close within 104 days, and none close after 138 days. Current `Engaging` deals have a median of 165 days in stage, so treating every `Engaging` deal as hot would produce a stale queue.

The score is deliberately split into explainable components:

| Component | Weight | Signal |
|---|---:|---|
| Momentum | 0–60 | Stage and time in `Engaging` against historical cycle limits |
| Value | 0–25 | Log-normalized product list price |
| Fit | 0–10 | Smoothed sector × product win-rate lift plus company size |
| Account history | 0–5 | Smoothed historical win rate for the linked account |

`Priority Score = round(momentum + value + fit + account history)`.

The interface exposes the score explanation only when requested, using seller language rather than raw model terminology. Missing account links receive neutral fit/history values and lower data confidence.

### Results / Findings

- The seller can browse the full queue, search by company/product/ID, and filter by seller, manager, region, and pipeline stage.
- The queue orders actionable work by due date first and Priority Score as the tie-breaker, so stale and due work is not hidden behind a static ranking.
- Queue Mode focuses on one opportunity at a time. It keeps the seller assignment, asks for the seller when no owner is selected, and advances to the next eligible opportunity after each action.
- After the fifth primary action in a Queue Mode session, a clearly separated Builder Card introduces the author using the portfolio's visual language. It is not an opportunity and does not affect score, queue state, or commercial metrics.
- `No Answer` records a real attempt and schedules a retry. `Skip` postpones without counting a call. `Contacted` requires a note and outcome, with optional follow-up date.
- Positive, neutral, and negative outcomes are recorded in the event history. Negative outcomes enter review instead of being automatically called again.
- The last observation is visible the next time the opportunity appears.

### Recommendations

1. Use Foco as a seller prioritization layer while keeping the CRM as the source of record.
2. Recalculate the score daily in a production integration and add live intent signals such as last contact, response, meeting, decision-maker, and buying timeline.
3. Add authenticated user identity and a transactional assignment/reservation step before enabling concurrent production use.
4. Review the scoring weights after collecting a few weeks of interaction and outcome data.

### Limitations

- The supplied data is a historical 2017 snapshot; the score is not a probability of closing.
- Open opportunities do not include negotiated value, contact details, activities, responses, or meeting history.
- This submission uses local SQLite storage and a simulated seller selector. It does not authenticate users, ingest new leads, or connect to a live CRM.
- The dataset contains 27 sellers with open opportunities in this snapshot, while the challenge context describes a larger live operation.

### Validation

The app was walked through in a browser against an isolated SQLite database. The three Queue Mode actions were checked, notes were persisted across reload, negative outcomes entered review, and the PDF/font assets returned successfully from the local server. `node --check app.js` completed successfully.

---

## Process Log — How I used AI

> **This section is mandatory.** A fuller narrative is available in [`process-log/AI_PROCESS_LOG.md`](./process-log/AI_PROCESS_LOG.md).

### Tools used

| Tool | How it was used |
|---|---|
| Codex | Repository and dataset inspection, exploratory analysis, scoring design, implementation, UI iteration, and validation |
| Impeccable | Design-system context, operate-mode guidance, and mechanical UI review |
| Design Taste | Initial design read and anti-slop review for the seller-facing interface |
| Image generation | Queue Mode mockup used to align the modal and action-button design |

### Workflow

1. Read the challenge README and submission guide, then mapped the dataset and the available account, product, seller, stage, and date fields.
2. Tested the initial hypothesis that `Engaging` meant hot. The historical timing showed that most current `Engaging` deals were stale, so recency became the dominant intent signal.
3. Built the score and explainability layer, then changed the interface from a static list into an operational queue with owner-aware actions.
4. Added persistent interaction events, follow-up cadence, review states, and account activity warnings.
5. Designed and implemented Queue Mode as a one-opportunity-at-a-time modal, then validated it against an isolated database.

### Where AI was wrong and how I corrected it

The first scoring direction would have treated `Engaging` as a hot lead and the first queue direction would have sorted everything directly by score. I corrected both after inspecting stage duration and thinking through a seller's daily workflow. The queue now respects due dates, protects high-priority opportunities from disappearing, counts real attempts separately from skips, and keeps the assigned seller responsible.

### What I added through human judgment

I defined the product framing as sales prioritization, chose the score weights, challenged the stage interpretation, specified the Queue Mode flow and action semantics, required sticky ownership for Round Robin, and kept the explanation compact so sellers can act without decoding a technical model.

---

## Evidence

- [x] Narrative process log: [`process-log/AI_PROCESS_LOG.md`](./process-log/AI_PROCESS_LOG.md)
- [x] Queue Mode concept image: [`process-log/screenshots/queue-mode-concept.png`](./process-log/screenshots/queue-mode-concept.png)
- [x] Local git branch and submission history
- [x] Browser validation described above
- [ ] Chat export or screenshots — optional supplement; the narrative process log is the primary evidence format used here

## Note to reviewers

The linked conversation contains the product reasoning behind the score, queue rules, seller workflow, and interface decisions. The written process log below is the self-contained submission record; the conversation is provided as additional context.

For the fastest product check, open Queue Mode, register a Contacted note, reload the opportunity, and confirm that the latest observation persists.

---

_Submission prepared on: 2026-10-07_
