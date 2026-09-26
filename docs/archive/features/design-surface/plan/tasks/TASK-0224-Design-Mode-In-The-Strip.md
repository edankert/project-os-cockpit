---
type: "[[task]]"
id: TASK-0224
aliases: ["TASK-0224"]
title: "A design mode in the strip, positioned second"
status: done
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

- [x] Seven modes, with `design` **second** — after Overview, before the structure modes — evidence: `test_design_sits_second_before_the_structure_modes` checks BOTH the TS constant and the button markup, since either alone can drift
- [x] The mode is reachable by click, keyboard, and a restored preference from a previous session — evidence: `test_the_button_is_keyboard_reachable_like_the_others`; a real `<button role="tab">`, so focus and Enter/Space already work with no extra machinery
- [x] `nav?mode=design` serves from the sidecar, matching the FEAT-0008 rule that every UI mode has a server mode — evidence: `_design_groups()`; `test_the_mode_has_a_button_an_icon_and_a_server_that_serves_it` asserts button + icon + server mode together
- [x] An existing stored preference (`overview`, `library`, …) still resolves — this adds a mode, removes none — evidence: `test_the_mode_adds_and_removes_nothing`
- [x] The Library's Design group and the design note banner keep working; the new mode is an additional door, not a replacement — evidence: untouched; the Library grouping and `buildDesignNoteBanner` were not modified, and their tests still pass
- [x] A test asserts the mode ORDER, not just membership — position is the decision here — evidence: order asserted in two places, plus `design` before each of features/tasks/issues by index

## Steps

- [x] Add to `NAV_MODES`, the strip markup, and the sidecar's mode handling
- [x] Icon and active state
- [x] Test order, restoration, and server-mode parity
- [x] Rebuild the bundle and re-run the stale-build guard

## Result

Design mode is unlike both of the modes it sits between. Overview and Review are pure virtual pages — they return early and the left pane is irrelevant. Features/Tasks/Issues are pure lists. Design is **both**: the left pane lists the system and the proposals, the main pane frames whichever is open. So its branch lands on the register and then falls through to the nav fetch rather than returning; a test asserts the absence of that `return`, because adding one would silently leave the previous mode's list in the pane.

Reselecting Design while an artifact is open keeps the artifact — `startsWith('~design')`, not equality. Reselecting a mode is not a request to lose your place, and equality would have made it one.

The system is a separate group from the proposals. A project has one design system that never leaves and many proposals that arrive, get decided, and go quiet; listed together the standing reference gets buried among the transient ones. A design with no declared `role` is a proposal — defaulting the other way would promote every unlabelled draft into the slot that has to stay small.

Nav items point at `~design/<id>`, not the Markdown file. That override is the whole reason this task exists: clicking a design in the Library did nothing, because the item pointed somewhere the design surface never claimed.

The stale-build guard fired on the first full run, before the bundle was rebuilt. Working as designed.

## Notes

The position is the substance, so it gets its own assertion. The strip encodes kinds of thing — state · structure ×3 · queue · record — and design belongs upstream of structure: what it should be, before what is being built.

This reverses a two-day-old decision that six modes was the ceiling, taken when Active and Recent were retired to make room for Review. Reversing it deliberately is fine; drifting past it without noticing would not be, which is why it is written down here.

**Keep the other doors.** Two reachability bugs in two days came from having exactly one path to this surface. Redundant entry points are the fix, not a smell.
