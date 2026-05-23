---
type: "[[task]]"
id: TASK-0048
aliases: ["TASK-0048"]
title: "Cockpit: agent-drives-cockpit — POST /api/cockpit/focus + SSE fan-out"
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
blocks: ["[[TASK-0049]]", "[[TASK-0050]]", "[[TASK-0053]]"]
related: []
tests: []
---

# TASK-0048 — agent-drives-cockpit — POST /api/cockpit/focus + SSE fan-out

## Summary
Server-side: new POST /api/cockpit/focus endpoint resolves a target (note ID, docs-relative path, or cockpit URL) and broadcasts a `cockpit:focus` SSE event. Every connected cockpit tab with Following=ON jumps to the resolved URL.

## Disposition
Shipped as part of the LLM-drives-cockpit roll-up. No CHG note was written at the time; authoritative record is git commit 19746cc. This stub note was created post-hoc (2026-05-23) so the link graph is complete. [[CHG-20260523-Cockpit-Bi-Directional-State]] later extended the bi-directional sync.

## Links
- Feature: [[FEAT-0006]]
- Sibling tasks: [[TASK-0048]] [[TASK-0049]] [[TASK-0050]] [[TASK-0051]] [[TASK-0052]]
