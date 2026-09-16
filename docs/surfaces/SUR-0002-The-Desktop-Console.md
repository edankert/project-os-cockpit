---
type: "[[surface]]"
id: SUR-0002
aliases: ["SUR-0002"]
title: "The desktop console"
status: active
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
kind: screen
platforms: []
parent: ""
gallery: []
related: ["[[FEAT-0003]]", "[[ISS-0310]]", "[[TASK-0627]]"]
tags: [surface]
---

# The desktop console

## What it is

The Electron cockpit opens this console below the workspace page. A person can run a shell, Claude Code, or Codex, and can open the console's retained history while the current program keeps running. The pane stays available when the person changes workspace.

## Boundaries

The console shows a live terminal and tmux's retained screen history. Codex's own transcript belongs to Codex and may contain output that a terminal redraw never placed in tmux history. The browser-only `ttyd` terminal is a separate path.

## Coverage

Checks covering this surface are derived from their `area:` values.
