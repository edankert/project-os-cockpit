---
type: "[[task]]"
id: TASK-0121
aliases: ["TASK-0121"]
title: "Dispatch action — templates, context menu, agent picker, PTY input"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-05
parent: "[[FEAT-0021-Task-Dispatch]]"
effort: "M"
depends: []
blocks: ["[[TASK-0122]]"]
related: []
tests: []
---

# Dispatch action

## Definition of Done
- [ ] "Start with agent" appears in the native context menu on TASK/ISS rows and the centre-pane doc header.
- [ ] Dispatch types a templated command (`claude "Work on TASK-…. Read <path> first, follow the project-os lifecycle."`) into the workspace PTY and focuses the terminal.
- [ ] Claude Code / Codex picker; last choice remembered per workspace.
- [ ] If the agent is mid-session (instrumented session busy), the prompt text is pasted without a leading command.

## Steps
- [ ] Template set (dispatch/fix/resume) with id/path/title substitution, per-agent variants.
- [ ] Context-menu + doc-header wiring; busy detection from hook-fed state.
- [ ] PTY input via existing `terminal:input` IPC; shell-quote safely.

## Notes
The templated prompt must instruct the agent to read the note first — the note is the spec.
