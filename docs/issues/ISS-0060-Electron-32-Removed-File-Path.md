---
type: "[[issue]]"
id: ISS-0060
aliases: ["ISS-0060"]
title: "Electron 32 removed File.path, so every file drop silently did nothing"
status: fixed
severity: high
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["user report 2026-07-28: 'drop anything there especially screenshots and images but that doesn't seem to work'"]
related: ["[[FEAT-0045-Project-Inbox]]", "[[TASK-0233-Drop-And-Paste-Into-The-Inbox]]"]
fixed_by: []
---

# Drop did nothing, and said nothing

```js
const absPath = (file as File & { path?: string }).path;
if (!absPath) return;          // ← every drop, since Electron 32
```

**Electron 32 removed `File.path`** (deprecated in 30). Confirmed in the running app: `f.path` is `undefined`. So the handler returned before doing anything, with no error, no status message, and no console output.

That broke **two** things, one of them long before the inbox existed:

- Dropping a `.md` stopped navigating — a FEAT-0012 feature, silently dead since the Electron upgrade, and nothing noticed because nothing checks.
- Dropping a screenshot never reached the inbox code at all, which is what Edwin hit within minutes of the feature shipping.

## Fix

`webUtils.getPathForFile` replaces it, and **must be called in the preload** — `webUtils` is not exposed to the renderer, so reading it there returns undefined and reproduces the same silence.

More importantly: **the path is now optional.** Filing into the inbox needs the file's *bytes*, not its location, so a drop with no resolvable path files rather than returning. Requiring a path for something that never needed one is what made this fail closed and silent.

## What I got wrong, precisely

I tested the store endpoint over HTTP, and I tested **paste** in the app by dispatching a synthetic `ClipboardEvent`. I never dispatched a `drop`. So I verified the thing next to the thing Edwin asked for.

That is the same failure as [[ISS-0043]], [[ISS-0046]], [[ISS-0047]] and [[ISS-0058]] — *verified in a context the app never uses* — and it is now the fifth. The tell was available in one line: dispatch a `DragEvent` instead of a `ClipboardEvent`, which is what finally proved it.

## The second defect, found while fixing the first

The new screenshot capture reported **any** missing file as `cancelled: true`, because `screencapture` exits 0 when the user presses Escape. But it exits **non-zero with a message** when it genuinely fails — verified: `could not create image from rect`, exit 1.

So a macOS **Screen Recording** denial — the first thing anyone hits on a new machine — would have told Edwin he cancelled something he never started. There are three outcomes, not two, and the error now names the permission and where to grant it.
