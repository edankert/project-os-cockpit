---
type: "[[plan]]"
id: PLAN-FEAT-0010
aliases: ["PLAN-FEAT-0010"]
title: "Plan: Native nav surface (workspace rail + in-workspace nav + right pane)"
status: active
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
implements: ["[[FEAT-0010-Native-Nav-Right-Pane]]"]
related: ["[[FEAT-0013-Agent-State-Signal]]", "[[FEAT-0008-Cockpit-API-Hardening]]", "[[FEAT-0011-Native-Center-Pane]]", "[[PHASE-006-Native-Cockpit-UI]]"]
---

# Plan — FEAT-0010 Native nav surface

## Design decision: activity-bar over tabs

We considered tabs across the top of the stage (browser-like, one tab
per workspace). Rejected because:
- The agent-state indicator wants to be a peripheral glance, not in the
  centre of your attention — a left-edge rail of small dots reads
  better as "ambient status" than tabs that fight for hierarchy with
  the doc title.
- IDE peers (VS Code, Cursor, Antigravity) all use the activity-bar
  shape; users opening the cockpit have the muscle memory.
- Tabs don't scale gracefully past ~6 workspaces without horizontal
  scrolling or overflow menus; the rail handles 20+ trivially.

Layout (4 columns):

```
┌────┬──────────┬──────────────────────────────┬──────────────┐
│ rail│ in-ws nav│  centre (doc-view, FEAT-0011) │  right pane  │
│ 52px│ 240px    │  1fr (flex)                  │  240px       │
└─────┴──────────┴──────────────────────────────┴──────────────┘
```

Right pane is **collapsible** (default off in v1) so the narrow-window
case isn't cramped.

## Delivery sequence

1. **[[TASK-0080]] — Activity-bar layout shell.** Reshape `.app`'s
   grid from `240px 1fr` to `52px 240px 1fr [right-pane]`. Add empty
   `<aside id="rail">` and `<aside id="ws-nav">` siblings; move
   workspace logic out of `.switcher` into `#rail`; placeholder
   content in `#ws-nav`. Right-pane column reserved but not built
   yet. CSS only — no behaviour changes beyond placement.

2. **[[TASK-0081]] — Agent-state file persistence (amends FEAT-0013).**
   `CockpitState.record_agent_state` ALSO writes to
   `<project-root>/.cockpit/agent-state.json`. The file holds the
   latest state. This is the data the rail polls — sidecar-lifecycle-
   independent. Tested in `test_agent_state.py` (new case).

3. **[[TASK-0082]] — Workspace rail rendering + dot polling.** Each
   workspace becomes a clickable icon (first letter + colored ring).
   For every discovered workspace, renderer polls
   `<root>/.cockpit/agent-state.json` every 5 s and paints the dot.
   Active workspace gets an accent. Hover = tooltip with name +
   last state message. Polling lives in main (filesystem access) and
   IPCs the per-workspace state to the renderer.

4. **[[TASK-0083]] — In-workspace nav framework + Features-by-phase
   mode.** `<aside id="ws-nav">` becomes the second column. Fetches
   `/api/cockpit/nav?mode=features`, renders feature rows grouped by
   phase, status chips, type-aware group icons, requirement nesting
   (collapsed by default). Click a feature → centre pane navigates.
   Active note's row gets the cockpit-focus highlight.

5. **[[TASK-0084]] — Other nav modes + mode toggle.** Adds
   Tasks / Issues / Library / Recent. A small pill row at the top
   of `#ws-nav` toggles modes. Hybrid Changes buckets for Library.
   Pin button for Library entries. Platform filter
   (auto-discovered).

6. **[[TASK-0085]] — Right pane (linked + backlinks).** New
   `<aside id="right-pane">` column. Fetches
   `/api/cockpit/context?this=<rel>` whenever centre nav changes.
   Renders outbound (`linked`) + inbound-only (`backlinks`) groups.
   Right-pane toggle button (chevron) in the title bar collapses
   the column; state persisted to userData. Active note severity /
   status chip in the header.

7. **[[TASK-0086]] — SSE soft-reload + tab heartbeat + drop Browse
   panel.** Renderer subscribes to the active sidecar's `/_events`
   (already done for agent-focus); on `file-changed` debounces a
   re-fetch of the active mode + right pane + centre. Tab-state
   heartbeat POSTs `/api/cockpit/tab-state` every 15 s with a
   renderer-local `tab_id`. The "Browse this workspace" panel from
   FEAT-0011's READMEs goes away (real nav supersedes it).

## Dependencies

- **Hard:** FEAT-0013 (the state pipe) — already shipped. TASK-0081
  amends it with the file-write so polling is possible.
- **Hard:** FEAT-0008 (`/api/cockpit/nav` + `/api/cockpit/context`
  contract) — shipped.
- **Hard:** FEAT-0011 (centre pane navigateTo) — shipped. Each nav
  row click drives that.
- **Soft:** FEAT-0009 (title bar / theme) — independent. The
  right-pane toggle in TASK-0085 anticipates a title-bar slot but
  doesn't require it (button can sit in the in-workspace nav header
  for v1).

## Sequencing notes

- TASK-0080 + TASK-0081 are independent and small. Do them in
  parallel mentally; commit 0080 first so 0082 has a column to render
  into.
- TASK-0082 unblocks the rail demo. After it lands, the user sees
  agent-state dots on multiple workspaces simultaneously — the
  visible payoff of FEAT-0013.
- TASK-0083..0085 build the conventional in-workspace experience.
  Each ports a specific mode-1 behaviour; minimal new design.
- TASK-0086 is the polish + cleanup. Safe to scope-trim if energy
  runs out (the soft-reload is a regression-protection layer; without
  it, user manually clicks "Rescan" or reloads the window).

## Natural review checkpoints

- **After TASK-0082**: rail with live dots works. Demo-able. Likely
  the most novel part to verify visually.
- **After TASK-0084**: full in-workspace nav. The Browse panel can
  go now (or wait for 0086).
- **After TASK-0085**: right pane lands. FEAT-0010 functionally
  complete pending soft-reload polish.

## Open questions to pin during implementation

- **Polling interval for dot data** — 5 s feels right; configurable
  via constant. Land-time.
- **Rail icon shape** — single letter on a colored chip, or
  workspace short-name truncated to fit? Letter for v1; the
  tooltip carries the full name. Decided in TASK-0082.
- **`.cockpit/agent-state.json` format** — same shape as the SSE
  payload (`{state, ts, target?, agent?, message?}`). Decided in
  TASK-0081.
- **Right-pane default state** — collapsed or expanded? Mode 1 has
  it expanded; on narrow desktops we may want collapsed by default.
  Decided in TASK-0085.
- **Mode-toggle UX** — pill row vs dropdown vs left-rail submenu.
  Pill row (like mode 1's `.cockpit-mode-tabs`) is simplest. Decided
  in TASK-0084.

## Out of plan

- Multi-window — FEAT-0012.
- Cmd+P quick-switch over notes — FEAT-0012.
- OS notifications when a workspace flips to `waiting` — FEAT-0012.
- Drag-to-reorder workspaces in the rail. Maybe one day; not v1.
- Inline note editing.
- Per-workspace persistent UI state (which mode was last selected
  per workspace) — could be FEAT-0012 territory; v1 uses a single
  global last-selected mode.
