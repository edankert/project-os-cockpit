---
type: "[[change]]"
id: CHG-20260825-The-Console-Stops-Clipping-Its-Last-Line
aliases: ["CHG-20260825-The-Console-Stops-Clipping-Its-Last-Line"]
title: "The console stops clipping its last line — the element xterm is opened into no longer carries padding the fit addon spends"
status: merged
owner: user:edwin
created: 2026-08-25
updated: 2026-08-25
source: ["[[ISS-0255]]"]
commit: ""
pr: ""
impacts: ["desktop/src/renderer/renderer.css", "tools/GRANDFATHERED.yaml"]
issues: ["[[ISS-0255]]"]
features: ["[[FEAT-0003]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TASK-0577]]", "[[TST-0078]]", "[[ISS-0016]]"]
---

# The console stops clipping its last line

## Summary

The desktop shell's console was cutting its bottom row through the middle of the glyphs, and its last two columns off the right edge. `@xterm/addon-fit` sizes the terminal from `getComputedStyle(parent).height` and subtracts only the *xterm element's* own padding — correct under CSS's default `content-box`, where the parent's padding is already outside the reported height. `base.css` puts every element in both front doors in `box-sizing: border-box`, where it is inside. `.terminal-mount` carried `padding: 6px 8px`, so the addon spent 12px of height and 16px of width that the terminal could never occupy, asked the PTY for rows and columns outside the box, and `overflow: hidden` removed them.

The inset moved to `.terminal-pane`. The element xterm is opened into now has the same border box and content box, so the addon's measurement is exact.

## Impact

- **The console.** Nothing is clipped at any pane size. Measured against the rebuilt stylesheet: 0 clipped rows over 581 pane heights (was 466) and 0 clipped columns over 129 widths (was all of them, by up to 16px).
- **Nothing else moves.** The xterm keeps the same rect and the divider the same position, pixel for pixel — the pane's padding removes exactly what the mount's used to, and the divider is absolutely positioned, so its offsets resolve against the padding box, which padding does not change.
- **A restart is needed to see it.** The renderer is loaded at app start; a running shell keeps the old stylesheet.
- Mode 1 (the browser cockpit's `ttyd` iframe) is untouched — ttyd fits inside the iframe, where this padding is not in the measurement path.
- **Two grandfathered debts paid, incidentally.** `FEAT-0003` had to name [[TASK-0577]] in `tasks:` (PARENT-BACKLINK), and [[TASK-0185]]/[[TASK-0186]] — the ISS-0016 fixes, unlisted since 2026-07-21 — were added in the same line. `tools/GRANDFATHERED.yaml` shrinks 77 → 75, which is the only direction that file moves.

## Documentation Coverage (All Types Considered)

- features: not-applicable — [[FEAT-0003]] is `done` and its scope is unchanged
- requirements: not-applicable
- tasks: new — [[TASK-0577]]
- issues: new — [[ISS-0255]]
- tests: new — [[TST-0078]] (`tests/test_terminal_fit.py`)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new — this note
- snapshot: updated — focus, `issues`, `tasks`, `tests`, `changes`, `phases`

## Follow-ups

- [ ] Independent review is owed on this note and on [[TST-0078]] (QUALITY.md); not run in the authoring session.
