---
type: "[[task]]"
id: TASK-0090
aliases: ["TASK-0090"]
title: "Native context menus on nav rows + doc links + rail pills"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0012"
effort: ""
due: ""
depends: ["[[TASK-0083]]"]
blocks: []
related: []
tests: []
---

# Native context menus

## Definition of Done
- [ ] Right-click on a nav row → native macOS context menu
      (`Menu.popup()` via IPC) with: *Copy ID*, *Copy path*,
      *Reveal in Finder*, *Open in new window* (no-op until
      TASK-0092).
- [ ] Right-click on a centre-pane wikilink → same menu plus
      *Copy link*.
- [ ] Right-click on a rail pill → context with: *Open*, *Reveal
      repo in Finder*, *Pin* (no-op until pinning lands), *Remove
      from rail*.
- [ ] Default Chromium right-click menu suppressed in the
      renderer.

## Steps
- [ ] Renderer: capture `contextmenu` events on the relevant
      surfaces; preventDefault; ipcRenderer.invoke('menu:show', …).
- [ ] Main: build the menu template per context type; show via
      `Menu.popup()`; route action results back via IPC.
