---
type: "[[change]]"
id: CHG-20260525-Cockpit-IA-Rework
aliases: ["CHG-20260525-Cockpit-IA-Rework"]
title: "Cockpit IA rework: workspace tabs, mode ribbon, full item-render port"
status: merged
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[TASK-0097]]", "[[TASK-0098]]", "[[TASK-0099]]"]
commit: ""
pr: ""
impacts:
  - "desktop/src/renderer/index.html (tab strip, mode ribbon, splitters, status footer wired into DOM at last)"
  - "desktop/src/renderer/renderer.css (grid-template-areas with tabs+rail+nav+stage+right+footer; tab + ribbon styles; old workspace-list + ws-nav-modes styles deleted)"
  - "desktop/src/renderer/renderer.ts (renderTabs replaces renderList; ribbon SVG injection + click wiring; full item-render port from cockpit.js — TYPE_ICONS / GROUP_ICONS / typeIcon / groupIcon / pickItemRenderer + 4 layouts; right pane reuses navItem)"
issues: []
features: ["[[FEAT-0014-Cockpit-IA-Rework]]"]
related: ["[[FEAT-0009-Native-Shell-Layout]]", "[[FEAT-0010-Native-Nav-Right-Pane]]"]
---

# Cockpit IA rework

## Summary

Closes FEAT-0014. Fixes three usability regressions from the earlier
native-shell push:

| Task | Capability |
|---|---|
| **TASK-0097** | **Workspace tabs.** Tab strip under the hiddenInset title bar. Each tab has a name + agent-state dot (pulses on `waiting`). Click switches; middle-click closes; `Cmd+1..9` jumps to tab N; `Cmd+W` closes the active tab. `+` rescans (full picker is a follow-up). |
| **TASK-0098** | **Mode ribbon.** The 52 px left column is now a vertical icon ribbon: 5 nav modes on top (Features/Tasks/Issues/Library/Recent), an extras section below (Search/Pinned/Graph — disabled placeholders for follow-ups), and a Tools section at the bottom (Terminal active, Settings disabled). Active mode highlighted with accent-soft background + accent left-bar. |
| **TASK-0099** | **Item-render port.** `renderer.ts` now emits the same DOM `cockpit.js` does — `.nav-item`, four layout variants (`stacked` / `compact` / `nested` / nested-children), type icons, group icons, status chip palette, subtitle rows. Right pane reuses `navItem` so linked + backlinks rows match nav rows. |

Plus: the status footer + splitter divs (TASK-0094/0095/0096) that
were committed against the previous push **but never actually landed
in `index.html`** are now present. Sidecar dot, click-to-copy path,
agent dot, theme picker, and column splitters are all live.

## Design notes (worth keeping)

- **cockpit.css was already loaded.** `copy-assets.mjs` ships
  `base.css` + `cockpit.css` to `dist/renderer/` and `index.html`
  links both. The TS port only needed to emit matching DOM —
  `.nav-item`, `.type-icon[data-type]`, `.status-chip[data-status]`
  etc. — for the existing cockpit.css selectors to style everything.
  Saved ~150 lines of CSS that would have drifted from the upstream.

- **Grid template areas.** `.app` switched from a single-row 4-column
  grid to a 3-row × 4-column areas grid:
  ```
  "tabs   tabs  tabs  tabs"
  "rail   nav   stage right"
  "footer footer footer footer"
  ```
  Cleaner than nesting + means the splitter widths live on the
  middle row only.

- **Workspace tabs vs rail.** The rail still exists — it's the
  *mode* rail now, not the *workspace* rail. Workspace pills
  disappeared entirely (no more letter-pill UX); tabs are the
  switcher. Agent-state pulse moved from the pill dot to the tab
  dot (same `ws-waiting-pulse` keyframe).

- **Ribbon highlighting.** Active mode gets an accent-coloured
  3-px stripe on its left edge (via `::before`) + accent-soft
  background. Closer to JetBrains / VS Code than the previous
  outlined-pill look.

- **Right-pane items now match nav items.** The old
  `right-pane-group ul/li` mini-renderer is gone. Linked +
  backlinks rows are full `.nav-item`s — same icons, same chips,
  same hover affordance. Slightly more vertical space per row in
  exchange for visual coherence.

- **What's intentionally still simple:** the `+` button rescans
  rather than opening a true workspace picker. Drag-to-reorder
  tabs is a deferred follow-up. Both are noted in TASK-0097.

## Documentation Coverage
- features: FEAT-0014 → `done` (3/3 tasks done).
- requirements: not-applicable
- tasks: TASK-0097, TASK-0098, TASK-0099 → `done`
- issues: not-applicable
- tests: not-applicable (renderer-side chrome; no pytest target)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: tasks_done 96 → 99; features_done 7 → 8; FEAT-0014 →
  done; focus cleared.
