---
type: "[[task]]"
id: TASK-0072
aliases: ["TASK-0072"]
title: "History stack (back / forward) + mouse buttons + menu accelerators"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0011"
effort: ""
due: ""
depends: ["[[TASK-0071]]"]
blocks: ["[[TASK-0073]]"]
related: []
tests: []
---

# History stack

## Definition of Done
- [ ] In-memory `historyStack: string[]` + `historyCursor: number`.
- [ ] `navigateTo(rel, {replace?: boolean})` pushes onto the stack
      unless `replace` is set (used for refreshes / SSE focus
      events that shouldn't pollute history).
- [ ] `back()` / `forward()` decrement / increment cursor and
      re-mount the doc; respect bounds.
- [ ] Wired to: mouse button 4 (back) / 5 (forward); View menu Back
      (Cmd+[) and Forward (Cmd+]).
- [ ] Stack capped at 100 entries (drop oldest on overflow).

## Steps
- [ ] Renderer: maintain stack + cursor; helper `navigateTo` already
      exists from TASK-0070.
- [ ] Renderer: `mouseup` listener on document for buttons 3 / 4
      (`event.button` values 3 / 4 mapped to back/forward).
- [ ] Main: add `Back` / `Forward` menu items with
      `Cmd+[` / `Cmd+]`; IPC to renderer via `menu:back` / `menu:forward`.
- [ ] Preload: expose `menu.onBack` / `menu.onForward` listeners.

## Notes
Visited state for the centre pane only — left nav state isn't part
of history yet (FEAT-0010 / FEAT-0012 may add a richer model).
