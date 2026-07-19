---
type: "[[plan]]"
id: PLAN-FEAT-0012
aliases: ["PLAN-FEAT-0012"]
title: "Plan: Native UX wins"
status: active
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
implements: ["[[FEAT-0012-Native-UX]]"]
related: ["[[FEAT-0013-Agent-State-Signal]]", "[[FEAT-0010-Native-Nav-Right-Pane]]", "[[FEAT-0011-Native-Center-Pane]]", "[[PHASE-006-Native-Cockpit-UI]]"]
---

# Plan — FEAT-0012 Native UX wins

## Six independent additions

Each item is pure addition — no behaviour from earlier features
changes — and each is individually scope-trimmable if energy runs
out. Sequencing intent: highest payoff first.

1. **[[TASK-0087]] — OS notifications on agent-state `waiting`.**
   When any workspace's agent-state transitions to `waiting` AND the
   user isn't already looking at that workspace (window unfocused, or
   focused on a different workspace), fire a native OS notification:
   "Cockpit · `<workspace>` is waiting — `<message>`". Click brings
   the window forward and switches to that workspace. This is the
   most-asked-for piece — the original FEAT-0013 conversation
   surfaced this as the agent-state pipe's primary consumer.

2. **[[TASK-0088]] — Cmd+P quick-switch.** Fuzzy search palette over
   every note in the active workspace. Enter navigates the centre
   pane; Esc closes. Same data as `/api/cockpit/nav` (no new
   endpoint needed). Renderer-side overlay; no main-process work.

3. **[[TASK-0089]] — Cmd+F find-in-doc.** Native find-bar searching
   within the currently-mounted Markdown body in `#doc-view`.
   Highlights + match count + next/prev. Pure renderer; no
   Python involvement.

4. **[[TASK-0090]] — Native context menus.** Right-click on nav rows
   → native `Menu.popup()` via IPC: *Copy ID*, *Copy path*, *Reveal
   in Finder*, *Open in new window* (when multi-window lands). Same
   on centre-pane links and rail pills.

5. **[[TASK-0091]] — Drag-and-drop file → note.** Drop a `.md` from
   Finder onto the cockpit; if inside the current workspace's docs
   root, navigate to it; if outside, surface a toast offering "open
   containing repo as workspace."

6. **[[TASK-0092]] — Multi-window + per-workspace window state.**
   ⌘N opens another workspace in a new window (each with its own
   sidecar already; FEAT-0007 supports this). Window menu lists open
   windows by workspace name. Per-workspace `{x, y, width, height}`
   persistence layered on top of the existing app-wide state.

## Dependencies

- **Hard for TASK-0087:** FEAT-0013 + the agent-state poller from
  FEAT-0010 / TASK-0082. (Both shipped.)
- **Hard for TASK-0088:** FEAT-0010 (left nav supplies the search
  corpus).
- **Hard for TASK-0089:** FEAT-0011 (centre pane mounts the
  searchable HTML).
- **Soft for TASK-0090:** FEAT-0011's click-interception path — the
  context menu intercepts right-clicks on the same targets.
- **Hard for TASK-0091:** FEAT-0011 (drop-target navigation).
- **Hard for TASK-0092:** FEAT-0007 (the workspace + sidecar model).

## Sequencing notes

- TASK-0087 ships first (already explicitly called for; the data
  pipe is hot).
- TASK-0088 and TASK-0089 are independent renderer-only adds — fast,
  high user value, can land in either order.
- TASK-0090 lands once the menu surfaces above stabilise.
- TASK-0091 + TASK-0092 are heavier and more orthogonal to the
  cockpit's core function — defer if the rest of FEAT-0012 lands
  cleanly and the user wants to move on to other things.

## Out of plan
- A real plugin / extension API.
- Inline note editing.
- Touch Bar / macOS-tab integration.
- Linux/Windows OS notification parity verification (native
  Notification API differs subtly per platform; macOS first).
