---
type: "[[plan]]"
id: PLAN-FEAT-0016
aliases: ["PLAN-FEAT-0016"]
title: "Plan — FEAT-0016 project management"
status: doing
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
parent: "[[FEAT-0016-Project-Management]]"
---

# Plan — FEAT-0016

## Sequence

1. **TASK-0108 — schema + CRUD IPC.** Add `userName?` /
   `userIcon?` to Workspace. Add `effectiveName(ws)` /
   `effectiveIcon(ws)` helpers in renderer. New IPC handlers:
   - `workspaces:add({ root, name?, icon? })` — adds one workspace
     to the store (rejects duplicates).
   - `workspaces:update({ id, userName?, userIcon? })` — patches
     overrides.
   - `workspaces:remove(id)` — drops from list. Kills sidecar +
     terminal PTY if running.
   - `workspaces:pickIcon()` — opens image file picker, encodes
     to data URI (200 KB cap), returns string.

2. **TASK-0106 — directory picker.** Rail `+` handler calls a new
   `workspaces:pickAndAdd` IPC method which:
   - Opens `dialog.showOpenDialog({ properties: ['openDirectory'] })`
   - If selected path has `SNAPSHOT.yaml` at root → add single
   - Else recursively scans (existing `walk()`), shows a renderer-
     side confirm with the found list, adds all on confirm
   Auto-discovery removed: `loadOrDiscover` always returns the
   stored list (no fallback walk on empty).

3. **TASK-0107 — settings popover.** Add `⋮` button to the
   project header. Popover (custom, same shape as platform combo
   menu) with rename input + 4 action items. Rename is inline
   text; icon picker calls `workspaces:pickIcon`; remove triggers
   `confirm()` then `workspaces:remove`. All actions refresh the
   rail + header.

## Notes
- Auto-discovery on first launch is removed. Existing
  workspaces.json users keep their list; the next rescan won't
  do a fresh walk unless explicitly invoked.
- `userName` / `userIcon` are read-or-fallback: if unset, fall
  back to the SNAPSHOT-derived `name` / auto-probed `icon`.
- Removing a workspace also kills its sidecar (otherwise the
  Python process keeps running until app exit).
