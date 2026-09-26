---
type: "[[issue]]"
id: ISS-0044
aliases: ["ISS-0044"]
title: "A framed design could not be scrolled, sat light in a dark cockpit, and had no room around it"
status: fixed
severity: medium
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["user report 2026-07-28"]
related: ["[[ISS-0039-Nested-Scrollbars-On-The-Design-Surface]]", "[[ISS-0043-Sandboxed-Artifact-Cannot-Read-CSS]]", "[[TASK-0226-App-Shell-Design-Layout]]"]
fixed_by: []
---

# Three reports, one framed design

## 1. No way to scroll the document

A declared viewport of 900px made the frame 900px tall inside a stage of about 767px, so the **stage** became a scroller with roughly 130px of travel. Centred in a 1356px pane, that left ~450px of dead stage either side of the design: the wheel landed there, moved the stage a few pixels, and stopped. The artifact scrolled only when the pointer was directly over it.

Measured in a bare frame first, where scrolling worked — which is what made it a *chrome* problem rather than a frame problem.

**Fix:** a framed design is **scaled to fit** the stage instead of overflowing it, and the framed stage is no longer a scroller at all. Scaling preserves what framing is for — the artifact still lays out at its declared width, so a 420px design is still a 420px design — and only the presentation shrinks, only when it must.

## 2. Light page in a dark cockpit

The artifact is sandboxed with an **opaque origin** ([[ISS-0043]]): it can reach neither the parent nor `localStorage`, so there was no channel by which it could know the app's theme. The theme now travels in the asset URL. An artifact may honour or ignore it — a design mock that is deliberately light stays light; the style guide, which documents both schemes, follows the app.

Turning that on immediately exposed a second defect: the guide read both palettes through a **probe element**, and a probe cannot escape the document's own theme, because light is the `:root` default and only `[data-theme="dark"]` exists. With the app dark, the LIGHT column silently showed dark values. It now reads the **declarations**, which is theme-independent — and, being a cascade walk, also surfaces the shell overriding `base.css` ([[ISS-0042]]).

A third fell out of that: `base.css` writes its dark block as a bare `[data-theme="dark"]` while `renderer.css` writes `:root[data-theme="dark"]`. Requiring the `:root` skipped base.css's dark palette entirely, so the dark column showed light values for every token the shell does not override.

## 3. Squashed

The app-shell layout ([[TASK-0226]]) had tightened the page against its chrome. A design needs room around it to read as a design rather than as part of the application: page padding restored, and the guide's own body padding widened.
