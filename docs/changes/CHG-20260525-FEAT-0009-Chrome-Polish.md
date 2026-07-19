---
type: "[[change]]"
id: CHG-20260525-FEAT-0009-Chrome-Polish
aliases: ["CHG-20260525-FEAT-0009-Chrome-Polish"]
title: "FEAT-0009 done: status footer, theme picker, resizable column splitters"
status: merged
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[TASK-0094]]", "[[TASK-0095]]", "[[TASK-0096]]"]
commit: ""
pr: ""
impacts:
  - "desktop/src/renderer/index.html (footer cells + splitter strips)"
  - "desktop/src/renderer/renderer.ts (status-footer helpers, theme pref, splitter drag)"
  - "desktop/src/renderer/renderer.css (status-footer + splitter + theme-button styles, CSS-var-driven grid template)"
issues: []
features: ["[[FEAT-0009-Native-Shell-Layout]]"]
related: ["[[FEAT-0010-Native-Nav-Right-Pane]]", "[[FEAT-0011-Native-Center-Pane]]", "[[FEAT-0012-Native-UX]]"]
---

# FEAT-0009 chrome polish (status footer · theme · splitters)

## Summary

Closes the FEAT-0009 backlog. The native shell now has a persistent
status footer, an explicit theme picker, and drag-to-resize splitters
between the columns — the three remaining "make it feel like an IDE"
items after the hiddenInset title bar landed in CHG-20260525-Native-UX-Wins.

| Task | Capability |
|---|---|
| **TASK-0094** | **Status footer** — sidecar dot (idle/spawning/ready/failed/exited), current note rel-path (click to copy), agent-state dot (busy/waiting/error/done) live-updated via SSE for the active workspace. |
| **TASK-0095** | **Theme picker** — three-pill `Sys / Lt / Dk` toggle in the footer; pref persisted at `cockpit:theme`; system mode delegates to `prefers-color-scheme`. |
| **TASK-0096** | **Resizable splitters** — 6 px draggable strips on the right edge of the in-workspace nav and the left edge of the right pane. CSS-var-driven grid template (`--nav-width` / `--right-width`); widths persisted to `localStorage`. Clamped to sensible min/max. |

## Design notes (worth keeping)

- **Footer cells share a colour vocabulary** with the rail dots
  (TASK-0082). Same `--status-done` / `--severity-medium` /
  `--severity-critical` tokens, same `ws-waiting-pulse` keyframe.
  When `waiting`, both the rail pill *and* the footer agent dot
  pulse — a single visual idiom for "the agent wants you back."

- **Theme pref vs. system:** the renderer keeps `themePref` as the
  canonical store; `applyTheme()` is the only thing that touches
  `document.documentElement.dataset.theme`. The system branch attaches
  a `prefers-color-scheme` listener once at boot; explicit branches
  set the attribute directly. Switching to `Sys` re-evaluates the
  current media-query value, so the toggle is reversible.

- **Splitter mechanics:** kept the existing 4-column grid intact
  (`52px <nav> 1fr <right>`) and replaced the literal column widths
  with CSS variables. The drag handler reads `getComputedStyle` on
  mousedown (so the cursor delta is stable even outside the
  splitter), then calls `setProperty` per mousemove. Cleaner than
  introducing two extra "gutter" grid columns just to hold the
  drag handle.

- **Right splitter when right pane is collapsed:** hidden via
  `.app.right-collapsed .splitter-right { display: none }`. No
  special-casing in JS — if the pane isn't visible, the splitter
  isn't either.

- **Click-to-copy path:** uses `navigator.clipboard.writeText` and
  flashes the existing `#status-bar` toast. The path field's
  `max-width: 40vw` + ellipsis means it never pushes the theme
  buttons off-screen even with deeply nested notes.

## Documentation Coverage
- features: FEAT-0009 → `done` (4/4 tasks done — TASK-0093 from the
  earlier UX-wins push, TASK-0094..0096 in this push).
- requirements: not-applicable
- tasks: TASK-0094, TASK-0095, TASK-0096 → `done`
- issues: not-applicable
- tests: not-applicable (pure renderer-side chrome; no pytest
  target. Manual smoke per task in the renderer.)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: tasks_done 93 → 96 (+3 done); FEAT-0009 → done;
  features_done 6 → 7; focus updated.
