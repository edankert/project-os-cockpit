---
type: "[[task]]"
id: TASK-0187
aliases: ["TASK-0187"]
title: "A `Restart console` action on the terminal context menu, so a wedged console can be recovered without restarting the app"
status: done
phase: "[[PHASE-004-Embedded-Terminal]]"
owner: user:edwin
created: 2026-07-22
updated: 2026-09-07
source: ["[[ISS-0017]]"]
parent: "FEAT-0015"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[TASK-0144]]"]
tests: []
---

# Restart console

*Reconstructed 2026-09-07 ([[ISS-0287]]). This note was committed as a **zero-byte file** on 2026-07-22 and stayed empty, so every citation of it resolved to nothing and it was absent from the snapshot and every count. What follows is taken from the delivering commit `3536687` and from the issue it closed — nothing here is inferred beyond what those record.*

## What it did

A workspace console could wedge — a TUI stuck on a picker, a hung pager, a broken PTY — with no way back inside the app. **Restarting the app did not help**, because the terminal is tmux-backed ([[TASK-0144]]): the shell reattaches to the same stuck session.

So the recovery has to kill the session rather than the window. `Restart console` on the terminal context menu disposes the active workspace's PTY — `killPty` also kills its backing tmux session — clears the renderer's live-terminal and saved mouse-mode state, and re-attaches, spawning a fresh shell in place.

It is behind a confirm, because it kills whatever is running there, including a Claude or Codex session.

It closed [[ISS-0017]].

## Verification

Carried by the delivering commit's own review; no test note is claimed, because none was written at the time and inventing one now would be a false record.
