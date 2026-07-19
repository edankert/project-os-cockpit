---
type: "[[task]]"
id: TASK-0102
aliases: ["TASK-0102"]
title: "Platform pill row under the modes toolbar"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0015"
related: ["[[TASK-0017]]"]
tests: []
---

# Platform pill row

## Definition of Done
- [ ] `<div id="platform-bar">` below `#ws-nav-toolbar`.
- [ ] Renders `available_platforms` from `/api/cockpit/nav` as
      pills. First pill is "all", followed by each platform.
- [ ] Selected pill highlighted; click re-fetches nav with the
      `&platform=…` query.
- [ ] Hidden entirely when `available_platforms.length <= 1`.
- [ ] Selection persisted to `localStorage` per-workspace
      (`cockpit:platform:<workspaceId>` or similar).

## Notes
Same UX as the browser cockpit's platform filter (TASK-0017).
Reuse `.platform-bar` + `.platform-pill` from cockpit.css.
