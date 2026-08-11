---
type: "[[issue]]"
id: ISS-0144
aliases: ["ISS-0144"]
title: "A status toast never dismisses itself — 78 of the app's 110 status messages sit on the pane until something else overwrites them, and none can be clicked away"
status: fixed
severity: medium
owner: user:edwin
created: 2026-08-11
updated: 2026-08-11
phase: "[[PHASE-030-Obligations-Go-Home]]"
features: ["[[FEAT-0071-Since-You-Looked]]"]
tasks: []
related: ["[[ISS-0145]]"]
tags: [issue, renderer, ux]
---

# A status toast never dismisses

## What was found

Edwin, 2026-08-11, using the app: *"The caught up button … creates some caught up overlay instead which cannot be clicked away."*

He met it at `Caught up`, but it is not that button's bug.

`showStatus()` sets `statusBar.hidden = false`, **clears any pending hide timer**, and nulls the click handler. Hiding is the caller's job, via a separate `scheduleHide(ms)`. `.status-bar` is `position: absolute` across the bottom of the pane with a shadow — a floating panel, not a footer line.

**Measured across `renderer.ts`: 110 call sites, 78 of them with no `scheduleHide` or `hideStatus` within six lines.** The `Caught up` handler is one. So the default behaviour of the app's status channel is *persist forever*, and the exceptions are the 32 that remembered.

## Why it reads as an overlay

Because it is one, and because it has no exits: no timer, no close control, and `showStatus` explicitly sets `statusBar.onclick = null`, so clicking it does nothing. The only way out is to trigger another status message.

## The fix

**The default inverts.** `showStatus` schedules its own dismissal, and the bar is click-to-dismiss. Two deliberate details:

- **Errors stay longer, not forever.** An error that vanishes in two seconds is one the reader misses; an error that never leaves is the bug above. Different dwell, same guarantee.
- **`showActionStatus` keeps its own lifetime.** A toast with a click action ("Agent focus → TARGET · open") is an offer, and dismissing an offer before it can be taken is worse than leaving it — it already hides itself when the action is clicked.

Callers that already schedule a hide keep working: `scheduleHide` clears and replaces the pending timer, so an explicit dwell still wins.

## What the tests hold

`tests/test_status_toast_dismisses.py` reads the built bundle rather than the source, because this is a behaviour of the *shipped* renderer:

- `showStatus` arms a timer on every path — the assertion that fails if the default ever inverts back.
- The bar is click-to-dismiss.
- No call site is required to remember anything, which is the property that failed 78 times.
