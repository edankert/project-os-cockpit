---
type: "[[task]]"
id: TASK-0084
aliases: ["TASK-0084"]
title: "Other nav modes (Tasks / Issues / Library / Recent) + mode toggle"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0010"
effort: ""
due: ""
depends: ["[[TASK-0083]]"]
blocks: ["[[TASK-0086]]"]
related: []
tests: []
---

# Other nav modes + mode toggle

## Definition of Done
- [ ] Mode pill row at the top of `#ws-nav` with five buttons:
      `Features`, `Tasks`, `Issues`, `Library`, `Recent`.
- [ ] Active mode highlighted; click switches; persisted to
      userData (global single value v1).
- [ ] Each mode fetches `/api/cockpit/nav?mode=<key>` and renders
      its `groups[]`. The framework from TASK-0083 handles 80%;
      this task adds mode-specific row shapes:
      - **Tasks** — grouped by status bucket; type icons.
      - **Issues** — grouped by severity (default `low`).
      - **Library** — hybrid Changes month/week buckets
        (TASK-0039..0041 behaviour), curated + auto-discovered +
        rare types, pin button per row.
      - **Recent** — flat list, newest first.
- [ ] Platform filter pill (auto-discovered) shown only when the
      `available_platforms` field has > 1 entry. Selection
      persisted globally.

## Steps
- [ ] `desktop/src/renderer/ws-nav.ts` — extend the render
      function with per-mode item factories.
- [ ] `mode-toggle.ts` — small component for the pill row.
- [ ] CSS reuse from base/cockpit (chips, group headers).

## Notes
Mode 1's `cockpit.js` has all this logic already; this task ports
it forward to the native renderer. The `_library_groups` /
`_changes_subgroups` helpers in `cockpit.py` already produce the
right shape; we just render it.
