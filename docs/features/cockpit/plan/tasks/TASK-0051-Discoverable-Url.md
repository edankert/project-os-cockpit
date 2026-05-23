---
type: "[[task]]"
id: TASK-0051
aliases: ["TASK-0051"]
title: "Cockpit: discoverable URL via .cockpit/url + CLI walk-up + LLM directives"
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

# TASK-0051 — discoverable URL via .cockpit/url + CLI walk-up + LLM directives

## Summary
Server writes <project_root>/.cockpit/url on startup; CLI walks up from CWD to find it (multi-project safe). Companion: tools/instructions/COCKPIT.md + tools/skills/cockpit-driving/SKILL.md teach the LLM when to call `cockpit focus`.

## Disposition
Shipped as part of the LLM-drives-cockpit roll-up. No CHG note was written at the time; authoritative record is git commit 19746cc (cockpit) + the subsequent TASK-0051..0052 commits. This stub note was created post-hoc (2026-05-23) so the link graph (FEAT-0006.tasks back-link, depends/blocks chains) is complete. [[CHG-20260523-Cockpit-Bi-Directional-State]] later extended the bi-directional sync.

## Links
- Feature: [[FEAT-0006]]
- Sibling tasks: [[TASK-0048]] [[TASK-0049]] [[TASK-0050]] [[TASK-0051]] [[TASK-0052]]
