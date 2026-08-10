---
type: "[[change]]"
id: CHG-20260810-Reviewed-Register-Reads-The-Subject
title: "The reviewed register asks whether the subject is still open, not only what the verdict said — ten false obligations become zero"
status: merged
reviewed_by: ""
review_date: ""
review_verdict: ""
date: 2026-08-10
owner: user:edwin
component: [cockpit-payload, desktop-renderer]
related: ["[[ISS-0121-Reviewed-Register-Counts-Settled-Work-As-Owed]]", "[[TASK-0277-Changes-Requested-Is-Not-Finished]]", "[[PHASE-030-Obligations-Go-Home]]", "[[REL-0001-The-Human-Has-Levers]]"]
---

# The reviewed register reads the subject

## What changed

`~review`'s register headed **`Changes requested · 10`**. All ten subjects were terminal — `fixed`, `done` or `merged`. The desk's most prominent statement about what a human owed was entirely false, and had been since 2026-07-30 for eight of them.

`review_verdict` is a **sticky** frontmatter field: a reviewer writes `changes-requested`, the work is done, the note reaches a terminal status, and nothing clears the stamp. [[TASK-0277]] promoted those rows to sit with live work — right about the hazard, wrong about the evidence, because it read the verdict alone.

The register now asks a second question: **is the subject still open?**

```
Changes requested · 10   →   Changes requested · 0
Reviewed · 103           →   Completed · 104 rows, correctly banded
```

## Where the predicate lives

`cockpit.py`, in `_verdict_is_owed`, beside the status vocabulary it reads. The payload gains an `owed` flag per row and the renderer draws what it is sent — `isOwedVerdict` now takes the item and returns `item.owed`, restating nothing. That is the [[ISS-0023]] rule applied to a second vocabulary.

The renderer falls back to `false` when the flag is absent, so an older sidecar under-reports rather than resurrecting ten false obligations.

## Measured first, and the obvious approach was wrong

The intended discriminator was to compare a note's `updated` against its `review_date` — work landing after a verdict settles it. **Measured before implementing, and it fails**: 10 of the 10 rows, and 85 of the 103 verdicts in the corpus, have `updated <= review_date`, because *stamping the verdict is itself an edit* and sets `updated` to the review's own day. That comparison would have called every one of them still-owed — backwards. The measurement is recorded on [[ISS-0121]].

## Known limitation

A genuine re-review of already-finished work — a `merged` change someone then asks changes of — now reads as settled. Separating it needs the date the note *became* terminal, which frontmatter does not carry. `status_diff` recovers that from `git log`, and wiring git history into a per-request register is disproportionate to a case this corpus has never produced. Recorded on [[ISS-0121]] with its remedy named.

## Paths

- `src/project_os_cockpit/cockpit.py` — `OWED_VERDICTS`, `_verdict_is_owed`, the `owed` flag in `_reviewed_register`
- `desktop/src/renderer/renderer.ts` — `ReviewRegisterReviewed.owed`, `isOwedVerdict`
- `tests/test_completed_work_ordering.py` — the TASK-0277 guard, amended rather than relaxed: it now asserts the vocabulary in `cockpit.py`, the sticky-field behaviour, **and** that the renderer does not restate either

## Restart required

Mode 3 is a built bundle; `desktop/dist/` was rebuilt. The change is live after the desktop app restarts.
