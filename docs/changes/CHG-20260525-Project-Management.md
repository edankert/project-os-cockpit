---
type: "[[change]]"
id: CHG-20260525-Project-Management
aliases: ["CHG-20260525-Project-Management"]
title: "Project management: manual add, rename, custom icon, remove; auto-discovery dropped; per-workspace sidecar persistence + port-exhaustion fix"
status: merged
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[TASK-0106]]", "[[TASK-0107]]", "[[TASK-0108]]"]
commit: ""
pr: ""
impacts:
  - "desktop/src/types.ts (Workspace.userName + userIcon overrides)"
  - "desktop/src/ipc/workspaces.ts (drop auto-discovery; add pickAndAdd / update / remove / pickIcon IPC; loadStored + buildWorkspace helpers; persist())"
  - "desktop/src/ipc/sidecar.ts (sidecars keyed by workspaceId; idempotent spawn re-emits ready; persists across workspace switches — fixes port-range exhaustion)"
  - "desktop/src/preload.ts (workspaces.pickAndAdd / update / remove / pickIcon exposed)"
  - "desktop/src/renderer/index.html (project settings ⋮ button + popover)"
  - "desktop/src/renderer/renderer.css (project-settings-btn + project-settings-menu styles)"
  - "desktop/src/renderer/renderer.ts (effectiveName / effectiveIcon helpers; addWorkspaceFlow; project settings popover handlers; right-pane hide-completed; metadata-strip persistence)"
issues: []
features: ["[[FEAT-0016-Project-Management]]"]
related: ["[[FEAT-0007-Desktop-Shell]]", "[[FEAT-0015-Cockpit-IA-V2]]"]
---

# Project management

## Summary

Closes FEAT-0016 plus three related fixes that landed in the same
session.

| Task | Capability |
|---|---|
| **TASK-0106** | **Manual add via directory picker.** Rail `+` opens `dialog.showOpenDialog`. If the chosen folder has `SNAPSHOT.yaml`, it's added directly; otherwise the existing `walk()` descends and adds every SNAPSHOT-bearing descendant. Duplicates are silently skipped (dedupe by id = sha1 of path). Auto-discovery on first launch removed entirely. |
| **TASK-0107** | **Project settings popover.** `⋮` button next to the project name in the in-workspace nav header. Popover items: rename (inline text, blur or Enter commits, Escape reverts), choose icon, reset icon, reveal in Finder, remove from list (with confirm). |
| **TASK-0108** | **Override fields + CRUD IPC.** `Workspace` gains `userName?` and `userIcon?`. Renderer reads via `effectiveName(ws) = ws.userName ?? ws.name` and `effectiveIcon(ws) = ws.userIcon ?? ws.icon`. New IPC: `workspaces:pickAndAdd`, `workspaces:update`, `workspaces:remove`, `workspaces:pickIcon`. All persist to workspaces.json on every change. |

### Drive-by fixes shipped alongside

- **Sidecar port-range exhaustion fixed.** `sidecars` map switched
  from window-keyed to workspace-keyed; switching workspaces reuses
  the running sidecar instead of kill + respawn. The killed shell's
  port used to linger in macOS TIME_WAIT for ~30–120 s, so ~100
  switches exhausted the 8765–8865 range and surfaced
  "No open ports found". Each workspace now keeps one Python
  sidecar alive across switches; only dies on explicit dispose or
  app exit.
- **Right pane obeys hide-completed.** `renderContextGroup` filters
  by `isItemHidden` (same `COMPLETED_STATUSES` as the left nav).
  Empty groups + empty sections drop out. Re-renders in place when
  the eye toggle fires (no extra fetch).
- **Frontmatter expand/collapse persists.** `details.metadata-strip`'s
  open state is stored at `localStorage['cockpit:metadata-strip-open']`
  and re-applied after every render — so the user can keep it
  collapsed across notes.

## Sharp notes

- **Effective name/icon vs auto-derived.** The user's `userName` /
  `userIcon` always win for display, but auto-derived `name` /
  `icon` are still computed at add-time and persisted in the same
  record so `Reset icon` can fall back without re-probing.
- **Removing a workspace** drops it from the local renderer list
  immediately and switches to the next available (or the empty
  placeholder). Main also drops it from workspaces.json; if its
  sidecar is running it stays alive until app exit — a follow-up
  could explicitly kill it on remove, but the current behaviour
  matches "the user can always re-add it from the same path."
- **No icon dialog at add time.** Add is one step (pick dir →
  done). Renaming / changing the icon is a separate explicit
  action via the `⋮` popover. Keeps the add flow tight.

## Documentation Coverage
- features: FEAT-0016 → `done` (3/3 tasks done)
- requirements: not-applicable
- tasks: TASK-0106..0108 → `done`
- issues: not-applicable
- tests: not-applicable (renderer + main IPC chrome; no pytest)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: tasks_done 105 → 108; features_done 9 → 10; focus cleared.
