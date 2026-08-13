---
type: "[[issue]]"
id: ISS-0158
aliases: ["ISS-0158"]
title: "The since-you-looked band can mount twice — it removes the old one before its fetch and inserts the new one after"
status: "fixed"
owner: user:edwin
created: 2026-08-13
updated: 2026-08-13
source: ["Edwin 2026-08-13: 'Sometimes the since you looked section gets repeated. For instance on the your-health overview page now.'"]
severity: medium
component: desktop-renderer
parent: ""
related: ["[[FEAT-0071]]", "[[DES-0008-The-Returning-Human]]", "[[TASK-0314]]"]
tests: []
---

# The since-you-looked band can mount twice

## Problem

`mountDigestBand()` clears the previous band on its **first** line and inserts the new one **after** an `await fetch(…)`. Two calls that overlap therefore both find nothing to clear, and both prepend:

```
A: remove (nothing there) → await fetch …
B: remove (nothing there) → await fetch …
A: prepend band ①
B: prepend band ②
```

Reported on `your-health`'s overview, which is a workspace whose sidecar answers slowly enough for the window to open.

## Why it happens at all

The dedupe and the insert are separated by the one thing that makes them race — the network. It is the same shape as [[TASK-0187]]'s PTY identity guard (*"node-pty's `onExit` is async — it can fire AFTER the fresh record is installed"*) and as the comment at `applyFleetHealthPayload` about data arriving after the surface that needs it has painted. **Third occurrence of that family in this file**, and the first that duplicates rather than drops.

## Expected

One band, whatever the call pattern. A second mount that starts while the first is in flight should win outright, not stack.

## Actual

Two identical bands, one above the other, until the next full overview render.

## Fix shape

A generation token: capture a counter on entry, and after the await, bail if a newer call has started. The winner then clears and inserts as one step — with the clear moved **after** the fetch, so the old band survives until there is something to replace it with, rather than blinking out during every refresh.

This is a stale-result guard, not a lock: the last call to start is the one whose data is freshest, so it is the one that should paint.

## Fixed — 2026-08-13

A generation token. Every mount takes a number on entry; after the fetch, a call that has been overtaken returns rather than painting. The winner clears and inserts as one step, and the clear moved **after** the fetch — so the band survives until there is something to replace it with instead of blinking out on each refresh.

**Demonstrated rather than argued**, in the running app on `your-health`:

- the pre-fix shape — clear, `await fetch`, prepend — run five times concurrently: **5 elements**
- the fixed `mountDigestBand`, five concurrent calls: **1 band**

The second reading is the fix working; the first is why it was needed, reproduced with the same async step in the same page rather than reasoned about.
