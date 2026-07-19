---
type: "[[feature]]"
id: FEAT-0016
aliases: ["FEAT-0016"]
title: "Project management — manual add, rename, custom icon, remove"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
goal: "Give the user explicit control over the workspace list: manually add a directory (single project or recursive scan of a parent folder), rename the display label, pick a custom icon, reset the icon, remove from the list. No more auto-discovery on launch — the user's selection is the source of truth."
related: ["[[FEAT-0007-Desktop-Shell]]", "[[FEAT-0015-Cockpit-IA-V2]]"]
requirements: []
tasks: ["[[TASK-0106]]", "[[TASK-0107]]", "[[TASK-0108]]"]
release: ""
tests: []
---

# Project management

## Goal

Replace auto-discovery (walk `~/Dev/repos`, depth 2, find every
`SNAPSHOT.yaml`) with explicit add/edit/remove. The user picks a
directory through a native dialog; either it's a single project or
we recursively scan it and add what we find. Names + icons become
user-editable and persist independently of auto-probed values.

## Scope

### In scope

- **Manual add (TASK-0106).** Rail `+` opens `dialog.showOpenDialog`.
  If the picked directory has `SNAPSHOT.yaml`, add it as a single
  workspace. Otherwise walk descendants for `SNAPSHOT.yaml`-bearing
  directories and add all of them. No duplicates (dedupe by id =
  sha1 of root path).
- **Project settings popover (TASK-0107).** `⋮` button next to the
  project name in the in-workspace nav header. Popover items:
  rename, choose icon, reset icon, reveal in Finder, remove from
  list (with confirm).
- **Override fields + CRUD IPC (TASK-0108).** Workspace type gains
  optional `userName` + `userIcon` (data-URI, 200 KB cap). New IPC
  handlers: `workspaces:add` (called by the picker flow),
  `workspaces:update` (rename / icon), `workspaces:remove`,
  `workspaces:pickIcon` (image file picker → data URI).

### Out of scope

- Auto-discovery on first launch. Removed entirely; user starts
  with an empty list and adds explicitly. The rescan menu item
  becomes a no-op (or is removed).
- Drag-to-reorder workspaces in the rail (future follow-up).
- Sharing workspaces between machines (sync via cloud / git).

## Acceptance

- Fresh install: rail shows `+ to add` empty state. Click `+` →
  native folder picker → pick `~/Dev/repos/project-os-cockpit` →
  workspace appears with auto-detected name + icon.
- Click `+` again → pick `~/Dev/repos` → confirm dialog lists every
  SNAPSHOT-bearing descendant → all added.
- Click `⋮` in the project header → rename the workspace → name
  changes everywhere (rail tooltip, project header, tab if shown).
- Click `⋮` → choose icon → pick PNG/SVG/JPG → square + header icon
  swap to the new image. Reset icon → reverts to auto-probed
  (or letter fallback if none found).
- Click `⋮` → remove → confirm → workspace disappears + its sidecar
  is killed if running.
- All edits persist across app restart via `workspaces.json`.

## Links
- Builds on [[FEAT-0007-Desktop-Shell]]'s workspace scaffold
- Replaces the auto-discovery half of [[TASK-0060]]
- Phase: [[PHASE-006-Native-Cockpit-UI]]
