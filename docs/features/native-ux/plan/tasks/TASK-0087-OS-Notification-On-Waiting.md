---
type: "[[task]]"
id: TASK-0087
aliases: ["TASK-0087"]
title: "OS notification when a workspace's agent-state flips to `waiting`"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[FEAT-0013-Agent-State-Signal]]"]
parent: "FEAT-0012"
effort: ""
due: ""
depends: ["[[TASK-0082]]"]
blocks: []
related: []
tests: []
---

# OS notification on `waiting`

## Definition of Done
- [ ] When `agent-state-poller` observes any workspace's state
      transition INTO `waiting`, the main process fires a native
      `Notification` with title `Cockpit · <workspace name>` and body
      `<message || "waiting for input">`.
- [ ] Notifications **not** fired when the desktop window is
      currently focused AND showing that same workspace — the rail
      dot is already in your face, no need to chime.
- [ ] Notifications are **edge-triggered** — exactly one fires per
      transition into `waiting`; the next requires the state to leave
      `waiting` and come back.
- [ ] Clicking the notification brings the window forward AND
      switches the active workspace to the one the notification
      refers to (via a new `workspaces:switch-to` IPC the renderer
      already supports — same path as deeplink-driven switch).
- [ ] macOS-first; the same `electron.Notification` API works on
      Windows / Linux out of the box but minor copy / icon tweaks
      may need a follow-up.

## Steps
- [ ] `agent-state-poller.ts`: track a per-workspace "last observed
      state" inside the in-memory cache (we already diff against the
      serialised payload — add a separate `last_state` map).
- [ ] On transition `* → waiting`, call a new helper
      `notifyWaiting(workspace, payload)` that:
      - checks `BrowserWindow.getFocusedWindow()` + the renderer's
        current `activeId` (via a small `getCurrentActiveId` getter
        in the main process or via the existing IPC list);
      - constructs and shows the Notification;
      - wires `click` → `window.show()` + `focus()` + send
        `workspaces:switch-to` to the renderer.
- [ ] preload.ts: expose `cockpit.workspaces.onSwitchTo(cb)`.
- [ ] renderer.ts: subscribe; on switch-to, call `openWorkspace(id)`.

## Notes
This is the visible payoff of FEAT-0013 that the agent-state-dot
covers passively: even when the desktop app is backgrounded, the
user gets pinged when the agent needs them.

The check "window focused AND on this workspace" needs the renderer
to tell main which workspace is active. We don't currently push
that on every workspace switch; small IPC addition.
