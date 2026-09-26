---
type: "[[task]]"
id: TASK-0105
aliases: ["TASK-0105"]
title: "Bug fixes — light theme override + Cmd+P selection"
status: done
phase: "[[PHASE-006-Native-Cockpit-UI]]"
owner: user:edwin
created: 2026-05-25
updated: 2026-05-25
source: []
parent: "FEAT-0015"
related: ["[[TASK-0088]]", "[[TASK-0095]]"]
tests: []
---

# Bug fixes

## Definition of Done
- [ ] Light theme: clicking `Lt` in the status footer overrides
      OS dark mode, and `Sys` re-syncs to OS.
- [ ] Cmd+P palette: clicking a result or pressing Enter navigates
      the centre pane.

## Root cause — light theme
`renderer.css` defines its colour variables inside a
`@media (prefers-color-scheme: dark)` block. The `applyTheme()`
function sets `data-theme="light"` on `<html>`, but the media
query ignores that attribute. Convert the dark-mode block to
`:root[data-theme="dark"] { … }` (matches the base.css
convention at line 54). The default block stays as the light
palette; the explicit attribute always wins.

## Root cause — Cmd+P
In `renderQuickResults`, every `<li>` has a `mouseenter` handler
that calls `renderQuickResults()` again. That destroys the LIs.
Between the user's mousedown and mouseup, the LI under the
cursor is replaced, so the browser never fires `click`. Fix:
toggle `.is-selected` on existing LIs instead of re-rendering
on hover.
