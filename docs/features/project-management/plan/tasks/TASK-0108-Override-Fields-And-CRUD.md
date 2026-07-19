---
type: "[[task]]"
id: TASK-0108
aliases: ["TASK-0108"]
title: "Workspace override fields + CRUD IPC"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
parent: "FEAT-0016"
---

# Workspace override fields + CRUD IPC

## Definition of Done
- [ ] `Workspace` type gains `userName?: string` and
      `userIcon?: string`.
- [ ] Renderer uses `effectiveName(ws) = ws.userName ?? ws.name`
      and `effectiveIcon(ws) = ws.userIcon ?? ws.icon` everywhere
      the workspace is displayed.
- [ ] Main exposes:
      - `workspaces:add({ root, name?, icon? })`
      - `workspaces:update({ id, userName?, userIcon? })`
      - `workspaces:remove(id)`
      - `workspaces:pickIcon()` — image file picker → data URI
        (200 KB cap, base64).
- [ ] All persist to workspaces.json synchronously after the IPC.
