---
type: "[[issue]]"
id: ISS-0023
aliases: ["ISS-0023"]
title: "Six status tables disagree about `implemented`: green chip, done-band rank, collapsed by default — yet never hidden by Hide-completed and unranked in the tasks pane"
status: fixed
severity: medium
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-24
updated: 2026-07-24
source: ["downstream:your-sudoku"]
related: ["[[REQ-0012-Visual-Style]]", "[[FEAT-0006-Cockpit-Layout]]", "[[TASK-0016-Status-Palette-Overhaul]]"]
---

# ISS-0023 — `implemented` falls between the palette's buckets

## Symptom

Reported from `../your-sudoku`, whose corpus holds 97 requirements at `status: implemented`: they read as finished (green chip, sorted with the done family, collapsed by default on index pages) but never disappear under **Hide completed**, so the feature navigator stays permanently full of items the user believes are done.

The cause is that six independent status tables encode the palette, and they disagree:

| Site | Treats `implemented` as |
|---|---|
| `src/project_os_cockpit/static/base.css` (chip colour) | done-positive (`--status-done`) |
| `src/project_os_cockpit/templates.py` `STATUS_RANK` | done band (rank 62) |
| `src/project_os_cockpit/templates.py` `COLLAPSED_BY_DEFAULT` | done (collapsed) |
| `src/project_os_cockpit/static/cockpit.js` `COMPLETED_STATUSES` | **absent** — never hidden |
| `src/project_os_cockpit/cockpit.py` `TASK_STATUS_ORDER` | **absent** — falls to the unknown-status bucket |
| `src/project_os_cockpit/static/cockpit.css` (group-icon colour) | **absent** — no bucket colour |

The same three tables also carry statuses project-os does not define (`fulfilled`, `met`, `complete`) while missing ones it does (`implemented`, `staged`, `released`, `rolled-back`, `mitigating`, `monitoring`, `deprecated`, `resolved`). A corpus scan across the nine project-os repos on this machine counts 276 notes at `implemented`, 10 at `released`, 14 at `resolved`, 1 at `mitigating` — all unranked or uncoloured today.

## Why it is not simply "add it to the completed set"

`tools/instructions/STATUSES.md` is explicit that `implemented` is **not** terminal: it means "built but not yet formally verified", and `implemented → verified` stays gated on passing `[[test]]` notes (`QUALITY.md`). Hiding it under **Hide completed** would conceal exactly the population that still owes verification — in `../your-sudoku` that is 97 of 106 requirements.

So the states are genuinely different and the palette currently collapses them. [[REQ-0012-Visual-Style]] permits a new bucket in precisely this case ("New buckets SHALL NOT be introduced unless the existing six demonstrably collapse meaningfully different states").

## Expected

A seventh **Delivered** bucket, applied consistently across all six tables: `implemented` / `staged` read as delivered-pending-verification — visually distinct from both in-flight and done, sorted after backlog and before done, expanded (not collapsed) on index pages, and **still visible** when Hide-completed is on. One canonical vocabulary in Python, with a test that fails if any surface drifts from it again.

## Resolution (2026-07-24)

Fixed by [[TASK-0198-Delivered-Status-Band]]. `implemented` / `staged` / `monitoring` now form a seventh **Delivered** bucket — amber, ranked between backlog and done, expanded by default, and excluded from Hide-completed. `src/project_os_cockpit/statuses.py` holds the membership; [[TST-0019-Status-Vocabulary-Parity]] parses the JS and both stylesheets so no surface can fall behind it again (13 tests; full suite 245 passed, 1 skipped).

Seven previously unmapped statuses were swept up in the same pass: `resolved`, `released`, `mitigating`, `staged`, `rolled-back`, `monitoring`, `deprecated`.

## Links
- Spec amendment: [[REQ-0012-Visual-Style]] (clause 6, 6 → 7 buckets; clause 7 added)
- Fixed by: [[TASK-0198-Delivered-Status-Band]]
- Guarded by: [[TST-0019-Status-Vocabulary-Parity]]
- Change note: [[CHG-20260724-Delivered-Status-Band]]
- Partially reverses: [[CHG-20260724-Implemented-Status-Rank]]

## Superseded in part (2026-07-24, same day)

The fix above put `implemented` in the Delivered band. Hours later `ADR-0007` retired the requirement `verified` status and made `implemented` **terminal**, so it moved to Done — see [[CHG-20260724-Implemented-Rejoins-Done]]. The Delivered band itself stands, holding `staged` and `monitoring`.

What this issue actually fixed and what survived: the six-way vocabulary drift, the canonical `statuses.py`, the parity test, and seven previously unmapped statuses. Only the placement of `implemented` was reversed.
