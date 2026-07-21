---
type: "[[task]]"
id: TASK-0177
aliases: ["TASK-0177"]
title: "Overview: stale phase scope across workspaces errors (Unknown phase) on phase-less projects"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-20
updated: 2026-07-20
source: []
parent: "FEAT-0023"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[TASK-0130]]"]
tests: []
---

# TASK-0177 — stale overview scope fallback

Selecting Overview on a project that lacks the remembered phase shows an error toast — user report: "Unknown phase: PHASE-999" (2026-07-20). `overviewScope` is module-level state that is not reset on workspace switch, so after viewing a phase scope (e.g. PHASE-999) in one project and switching to a phase-less project, `loadWsNav` routes to `~overview/PHASE-999`; the scoped stats endpoint 404s and `renderOverviewPage` surfaces `Unknown phase: <scope>`.

Fix: (1) reset `overviewScope`/`scopePhaseList` to null in `openWorkspace` so a new project starts at the unscoped project overview; (2) make `renderOverviewPage` resilient — on a 404 for a non-null scope, fall back to the unscoped project overview (reset the scope and re-render) instead of erroring. The explicit-error path stays only for the impossible null-scope 404.

Verification: CDP — view a phase scope in a project that has one, switch to a phase-less project, select Overview → renders the project overview with no error toast; a direct deep-link to a non-existent `~overview/PHASE-xxx` also degrades gracefully.

## Verification

CDP: viewed the PHASE-999 (Future/Unphased) scope in project-os-cockpit, switched to phase-less your-sudoku, selected Overview → the project overview renders (`.overview-pane` + Now board/phase section) with no status toast and no thrown exceptions (previously: `Unknown phase: PHASE-999`). `openWorkspace` now clears `overviewScope`/`scopePhaseList`; `renderOverviewPage` degrades a 404 non-null scope to the unscoped project overview. tsc clean; build OK.
