---
type: "[[task]]"
id: TASK-0073
aliases: ["TASK-0073"]
title: "Per-note scroll preservation + hash anchors"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0011"
effort: ""
due: ""
depends: ["[[TASK-0072]]"]
blocks: []
related: []
tests: []
---

# Scroll preservation + hash anchors

## Definition of Done
- [ ] `scrollPositions: Map<relPath, number>` remembers the centre
      pane's `scrollTop` at the moment of nav-away.
- [ ] On history back, restore the previous `scrollTop` after
      re-mount.
- [ ] `#heading` fragment in a `navigateTo(rel + '#heading')` call
      scrolls to the matching `[id=heading]` element after mount
      (using `requestAnimationFrame` so layout has happened).
- [ ] SSE `cockpit:focus` events route through `navigateTo` and
      land at the right note + anchor.

## Steps
- [ ] Renderer: capture `docView.scrollTop` in `navigateTo` before
      replacing innerHTML; key by current rel.
- [ ] Renderer: parse `#frag` from rel during navigate; after
      mount, `document.getElementById(frag)?.scrollIntoView()`.
- [ ] Wire to `agent.onFocus` (already exposed from FEAT-0007).

## Notes
The Markdown renderer emits slugger-style IDs (`## My Heading` →
`<h2 id="my-heading">`). Document the slugging convention in
`docs/references/COCKPIT-API.md` when this task closes.
