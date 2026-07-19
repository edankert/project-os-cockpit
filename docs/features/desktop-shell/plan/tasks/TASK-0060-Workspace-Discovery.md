---
type: "[[task]]"
id: TASK-0060
aliases: ["TASK-0060"]
title: "Workspace discovery + persistence + switcher UI"
status: done
phase: "[[PHASE-005-Desktop-Shell]]"
owner: user:edwin
created: 2026-05-24
updated: 2026-05-24
source: []
parent: "FEAT-0007"
effort: ""
due: ""
depends: ["[[TASK-0058]]"]
blocks: ["[[TASK-0061]]"]
related: []
tests: []
---

# Workspace discovery + switcher

## Definition of Done
- [ ] Main scans configured roots (default `~/Dev/repos/`) for `SNAPSHOT.yaml`
      files, depth-2.
- [ ] Discovered workspaces persisted to
      `app.getPath('userData')/workspaces.json` with shape
      `{id, root, name, last_opened, pinned}`.
- [ ] Renderer renders a workspace switcher listing the persisted set
      (name from `SNAPSHOT.yaml` `project.name`, fallback to dirname).
- [ ] Picking a workspace fires `ipc.workspaces.open(id)` (sidecar wiring
      lands in TASK-0061).
- [ ] Preferences UI (minimal — one root per line) for editing scan roots.
- [ ] "Rescan" menu item refreshes the list without restart.

## Steps
- [ ] `electron/ipc/workspaces.ts` — discovery + persistence + IPC handlers.
- [ ] `renderer/switcher.ts` — left-rail or top picker; keyboard nav.
- [ ] Workspace ID = SHA-1 of absolute repo path.
- [ ] Skip-list during scan: `node_modules`, `.git`, `target`, `dist`,
      `__pycache__`, `.venv`.
- [ ] Preferences pane: textarea, one root per line, persists to userData.

## Notes
No background polling — rescan is explicit. Decoupling discovery from sidecar
lifecycle keeps each piece debuggable in isolation.
