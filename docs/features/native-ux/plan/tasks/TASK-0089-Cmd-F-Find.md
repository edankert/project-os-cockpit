---
type: "[[task]]"
id: TASK-0089
aliases: ["TASK-0089"]
title: "Cmd+F find-in-doc"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0012"
effort: ""
due: ""
depends: ["[[TASK-0070]]"]
blocks: []
related: []
tests: []
---

# Cmd+F find-in-doc

## Definition of Done
- [ ] ⌘F opens a slim find bar at the top of `#stage-main`.
- [ ] Live search highlights matches inside `#doc-view`; match
      count + next/prev arrows.
- [ ] Enter cycles forward through matches; Shift+Enter back.
- [ ] Esc closes; highlight cleared.
- [ ] Wired both via menu (View → Find) and a renderer-side keydown
      listener.

## Steps
- [ ] Renderer-side `<details>`-style find bar (hidden by default).
- [ ] Text walker over `#doc-view` text nodes; wrap matches with
      `<mark class="find-match">`. Save / restore matches on every
      query change.
- [ ] Scroll active match into view; toggle `.is-current` for the
      navigation cursor.

## Notes
Electron also has `webContents.findInPage` but that operates on the
whole page including chrome — too broad. Hand-rolled DOM walker is
cleaner and avoids highlighting the rail / nav.
