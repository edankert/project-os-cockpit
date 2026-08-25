---
type: "[[test]]"
id: TST-0078
aliases: ["TST-0078"]
title: "The element xterm is opened into carries no padding — the box the fit addon measures and the box the terminal occupies are the same box"
status: active
covers: ["[[ISS-0255]]"]
owner: user:edwin
created: 2026-08-25
updated: 2026-08-25
phase: "[[PHASE-004-Embedded-Terminal]]"
source: ["[[ISS-0255]]"]
scope: feature
level: unit
entrypoint: ""
command: ".venv/bin/pytest tests/test_terminal_fit.py -q"
last_verified: ""
issues: ["[[ISS-0255]]"]
tasks: ["[[TASK-0577]]"]
artifacts: []
related: ["[[FEAT-0003]]"]
---

# The fit parent carries no padding

Automated, in `tests/test_terminal_fit.py`.

## What it pins

**That `.terminal-mount` declares no padding.** `@xterm/addon-fit` sizes the terminal from `getComputedStyle(parent).height` and subtracts only the *xterm element's* padding — exact under `content-box`, wrong under the `border-box` this renderer applies to everything. Padding on the fit parent is room the addon spends and the terminal cannot occupy, and `overflow: hidden` cuts what does not fit.

**That the premise is still true** — `base.css` still sets `* { box-sizing: border-box }`. If that ever changes, the rule stays safe but the *reason* recorded beside it stops being true, and a comment nothing checks is how a fix becomes folklore. Asserting the premise means the note fails loudly instead of quietly meaning something else.

**That `.terminal-mount` is still the fit parent** — `term.open(terminalMount)` in `renderer.ts`. Which element the addon measures is decided in TypeScript; a CSS rule about "the fit parent" that names the wrong element passes forever.

**That `overflow: hidden` stays.** It is what makes a mis-fit visible rather than a silent over-count, and what stops one spilling over the rest of the shell.

**That the inset survived the move.** The padding was not deleted — it moved to `.terminal-pane`. A test that only forbids padding on the mount is satisfied by deleting the inset, which would put the terminal's first line against the header divider.

## Why it asserts source and not pixels

The renderer has no DOM test harness, so there is nothing here that can lay out an xterm. The measurement that found the defect was made by hand in Chrome against the built `xterm.js` and the real stylesheet — 581 pane heights and 129 widths, before and after — and those numbers are in [[ISS-0255]]. What survives as a standing check is the invariant that made the numbers come out right, which is the part a future edit can break.

## Mutations checked

Both were applied and both failed the suite before it was recorded as passing:

- padding put back on `.terminal-mount` → `test_the_fit_parent_carries_no_padding` fails.
- padding dropped from `.terminal-pane` rather than moved → `test_the_inset_survived_the_move` fails.
