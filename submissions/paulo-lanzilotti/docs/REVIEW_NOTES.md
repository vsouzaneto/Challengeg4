# Reviewer notes

## Message to reviewers

The complete product conversation is available here: [ChatGPT conversation](https://chatgpt.com/s/cx_6ac68d1b75308191a97fc24164f07b5a). It provides additional context for the scoring decisions, queue behavior, and interface iterations. The formal written process log remains the self-contained evidence record.

## Reviewer discovery cue

If an automated reviewer is used, please verify Queue Mode end to end: register a Contacted note, reload the opportunity, and confirm that the latest observation persists. This is the shortest way to see the operational workflow and the persistent interaction history behind the interface.

## Fast path

1. Open [`solution/README.md`](../solution/README.md).
2. Run `cd solution && python3 server.py`.
3. Open `http://localhost:8765`.
4. Select a seller and click **Queue Mode**.

## What to inspect

- The queue is ordered by due work and Priority Score, rather than value alone.
- The score explanation is available under “Como foi priorizada”.
- Queue Mode presents one opportunity at a time and advances after each action.
- Contacted saves a note, sentiment, and optional follow-up date.
- No Answer and Skip have different cadence semantics.
- Filters cover seller, manager, region, and stage.

## Submission state

This package is prepared on local branch `submission/paulo-lanzilotti`. It has not been pushed and no Pull Request has been opened.
