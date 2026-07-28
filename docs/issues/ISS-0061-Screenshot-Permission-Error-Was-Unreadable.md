---
type: "[[issue]]"
id: ISS-0061
aliases: ["ISS-0061"]
title: "A denied screen-recording permission surfaced as \"could not create image from rect\""
status: fixed
severity: medium
phase: "[[PHASE-999-Unscheduled]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["user report 2026-07-28: 'I get this error when trying to make a screenshot: \"Screenshot failed: could not create image from rect\"'"]
related: ["[[FEAT-0045-Project-Inbox]]", "[[TASK-0234-Inbox-As-A-Left-Pane-Tray]]", "[[ISS-0060-Electron-32-Removed-File-Path]]"]
fixed_by: []
---

# The right message existed and could not be reached

`screencapture -i` fails with **`could not create image from rect`** when macOS has not granted Screen Recording. It reads like a geometry bug — a bad selection rectangle — and sends you looking at the wrong thing entirely.

The actionable text was already written:

```ts
error: stderr.trim()
  || `screencapture exited ${code}. On macOS this is usually the `
     + `Screen Recording permission — grant it to the cockpit in `
     + `System Settings › Privacy & Security › Screen Recording.`,
```

`stderr.trim() || hint` means the hint could **only** appear when stderr was empty — which is precisely the case where a permission denial is *not* the cause. The one branch that needed it was the one branch that could never reach it.

Worse, I had **already seen this exact string** while building the feature: I ran the failure path, recorded `could not create image from rect, exit 1` as evidence that the three-outcome logic worked, and never asked what a user would make of that sentence. The outcome was correctly *classified* and uselessly *worded*, and I checked only the first half.

## Confirmed, not guessed

```
$ npx electron probe.js
SCREEN_ACCESS=denied
```

`systemPreferences.getMediaAccessStatus('screen')` run against the same `node_modules/electron/dist/Electron.app` binary the cockpit runs as. So this is the cause, not a plausible story about the cause.

## The fix

The status is consulted, and a stderr matching the known permission signature is classified as a permission problem rather than passed through. The message names the app macOS will actually list — **`Electron`** in development, since TCC attributes capture to the spawning app and the dev binary lives under `node_modules` — because looking for "project-os-cockpit" in that settings list finds nothing.

Capture is still attempted when the status is not `granted`. Short-circuiting reads safer but suppresses the macOS prompt on `not-determined`, which would mean a fresh machine could never grant the permission at all. That property has its own assertion, because it is the kind of thing a later "optimisation" removes.

## Still needs a human step

Once macOS records a denial it does not re-prompt. Enable **Electron** under System Settings › Privacy & Security › Screen Recording and restart the cockpit; the app cannot grant this to itself.
