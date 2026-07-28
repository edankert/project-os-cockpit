---
type: "[[task]]"
id: TASK-0224
aliases: ["TASK-0224"]
title: "A design mode in the strip, positioned second"
status: backlog
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["[[FEAT-0043-Design-Top-Level-Surface]]"]
parent: "[[FEAT-0043-Design-Top-Level-Surface]]"
effort: "M"
depends: ["[[TASK-0223]]"]
blocks: []
related: ["[[FEAT-0008-Cockpit-API-Hardening]]"]
tests: []
---

# Design mode in the strip

## Definition of Done

- [ ] Seven modes, with `design` **second** — after Overview, before the structure modes
- [ ] The mode is reachable by click, keyboard, and a restored preference from a previous session
- [ ] `nav?mode=design` serves from the sidecar, matching the FEAT-0008 rule that every UI mode has a server mode
- [ ] An existing stored preference (`overview`, `library`, …) still resolves — this adds a mode, removes none
- [ ] The Library's Design group and the design note banner keep working; the new mode is an additional door, not a replacement
- [ ] A test asserts the mode ORDER, not just membership — position is the decision here

## Steps

- [ ] Add to `NAV_MODES`, the strip markup, and the sidecar's mode handling
- [ ] Icon and active state
- [ ] Test order, restoration, and server-mode parity
- [ ] Rebuild the bundle and re-run the stale-build guard

## Notes

The position is the substance, so it gets its own assertion. The strip encodes kinds of thing — state · structure ×3 · queue · record — and design belongs upstream of structure: what it should be, before what is being built.

This reverses a two-day-old decision that six modes was the ceiling, taken when Active and Recent were retired to make room for Review. Reversing it deliberately is fine; drifting past it without noticing would not be, which is why it is written down here.

**Keep the other doors.** Two reachability bugs in two days came from having exactly one path to this surface. Redundant entry points are the fix, not a smell.
