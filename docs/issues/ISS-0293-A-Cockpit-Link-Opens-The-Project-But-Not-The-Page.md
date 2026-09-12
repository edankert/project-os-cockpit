---
type: "[[issue]]"
id: ISS-0293
aliases: ["ISS-0293"]
title: "A cockpit:// link opens the project it names but not the page, so nothing outside the window can put a document in front of the reader"
status: fixed
phase: ""
owner: user:edwin
created: 2026-09-10
updated: 2026-09-10
source: ["Found 2026-09-10 in a your-health session. An agent wrote a design note with six mockups and was asked to show it in the cockpit; it had no way to open that page in the window. Edwin chose to have the cockpit taught to open a page from a link."]
severity: medium
component: desktop-shell
parent: ""
related: ["[[TASK-0064-App-Chrome]]", "[[TASK-0605-A-Cockpit-Link-Opens-The-Page-It-Names]]", "[[CHG-20260910-A-Cockpit-Link-Opens-The-Page-It-Names]]"]
tests: []
---

# A cockpit:// link opens the project it names but not the page

## Problem

A `cockpit://` link switches the window to a project and stops there. The part of the link that names a page is read and thrown away, so an agent or a script cannot put a particular document in front of the reader. The comment above the handler promises `cockpit://<workspace-id>/<target>`, and only the first half was ever built.

> [!quote] As reported — 2026-09-10 (user:edwin)
> But can you show the document in the cockpit?

`cockpit focus` does not cover this. It posts to one project's sidecar, and the window listens only to the sidecar of the project on screen. So a focus sent to any other project does nothing visible, and even on the right project it only opens the page when that project is set to Following.

## Repro

1. Open the cockpit on any project other than `your-health`.
2. From a terminal, send `cockpit://1992b48aeaa2a9be/docs/design/README.md` to the running app.
3. The window switches to your-health and shows its landing page, not `docs/design/README.md`.

## Expected

The link opens the page it names, in the project it names. A link written by a person or an agent names the project the way a cross-repo link does (`your-health`), not by the shell's internal workspace hash, which nobody outside the shell can know.

## Actual

- `renderer.ts` reads `new URL(url).host` as a workspace id and calls `openWorkspace`. `pathname` is never read.
- The host is matched against the internal workspace id only, so `cockpit://your-health/…` names no workspace.
- There is no way to deliver a link while the shell runs from source. macOS has no handler registered for `cockpit://` (`lsregister -dump` lists none), because `setAsDefaultProtocolClient` needs a packaged app bundle. The second-instance route is the only one open: a second `electron .` hands its argv to the running window and quits. That second process, though, runs the whole of `app.whenReady()` before it quits, because nothing checks the single-instance lock there.

## Evidence

- `desktop/src/renderer/renderer.ts`, the `cockpitApi.deeplink.onUrl` handler: `const wsId = u.host; if (wsId) void openWorkspace(wsId);`
- `desktop/src/main.ts`: `if (!gotLock) { app.quit(); }` with `app.whenReady().then(…)` unguarded below it.

## Next Actions

- [x] The link opens its target: a note ID (`FEAT-0107`) is located the way a cross-repo link is, and a path (`docs/design/README.md`) is opened directly.
- [x] The host matches a project id as well as a workspace id.
- [x] A switch into another project waits for that project's sidecar and does not lose the target to the landing page, reusing the cross-repo jump's parked target and its landing suppression.
- [x] A second instance hands over its link and quits without starting anything.
- [x] A script delivers a link to the running window from source: `desktop/scripts/open-link.sh`.

## A second cause, found in the window

The first fix parsed the link with `URL` and passed its node tests, and in the window every link still did nothing. Read through the debugging port: the renderer's Chromium 128 gives `new URL('cockpit://your-health/x')` an empty `host` and a `pathname` of `//your-health/x`, where Node gives `your-health` and `/x`. So `parseCockpitLink` returned null for every link. **The handler it replaced read `u.host` the same way, so a `cockpit://` link had never switched a project in this app either.** The parser now reads the link by hand, and its test runs with no `URL` in scope, so a parser that reaches for it fails there instead of in the window.

## Verified

In the running window, through the debugging port, 2026-09-10: with no project open, `open-link.sh your-health docs/design/recovery-and-food-feedback/README.md` switched to your-health and `currentRel` read `design/recovery-and-food-feedback/README.md`. With your-health already open, the same link opened the note without a switch.
