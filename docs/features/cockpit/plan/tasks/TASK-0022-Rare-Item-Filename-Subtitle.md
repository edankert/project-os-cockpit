---
type: "[[task]]"
id: TASK-0022
aliases: ["TASK-0022"]
title: "Cockpit: rare/pinned items show filename + parent dir"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-09
updated: 2026-05-23
source: []
implements: ["[[FEAT-0006]]", "[[REQ-0016]]"]
fixes: []
effort: S
due: ""
depends: []
blocks: ["[[TASK-0025]]"]
related: ["[[TASK-0019]]"]
tests: ["[[TST-0002]]"]
---

# TASK-0022 — Rare/Pinned items show filename + parent dir

## Definition of Done
- [x] `_rare_item` returns `title = record.path.name` (filename) and `subtitle = parent_dir + "/"` for files in subdirs (or `""` for docs-root notes).
- [x] Both Pinned and rare-types groups (Decisions / Releases / Risks / Tests / Workflows / Plans / References) use the new shape.
- [x] The stacked layout in JS renders the subtitle line under the title.
- [x] Tests pass; the legacy "drop subtitle" assertion is replaced by one that checks filename + path subtitle.

## Steps
- [x] Updated `_rare_item` in `cockpit.py`.
- [x] Extended `navItemStacked` in `cockpit.js` to render `item.subtitle` (mono `.nav-subtitle-stacked`) below the title.
- [x] Added `.nav-subtitle-stacked` CSS — mono, 11px, faint colour, ellipsised.
- [x] Updated `tests/test_cockpit.py` assertions for stacked items.

## Notes
The point of this change is recognisability — humans search by filename in tree views; titles are too generic for ADR/REQ corpora.
