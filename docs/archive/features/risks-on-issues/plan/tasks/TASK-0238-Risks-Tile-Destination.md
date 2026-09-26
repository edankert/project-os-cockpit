---
type: "[[task]]"
id: TASK-0238
aliases: ["TASK-0238"]
title: "The Risks stat tile navigates to the Issues mode"
status: done
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: []
parent: "[[FEAT-0047-Risks-On-The-Issues-Surface]]"
effort: XS
depends: ["[[TASK-0237-Risks-Group-In-Issues-Mode]]"]
blocks: []
related: ["[[ISS-0063-Dead-Stat-Tiles]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
---

# TASK-0238 — Risks tile destination

## Definition of Done
- [ ] The Risks tile is a `<button>` and navigates to the Issues mode
- [ ] The Reqs tile is deliberately left dead (out of scope — see [[PHASE-010]])
- [ ] Half of [[ISS-0063]] closed

## Steps
- [ ] Pass `'issues'` as `buildStatTile`'s `navMode` for the Risks tile (`renderer.ts:5240`)
- [ ] Verify the tile renders as a button with the existing hover affordance

## Notes

One argument, but it must not merge before [[TASK-0237]]: a tile that navigates to a mode not listing risks is a worse dead end than a tile that does nothing, because it looks like it worked.
