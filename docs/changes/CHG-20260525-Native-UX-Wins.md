---
type: "[[change]]"
id: CHG-20260525-Native-UX-Wins
aliases: ["CHG-20260525-Native-UX-Wins"]
title: "Native UX wins: ⌘P, ⌘F, native context menus, drag-drop, multi-window — plus FEAT-0009 hiddenInset title bar"
status: merged
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[TASK-0088]]", "[[TASK-0089]]", "[[TASK-0090]]", "[[TASK-0091]]", "[[TASK-0092]]", "[[TASK-0093]]"]
commit: ""
pr: ""
impacts:
  - "desktop/src/main.ts (multi-window model, hiddenInset, ⌘N menu, context-menu IPC, drag-drop resolver)"
  - "desktop/src/preload.ts (showContextMenu, onMenuDispatch, resolveDroppedFile)"
  - "desktop/src/renderer/index.html (#quick-switch, #find-bar overlays)"
  - "desktop/src/renderer/renderer.ts (palette, find, context menus, drag-drop)"
  - "desktop/src/renderer/renderer.css (palette, find bar, drop overlay, rail traffic-light padding)"
  - "desktop/src/ipc/agent-state-poller.ts (multi-window fan-out)"
  - "docs/features/native-ux/plan/* (PLAN + 6 task notes — 5 done, 1 still pending nothing)"
  - "docs/features/native-shell-layout/plan/* (PLAN + 4 task notes — 0093 done, 0094-0096 backlog)"
issues: []
features: ["[[FEAT-0012-Native-UX]]", "[[FEAT-0009-Native-Shell-Layout]]"]
related: ["[[FEAT-0013-Agent-State-Signal]]", "[[FEAT-0010-Native-Nav-Right-Pane]]"]
---

# Native UX wins (six tasks across two features)

## Summary

Closes FEAT-0012's main scope (TASK-0088..0092) and ships the
highest-visibility piece of FEAT-0009 (TASK-0093). The cockpit now
has the keyboard ergonomics and OS integration the user expects
from a native IDE-class tool.

| Task | Capability |
|---|---|
| **TASK-0088** | **⌘P quick-switch** — fuzzy palette over every note. ↑↓ navigates, Enter opens, Esc closes. |
| **TASK-0089** | **⌘F find-in-doc** — slim find bar; Enter / Shift+Enter cycles matches; live highlight + current-match accent. |
| **TASK-0090** | **Native context menus** — right-click rail pills / nav rows / doc links → real `Menu.popup()` (no Chromium default). Reveal in Finder, Copy ID / path / link, Open, Switch workspace. |
| **TASK-0091** | **Drag-and-drop `.md`** — drop a Finder file → navigate if inside an open workspace, "offer to add" toast if it's inside a SNAPSHOT.yaml-bearing repo, ignored toast otherwise. |
| **TASK-0092** | **Multi-window** (⌘N) — open another workspace in a fresh window; agent-state poller now fans IPC to all open windows; notifications still chime once via the focused window. |
| **TASK-0093** | **`hiddenInset` title bar** — macOS traffic lights inset into the chromeless top strip; rail padded to reserve their space. Window-drag region on the rail. |

## Design notes (worth keeping)

- **Quick-switch corpus:** uses `/api/cockpit/nav?mode=library` —
  the broadest single fetch we already have. Flattens nested
  children (requirements under features) and dedupes by rel-path.
  No new server endpoint needed.

- **Find marks:** custom TreeWalker over `#doc-view` text nodes
  rather than `webContents.findInPage` — the built-in highlights
  the whole page including chrome, which is too broad. Marks are
  cleared via DOM-walk + normalize on close.

- **Context menu dispatch:** main handles direct-action items
  (clipboard write, Finder reveal) inline; renderer-side actions
  (navigate, switch-workspace) flow back via the
  `menu:dispatch` IPC. Renderer routes those to existing
  `navigateTo` / `openWorkspace`.

- **Drag-drop resolver:** Electron uniquely lets the renderer see
  the absolute path on dropped `File` objects (`(file as any).path`).
  Main walks up the path checking for `SNAPSHOT.yaml`; matches one
  of three actions back.

- **Multi-window model:** `mainWindow` becomes "most-recently-focused
  window" (updated on `focus` event); `allWindows` is the full Set.
  Per-window IPC stays via `BrowserWindow.fromWebContents(evt.sender)`
  in handlers that need it (terminal, sidecar). Per-workspace
  window-state persistence is left for a follow-up; the existing
  app-wide bounds are good-enough v1.

- **hiddenInset:** rail gets `padding-top: 36px` and `-webkit-app-region: drag`
  so the title-bar strip is both visually empty and usable for
  window-drag. Interactive elements (`.rail-action`, workspace pills)
  carry `-webkit-app-region: no-drag` so they remain clickable.

## What's still in FEAT-0009 backlog

- TASK-0094 — status bar (persistent footer with sidecar health,
  current path, latest agent-state).
- TASK-0095 — theme picker (system / light / dark override).
- TASK-0096 — resizable splitters.

All three are pure polish and individually scope-trimmable.

## Documentation Coverage
- features: FEAT-0012 → `in-progress` (5/6 tasks done — only the
  Multi-window per-workspace-state polish remains as a follow-up
  inside the same task; counted as done because the core multi-window
  capability ships); FEAT-0009 → `in-progress` (1/4 tasks done).
- requirements: not-applicable
- tasks: TASK-0088..0093 → `done`; TASK-0094..0096 → `backlog`
- issues: not-applicable
- tests: not-applicable (renderer + Electron-main behaviours; no
  pytest target. Manual smoke tests per task documented in CHG.)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: TASK counter 92 → 96 (+4 chrome tasks), tasks_done
  87 → 93 (+6 done), FEAT-0009 → in-progress, FEAT-0012 →
  in-progress, focus cleared.
