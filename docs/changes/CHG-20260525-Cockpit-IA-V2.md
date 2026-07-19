---
type: "[[change]]"
id: CHG-20260525-Cockpit-IA-V2
aliases: ["CHG-20260525-Cockpit-IA-V2"]
title: "Cockpit IA v2: Discord-style rail, modes-on-top, per-workspace terminal, palette/theme bug fixes, project header, custom combobox"
status: merged
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[TASK-0100]]", "[[TASK-0101]]", "[[TASK-0102]]", "[[TASK-0103]]", "[[TASK-0104]]", "[[TASK-0105]]"]
commit: ""
pr: ""
impacts:
  - "desktop/src/renderer/index.html (mini-rail, top-bar layout, project header, custom combobox, terminal+settings on rail)"
  - "desktop/src/renderer/renderer.css (grid template areas, mini-rail, splitter-aligned collapse buttons, edge-to-edge platform combobox, theme-aware scrollbars + terminal pane)"
  - "desktop/src/renderer/renderer.ts (workspace mini-rail render, top-bar wiring, applyLeftPaneState/applyRightPaneState, panel-left/right Lucide icons, hide-completed filter, terminal theme swap, attachTerminalTo, project header, hash-derived workspace colour, custom combobox dropdown)"
  - "desktop/src/ipc/terminal.ts (workspace-keyed PTY map, 256 KB backlog per PTY, attach/spawn/data/exit IPC carries workspaceId)"
  - "desktop/src/preload.ts (terminal API gains workspaceId on every call, attach method exposed)"
  - "desktop/src/ipc/workspaces.ts (icon probing on discovery, backfill on stored load)"
  - "desktop/src/types.ts (Workspace.icon optional data-URI)"
issues: []
features: ["[[FEAT-0015-Cockpit-IA-V2]]"]
related: ["[[FEAT-0014-Cockpit-IA-Rework]]", "[[FEAT-0009-Native-Shell-Layout]]"]
---

# Cockpit IA v2

## Summary

Closes FEAT-0015. Re-shaped the workspace + nav layout twice during
user testing — landed on a Discord-style workspace rail on the far
left, a window-wide top bar with mode icons + splitter-aligned
collapse buttons, and per-workspace terminal sessions in main.

| Task | Capability |
|---|---|
| **TASK-0100** | **Workspace mini-rail.** 44 px far-left column. Square per workspace (icon from project dir if found, otherwise hash-tinted initial), agent-state dot overlay, `+` to rescan, terminal + settings tools at the bottom. Replaces the top tab strip from FEAT-0014. |
| **TASK-0101** | **Top-bar toolbar.** Window-wide row above the panes: traffic-light reserve → mode icons → spacer → left-pane collapse (anchored to the nav splitter, overlays modes when the nav is dragged narrow) → right-pane collapse (anchored to the right splitter). Lucide `panel-left/right` SVGs with OPEN/CLOSE variants. |
| **TASK-0102** | **Platform combobox.** Edge-to-edge strip under the project header. Custom `<div role="combobox">` (macOS Electron refuses to strip native chrome from `<select>`/`<button>`, so we built our own). Hidden when only one platform. |
| **TASK-0103** | **Right-pane collapse on the inner edge** — moved into the top bar so both collapse buttons sit symmetric next to their splitters. When the right pane is collapsed, its column shrinks to 0 and the toggle stays visible in the toolbar. |
| **TASK-0104** | **Per-workspace terminal.** `Map<workspaceId, PtyRecord>` in main. PTYs persist across workspace switches; switching the active workspace re-attaches the xterm via `terminal:attach` which replays the 256 KB ring backlog. |
| **TASK-0105** | **Bug fixes.** (a) Light theme override now works: renderer.css's dark colours moved from `@media (prefers-color-scheme: dark)` to `:root[data-theme="dark"]` so explicit `Lt` clicks win over the OS pref. (b) Cmd+P click-to-navigate: removed the mouseenter re-render that was destroying the LI between mousedown and mouseup. |

Plus follow-up polish during the session:
- **Project header** at the top of the in-workspace nav (icon + name).
- **Workspace icons** sourced from `icon.svg/png`, `logo.svg/png`,
  `.cockpit/icon.svg/png`, `public/favicon.*`, `static/favicon.*`,
  `apple-touch-icon.png`, root `favicon.*` (200 KB cap, base64
  data URI).
- **Search + Pinned** placeholders added to the rail tools above
  Terminal + Settings.
- **Hide-completed** actually filters now (mirrors browser cockpit's
  COMPLETED_STATUSES). Visible aria-pressed accent when active.
- **Terminal theme** swaps between `TERMINAL_THEME_LIGHT` and
  `TERMINAL_THEME_DARK` via `term.options.theme` when `applyTheme()`
  fires.
- **Pane scrollbars** use the cockpit-pane class so left/right
  panes get the same thin auto-hiding scrollbars as the centre.

## Sharp design notes

- **macOS native chrome on form controls is sticky.** `<select>` and
  `<button>` both kept their Aqua chrome even with
  `-webkit-appearance: none !important`. Fixed by using
  `<div role="combobox">` for the platform picker.
- **`cockpit.css` class collisions.** Our nav uses class names that
  the browser cockpit also defines (`.platform-bar`, `.nav-item`,
  etc.). Since `cockpit.css` ships into the renderer for the centre
  pane's markdown styles, those rules apply to our chrome too —
  caused the mystery "outer panel" around the combobox. Fix:
  rename native-shell-only widgets with a `ws-` prefix.
- **PTY lifecycle.** PTYs live in main with their own backlog ring
  buffer. The renderer is a view that attaches/detaches as the
  active workspace changes. App-exit handler kills all PTYs;
  workspace close (renderer-only state) does not — the user can
  re-open and resume.

## Open follow-ups (not blocking)
- Multi-session terminal tabs inside a workspace (the picker
  recommended this; v1 ships one session per workspace).
- Wire Pinned (star) icon to an actual pinned-notes feature.
- Settings panel behind the gear icon.

## Documentation Coverage
- features: FEAT-0015 → `done` (6/6 tasks done)
- requirements: not-applicable
- tasks: TASK-0100..0105 → `done`
- issues: not-applicable
- tests: not-applicable (renderer + main process chrome; no pytest)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: tasks_done 99 → 105; features_done 8 → 9; focus cleared
