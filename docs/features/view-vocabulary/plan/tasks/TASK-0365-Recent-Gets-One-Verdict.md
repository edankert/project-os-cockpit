---
type: "[[task]]"
id: TASK-0365
aliases: ["TASK-0365"]
title: "`recent` is live in both front doors or absent from both, and the note says which and why"
status: backlog
phase: "[[PHASE-029-One-Tool-Two-Front-Doors]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-09
source: ["Session 2026-08-09: `recent` is a live button in cockpit.js and a member of RETIRED_NAV_MODES in renderer.ts"]
parent: "[[FEAT-0084-One-View-Vocabulary]]"
effort: S
due: ""
depends: ["[[TASK-0364-Views-As-Declared-Data]]"]
blocks: []
related: ["[[ISS-0122-Active-Modes-Doing-Column-Counts-Notes-Nobody-Is-Working]]"]
tests: []
---

# Recent gets one verdict

## Definition of Done
- [ ] `recent` has one classification, honoured by both renderers
- [ ] If retired: `_recent_groups` and its icons go with it, or the note records why they stay
- [ ] If kept: it appears in both front doors with one label
- [ ] [[ISS-0122]]'s `active` question is resolved in the same pass or explicitly left open with a reason

## Steps
- [ ] Take the decision against [[ADR-0010]]'s rule — `recent` is a reading view, so it belongs in both or neither
- [ ] Apply, and delete the dead path rather than leaving it served
- [ ] Record the reason in [[FEAT-0084]]

## Notes
The evidence for retiring: mode 3 retired it in TASK-0204 on the argument that "what changed" is the overview's history band, and nothing has asked for it back. The evidence for keeping: mode 1 has no overview, so the argument that replaced it does not yet apply there — which is precisely what [[FEAT-0083]] changes. **So this task should run after [[TASK-0361]], not before**: the honest test of whether `recent` earns a place is whether anyone misses it once the reading surface has the history band.

`active` is the same shape and is filed separately as [[ISS-0122]] because it has a live consumer (`buildNowBoard`) and a measured defect, which `recent` does not.
