---
type: "[[feature]]"
id: FEAT-0015
aliases: ["FEAT-0015"]
title: "Cockpit IA v2 — workspace mini-rail, modes-on-top toolbar, per-workspace terminal"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
goal: "Second-pass IA fix: pull workspaces to a Discord-style mini-rail on the far left, surface nav modes as a horizontal toolbar above the in-workspace nav, give every workspace its own persistent terminal session, plus two bug fixes (light-theme override + Cmd+P selection)."
related: ["[[FEAT-0014-Cockpit-IA-Rework]]", "[[FEAT-0009-Native-Shell-Layout]]"]
requirements: []
tasks: ["[[TASK-0100]]", "[[TASK-0101]]", "[[TASK-0102]]", "[[TASK-0103]]", "[[TASK-0104]]", "[[TASK-0105]]"]
release: ""
tests: []
---

# Cockpit IA v2

## Goal

FEAT-0014 landed workspace tabs across the top, mode icons on a 52 px
left ribbon, and a full item-render port. User feedback flagged
three things to re-shape:

1. **Workspaces on top didn't land.** Tabs ate the prime horizontal
   strip and forced workspace names through a narrow chrome. Move
   to a Discord/Slack-style **mini-rail on the far left** instead.
2. **Nav modes belong above the in-workspace nav, not on a side
   ribbon.** Horizontal toolbar with the 5 mode icons + hide-completed
   toggle + left-pane collapse on the right edge.
3. **Terminals must be per-workspace.** A single global terminal
   forces the user to lose their REPL on every switch. Each
   workspace owns its own PTY; the pane swaps content with the
   active workspace.

Plus two bugs from user testing:
- Light theme doesn't override OS dark-mode (`renderer.css` reads
  `prefers-color-scheme` rather than `[data-theme]`).
- Cmd+P palette shows results but clicks don't navigate
  (mouseenter re-render destroys the LI between mousedown and
  mouseup, so the browser never fires `click`).

## Scope

### In scope

- **Mini-rail (TASK-0100).** ~40 px column on the far left. Square
  per workspace showing first initial + an agent-state dot. Click
  switches; `+` adds (rescan + picker); right-click context menu.
- **Modes toolbar (TASK-0101).** Horizontal strip above `#ws-nav`.
  Icon-only mode buttons + hide-completed toggle, all left-grouped;
  left-pane collapse on the far right (adjacent to the nav splitter).
- **Platform pill row (TASK-0102).** Below the modes toolbar.
  Shown only when `available_platforms.length > 1` (per the
  existing `/api/cockpit/nav` payload).
- **Right-pane inner-edge collapse (TASK-0103).** Move the
  collapse caret from the right-pane header to the left edge of
  the pane, adjacent to splitter-right. Symmetric with the
  left-pane affordance.
- **Per-workspace terminal (TASK-0104).** Each workspace has its
  own terminal session(s). The terminal pane swaps content with
  the active workspace. PTY persists across switches. `+` button
  in the terminal pane adds a session.
- **Bug fixes (TASK-0105).** renderer.css drives chrome from
  `[data-theme="dark"]` (matches base.css convention).
  `renderQuickResults` mouseenter no longer re-renders.

### Out of scope

- The earlier mode ribbon (52 px left strip) goes away entirely.
  Reserved Search / Pinned / Graph icons move to the modes
  toolbar as future entries (still disabled) or are deferred.
- Drag-to-reorder workspaces in the mini-rail — follow-up.
- Status bar at the bottom (FEAT-0009) and column splitters stay
  unchanged.

## Acceptance

- Workspaces appear as colored squares in a ~40 px far-left rail.
  Switching is one click.
- Above the in-workspace nav: a horizontal row of icon-only mode
  buttons. To the right: hide-completed icon + a collapse caret
  immediately left of the nav-splitter.
- Right-pane collapse caret sits at the left edge of the right
  pane, immediately right of splitter-right.
- Picking a workspace shows that workspace's terminal session(s)
  in the terminal pane. Switching away and back resumes the same
  PTY; output written while away is buffered.
- The "Lt" / "Dk" buttons in the status footer override the OS
  setting in both directions.
- Cmd+P → type → Enter or click → centre pane navigates.

## Links
- Supersedes the workspace+modes parts of [[FEAT-0014-Cockpit-IA-Rework]]
- Phase: [[PHASE-006-Native-Cockpit-UI]]
