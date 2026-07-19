---
type: "[[feature]]"
id: FEAT-0012
aliases: ["FEAT-0012"]
title: "Native UX wins (Cmd+P, Cmd+F, context menus, drag-drop, multi-window, per-workspace state)"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
goal: "The five things only-possible-after-rewrite: Cmd+P quick-switch, Cmd+F find-in-doc, native context menus, drag-and-drop file → note, window state per workspace + multi-window."
related: ["[[FEAT-0009-Native-Shell-Layout]]", "[[FEAT-0010-Native-Nav-Right-Pane]]", "[[FEAT-0011-Native-Center-Pane]]", "[[PHASE-006-Native-Cockpit-UI]]"]
requirements: []
tasks: []
release: ""
tests: []
---

# Native UX wins

## Goal
Ship the things the iframe shape blocked. Each item below is pure
addition — no behaviour from earlier features changes — and each is
individually scope-trimmable if energy runs out.

## Scope

### In scope

**Cmd+P quick-switch:**
- Fuzzy search across all note IDs + titles + filenames in the
  current workspace. Mounted as a centred command-palette overlay.
- Same source data as `/api/cockpit/nav` (no new endpoint needed).
- Enter navigates the centre pane; Esc closes.

**Cmd+F find-in-doc:**
- Native find-bar that searches within the currently-mounted
  Markdown body. Highlights + count + next / previous controls.
- Pure renderer-side; no Python involvement.

**Native context menus:**
- Right-click on a left-pane row → native `Menu.popup()` via IPC:
  *Open in new window*, *Copy ID*, *Copy path*, *Reveal in Finder*,
  *Pin / Unpin*.
- Right-click in centre pane → standard text-selection menu (copy,
  look up, search) plus *Copy link to this note*.

**Drag-and-drop:**
- Drag a `.md` file from Finder onto the cockpit window → if the
  file is inside the current workspace's docs root, navigate to it;
  if outside, surface a toast offering "open the containing repo as
  a workspace."

**Window state per workspace:**
- Extends FEAT-0007's app-wide state to per-workspace bounds keyed
  by `workspaceId`. Last opened workspace wins on first launch.

**Multi-window:**
- `Cmd+N` opens another workspace in a new window.
- Workspaces don't share sidecars across windows (one sidecar per
  window today; keep that).
- Window menu lists all open windows by workspace name.

### Out of scope
- Side-by-side compare view (two notes in one window). Could be a
  follow-up.
- Native tabs in title bar (macOS-style). Maybe in a later phase.
- Tag-based search, full-text search across the index. Different
  scope.
- Plugin / extension API for custom commands.
- Touch Bar support.

## Acceptance
- **Cmd+P**: open palette, type "FEAT-0006", hit Enter → centre
  pane loads that note.
- **Cmd+F**: open find-bar, type query → matches highlighted in
  the rendered note; Enter cycles forward, Shift+Enter back.
- **Right-click** on a nav row → native macOS context menu
  appears (not the Chromium default).
- **Drag** a `.md` from Finder → cockpit navigates (when in
  workspace) or offers to add workspace (when outside).
- **Quit and relaunch** → each workspace opens at the bounds it
  had last time, not the global app default.
- **Cmd+N** opens a second window; pick a different workspace;
  both render independently with separate sidecars.

## Sequence within the feature
The five items are independent. Land in this order to maximise
demo value:
1. Cmd+P (highest user value, smallest dep)
2. Native context menus
3. Cmd+F
4. Multi-window + per-workspace state (together — state
   provisioning happens once windows are plural)
5. Drag-and-drop (smallest payoff; finish line)

## Links
- Hosts: [[FEAT-0009-Native-Shell-Layout]] (chrome) + [[FEAT-0011-Native-Center-Pane]] (find target).
- Quick-switch + nav source: [[FEAT-0010-Native-Nav-Right-Pane]].
- Multi-window extends [[FEAT-0007-Desktop-Shell]]'s single-window model.
- Phase: [[PHASE-006-Native-Cockpit-UI]].
