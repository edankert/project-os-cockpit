---
type: "[[task]]"
id: TASK-0094
aliases: ["TASK-0094"]
title: "Status bar (footer)"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: ["[[CHG-20260525-FEAT-0009-Chrome-Polish]]"]
parent: "FEAT-0009"
related: []
tests: []
---

# Status bar

## Definition of Done
- [x] Thin (~22 px) footer at the bottom of the stage.
- [x] Surfaces: sidecar health, current note rel-path, latest
      agent-state.
- [x] Click on the path field copies it to the clipboard.

## Notes
Pure information surface. The existing `#status-bar` toast handles
ephemeral messages; this is the persistent always-visible variant.

## Implementation
`<footer id="status-footer">` lives between `#stage-main` and
`#terminal-pane`. Cells: `.sf-sidecar` (state dot + label, fed by
`setSidecarStatus`), `.sf-path` (mono, click-to-copy current rel-path,
fed by `refreshFooterPath`), `.sf-agent` (dot + state, fed by
`refreshFooterAgent` on `onAgentState` for the active workspace).
Dot colours reuse the existing `--status-*` / `--severity-*` palette
and the `ws-waiting-pulse` animation from TASK-0082.
