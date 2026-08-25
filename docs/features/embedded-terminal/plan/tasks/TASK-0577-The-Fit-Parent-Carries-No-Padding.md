---
type: "[[task]]"
id: TASK-0577
aliases: ["TASK-0577"]
title: "The element xterm is opened into carries no padding — move the console's inset from `.terminal-mount` to `.terminal-pane` so the fit addon's measurement is exact"
status: done
phase: "[[PHASE-004-Embedded-Terminal]]"
owner: user:edwin
created: 2026-08-25
updated: 2026-08-25
source: ["[[ISS-0255]]"]
parent: "FEAT-0003"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[TASK-0185]]"]
tests: ["[[TST-0078]]"]
---

# The fit parent carries no padding

## Definition of Done
- [x] `.terminal-mount` declares no padding; the 6px/8px inset lives on `.terminal-pane`.
- [x] The xterm's rect and the divider's rect are unchanged — this is a fit fix, not a layout change.
- [x] No pane height between 120px and 700px clips a row; no width between 500px and 1400px clips a column.
- [x] [[TST-0078]] fails if the padding returns to the fit parent.

## Steps
- [x] Move `padding: 6px 8px` from `.terminal-mount` to `.terminal-pane` in `desktop/src/renderer/renderer.css`.
- [x] Leave the reason at the invariant — the addon's measurement is not visible from the rule.
- [x] Add `tests/test_terminal_fit.py` asserting it.

## Evidence

Measured in Chrome against the rebuilt `dist/renderer/renderer.css` and the vendored `xterm.js`, with no inline overrides: **0 clipped rows** over pane heights 120–700px (was 466 of 581) and **0 clipped columns** over widths 500–1400px (was every one, by up to 16px). Geometry identical before and after — xterm `1904×387` at `(8, 570)`, divider `1920` wide at top `562`.

## Notes

The inset was on the mount to keep the terminal's first line off the header divider. It still is — the pane paints the same background, and padding on the pane removes exactly the pixels the mount's padding used to, so the xterm lands on the same coordinates.

**The divider does not move**, which is the non-obvious part. It is `position: absolute; left: 0; right: 0` inside the pane, and an absolutely positioned box resolves its offsets against the containing block's *padding* box — which padding does not change. So the drag handle still spans the full pane width.

Why not keep the padding and fix the measurement instead: see the rejected alternative in [[ISS-0255]].

`FEAT-0003` had to name this task in `tasks:` for PARENT-BACKLINK. [[TASK-0185]] and [[TASK-0186]] were missing from the same list and went in with it, so `tools/GRANDFATHERED.yaml` loses two entries (77 → 75) — `test_the_ledger_only_covers_debt_that_still_exists` catches a paid debt still listed, which is how this surfaced.
