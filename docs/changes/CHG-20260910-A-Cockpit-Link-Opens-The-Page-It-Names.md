---
type: "[[change]]"
id: CHG-20260910-A-Cockpit-Link-Opens-The-Page-It-Names
aliases: ["CHG-20260910-A-Cockpit-Link-Opens-The-Page-It-Names"]
title: "A cockpit:// link now opens the page it names, in the project it names; images in a note load in the desktop app; and a file change no longer moves the reader off the open note"
status: merged
owner: user:edwin
created: 2026-09-10
updated: 2026-09-10
source: ["Edwin, 2026-09-10, in a your-health session: 'But can you show the document in the cockpit?', then '2 please' to having the cockpit taught to open a page from a link"]
commit: "a6a33a6"
pr: ""
impacts: ["desktop/src/renderer/deep-link.ts", "desktop/src/renderer/renderer.ts", "desktop/src/renderer/index.html", "desktop/src/main.ts", "desktop/scripts/open-link.sh", "desktop/tests/deep-link.test.mjs", "tests/test_desktop_note_mounts.py", "tests/test_cross_repo_links.py", "tests/test_checks_view.py", "docs/reference/cockpit-capability-register.md"]
issues: ["[[ISS-0293-A-Cockpit-Link-Opens-The-Project-But-Not-The-Page]]", "[[ISS-0294-Images-In-A-Note-Are-Broken-In-The-Desktop-App]]", "[[ISS-0295-A-File-Change-Moves-The-Reader-Off-The-Open-Note]]"]
features: ["[[FEAT-0007-Desktop-Shell]]"]
requirements: []
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TASK-0605-A-Cockpit-Link-Opens-The-Page-It-Names]]", "[[TASK-0064-App-Chrome]]"]
---

# A cockpit link opens the page it names

## Summary

An agent or a script can now put a particular page in front of the reader. `cockpit://your-health/docs/design/README.md` switches the window to your-health and opens that page. `cockpit://your-health/FEAT-0107` opens that note wherever it lives. Until now the link switched project and stopped, because the page half was never read ([[ISS-0293-A-Cockpit-Link-Opens-The-Project-But-Not-The-Page]]).

From source, send a link with the script:

```bash
desktop/scripts/open-link.sh your-health docs/design/README.md
desktop/scripts/open-link.sh your-health FEAT-0107
```

Two more defects stood between an open page and a readable one, and both are fixed here. **Every image in a note was a broken icon in the desktop app** ([[ISS-0294-Images-In-A-Note-Are-Broken-In-The-Desktop-App]]). **In Design mode, any file change in the project replaced the open note with the Design page** ([[ISS-0295-A-File-Change-Moves-The-Reader-Off-The-Open-Note]]), so a note opened while agents were writing stayed on screen for seconds.

## What a person sees

- The window comes forward, switches to the project the link names, and opens the page. If the project is already on screen, the page opens without a switch.
- A link to a project that is not on this machine says so in the status line. So does anything that is not a cockpit link.
- The project can be written as its project id (`your-health`), the same name a `[[your-health#ID]]` link uses. The internal workspace id still works.
- Images in a note show in the desktop app, in the centre pane, in a check's procedure text and on the review page.
- A note stays open when a file in the project changes, in every left-pane mode.

## What changed

- **`desktop/src/renderer/deep-link.ts` is new.** `parseCockpitLink` takes a link apart into a project and a target: nothing, a note ID, or a path. It is a plain global loaded before `renderer.js`, so the node suite can test it without a window. **It reads the link by hand.** The renderer's Chromium 128 reads no host from a `cockpit://` URL, where Node's `URL` does, so the first version passed its node tests and returned null for every link in the window. The handler it replaced had the same flaw, so a `cockpit://` link had never switched a project here.
- **`renderer.ts` opens the target.** A link into another project parks its target in `pendingCrossRepoJump` and arms `suppressLandingOnce`, the same route a cross-repo link takes, so the arriving project's landing page does not overwrite it. `pendingCrossRepoJump` now carries a path as well as a note ID.
- **`main.ts` lets a second instance do nothing but hand over its link.** `app.quit()` did not stop `whenReady` from running in the second process, so a second `electron .` built the menu and started the agent-state poller and the url janitor before it quit. Both `whenReady` and `before-quit` now return early when the process did not get the single-instance lock.
- **`pointImagesAtSidecar` rewrites a note's images.** The sidecar writes `<img src="/docs/…">`, and the window's page is `file://`, so each image resolved to `file:///docs/…`. The rewrite runs at all three places that mount a note.
- **`loadWsNav` takes `{ land: false }`, and the soft reload passes it.** The soft reload called `loadWsNav()` to refresh the list, and that also landed the mode on its page.
- **`desktop/scripts/open-link.sh` is new.** macOS routes a URL scheme only to a packaged app, so `open cockpit://…` reaches nothing while the shell runs from source. The script launches a second `electron .` with the link, which is the route the single-instance lock already provides.

## Not covered

- **A cold start drops the link.** If the cockpit is not running, the script starts it and the page is not opened.
- **`cockpit focus` is unchanged.** It follows an agent within the project on screen. A focus from a background project still does not pull the window there, because agents focus often and nobody asked for them. A link is an explicit request, which is why it may switch.

## Verification

- `desktop/tests/deep-link.test.mjs`: 11 passed, run with no `URL` in scope. With the parser made to ignore the target, 6 of the first 8 failed.
- `tests/test_desktop_note_mounts.py`: 3 passed. Removing the image rewrite from one mount, and putting the soft reload back to `loadWsNav()`, turned two of them red.
- Two existing source guards named the old form of `loadWsNav` and were rewritten, not loosened: `test_cross_repo_links.py` still requires the landing suppression to decide every landing, and `test_checks_view.py` finds the function by name.
- In the running window, through a debugging port opened for the purpose: a link opened the note from no project and from your-health, all six images loaded, and the note stayed open after its file was touched.
- Desktop node suite: 120 passed. Full suite: 2236 passed, 6 skipped, 1 failed. The failure is `tests/test_release_evidence.py::test_both_corrupt_store_artifacts_are_reported_and_the_others_are_not`, which pins two broken store files in your-trainer and fails, as its docstring says it will, now that REL-0007's has been repaired. Nothing in this change touches it.
