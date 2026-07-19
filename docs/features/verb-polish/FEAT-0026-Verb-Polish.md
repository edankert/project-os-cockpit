---
type: "[[feature]]"
id: FEAT-0026
aliases: ["FEAT-0026"]
title: "Verb polish — status-aware menus, palette verbs, type-from-data"
status: in-review
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
goal: "Verbs respect the lifecycle (menus filtered by the note's status via `when:` lists in the registry), are keyboard-reachable (⌘P understands 'refine TASK-0115'), and resolve the note type from row data instead of hardcoded ID prefixes so downstream verb types work."
requirements: []
tests: ["[[TST-0014]]", "[[TST-0011]]"]
tasks: ["[[TASK-0137]]", "[[TASK-0138]]", "[[TASK-0139]]", "[[TASK-0140]]"]
related: ["[[FEAT-0024-Agent-Verbs]]"]
---

# Verb polish

## Why

FEAT-0024 review: the menu offers "Close out" on done tasks and "Implement" on cancelled ones (the registry knows nothing of statuses although the rows carry them); there is no keyboard path to dispatch; and `NOTE_TYPE_BY_PREFIX` hardcoded renderer-side means a downstream `actions.yaml` adding verbs for a custom type can never surface them.

## Scope

1. **Status-aware verbs** (TASK-0137). Registry entries gain optional `when: [statuses]`; the renderer filters menus by the row's status (nav rows, doc header, scoped feature rows). Entries without `when` always show — the registry stays permissive by default.
2. **Palette verbs** (TASK-0138). ⌘P parses a leading verb token ("refine TASK-0115", "groom PHASE-007"): results are filtered to items whose type carries that verb and Enter dispatches instead of navigating; rows are visibly action-styled.
3. **Type-from-data + hardening** (TASK-0139). Nav/context rows carry `data-type`/`data-status` from the payload (prefix guess kept as fallback); REPL delivery warns when the live session's agent differs from the chosen one; dead code from the FEAT-0024 first cut removed.

## Acceptance

- A `done` task's menu shows Review/Close out but not Implement; a `backlog` task shows Implement/Refine but not Close out.
- Typing "refine TASK-01" in ⌘P lists dispatch actions; Enter types the refine prompt into the terminal.
- A custom type registered only in `actions.yaml` gets its menu on rows whose `data-type` matches.
