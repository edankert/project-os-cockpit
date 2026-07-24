---
type: "[[change]]"
id: CHG-20260724-Implemented-Rejoins-Done
title: "`implemented` rejoins the Done band — ADR-0007 made it the terminal requirement status; Delivered keeps `staged` and `monitoring`"
status: merged
owner: user:edwin
created: 2026-07-24
updated: 2026-07-24
source: ["upstream:project-os-dev ADR-0007"]
commit: ""
pr: ""
impacts: ["src/project_os_cockpit/statuses.py", "src/project_os_cockpit/cockpit.py", "src/project_os_cockpit/templates.py", "src/project_os_cockpit/static/base.css", "src/project_os_cockpit/static/cockpit.css", "src/project_os_cockpit/static/cockpit.js", "tests/test_status_vocabulary.py", "tests/test_index.py"]
issues: []
features: ["[[FEAT-0006-Cockpit-Layout]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[CHG-20260724-Delivered-Status-Band]]", "[[REQ-0012-Visual-Style]]", "[[TST-0019-Status-Vocabulary-Parity]]"]
---

# `implemented` rejoins Done

## Summary

Partly reverses [[CHG-20260724-Delivered-Status-Band]], which landed earlier the same day. That change gave `implemented` its own non-terminal **Delivered** band, on the grounds that project-os gated `implemented → verified` on passing test notes — so `implemented` meant "built, not yet proven" and had to stay visible under Hide-completed.

`ADR-0007` (in `../project-os-dev`) then removed that gate: the requirement `verified` status is retired and **`implemented` is terminal**. The premise for holding it out of Done no longer exists, so it moves back: teal chip, done-band rank (62), collapsed by default on index pages, and hidden by Hide-completed.

The Delivered band **stays**, with two members instead of three — `staged` (release verified and ready, not yet live) and `monitoring` (risk mitigated, still under watch). Both are genuinely non-terminal, so the seven-bucket palette and its exclusion from Hide-completed are still correct.

## Why the churn was worth it

The original complaint that produced [[ISS-0023-Implemented-Status-Band-Drift]] was "requirements at `implemented` never show as completed". The first fix said: *they aren't completed — the palette was lying by colouring them done.* Upstream then concluded the opposite is truer: *they are completed — the taxonomy was lying by demanding a second verification step nobody performed* (across 7 repos, 71% of `verified` requirements referenced no test and not one carried a waiver).

Both fixes were right about the same underlying fault: `implemented` was rendered as done while being defined as not-done. One repaired the rendering, the other repaired the definition. The definition winning is the better outcome, and the palette work is what made the inconsistency legible enough to decide.

## What caught the drift

[[TST-0019-Status-Vocabulary-Parity]] — authored with the Delivered band — failed on **7 of 13** cases the moment `statuses.py` changed, naming every surface still treating `implemented` as delivered: the JS Hide-completed set, both stylesheets' rules, the two ordering tables, and the collapse set. That is exactly the job it was written for; without it this change would have re-created the six-way drift the band was introduced to fix.

## Impact

- `implemented` items are now hidden by **Hide completed** and their index groups collapse by default. Downstream repos with large `implemented` populations (your-sudoku 95, your-trainer 145) will see them drop out of the default view — that is the intent.
- Visual: teal-green instead of amber. `staged` / `monitoring` keep amber.
- Purely presentational; no API, schema, or data change.

## Documentation Coverage (All Types Considered)

- features: not-applicable (adjustment within shipped [[FEAT-0006-Cockpit-Layout]])
- requirements: updated ([[REQ-0012-Visual-Style]] — bucket table corrected, acceptance example re-pointed to `staged`, `## Amendments` records the reversal)
- tasks: not-applicable (small taxonomy realignment; documented via this change note per LIFECYCLE "Mandatory Automated Documentation")
- issues: not-applicable
- tests: updated ([[TST-0019-Status-Vocabulary-Parity]] contract flipped; `tests/test_index.py` contract flipped back to the done-band assertion)
- workflows / decisions / risks: not-applicable (the decision is upstream ADR-0007)
- changes: new
- snapshot: updated

## Verification

`.venv/bin/pytest -q` → **245 passed, 1 skipped**. `ruff check src/ tests/` → 15 errors, unchanged from the pre-change baseline. `validate-docs.sh` → OK.

## Follow-ups

- [ ] Independent review is owed per `QUALITY.md` (this change updates a `TST-*` and carries a `CHG-*`).
- [ ] Browser visual pass: `implemented` teal and `staged` amber, both themes.
