---
type: "[[task]]"
id: TASK-0364
aliases: ["TASK-0364"]
title: "The view set is declared once with a reading/actuating classification, and both renderers consume it"
status: backlog
phase: "[[PHASE-029-One-Tool-Two-Front-Doors]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-09
source: ["[[REQ-0032-Two-Front-Doors-Agree-Or-Differ-On-The-Record]]"]
parent: "[[FEAT-0084-One-View-Vocabulary]]"
effort: M
due: ""
depends: ["[[ADR-0010-What-The-Browser-Cockpit-Is-For]]"]
blocks: ["[[TASK-0365-Recent-Gets-One-Verdict]]"]
related: []
tests: []
---

# Views as declared data

## Definition of Done
- [ ] One declaration: id, label, classification (`reading` / `actuating`), and whether it has a virtual landing
- [ ] Neither `cockpit.js` nor `renderer.ts` declares its own view list
- [ ] One id has one label across both front doors
- [ ] A parity test fails on a view that is unclassified, or classified and unhandled by a renderer that should have it

## Steps
- [ ] Put the declaration beside `NAV_MODES` in `cockpit.py`, which already owns the server's idea of the set, and serve it
- [ ] Extend `tests/test_status_vocabulary.py`'s technique — it already parses `cockpit.js`, both stylesheets and `renderer.ts` — or add a sibling suite in the same style
- [ ] Preserve `RETIRED_NAV_MODES` and its fallback map: a stored preference pointing at a retired view must still migrate, or a user lands in a view with no button and no way out

## Notes
This is [[ISS-0023]] one level up. There, a status vocabulary lived in eight places and drifted until the corpus rendered a wrong colour for weeks. The view set lives in two places and has already drifted — `recent` is live in one and retired in the other, and `library` is labelled "Project" in one and "Library" in the other.

The classification is what makes the declaration worth having rather than merely tidy: it is what lets a reader see *why* a view is missing from a front door, and what [[REQ-0032]]'s guard tests against.
