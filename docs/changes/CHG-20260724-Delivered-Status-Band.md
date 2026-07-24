---
type: "[[change]]"
id: CHG-20260724-Delivered-Status-Band
title: "Seventh palette bucket — `implemented` becomes Delivered (amber, non-terminal) and one canonical vocabulary now backs all six status surfaces"
status: merged
owner: user:edwin
created: 2026-07-24
updated: 2026-07-24
source: ["downstream:your-sudoku"]
commit: ""
pr: ""
impacts: ["src/project_os_cockpit/statuses.py", "src/project_os_cockpit/cockpit.py", "src/project_os_cockpit/templates.py", "src/project_os_cockpit/static/base.css", "src/project_os_cockpit/static/cockpit.css", "src/project_os_cockpit/static/cockpit.js", "tests/test_status_vocabulary.py", "tests/test_index.py"]
issues: ["[[ISS-0023-Implemented-Status-Band-Drift]]"]
features: ["[[FEAT-0006-Cockpit-Layout]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[CHG-20260724-Implemented-Status-Rank]]", "[[REQ-0012-Visual-Style]]", "[[TST-0019-Status-Vocabulary-Parity]]"]
---

# Delivered status band

## Summary

Partially reverses [[CHG-20260724-Implemented-Status-Rank]], which put `implemented` in the done band. Reported from `../your-sudoku`: 97 of its 106 requirements sit at `implemented`, so they read as finished (green chip, done-band rank, collapsed by default) yet never cleared under **Hide completed** — the navigator stayed permanently full of work the user believed was done.

The earlier fix was half-right. `implemented` did need an explicit rank and colour, but not the done family's: project-os defines it as *built but not yet formally verified* and gates `implemented → verified` on passing test notes (`STATUSES.md`, `QUALITY.md`). Folding it into "completed" would have hidden precisely the population that still owes a verification record.

`implemented`, `staged`, and `monitoring` now form a seventh **Delivered** bucket — amber `hsl(42 46% 34%)` / `hsl(42 46% 60%)`, ranked between the backlog and done bands, expanded by default, and deliberately *excluded* from Hide-completed.

The deeper cause was that the vocabulary lived as six independent literals — two Python tables, a JS object, two CSS rule blocks, and the collapse set — which had drifted:

| Surface | Before |
|---|---|
| `base.css` chip colour | done-positive |
| `templates.py` `STATUS_RANK` | done band (62) |
| `templates.py` `COLLAPSED_BY_DEFAULT` | collapsed |
| `cockpit.js` `COMPLETED_STATUSES` | absent |
| `cockpit.py` `TASK_STATUS_ORDER` | absent |
| `cockpit.css` group-icon | absent |

`src/project_os_cockpit/statuses.py` is now the single source of membership, and [[TST-0019-Status-Vocabulary-Parity]] parses the JS and both stylesheets to hold every surface to it.

Seven statuses that appear in real corpora or the taxonomy but had no rule anywhere are now mapped: `resolved` (14 notes across the nine repos), `released` (10), `mitigating` (1), plus `staged`, `rolled-back`, `monitoring`, `deprecated`.

## Impact

- **Behaviour change:** `implemented` / `staged` / `monitoring` items remain visible when Hide-completed is on, and their index-page groups start expanded. Downstream corpora with large `implemented` populations (`your-sudoku` 97, `your-trainer` 145) will see those items stay on screen — that is the intent, not a regression.
- **Visual change:** those statuses render amber instead of teal-green. Terminal statuses are unaffected.
- Purely presentational; no API, schema, or data change.
- Ships to `project-os/tools/cockpit/` via `tools/scripts/release-to-project-os.sh`, then to the nine downstream repos by template sync.

## Documentation Coverage (All Types Considered)

- features: not-applicable (defect in shipped [[FEAT-0006-Cockpit-Layout]] surface)
- requirements: updated ([[REQ-0012-Visual-Style]] — clause 6 amended 6→7 buckets, clause 7 added, two acceptance criteria added, `## Amendments` records the argument)
- tasks: new ([[TASK-0198-Delivered-Status-Band]])
- issues: new ([[ISS-0023-Implemented-Status-Band-Drift]])
- tests: new ([[TST-0019-Status-Vocabulary-Parity]]); `tests/test_index.py` contract rewritten
- workflows: not-applicable
- decisions: not-applicable (amended REQ-0012 under its own escape clause rather than opening a new ADR; [[ADR-0003]] still holds for the palette's shape)
- risks: not-applicable
- changes: new
- snapshot: updated (counters ISS/TASK/TST, new items, focus, metrics)

## Follow-ups

- [ ] Browser visual pass on the amber hue in both themes (the one REQ-0012 clause automation cannot cover).
- [ ] Independent review — this change carries a `TST-*` and a `CHG-*` and amends a `verified` requirement, so `QUALITY.md` requires a cross-family or human pass.
