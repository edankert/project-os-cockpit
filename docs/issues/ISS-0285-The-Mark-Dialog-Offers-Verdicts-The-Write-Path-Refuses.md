---
type: "[[issue]]"
id: ISS-0285
aliases: ["ISS-0285"]
title: "Marking a check Fail in a repo with no ledger is refused, and the reason the person typed is lost"
status: open
phase: ""
owner: user:edwin
reported_by: user:edwin
created: 2026-09-06
updated: "2026-09-19"
source: ["Edwin, 2026-09-06, walking project-os-deck's first acceptance checks: 'I just marked TST-0008 as a fail with a lot of explanations, but you suggested that fail is not a valid state and does this mean the explanation has been removed?'"]
severity: high
component: ui
parent: ""
related: ["[[ISS-0281-A-Failing-Verdict-Is-Erased-From-The-Checks-View]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[project-os-deck#PHASE-0001]]"]
tests: []
---

# Marking a check Fail in a repo with no ledger loses the typed reason

In a repo that has no ledger and no open release with a platform, choosing Fail, Not applicable or Blocked in the mark dialog is refused, and the reason the person typed is thrown away.

## Problem

**A person walked a check, chose Fail, typed a page of reasoning, and lost all of it.** Nothing was written anywhere: not to the note, not to a ledger, not to any file in the repository.

The mark dialog offers eight verdicts, which are the ledger's vocabulary. A repository with no ledger takes the pre-ledger write path, whose vocabulary is different, and three of the eight do not exist there.

| the dialog offers | `acceptance.VERDICTS` accepts |
| --- | --- |
| `pass`, `partial`, `excused`, `question` | the same four |
| `fail` | **`failed`** |
| `na`, `blocked` | **absent** |

`VERDICTS.get("fail")` returns nothing, `mark_check` raises a `WriteError`, the server answers 400, and `walkOneCheck` shows the message in a toast. The dialog has already closed, and the reason went with it.

## Where it is

- The dialog's verdicts: `desktop/src/renderer/renderer.ts:2312-2337`, eight entries ending `needs-re-run`.
- The old vocabulary: `src/project_os_cockpit/acceptance.py:2289`, seven keys, `failed` where the dialog says `fail`.
- The branch that chooses: `src/project_os_cockpit/server.py`, `_serve_mark_check` — `if platform:` takes the ledger path, otherwise `note_writes.mark_check`.
- The toast that loses the text: `desktop/src/renderer/renderer.ts:8951`, the `catch` around `postJson`.

## Why it bites a new repository hardest

A repository with no ledger always takes the old path, and a repository created today has migrated nothing. So the newest projects are the ones on the pre-migration road, and the mismatch is the first thing they meet. Measured in `../project-os-deck` on 2026-09-06: six acceptance notes, zero ledgers, and every attempt to record a verdict refused.

## The two halves

1. **The dialog must offer only what the target path accepts.** It knows which path it will take, because it computes `verdictPlatform()` before sending.
2. **A refusal must hand the reason back.** This is the half that hurt. A person's paragraph is the expensive part of a walk, and a 400 currently destroys it. Re-open the dialog with the text still in it, or keep it until the write lands.

## What it is not

Not the same as [[ISS-0281-A-Failing-Verdict-Is-Erased-From-The-Checks-View]]. That one loses a verdict that was successfully written, on the way back to the page. This one never writes it.

## Checked against the code, 2026-09-19: still true, kept

**What a user notices:** A person walks a check, picks Fail, writes an explanation, and gets an error toast; the dialog has closed and the explanation is gone.

Evidence: The dialog still offers `fail`, `na` and `blocked` (`desktop/src/renderer/renderer.ts:2371-2396`). `acceptance.py:2387` `VERDICTS` has `failed`, not `fail`, and no `na` or `blocked`. `server.py:2625-2627`: with no platform from the request, an open release or a single ledger, the write goes to `note_writes.mark_check`, which raises a 400 for an unknown verdict (`note_writes.py`, `acceptance.VERDICTS.get(verdict)` then `raise WriteError`). `postCheckVerdict` in `renderer.ts` catches the refusal, shows a status toast and returns false; `walkOneCheck` then returns without reopening the dialog, so `chosen.reason` is dropped.

**Belongs to:** no feature (ADR-0037 ledger work). **Next:** Bigger (two places): offer only the verdicts the target path accepts, and reopen the dialog with the reason still filled in when the write is refused.

Checked as part of project-os-dev FEAT-0036 (TASK-0141).
