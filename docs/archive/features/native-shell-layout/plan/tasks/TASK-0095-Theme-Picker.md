---
type: "[[task]]"
id: TASK-0095
aliases: ["TASK-0095"]
title: "Theme picker — system / light / dark"
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

# Theme picker

## Definition of Done
- [x] Dropdown (or three-pill toggle) in the rail or status bar
      offering: system / light / dark.
- [x] Persisted to `localStorage` as `cockpit:theme`.
- [x] When set to system, the existing `prefers-color-scheme`
      bridge from TASK-0075 drives the value. When set explicitly,
      the picker wins.

## Notes
Light path is rarely used by category peers but cheap to ship.

## Implementation
Three-pill toggle (`.sf-theme-btn`s) inside the status footer (label
`Sys` / `Lt` / `Dk`). `ThemePref = 'system' | 'light' | 'dark'`
persisted at `cockpit:theme`. `applyTheme()` reads the pref;
'system' branch listens to `prefers-color-scheme`, explicit branches
set `data-theme` on `<html>`. The active button gets the `active`
class via `refreshThemeButtons()`.
