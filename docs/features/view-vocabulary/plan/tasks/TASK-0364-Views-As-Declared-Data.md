---
type: "[[task]]"
id: TASK-0364
aliases: ["TASK-0364"]
title: "The view set is declared once with a reading/actuating classification, and both renderers consume it"
status: backlog
phase: "[[PHASE-029-One-Tool-Two-Front-Doors]]"
owner: user:edwin
created: 2026-08-09
updated: "2026-08-20"
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

## Which stage this waits on ([[ISS-0246]], 2026-08-20)

[[ADR-0010]] is `accepted` on **option 4 — parity gated on an authenticated write path**. So a *both front doors* obligation is never simply owed; it waits on one of three stages, and saying which is the difference between a plan and a nag:

1. **The eleven reading views** — owed now, nothing gates them ([[FEAT-0083]]).
2. **An authenticated write path** — the gate. There is no authentication in this tool, and `REL-0001`'s acceptance pass measured **ten of ten** mutation endpoints returning 403 over the LAN while reads returned 200 ([[REQ-0027]], [[RISK-0005]]).
3. **The writing surfaces** — after (2).

**This note waits on stage 1.**
