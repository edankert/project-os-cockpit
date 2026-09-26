---
type: "[[task]]"
id: TASK-0156
aliases: ["TASK-0156"]
title: "Severity remap — idle_prompt means waiting, not needs-input; red reserved for blocked-mid-work"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
parent: "FEAT-0030"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[TASK-0153]]"]
tests: []
---

# TASK-0156 — idle_prompt severity remap

A normally-finished turn currently escalates: `Stop` → amber waiting, then ~60s later Claude Code's `idle_prompt` notification → red needs-input pulse (user report 2026-07-19 — "session completed and the item keeps blinking red"). Finished is not blocked: move `idle_prompt` out of `_NEEDS_INPUT_NOTIFICATIONS` in the tracker so it records `waiting`; red stays for `permission_prompt` and `elicitation_dialog`. Mirror the semantics in the external-hook embedded script (coordinate with TASK-0153, which ports the subtype gate there). Update the ingest test table. Verification: pytest — idle_prompt Notification → waiting; permission_prompt → needs-input.
