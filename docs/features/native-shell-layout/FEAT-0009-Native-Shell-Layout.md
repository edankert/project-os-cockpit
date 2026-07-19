---
type: "[[feature]]"
id: FEAT-0009
aliases: ["FEAT-0009"]
title: "Native shell layout (3-pane grid, title bar, theme, status bar)"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
goal: "Own the outer chrome natively. Replace the Python-rendered cockpit shell + iframe with a TypeScript 3-pane grid, resizers, collapse state, hiddenInset title bar with breadcrumb, status bar, and system-theme matching."
related: ["[[FEAT-0007-Desktop-Shell]]", "[[FEAT-0010-Native-Nav-Right-Pane]]", "[[FEAT-0011-Native-Center-Pane]]", "[[PHASE-006-Native-Cockpit-UI]]"]
requirements: []
tasks: []
release: ""
tests: []
---

# Native shell layout

## Goal
The outermost chrome of the cockpit — three panes (left nav · centre
doc · right context), the resizable splitters between them, the
title bar with breadcrumb, the status bar at the bottom, the global
theme — all become first-class TypeScript widgets in the Electron
renderer. The iframe goes away (FEAT-0011 takes over the centre).

## Scope

### In scope
- **3-pane grid** with persisted collapse state for left and right
  panes (today's behaviour, lifted out of `cockpit.css`).
- **Vertical splitters** with drag-to-resize between left/centre and
  centre/right; widths persisted to `userData`.
- **Title bar.** `BrowserWindow({ titleBarStyle: 'hiddenInset' })` on
  macOS so the traffic lights sit inline with our chrome. Use that
  space for: workspace name on the left, breadcrumb path
  (workspace → folder → note) centre, view-toggles on the right
  (pane toggles, theme picker, settings).
- **Status bar.** Bottom strip with: sidecar health, current focus
  source (user vs agent), current note path, save-state indicator
  for interactive checkboxes (FEAT-0011), terminal indicator.
- **Theme.** System / light / dark, persisted; `prefers-color-scheme`
  drives the default. CSS variables follow the same names as the
  existing cockpit (one source of truth so FEAT-0011's mounted
  Markdown body inherits them).
- **Inventory + port** the small visual refinements from
  `cockpit.css` that aren't pane-internal: status palette colours,
  type-aware icons, Obsidian-style tree styling, focus rings, etc.

### Out of scope
- Pane contents — that's FEAT-0010 (left/right) and FEAT-0011
  (centre).
- The bottom terminal panel — already native (TASK-0063).
- Multi-window — that's FEAT-0012.
- Animations beyond simple CSS transitions.

## Acceptance
- The shell launches with the three panes laid out the same as
  today's cockpit, no iframe visible, no Python-rendered HTML on
  screen.
- Drag any splitter; the new width persists across launches.
- Toggle left or right pane collapsed; state persists across
  launches.
- Switch the system theme; the cockpit theme follows within a frame.
- Resize the window from minimum (900×600) to fullscreen; layout
  reflows cleanly.
- Title bar shows `<workspace> · <breadcrumb> · <note title>`; the
  three traffic-light buttons remain accessible and don't overlap.

## Open question for the phase
**Where does the cockpit CSS live now?** Today Python serves
`/_static/cockpit.css`. Three options:

1. **Keep one copy in Python** and have the desktop renderer fetch +
   inject it on launch. Single source of truth; mode 1 unaffected.
2. **Dual copies** (one in Python, one in `desktop/`). Risk of
   drift; explicit sync rule needed.
3. **Move to `desktop/`** and have Python load it from there in mode
   1 (or accept divergent mode-1 styling).

Decide in FEAT-0009's first task. Recommendation: option 1.

## Links
- Replaces the outer chrome that came from [[FEAT-0006-Cockpit-Layout]]
- Pane content owners: [[FEAT-0010-Native-Nav-Right-Pane]], [[FEAT-0011-Native-Center-Pane]]
- Hosting shell: [[FEAT-0007-Desktop-Shell]]
- Phase: [[PHASE-006-Native-Cockpit-UI]]
