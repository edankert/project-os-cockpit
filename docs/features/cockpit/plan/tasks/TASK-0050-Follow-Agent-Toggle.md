---
type: "[[task]]"
id: TASK-0050
aliases: ["TASK-0050"]
title: "Cockpit: per-tab Following toggle (default ON, localStorage-persisted)"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-09
updated: 2026-05-23
source: []
implements: ["[[FEAT-0006]]"]
fixes: []
effort: S
due: ""
depends: []
blocks: []
related: []
tests: []
---

# TASK-0050 — per-tab Following toggle (default ON, localStorage-persisted)

## Summary
Header pill flips between Following / Manual. When Manual, the tab ignores agent `cockpit:focus` events. State persists in localStorage so refresh keeps the user's preference.

## Disposition
Shipped as part of the LLM-drives-cockpit roll-up. No CHG note was written at the time; authoritative record is git commit 19746cc (cockpit) + the subsequent TASK-0051..0052 commits. This stub note was created post-hoc (2026-05-23) so the link graph (FEAT-0006.tasks back-link, depends/blocks chains) is complete. [[CHG-20260523-Cockpit-Bi-Directional-State]] later extended the bi-directional sync.

## Links
- Feature: [[FEAT-0006]]
- Sibling tasks: [[TASK-0048]] [[TASK-0049]] [[TASK-0050]] [[TASK-0051]] [[TASK-0052]]
