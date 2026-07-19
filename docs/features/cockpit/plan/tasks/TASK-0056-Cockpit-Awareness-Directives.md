---
type: "[[task]]"
id: TASK-0056
aliases: ["TASK-0056"]
title: "Cockpit: LLM directives for reading the user's view"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-23
updated: 2026-05-23
source: []
parent: "[[FEAT-0006]]"
fixes: []
effort: XS
due: ""
depends: ["[[TASK-0054]]"]
blocks: []
related: ["[[TASK-0051]]"]
tests: []
---

# TASK-0056 — Awareness directives

## Goal
Teach the agent when and how to use `cockpit state` so the loop closes: agent reads the user's view, decides whether to follow / lead / diverge.

## Definition of Done
- [ ] `tools/instructions/COCKPIT.md` gains a "Reading the user's view" section covering:
  - the `cockpit state` command and its JSON shape
  - when to query (before significant work, after major progress)
  - how to interpret divergence (user on different note → mention, don't ignore)
  - respecting Following=OFF (don't push, but still describe in text)
- [ ] `tools/skills/cockpit-driving/SKILL.md` adds a step-0: "check state to see where the user is" before the start-focus call.
- [ ] LIFECYCLE.md preflight step 7 references state-check (optional but recommended).
