---
type: "[[change]]"
id: CHG-20260525-Overview-Dashboard
aliases: ["CHG-20260525-Overview-Dashboard"]
title: "Overview dashboard + dashboard-adjacent polish (identicons, colour swatches, top-bar back/forward + search + star, paste-a-path, header alignment)"
status: merged
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[TASK-0109]]", "[[TASK-0110]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/cockpit.py (stats_payload — hero / status_mix / phases / weekly histogram / recent CHGs)"
  - "src/project_os_cockpit/server.py (/api/cockpit/stats route)"
  - "desktop/src/renderer/renderer.ts (overview NavMode, loadOverview + renderOverview + buildHero/buildPhaseSection/buildBottomGrid/buildRecentFeed; identicon SVG + colour swatches + emoji icon; top-bar back/forward/search/star; paint helpers for star + history; flattenNavItems walks subgroups + items without ids)"
  - "desktop/src/renderer/renderer.css (.ov-* dashboard tiles; identicon + emoji visuals; top-bar nav-btn / search / star styles; --pane-header-height shared 44 px)"
  - "desktop/src/renderer/index.html (top-bar back / forward / search / star; project-header icon picker — emoji + 8 swatches; overview mode icon)"
  - "desktop/src/main.ts (app.setPath('userData', …project-os-cockpit-desktop) so renaming app.name doesn't move the data dir; app:revealInFinder IPC)"
  - "desktop/src/ipc/workspaces.ts (workspaces:pickIcon accepts workspaceId → opens at project root; userEmoji / userColor in patch)"
  - "desktop/src/types.ts (Workspace.userEmoji + userColor)"
issues: []
features: ["[[FEAT-0017-Overview-Dashboard]]"]
related: ["[[FEAT-0015-Cockpit-IA-V2]]", "[[FEAT-0016-Project-Management]]"]
---

# Overview dashboard

## Summary

Closes FEAT-0017 — a project-wide stats view in the centre pane — and
bundles all the dashboard-adjacent polish that landed in the same
session.

| Task | Capability |
|---|---|
| **TASK-0109** | **Server `/api/cockpit/stats`.** `stats_payload(index)` aggregates from the live index: hero counts (features / tasks / issues / tests / risks / requirements + last CHG), per-type status mix, per-phase task buckets (done / in-progress / backlog), 13-week activity histogram, and 10 most-recent CHGs. CHG dates parsed straight from the `CHG-YYYYMMDD-…` ID — no extra IO. |
| **TASK-0110** | **Overview mode + dashboard renderer.** `overview` added as the first nav mode (bar-chart icon in the top bar). Selecting it fetches `/api/cockpit/stats` and mounts 4 tiles in the centre pane (hero strip, phase bars, conic-gradient donuts, weekly bar chart + click-to-open recent CHG feed). Clicking a CHG row navigates the centre pane and flips mode back to Features so the nav comes back. |

### Polish landed alongside

- **Identicon fallback** for workspaces without an icon. 5×5 symmetric SVG derived from the workspace id. Tile bg gets a faint matching tint. Replaces the colored-letter fallback.
- **Per-workspace icon overrides**: `userEmoji` (any emoji) + `userColor` (8 preset swatches + "auto"). Highest-priority `userIcon` (uploaded image) still wins. Reset clears all three.
- **Icon picker opens at the project root** — `workspaces:pickIcon` accepts a workspaceId.
- **Reveal in Finder** got a direct IPC (`app:revealInFinder`) instead of routing through the context-menu shim.
- **Top bar additions** (centred between modes and collapse toggles): back / forward chevrons with `disabled` state synced to history, search "input" (button styled as input — click to open ⌘P palette, since macOS native `<select>` can't be cleanly styled), star toggle for pinning the current doc (rail star removed; pin state per-workspace in `cockpit:pinned:<id>`).
- **⌘P paste-a-path now works** — `flattenNavItems` walks `group.subgroups` recursively and keeps items that have only `rel` without an `id`.
- **Pane header alignment** — `--pane-header-height: 44px` applied to project header, find bar, and right-pane Context header so the row-0 strip lines up across panes.
- **TASK-0070 paperwork** — was stale `doing` in SNAPSHOT; flipped to `done` since its work shipped via `CHG-20260525-Native-Center-Pane`.

## Sharp design notes

- **stats_payload is pure aggregation** off the live index — every projection (status mix, phase bucket, weekly histogram) is a single pass through one type's record list. CHG-date parsing is a regex against the note id; if a CHG doesn't follow the `CHG-YYYYMMDD-…` convention it falls back to frontmatter `updated` / `created`.
- **Donut rendering uses `conic-gradient`** instead of SVG arc paths — themes by CSS variables, no chart library, 80 lines of CSS for 4 donuts.
- **Overview mode is a `NavMode`**, not a special case. Branching happens once in `loadWsNav`: if the active mode is `overview`, call `loadOverview` instead of fetching nav data. Keeps the top-bar mode-button machinery simple.
- **Identicon palette** — pure SVG, no PNG generation. Hue derived from a 32-bit FNV-like hash of `workspace.id` so the same project gets the same shape + colour across launches and machines.

## Documentation Coverage
- features: FEAT-0017 → `done` (2/2 tasks done)
- requirements: not-applicable
- tasks: TASK-0109, TASK-0110 → `done`; TASK-0070 paperwork → `done`
- issues: not-applicable
- tests: not-applicable (renderer + main IPC chrome; no pytest)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: tasks_done 108 → 110; features_done 10 → 11; FEAT-0017 → done; focus cleared.
