---
type: "[[task]]"
id: TASK-0572
aliases: ["TASK-0572"]
title: "No UI string says *run* or *walk*"
status: backlog
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
source: []
parent: "[[FEAT-0140-Sections-Are-Derived-Not-Filed]]"
effort: "S"
due: ""
depends: []
blocks: []
related: []
tests: []
---

# No UI string says *run* or *walk*

## Definition of Done
- [ ] No user-visible string in either front door contains *run* or *walk*
- [ ] A test asserts it, so the words cannot drift back
- [ ] Identifiers, filenames and quotations are untouched

## Steps
- [ ] Sweep the rendered strings in `cockpit.py`, the templates and the static assets
- [ ] Use *do*, *execute*, *check*, *complete*
- [ ] Add the guard over user-visible strings only

## Notes

Edwin, 2026-08-19: *do not use run either*, and *leave run in the docs but don't use it in the UI*. So this is scoped to UI strings — the 1016 occurrences in `docs/` stay.

**The guard is the point.** *Walk* was retired once by [[DES-0012]] D5 and came back, including into two decision records written this session. A vocabulary rule with no check is a preference.
