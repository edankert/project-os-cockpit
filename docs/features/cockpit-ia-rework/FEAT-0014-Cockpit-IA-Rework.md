---
type: "[[feature]]"
id: FEAT-0014
aliases: ["FEAT-0014"]
title: "Cockpit IA rework — workspace tabs, mode ribbon, item-render port"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
goal: "Replace the workspace pill rail with tabs, move nav-mode switching to an icon ribbon on the left, and port the Python cockpit's polished item-rendering conventions to the native renderer."
related: ["[[FEAT-0007-Desktop-Shell]]", "[[FEAT-0009-Native-Shell-Layout]]", "[[FEAT-0010-Native-Nav-Right-Pane]]", "[[PHASE-006-Native-Cockpit-UI]]"]
requirements: []
tasks: ["[[TASK-0097]]", "[[TASK-0098]]", "[[TASK-0099]]"]
release: ""
tests: []
---

# Cockpit IA rework

## Goal

Fix three usability regressions surfaced after the FEAT-0009 chrome
polish landed:

1. **Workspace switching as a vertical pill rail** was the wrong
   pattern — it wastes the prime left column and doesn't scale.
   Tabs at the top are the conventional pattern (Chrome / VS Code /
   Obsidian-with-tabs).
2. **Nav modes (Features / Tasks / Issues / Library / Recent) live
   inside the panel as text buttons**, burning ~32 px of vertical
   space and leaving no room for Obsidian-style extras (search,
   pinned, graph). They should be an icon ribbon on the *outside*
   of the panel.
3. **Native nav + right-pane items lost the polish** of the Python
   cockpit when ported to TS: only 1 of the 4 item layouts made it
   across, no type icons, no group icons, no subtitle rows. The
   gap is mechanical — the work to lift those renderers was just
   skipped.

## Scope

### In scope

- **Workspace tabs.** Tab strip under the hiddenInset title bar.
  Each tab: workspace name + agent-state dot (pulses on `waiting`).
  Click switches; middle-click closes; drag to reorder; `+` opens
  the workspace picker. `Cmd+1..9` jumps to tab N. Multi-window
  stays — each window owns its own tab set.

- **Mode ribbon (52 px left strip).** Vertical icons, top-down:
  - **Top section:** Features, Tasks, Issues, Library, Recent.
  - **Bottom section (reserved):** Search, Pinned, Graph view,
    Settings — wired empty/disabled now, filled in over
    follow-ups.

- **Item-render port (full).** Lift the four layout variants from
  `cockpit.js` (`stacked` / `compact` / `nested` / `nested-children`)
  into TS helpers. Pick per-group via the existing
  `group.item_layout` field on `/api/cockpit/nav`. Include type
  icons, group icons, status chip palette, and subtitle rows.
  Right pane reuses the same `renderItem(item, layout)` so linked
  + backlinks rows match nav rows.

- **CSS port.** Copy the relevant token-driven selectors from
  `cockpit.css` into `renderer.css`. They depend on existing
  `--type-*` / `--status-*` / `--severity-*` variables (already
  defined in `base.css`), so the palette stays a single source of
  truth.

### Out of scope

- New nav modes / new ribbon icons beyond the 5 existing modes.
  The bottom section is reserved but empty until follow-ups.
- A workspace-picker overlay redesign — the `+` opens the existing
  picker.
- Graph view, full-text search, or any of the "Obsidian-style
  extras" — those need their own features.

## Acceptance

- Top of the window shows a tab strip; no left-rail workspace
  pills remain.
- Left 52 px column is the mode ribbon; clicking any icon switches
  the nav panel mode; tooltips on hover; bottom-section icons are
  visible but inactive.
- Nav items render with type icons, status chips, and (where the
  layout calls for it) subtitle rows — visually matching the
  Python cockpit.
- Right-pane linked + backlinks rows render with the same item
  component as nav rows.
- Agent-state dot moves from the rail pill to the tab; the pulse
  on `waiting` still works.

## Links
- Replaces the workspace-rail half of [[FEAT-0010-Native-Nav-Right-Pane]]
- Builds on [[FEAT-0009-Native-Shell-Layout]] (status footer / splitters / theme stay)
- Phase: [[PHASE-006-Native-Cockpit-UI]]
