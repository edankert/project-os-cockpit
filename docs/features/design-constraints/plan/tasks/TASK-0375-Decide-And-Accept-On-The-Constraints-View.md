---
type: "[[task]]"
id: TASK-0375
aliases: ["TASK-0375"]
title: "A proposed ADR and a proposed design surface as this view's obligations"
status: backlog
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]"]
parent: "[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]"
effort: S
due: ""
depends: ["[[TASK-0374-Constraints-Membership]]", "[[TASK-0369-The-Obligation-Registry]]"]
blocks: []
related: ["[[FEAT-0042-Design-Bench]]"]
tests: []
---

# Decide and accept on the constraints view

## Definition of Done
- [ ] `adr @ proposed` → **decide** and `design @ proposed`/offered → **accept** appear as this view's obligations, from the registry
- [ ] Both counted in the view's badge
- [ ] Accepting a design still stamps `design_revision` through `/api/design/verdict` — never through the generic proposal path
- [ ] Rejecting still writes the design's own guarded transition
- [ ] The actuators are on the note, not in the panes

## Steps
- [ ] Mark obligated rows in the view; group them if the count warrants, without creating a second list
- [ ] Route to the existing design-verdict machinery ([[FEAT-0042]]), which is not rebuilt
- [ ] Assert the design path is used for designs — a design going through the proposal path is [[ISS-0056]]

## Notes
[[ISS-0056]] is the specific hazard: a design sent through the generic proposal path stamps `plan-accepted` with no revision, and rejection writes `cancelled` onto a design that may be `implemented`. An approval given to revision 3 must never launder revision 6, and the only thing preventing that is using the right endpoint.
