---
type: "[[change]]"
id: CHG-20260525-Agent-Waiting-Notification
aliases: ["CHG-20260525-Agent-Waiting-Notification"]
title: "OS notification on agent `waiting` — first FEAT-0012 task; FEAT-0012 plan + 5 remaining tasks drafted"
status: merged
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[TASK-0087]]"]
commit: ""
pr: ""
impacts:
  - "desktop/src/ipc/agent-state-poller.ts (+lastState edge-trigger, +maybeNotifyWaiting)"
  - "desktop/src/main.ts (+activeWorkspaceId tracker, +getActiveWorkspaceId dep)"
  - "desktop/src/preload.ts (+workspaces.onSwitchTo, +workspaces.notifyActiveChanged)"
  - "desktop/src/renderer/renderer.ts (+notifyActiveChanged on openWorkspace, +onSwitchTo handler)"
  - "docs/features/native-ux/plan/PLAN.md (new)"
  - "docs/features/native-ux/plan/tasks/TASK-0087..TASK-0092 (new)"
issues: []
features: ["[[FEAT-0012-Native-UX]]"]
related: ["[[FEAT-0013-Agent-State-Signal]]", "[[FEAT-0010-Native-Nav-Right-Pane]]"]
---

# Agent-waiting OS notification

## Summary

First task of FEAT-0012. The desktop shell now pings the OS when a
workspace's agent-state flips into `waiting` — the
"agent finished and needs me" signal that motivated FEAT-0013.

Notification fires when:
- A workspace's `.cockpit/agent-state.json` transitions from any
  state to `waiting`, AND
- The user isn't already looking at that workspace
  (`window.isFocused() && activeWorkspaceId === ws.id` → suppressed).

Notification is edge-triggered: exactly one fires per transition
into waiting; subsequent polls with the same state stay silent.

Click → window.show() + focus() + `workspaces:switch-to` IPC →
renderer's `openWorkspace(id)` switches to that workspace.

Also drafted: FEAT-0012 PLAN.md + TASK-0088..0092 (Cmd+P quick-switch,
Cmd+F find-in-doc, native context menus, drag-and-drop, multi-window).
All currently `backlog`.

## What landed

### TASK-0087 — OS notification on waiting

`agent-state-poller.ts`:
- New `lastState: Map<workspaceId, state>` alongside the existing
  `lastSerialised` map. Diffs the state name directly so the edge
  trigger doesn't depend on the full payload changing.
- `maybeNotifyWaiting(ws, payload, window)` checks the focus
  condition, calls `Notification.isSupported()`, and shows a
  native notification with title `Cockpit · <workspace name>`.
- `notification.on('click', …)` brings the window forward (restore
  + show + focus) and sends `workspaces:switch-to` IPC.
- Primer pass on `startAgentStatePoller` doesn't fire notifications —
  state that's been sitting in the file before app launch isn't
  "news."

`main.ts`:
- Tracks `activeWorkspaceId` from the renderer via a new
  `workspaces:active-changed` IPC.
- Passes `getActiveWorkspaceId` into the poller so the focus-
  suppression check works.

`preload.ts`:
- `cockpit.workspaces.onSwitchTo(cb)` — subscribes to the click-
  triggered switch event.
- `cockpit.workspaces.notifyActiveChanged(id)` — fire-and-forget
  from renderer when the active workspace changes.

`renderer.ts`:
- `openWorkspace()` now calls `notifyActiveChanged` on every
  switch.
- New `onSwitchTo` subscriber routes the click back through the
  existing `openWorkspace` path.

### FEAT-0012 drafted

PLAN.md plus six task notes (TASK-0087..0092). Five of those —
Cmd+P, Cmd+F, native context menus, drag-and-drop, multi-window —
are sequenced after this notification ships and each is individually
scope-trimmable.

## Smoke-test

```sh
# Mode-1 cockpit somewhere for .cockpit/url discovery
python -m project_os_cockpit ./docs &

# Background the desktop window (Cmd+H) or open a different
# workspace in it. Then in another terminal:
cockpit signal waiting --message "review my PR"
# → macOS Notification banner: "Cockpit · project-os-cockpit"
#   body "review my PR". Click → window comes forward, workspace
#   switches.
```

## Documentation Coverage
- features: covered (FEAT-0012 → `in-progress`)
- requirements: not-applicable
- tasks: TASK-0087 → `done`; TASK-0088..0092 → `backlog` (drafted)
- issues: not-applicable
- tests: not-applicable (renderer + Electron-main behaviour; no
  pytest target. Future task could add an Electron test if needed.)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (TASK counter 86 → 92, focus → TASK-0087,
  FEAT-0012 → in-progress, tasks_done 86 → 87)
