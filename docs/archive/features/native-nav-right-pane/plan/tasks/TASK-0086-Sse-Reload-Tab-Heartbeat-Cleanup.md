---
type: "[[task]]"
id: TASK-0086
aliases: ["TASK-0086"]
title: "SSE soft-reload + tab heartbeat + drop temporary Browse panel"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0010"
effort: ""
due: ""
depends: ["[[TASK-0083]]", "[[TASK-0084]]", "[[TASK-0085]]"]
blocks: []
related: []
tests: []
---

# Soft-reload + tab heartbeat + cleanup

## Definition of Done
- [ ] Renderer subscribes to the active sidecar's `/_events`
      already (FEAT-0007 / agent-focus bridge). Add a
      `file-changed` listener that debounces (150 ms) re-fetches
      of: the active nav mode, the right pane, and the centre's
      current note.
- [ ] Tab-state heartbeat: every 15 s, POST
      `/api/cockpit/tab-state` with a renderer-local `tab_id`
      (persisted in `localStorage`), the current URL, and
      `following: true`.
- [ ] Drop the "Browse this workspace" panel that ships in
      FEAT-0011's README mount — `renderBrowsePanel()` and all its
      CSS are removed; the call site in `navigateTo` is removed.
- [ ] Dead CSS cleanup pass: drop `.browse-panel`,
      `.frontmatter-card` (the hand-built v1 — server emits
      `.metadata-strip` now), and any other class no longer
      emitted.

## Steps
- [ ] Renderer SSE handler: extend the existing `agent-focus`
      subscription path or add a new `file-changed` listener
      against the active sidecar URL.
- [ ] Implement `tab-state-heartbeat.ts` — 15 s interval,
      pings + on every navigateTo.
- [ ] Delete browse-panel code + styles; delete dead frontmatter
      CSS.

## Notes
Last polish task. The soft-reload is the regression-protection
layer — edits to source notes (made externally by the user or by
an agent) immediately reflect in the running cockpit view. Without
it, the user has to manually reload.

The Browse-panel removal closes a temporary scaffold the user has
been looking at since FEAT-0011 — it should disappear cleanly.
