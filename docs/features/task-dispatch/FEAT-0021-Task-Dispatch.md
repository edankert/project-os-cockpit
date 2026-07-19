---
type: "[[feature]]"
id: FEAT-0021
aliases: ["FEAT-0021"]
title: "Task dispatch — start agent work from the task board"
status: in-review
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-05
goal: "Dispatch a TASK or ISS note to the agent directly from the nav: a context-menu action types a templated, note-aware prompt into the workspace terminal, and follow mode makes the resulting work observable end-to-end."
requirements: []
tests: ["[[TST-0011]]"]
tasks: ["[[TASK-0121]]", "[[TASK-0122]]"]
related: ["[[FEAT-0019-Agent-Hook-Ingestion]]", "[[FEAT-0013-Agent-State-Signal]]"]
---

# Task dispatch

## Why

vibe-kanban's core loop is "kanban card → agent works it"; Nimbalyst added a session kanban; Codex/Claude Desktop added automations. The cockpit already has the board — the tasks nav mode groups durable TASK notes by status, and issues by severity — but the path from "I'm looking at TASK-0042" to "the agent is working TASK-0042" is manual typing. Closing that gap turns the project-os backlog into the dispatch queue, with the advantage that the queue is versioned markdown the agent can read directly.

## Goal

From any TASK/ISS row (nav, library, right pane), one action starts the agent on that item in the workspace terminal, and the user can watch the work land via follow mode.

## Scope

1. **Dispatch action.** "Start with agent" in the existing native context menu on task/issue rows and in the centre-pane doc header. Types a templated prompt into the workspace PTY — e.g. `claude "Work on TASK-0042. Read docs/features/<slug>/plan/tasks/TASK-0042-….md first, follow the project-os lifecycle."` — and focuses the terminal. If a shell prompt is not idle (agent mid-session), paste the prompt text without a leading command so the user can steer.
2. **Agent choice.** Claude Code / Codex picker (remember last choice per workspace); template per agent.
3. **Prompt templates.** A small, editable template set (dispatch task, fix issue, resume task) resolved with note id, path, and title. Stored app-side; per-workspace overrides can come later.
4. **Round-trip visibility.** Dispatch marks the item as the workspace's agent-focus hint so follow mode and the FEAT-0020 activity strip pick it up immediately.

## Out of scope

- Headless execution, queues, parallel dispatch, auto-status transitions — the agent updates statuses per the lifecycle, not the dispatcher.
- Writing to note frontmatter from the cockpit (viewer constraint stands).
- Editing templates in-app (v1 ships sensible defaults).

## Acceptance

- Right-click a backlog TASK in the tasks nav → Start with agent → the terminal receives the templated command with correct id and path, and the terminal pane is focused.
- The picker switches between `claude` and `codex` templates and remembers the choice per workspace.
- Dispatching while the agent is mid-session pastes the prompt without executing a new `claude` command.
- After dispatch, follow mode + activity strip show the item being worked without further user action.

## Links

- Tasks: to be broken down (`plan/PLAN.md`)
- Context-menu surface: `desktop/src/main.ts` (`buildContextTemplate`), `desktop/src/renderer/renderer.ts` (nav row menus)
- PTY input: `desktop/src/ipc/terminal.ts`
