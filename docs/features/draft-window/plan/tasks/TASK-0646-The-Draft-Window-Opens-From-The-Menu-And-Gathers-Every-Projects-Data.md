---
type: "[[task]]"
id: TASK-0646
aliases: ["TASK-0646"]
title: "The draft window opens from the menu and gathers every project's data"
status: doing
phase: "[[PHASE-045-The-Cockpit-In-Layers]]"
owner: user:edwin
created: 2026-10-13
updated: 2026-10-13
source: ["Edwin 2026-10-13: 'a new window beside the present one, keep the sidecar'"]
parent: "[[FEAT-0160-A-Draft-Window-Shows-What-Needs-You]]"
effort: "M"
due: ""
depends: []
blocks:
  - "[[TASK-0647-The-Draft-Windows-Page-Shows-Three-Areas-And-Opens-The-Present-Window]]"
  - "[[TASK-0648-Harness-Unit-Tests-And-A-Register-Row-For-The-Draft-Window]]"
related: []
tests: []
---

# The draft window opens from the menu and gathers every project's data

The main process opens a second window of a new kind from a menu item, and collects for it what every project owes, where its active phase stands and what its AI session is doing. This task draws nothing beyond a placeholder page; the page is [[TASK-0647-The-Draft-Windows-Page-Shows-Three-Areas-And-Opens-The-Present-Window]].

## Definition of Done

- [ ] The application menu has an item that opens the draft window. Choosing it again while the window is open brings that window to the front and does not open a second one.
- [ ] The present window keeps working while the draft window is open and after it is closed: its pages, its console and its live updates are unaffected. Closing the draft window does not quit the application or stop a sidecar.
- [x] The draft window is never the target of a `cockpit://` link. `handleDeepLink` in `desktop/src/main.ts` still sends to the present window.
- [x] The main process returns one payload to the draft window with, per project the shell discovers: its owed rows (project, subject, the one verb, and what a link needs to open it), its active phase with the facts the four questions need, and its AI session's state.
- [x] A project that could not be read appears in the payload marked as not read, with the reason. It is not left out and not given an empty list.
- [ ] The draft window can ask the main process to open a `cockpit://<project>/<target>` link, and the present window comes to the front at that page.
- [x] No request made for this payload is a write. The module calls `GET` routes only, and nothing under `src/project_os_cockpit/` gains or changes a write route.
- [x] While the draft window is closed, nothing extra is asked of the sidecars.
- [x] `npm run typecheck` in `desktop/` passes.

## Steps

- [x] Read how File, New Window makes its window in `main.ts` (`createWindow`, the menu template) and how `mainWindow` is tracked, so the draft window is a separate kind and not another copy.
- [x] Add the draft window: its own HTML entry and its own small preload bridge, exposing only "get the payload", "payload changed" and "open this link".
- [x] Add a module under `desktop/src/ipc/` that builds the payload. Reuse `getAllWorkspaces` (`ipc/workspaces.ts`), `sidecarUrlFor` (`ipc/sidecar.ts`), the poller's states (`ipc/agent-state-poller.ts`) and the rows `ipc/agents-fleet.ts` already assembles. Keep the function that shapes sidecar answers into the payload pure, so [[TASK-0648-Harness-Unit-Tests-And-A-Register-Row-For-The-Draft-Window]] can test it.
- [x] Read owed rows from `/api/cockpit/obligations` and `/api/cockpit/landing?view=`, and the phase from `/api/cockpit/stats?scope=`. Take the feature note's defaults for cold projects and for a missing fact (open questions 1 and 3).
- [x] Add the "open this link" channel, routed through the existing `handleDeepLink`.
- [x] Add the built page to `desktop/scripts/copy-assets.mjs` if the build needs it.

## Notes

- The shell already polls session state and caches fleet rows for a few seconds. The draft window should share that cache, not add a second polling loop.
- Which phase is "active" for a project: the one in its `focus.phase`; otherwise its phases at `active`; otherwise none. The feature note records this as an assumption.
- Do not stop a running cockpit to try this. Other sessions share the running window; a test copy is started and stopped by its own process id only.

## State on 2026-10-13

Built, and not yet run inside the application. The task stays `doing` until Edwin has rebuilt and restarted the cockpit and the three unticked lines above have been seen to hold.

- **Where it is.** `desktop/src/ipc/home-window.ts` opens the window and gathers the payload; `desktop/src/ipc/home-payload.ts` holds the pure shaping; `desktop/src/preload-home.ts` is the bridge. `desktop/src/main.ts` gains the menu item File, Home (draft) with ⇧⌘H, the registration, and a Copy that works in the draft window.
- **Three differences from the list above.** The AI session's state is not in the payload: the page reads it from the existing `agents:fleet` channel, so nothing was duplicated. There is no "payload changed" push: the page asks again every 15 seconds and when it gets focus. A project counts as not read both when it has no live sidecar and when its sidecar does not answer.
- **Not checked.** Opening from the menu, the present window carrying on, and a link reaching the present window all need the running application. A link sent while no present window is open reaches the new window when its page has loaded; whether the page is ready for it then is not known.

## Second cut on 2026-10-13

The window is now small (560 by 660 points by default) and always on top at the `floating` level, at Edwin's request. Nothing else in this task changed.
