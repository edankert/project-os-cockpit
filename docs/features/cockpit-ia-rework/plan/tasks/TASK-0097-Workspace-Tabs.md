---
type: "[[task]]"
id: TASK-0097
aliases: ["TASK-0097"]
title: "Workspace tabs (top strip, replacing the rail pills)"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0014"
related: ["[[TASK-0082]]"]
tests: []
---

# Workspace tabs

## Definition of Done
- [x] `<nav id="tab-strip">` lives under the title-bar drag region.
- [x] One tab per open workspace; click → switch; middle-click →
      close; `+` at the end (currently re-runs rescan; full picker
      is a follow-up).
- [x] Each tab shows workspace name + agent-state dot (idle / busy
      / waiting / error / done), reusing `ws-waiting-pulse`.
- [x] `Cmd+1..9` jumps to tab N. `Cmd+W` closes active tab.
- [x] Width: per-tab clamps to 120–220 px; long names ellipsis.
- [ ] Drag-to-reorder — deferred follow-up.
- [x] Active tab persists across launches (existing localStorage).

## Notes
The old `.ws-rail` element is repurposed in TASK-0098 — keep the
ID stable so existing IPC paths still match.
