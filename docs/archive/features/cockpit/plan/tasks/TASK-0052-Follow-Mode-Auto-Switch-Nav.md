---
type: "[[task]]"
id: TASK-0052
aliases: ["TASK-0052"]
title: "Cockpit: follow-mode auto-switches nav so the agent's focus is highlighted in the left nav"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-09
updated: 2026-05-23
source: []
parent: "[[FEAT-0006]]"
fixes: []
effort: S
due: ""
depends: []
blocks: []
related: []
tests: []
---

# TASK-0052 — follow-mode auto-switches nav so the agent's focus is highlighted in the left nav

## Summary
When a `cockpit:focus` event arrives, the cockpit infers the appropriate left-nav mode (TASK→tasks, FEAT→features, ISS→issues, REQ/PHASE→features, etc.) and switches to it. Then highlights + scrolls the active item into view so the user can see what the agent is on.

## Disposition
Shipped as part of the LLM-drives-cockpit roll-up. No CHG note was written at the time; authoritative record is git commit 19746cc (cockpit) + the subsequent TASK-0051..0052 commits. This stub note was created post-hoc (2026-05-23) so the link graph (FEAT-0006.tasks back-link, depends/blocks chains) is complete. [[CHG-20260523-Cockpit-Bi-Directional-State]] later extended the bi-directional sync.

## Links
- Feature: [[FEAT-0006]]
- Sibling tasks: [[TASK-0048]] [[TASK-0049]] [[TASK-0050]] [[TASK-0051]] [[TASK-0052]]
