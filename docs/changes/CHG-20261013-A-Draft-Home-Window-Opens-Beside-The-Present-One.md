---
type: "[[change]]"
id: CHG-20261013-A-Draft-Home-Window-Opens-Beside-The-Present-One
title: "A draft home window opens beside the present one and shows what needs you, where a phase stands and what the AIs are doing"
status: merged
owner: user:edwin
created: 2026-10-13
updated: 2026-10-13
source: ["[[TASK-0646-The-Draft-Window-Opens-From-The-Menu-And-Gathers-Every-Projects-Data]]", "[[TASK-0647-The-Draft-Windows-Page-Shows-Three-Areas-And-Opens-The-Present-Window]]", "[[TASK-0648-Harness-Unit-Tests-And-A-Register-Row-For-The-Draft-Window]]"]
commit: ""
pr: ""
impacts: ["desktop/src/main.ts", "desktop/src/ipc/home-window.ts", "desktop/src/ipc/home-payload.ts", "desktop/src/preload-home.ts", "desktop/src/renderer/home.html", "desktop/src/renderer/home.css", "desktop/src/renderer/home.ts", "desktop/src/renderer/home-model.ts", "desktop/scripts/copy-assets.mjs", "desktop/tests/home-model.test.mjs", "desktop/harness/home-harness.html", "docs/reference/cockpit-capability-register.md"]
platforms: [macos]
issues: []
features: ["[[FEAT-0160-A-Draft-Window-Shows-What-Needs-You]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TST-0093-The-Draft-Window-Lists-Owed-Work-A-Phase-And-The-AIs]]", "[[PHASE-045-The-Cockpit-In-Layers]]"]
---

# A draft home window opens beside the present one

## Summary

File, Home (draft), or ⇧⌘H, opens a second kind of window with three areas: what needs you across every project, where the chosen project's active phases stand, and what each project's AI is doing. It is a draft for Edwin to judge. The present window is unchanged and stays the place where every act is done.

**When this note was first written the window had not been run inside the application.** Later the same day the cockpit was rebuilt and restarted at Edwin's request, and he tried it; see "Second cut" below.

## Impact

- No screen changed: every page of the present window is untouched. The draft window is a new screen with no surface note yet, which is part of [[ISS-0306]].

What someone using it sees:

- **A new menu item.** File, Home (draft), with ⇧⌘H. Choosing it again brings the open draft window forward; there is only ever one.
- **Needs you.** One list across all projects that are open in the cockpit. Each row has one verb, the subject's title, and its project and ID. Decisions come first and pushing comes last. Commits to push or deploy are one row per project, not one row per commit.
- **Where we are.** A project picker, then each active phase with four answers: how many features are done, which are in progress, which are next, and what is left. "Left" is the count of open tasks and the phase's unticked exit criteria. The phase the project's focus names is first. A release in preparation is one row under the phases.
- **The AIs.** One line per project with one of six words: working, needs your answer, finished its turn, stuck, quiet, not open.
- **Choosing a row opens the present window** at that note, phase, release, feature or project. The draft window has no button that changes anything.
- **A project that could not be read is named,** with the reason and, where one exists, the count and date of the last background check. It is never shown as owing nothing.
- **Copy** (⌘C) with the draft window in front copies from the draft window. The Edit menu's Copy used to go to the present window regardless.

What someone building on it should know:

- **It only reads.** `ipc/home-window.ts` sends `GET` to each live sidecar's `/api/cockpit/obligations`, `/api/cockpit/landing?view=`, `/api/cockpit/stats`, `/api/cockpit/stats?scope=<phase>` and `/api/cockpit/release`. No sidecar route was added or changed. Nothing is asked while the draft window is closed.
- **Two new IPC channels,** `home:data` and `home:open`, on a preload of its own (`preload-home.ts`) that exposes those two and the existing `agents:fleet`. The draft window is given none of the present window's write paths.
- **It is never `mainWindow`.** A `cockpit://` link still goes to the present window. If no present window is open, one is created and gets the link when it has loaded.
- **The page refreshes every 15 seconds and when it gets focus.** There is no push channel from main.

## Second cut the same day: a picture, small and on top

Edwin tried the window after a rebuild and restart and said: "It is too much text heavy instead we should be using diagrams or images to make this understable just by looking at, the text can be in the main application when opening the note. also if we want this as separate navigation window then the window should stay on top."

The page was redrawn as a board. Each project is one row: a mark for its AI's state, a mark per thing owed shaped by its verb, and a bar per active phase with a mark per feature and a dot per exit criterion. The top line gives each mark with its count and its word. Words are in tooltips; choosing a mark opens the present window, as before. The window is now 560 by 660 points by default and always on top, above other applications' windows too. The list under Impact above describes the first cut; the feature note describes the board.

For this cut the build was redone in place, all 187 node tests pass in the repository, five more deliberate breakages were each caught, and the cockpit was restarted twice by stopping its own verified process. The two Python tests that failed before the first build pass.

## What was checked

- `npm run typecheck` passes for the whole shell.
- 17 unit tests in `desktop/tests/home-model.test.mjs` pass against a build of these sources made outside the repository. They cover the page's pure functions and the payload shaping in `ipc/home-payload.ts`.
- The page was rendered in a browser through `desktop/harness/home-harness.html`, in light, and with payloads fetched read-only from the eight sidecars running on 2026-10-13, in dark. A scripted click on each kind of row produced the expected project and target.
- The whole node suite, run against that outside build: 176 of 182 pass. The six that fail are the git-state tests, and the same six fail when the untouched `HEAD` sources are built outside the repository the same way, so they are an effect of building outside the repository and not of this change. In place, against the build the running application uses, the 165 existing tests pass and the new file fails for want of its built script.

- The Python suite, with the repository's own environment: 2139 pass, 11 are skipped and 2 fail. Both failures come from the build not having been redone. `test_desktop_node_suite_passes` runs the node suite in place, where the new test file has no built script yet. `test_desktop_build_is_not_stale` reports that `dist/` was built from a different `renderer.ts` than the one on disk; this change does not touch `renderer.ts`, so the build was already behind the sources before it.

## What was not checked

- **The window inside the application.** The menu item, the second window, the link reaching the present window and Copy have not been exercised. That needs `npm run build` and a restart, which is Edwin's to do, and [[TST-0093-The-Draft-Window-Lists-Owed-Work-A-Phase-And-The-AIs]] is the check.
- **A link sent when no present window is open.** The new window gets the link when its page has loaded; whether its page is ready to act on it at that moment is not known.
- **The node suite in place against a build of these sources.**

## Test adequacy

Eleven deliberate breakages were made to the built functions, one at a time, and each made at least one test fail: commits no longer collapsing to one row; a note ID not sent in the link; an unread project reading as "nothing needs you"; ticked criteria listed as still standing; an unknown agent state reading as working; the verb order ignored; every phase treated as active; finished phases kept in the payload; exit criteria taken from another phase's answer; a shipped release shown as in preparation; the focus phase not first. The last was missed on the first run and the test was corrected.

## Limits of the draft

- "Where we are" answers for a phase and, in one row, a release. It does not answer for a single feature.
- Only projects with a live sidecar are listed row by row. The others show the last background count.
- There is no console in the draft window and still one AI session per project. Several sessions, each on its own branch or copy, are a later step recorded in the feature note.
