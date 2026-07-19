---
type: "[[task]]"
id: TASK-0071
aliases: ["TASK-0071"]
title: "Internal link interception + soft nav + external openExternal"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0011"
effort: ""
due: ""
depends: ["[[TASK-0070]]"]
blocks: ["[[TASK-0072]]"]
related: []
tests: []
---

# Internal link interception + soft nav

## Definition of Done
- [ ] Click handler on `#doc-view` intercepts `<a>` clicks.
- [ ] Docs-internal (`/docs/<rel>` or absolute URL within sidecar
      origin) → `navigateTo(rel)`.
- [ ] External (`http(s)://...` outside sidecar origin) →
      `shell.openExternal(url)` via main process IPC; default
      navigation suppressed.
- [ ] Fragment-only (`#heading`) → scroll within `#doc-view` (no
      navigation).
- [ ] Cmd/Ctrl-click respects "open external in browser" intent
      even for docs-internal links (escape hatch).

## Steps
- [ ] Add `openExternal(url)` IPC to preload + main.
- [ ] Renderer: single delegated click handler on `#doc-view`;
      examine target `<a>` (walk up if click hit a descendant);
      branch on URL shape.
- [ ] Use `URL` parser against sidecar origin to classify.

## Notes
The cockpit's `cockpit.js` does a similar interception today (for
in-iframe nav). Mirror its classification.
