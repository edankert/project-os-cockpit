---
type: "[[task]]"
id: TASK-0082
aliases: ["TASK-0082"]
title: "Workspace rail rendering + agent-state dot polling"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0010"
effort: ""
due: ""
depends: ["[[TASK-0080]]", "[[TASK-0081]]"]
blocks: []
related: []
tests: []
---

# Workspace rail with agent-state dots

## Definition of Done
- [ ] `#rail` renders one row per discovered workspace as a
      52×52 px icon button with:
      - The workspace's first letter (uppercase) as the glyph.
      - A colored ring / dot encoding the agent state.
      - An active-workspace accent on the currently-loaded row.
- [ ] Status color legend:
      - `busy` → green
      - `waiting` → amber, gentle CSS-animation pulse
      - `done` / `idle` → grey
      - `error` → red
      - No file / unknown → no dot (just the letter pill)
- [ ] Hover shows a tooltip with the full workspace name plus
      `"{state}: {message}"` if available.
- [ ] Click switches the active workspace (existing
      `openWorkspace(id)` flow).
- [ ] Main process polls every workspace's
      `<root>/.cockpit/agent-state.json` every 5 s (configurable
      constant), forwards changes to the renderer via a new
      `workspaces:agent-state` IPC. Polling is debounced — only
      send IPC when a workspace's state actually changes.
- [ ] Terminal toggle moved from old footer to a rail-footer slot
      (small icon-only button) so the rail owns its full column.
- [ ] Renderer tests covered by manual smoke; no automated
      renderer test framework yet.

## Steps
- [ ] `desktop/src/ipc/agent-state-poller.ts` (new): reads each
      workspace's state file, sends IPC on change. Uses
      `fs.promises.readFile` and a simple in-memory cache so we
      only fan out diffs.
- [ ] `main.ts`: start the poller when workspaces are loaded;
      stop it on quit.
- [ ] `preload.ts`: expose `cockpit.workspaces.onAgentState(cb)`.
- [ ] `renderer.ts`: render the rail; subscribe to
      `onAgentState`; update DOM on each event.
- [ ] `renderer.css`: rail row + dot + active-accent + pulse
      animation styles.

## Notes
This is the visible payoff of FEAT-0013: the user sees status dots
on multiple workspaces simultaneously, including ones whose cockpits
aren't actively spawned by the desktop shell — as long as some
cockpit (mode 1 or mode 3 in another window) has written
`.cockpit/agent-state.json` recently.

The poller is fs-only, so it works whether or not the workspace's
cockpit is currently running. Last-known-state is shown until
something rewrites the file.
