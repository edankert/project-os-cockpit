---
type: "[[issue]]"
id: ISS-0047
aliases: ["ISS-0047"]
title: "Re-injected app stylesheets landed after the artifact's own reset and outranked it"
status: fixed
severity: high
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["user report 2026-07-28: 'Still the same! This is in the Electron App, where are you checking'"]
related: ["[[ISS-0043-Sandboxed-Artifact-Cannot-Read-CSS]]", "[[ISS-0046-Artifact-Inherits-The-App-Shell-Body]]", "[[TASK-0228-Living-Style-Guide]]"]
fixed_by: []
---

# One fix undid another

## What it was

[[ISS-0046]] fixed the artifact inheriting the app-shell body by resetting `html`/`body` in the page's own `<style>` — relying on plain source order, since the `<link>` elements come first.

[[ISS-0043]]'s repair then **fetched those stylesheets and appended them to `<head>` as inline `<style>` elements** — after the page's own. So `body { overflow: hidden }` landed *after* the reset written to undo it, won on source order, and the page could not scroll. Measured in the running app:

```
sheets:  base.css:-1  cockpit.css:-1  renderer.css:-1     ← blocked, opaque origin
         inline:26                                        ← the page's own reset
         inline:141  inline:252  inline:842               ← re-injected, and LAST
body:    overflow hidden · padding 0px · height 570px · content 4597px
```

Both of Edwin's symptoms, again, from the interaction of two fixes that were each correct alone.

## Fix

Re-injected sheets are inserted **before** the page's own `<style id="own-styles">`, never appended. Borrowed styles first, author styles last — the ordering every stylesheet already assumes.

Verified in the Electron app: `overflow: visible`, padding `28px 34px 72px`, body 4705px in a 570px viewport, `scrollY` 0 → 4135 reaching the Motion and Accessibility sections.

## Why three attempts missed it

Every earlier check ran somewhere the re-injection **never happens**: opened directly in a browser tab, the stylesheets are same-origin, `cssRules` works, nothing is re-injected, and the reset stays last. The failure existed only in the sandboxed path — which is the only path the app uses.

Edwin, after the third attempt: *"This is in the Electron App, where are you checking, why not just check the electron app directly?"* Correct, and the answer was that I had no way to — so I built one rather than continuing to reason from adjacent contexts. `scratchpad/cdp.py` is a dependency-free DevTools Protocol client: launch Electron with `--remote-debugging-port`, attach to the renderer *and to the design frame as its own target*, and measure what is actually on screen. The bug was visible in the first measurement.

**The rule this establishes:** the design frame's runtime is sandboxed, opaque-origin and cross-process. Any check of an artifact conducted outside it is checking a different thing. Three separate bugs ([[ISS-0043]], [[ISS-0046]], this one) hid in exactly that gap.
