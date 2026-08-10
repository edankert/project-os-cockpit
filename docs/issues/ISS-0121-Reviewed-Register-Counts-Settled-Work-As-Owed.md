---
type: "[[issue]]"
id: ISS-0121
aliases: ["ISS-0121"]
title: "The reviewed register counts settled work as owed — all ten `Changes requested` rows are terminal"
status: fixed
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-10
source: ["Session 2026-08-09: reviewing a proposed board layout for ~review, the payload was rendered to see what a card would carry"]
severity: medium
component: "review-desk"
parent: ""
related: ["[[CHG-20260810-Reviewed-Register-Reads-The-Subject]]", "[[DES-0010-The-Desk-Shows-What-It-Owes]]", "[[FEAT-0049-Review-Desk-As-Record]]", "[[TASK-0277-Changes-Requested-Is-Not-Finished]]"]
tests: []
---

# The reviewed register counts settled work as owed

## Problem

`~review` displays **`Changes requested · 10`** at the top of its register, promoted by [[TASK-0277]] to sit with live work. Every one of those ten notes is terminal. The desk's most prominent statement about what a human owes is, today, entirely false.

`review_verdict` is a **sticky frontmatter field**. A reviewer writes `changes-requested`; the requested work is then done and the note reaches `fixed` / `done` / `merged`; nothing clears or re-stamps the verdict. So the register accumulates permanent false positives, one per review round that ever asked for a change.

TASK-0277's reasoning was right and is not in question — *"a reviewer asked for a change and nothing records it having happened"* is a real hazard, and filing those rows under "reviewed" was the same error as a terminal-looking label on open work. The defect is that the field it reads cannot distinguish "still owed" from "was owed, and was done".

## Repro

```
python3 - <<'PY'
import sys; sys.path.insert(0, "src")
from pathlib import Path
from project_os_cockpit.index import Index
from project_os_cockpit import cockpit, statuses
idx = Index.build(Path("docs"))
rows = [r for r in cockpit.review_queue_payload(idx, None)["registers"]["reviewed"]
        if (r.get("verdict") or "").lower() == "changes-requested"]
for r in rows:
    rec = idx.get(idx.by_id(r["id"]))
    print(r["id"], rec.status, statuses.is_completed(rec.status))
PY
```

## Expected

A row headed `Changes requested` names work a human still owes. When its subject reaches a terminal status after the verdict was written, it is settled and belongs in the completed band with the other verdicts.

## Actual

All ten rows are terminal, and have been since 2026-07-30 for eight of them.

| note | verdict date | status now |
|---|---|---|
| FEAT-0056 | 2026-08-02 | `done` |
| CHG-20260802-Completed-Work-Collapses | 2026-08-02 | `merged` |
| PHASE-013 | 2026-07-30 | `done` |
| PHASE-011 | 2026-07-30 | `done` |
| ISS-0069 | 2026-07-30 | `fixed` |
| ISS-0068 | 2026-07-30 | `fixed` |
| ISS-0057 | 2026-07-30 | `fixed` |
| ISS-0037 | 2026-07-30 | `fixed` |
| FEAT-0045 | 2026-07-30 | `done` |
| CHG-20260730-Two-Features-Closed | 2026-07-30 | `merged` |

**Genuinely owed: 0.** The desk's real load is 3 (the `draft` requirements REQ-0029/0030/0031), not 13.

## Evidence

- `src/project_os_cockpit/cockpit.py` — `_reviewed_register`, which reads `review_verdict` and nothing else
- `desktop/src/renderer/renderer.ts:4325` — `isOwedVerdict`, the renderer-side split that promotes these rows
- Measured 2026-08-09 against this corpus: 103 verdicts recorded, 10 headed owed, 0 actually owed

## Why it matters beyond the count

A desk that overstates what it owes by a factor of four teaches its reader to discount it. That is worse than showing nothing, and it is the failure mode the whole review-desk line of work exists to remove — the same shape as [[ISS-0068]], where a list re-stated items that already had a home, and as the Hide-completed switch that put a terminal label on open work.

It also blocks measurement: any layout change to `~review` (see [[DES-0010]]) would render these ten more prominently, not less.

## Measured 2026-08-10 — the date-based discriminator does not work

The third action below proposed distinguishing *"was owed, then done"* from *"a re-review of finished work"* by comparing the note's `updated` against its `review_date`. **Measured before implementing, and it fails.**

| | |
|---|---|
| the 10 `changes-requested` rows with `updated` **≤** `review_date` | **10 of 10** |
| all terminal notes with a verdict, same comparison | **85 of 103** |

The cause is structural: **stamping the verdict is itself the last edit.** A reviewer writes `review_verdict` and `review_date` into the note, and that write sets `updated` to the same day. So `updated` can never post-date `review_date` in the normal flow, and the comparison classifies every one of the ten as *still owed* — precisely backwards.

**So the predicate is the simple one:** a `changes-requested` verdict on a note that is **now terminal** is settled.

**And the inverse case is a recorded limitation rather than a solved problem.** A genuine re-review of already-finished work — a `merged` CHG that someone then asks changes of — will be misclassified as settled by this predicate, because the only evidence that would separate the two cases is *when the note became terminal*, and `updated` cannot supply it. That date is recoverable from git (`status_diff.py` already parses `git log -U0` for status transitions), but wiring git history into a per-request register is disproportionate to a case that has never occurred here. If it occurs, that is the fix.

## Next Actions

- [x] Filter the owed split on the subject's current status: a verdict whose note is terminal is settled, and joins the completed band under its own verdict name rather than the owed heading — evidence: the measurement above
- [x] Decide where the predicate lives — `_reviewed_register` server-side, so the renderer keeps drawing what it is sent (the [[ISS-0023]] rule)
- [~] Check the inverse case has a home — **reconciled**: undetectable from note frontmatter for the reason measured above; recorded as a limitation with its remedy named
