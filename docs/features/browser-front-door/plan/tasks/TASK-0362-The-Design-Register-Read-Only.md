---
type: "[[task]]"
id: TASK-0362
aliases: ["TASK-0362"]
title: "The design register and artifact framing reach the browser, with no verdict or capture control"
status: backlog
phase: "[[PHASE-029-One-Tool-Two-Front-Doors]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-09
source: ["[[ADR-0010-What-The-Browser-Cockpit-Is-For]]"]
parent: "[[FEAT-0083-The-Browser-Cockpit-Answers-Questions]]"
effort: S
due: ""
depends: ["[[ADR-0010-What-The-Browser-Cockpit-Is-For]]"]
blocks: []
related: []
tests: []
---

# The design register, read-only

## Definition of Done
- [ ] Mode 1 lists designs and frames an artifact in its pane
- [ ] No verdict, capture, comment or revision control exists in the DOM — not hidden, absent
- [ ] Region highlighting, if ported, is display only

## Steps
- [ ] Add the register from `/api/cockpit/designs`
- [ ] Frame the artifact under the same boundary the shell uses — an artifact is content, not code (design-authoring skill)
- [ ] Assert absence rather than disablement in the test: a disabled control is a control

## Notes
Reading a design is reading; judging one is a decision, and decisions are the desk's. The split matters more here than elsewhere because a design verdict stamps `design_revision` — an approval given to v3 must never launder v6, and that guard lives server-side where the browser cannot reach it anyway.
