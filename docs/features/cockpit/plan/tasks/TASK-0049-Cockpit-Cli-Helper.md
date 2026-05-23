---
type: "[[task]]"
id: TASK-0049
aliases: ["TASK-0049"]
title: "Cockpit: `cockpit` CLI helper (focus subcommand)"
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
blocks: ["[[TASK-0051]]"]
related: []
tests: []
---

# TASK-0049 — `cockpit` CLI helper (focus subcommand)

## Summary
Tiny console script `cockpit focus <target>` POSTs to /api/cockpit/focus from any terminal. Designed for the LLM session inside the embedded ttyd, but works from any shell with COCKPIT_URL set.

## Disposition
Shipped as part of the LLM-drives-cockpit roll-up. No CHG note was written at the time; authoritative record is git commit 19746cc. This stub note was created post-hoc (2026-05-23) so the link graph is complete. [[CHG-20260523-Cockpit-Bi-Directional-State]] later extended the bi-directional sync.

## Links
- Feature: [[FEAT-0006]]
- Sibling tasks: [[TASK-0048]] [[TASK-0049]] [[TASK-0050]] [[TASK-0051]] [[TASK-0052]]
