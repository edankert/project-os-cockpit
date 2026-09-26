---
type: "[[task]]"
id: TASK-0129
aliases: ["TASK-0129"]
title: "Scope panes — left scope list, scoped centre dashboard, right Now + context"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
parent: "[[FEAT-0023-Overview-Scopes]]"
effort: "L"
depends: ["[[TASK-0128]]"]
blocks: []
related: ["[[TASK-0118]]"]
tests: []
---

# Scope panes

## Definition of Done
- [x] Left pane in Overview lists Project + all phases with mini progress bars; the current scope is highlighted; clicking selects the scope (renders detail in the centre — the app-wide contract).
- [x] Centre with a phase scope: breadcrumb + title + status + "open note" link, scoped hero, feature rows with task squares, exit-criteria checklist, scoped activity feed. Project scope: the existing all-up dashboard (phase rows become clickable scope links; centre live banner removed).
- [x] Right pane in Overview: live agent Now card + needs-input entries on top; below, the scope's linked/backlinks context (via the existing context API for the phase note); Project scope shows Now + pinned notes; never stale note context.

## Steps
- [x] `renderOverviewScopePane`, `renderScopedOverview`, `renderOverviewRightPane`.
- [x] Reuse `loadRightPane(phase rel)` for scope context; Now card component shared with the strip's data.
- [x] CSS for scope list, scoped header, exit criteria.

## Notes
Option D from the 2026-07-06 mockup review; the Now column replaces the centre banner from TASK-0127.
