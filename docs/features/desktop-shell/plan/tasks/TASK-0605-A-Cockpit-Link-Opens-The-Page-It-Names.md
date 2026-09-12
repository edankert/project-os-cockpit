---
type: "[[task]]"
id: TASK-0605
aliases: ["TASK-0605"]
title: "A cockpit:// link opens the page it names, in the project it names, and a script can send one to the window running from source"
status: done
phase: "[[PHASE-005-Desktop-Shell]]"
owner: user:edwin
created: 2026-09-10
updated: 2026-09-10
source: ["Edwin, 2026-09-10, in a your-health session: 'But can you show the document in the cockpit?', then '2 please' to having the cockpit taught to open a page from a link"]
parent: "FEAT-0007"
effort: "S"
due: ""
depends: []
blocks: []
related: ["[[ISS-0293-A-Cockpit-Link-Opens-The-Project-But-Not-The-Page]]", "[[ISS-0294-Images-In-A-Note-Are-Broken-In-The-Desktop-App]]", "[[ISS-0295-A-File-Change-Moves-The-Reader-Off-The-Open-Note]]", "[[TASK-0064-App-Chrome]]"]
tests: []
---

# A cockpit link opens the page it names

This is the fix for [[ISS-0293-A-Cockpit-Link-Opens-The-Project-But-Not-The-Page]]. [[TASK-0064-App-Chrome]] built the `cockpit://` handler and read only the project half of the link.

## Definition of Done
- [x] `parseCockpitLink` in `desktop/src/renderer/deep-link.ts` reads the project and the target, by hand rather than with `URL`, which the renderer's Chromium 128 cannot use for a custom scheme. A target is nothing, a note ID, or a path under `docs/`, and a fragment is kept. It is a pure global loaded before `renderer.js`, like `cache-temperature.js`.
- [x] The renderer matches the project by project id as well as workspace id, opens a path with `navigateTo` and a note ID with `locateAndOpen`.
- [x] A link into another project parks its target in `pendingCrossRepoJump`, which now carries a path as well as an ID, and arms `suppressLandingOnce`, so the arriving project's landing page does not overwrite it.
- [x] `main.ts` returns early from `whenReady` and `before-quit` in a second instance, so a second `electron .` hands over its link and starts nothing.
- [x] `desktop/scripts/open-link.sh <project> [<target>]` sends a link to the running window.
- [x] `desktop/tests/deep-link.test.mjs`: eleven cases, run with no `URL` in scope. Making the parser ignore the target turned six of the first eight red.
- [x] Seen working in the running window: a link sent from outside opens a page in a project that was not on screen.
- [x] Two defects that stopped the page being readable once it opened, found in the same session and fixed with it: images in a note were broken in the desktop app ([[ISS-0294-Images-In-A-Note-Are-Broken-In-The-Desktop-App]]), and in Design mode any file change replaced the open note with `~design` ([[ISS-0295-A-File-Change-Moves-The-Reader-Off-The-Open-Note]]).

## Notes
- **Not covered: a cold start.** If the cockpit is not running, `open-link.sh` starts it and the link is dropped, because a first instance does not read its own argv. Delivering it would mean waiting for the workspace list and the sidecar, and nobody has needed it yet.
- **`open cockpit://…` still does nothing from source.** macOS registers a URL scheme only for a packaged app bundle. The packaged app is where `open` will work; from source the script is the route.
- **`cockpit focus` is a different thing and stays as it was.** It follows an agent inside the project on screen, and a focus from a project in the background is deliberately not allowed to pull the window there. A link is an explicit request, so it may switch.
