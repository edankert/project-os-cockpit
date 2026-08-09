---
type: "[[feature]]"
id: FEAT-0084
aliases: ["FEAT-0084"]
title: "One view vocabulary — the view set is declared once, classified reading or actuating, and both renderers consume it"
status: planned
phase: "[[PHASE-029-One-Tool-Two-Front-Doors]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-09
source: ["[[ADR-0010-What-The-Browser-Cockpit-Is-For]]", "Session 2026-08-09: `recent` is a live button in cockpit.js and a member of RETIRED_NAV_MODES in renderer.ts, simultaneously"]
goal: "Make the view set a single source with a classification per view, so a view added to one front door cannot silently be missing from the other — the ISS-0023 fix applied to views instead of statuses."
requirements: ["[[REQ-0032-Two-Front-Doors-Agree-Or-Differ-On-The-Record]]"]
tasks:
  - "[[TASK-0364-Views-As-Declared-Data]]"
  - "[[TASK-0365-Recent-Gets-One-Verdict]]"
release: ""
related: ["[[PHASE-029-One-Tool-Two-Front-Doors]]", "[[ISS-0023-Status-Vocabulary-Drift]]", "[[ISS-0122-Active-Modes-Doing-Column-Counts-Notes-Nobody-Is-Working]]"]
tests: []
---

# One view vocabulary

## Goal

The nav vocabulary is declared twice — `NAV_MODES` in `cockpit.js` and `NAV_MODES` in `renderer.ts` — with different members, different labels for the same id (`library` is "Project" in one and "Library" in the other), and no comparison between them. It has already drifted in the way [[ISS-0023]] documented for statuses, and by the same mechanism: two hand-maintained lists and nothing that reads both.

## Scope

**In:**

- One declaration of the view set, each entry carrying its id, label, and a `reading` / `actuating` classification
- Both renderers consuming it; neither carrying its own list
- A parity test in the style of `tests/test_status_vocabulary.py`, which already parses `cockpit.js`, both stylesheets and the Electron renderer for exactly this class of drift
- `recent` resolved to one verdict, and `active` resolved alongside it or explicitly deferred to [[ISS-0122]]

**Out:**

- Changing which views exist. That is [[ADR-0010]]'s and [[FEAT-0083]]'s. This makes the set declarable; it does not decide the members.
- The label question beyond making it single-sourced. Whether `library` should read "Project" or "Library" is a naming decision for whoever picks; the point here is that it cannot be both.

## Acceptance

- [ ] The view set is declared in one place with a classification per view
- [ ] Neither renderer declares a view list of its own
- [ ] A test fails when a view exists in one renderer and is unclassified, or classified and unhandled
- [ ] One id has one label across both front doors
- [ ] `recent` is either live in both or absent from both, and the note says which and why
- [ ] The retired-mode migration path (`RETIRED_NAV_MODES` → fallback) still works, so a stored preference cannot strand a user in a view with no button

## Links

- Precedent: `src/project_os_cockpit/statuses.py` and `tests/test_status_vocabulary.py` — the same problem solved once already, for statuses
- Decision: [[ADR-0010-What-The-Browser-Cockpit-Is-For]]
- Paths: `src/project_os_cockpit/static/cockpit.js`, `desktop/src/renderer/renderer.ts`, `src/project_os_cockpit/cockpit.py` (`NAV_MODES`)
