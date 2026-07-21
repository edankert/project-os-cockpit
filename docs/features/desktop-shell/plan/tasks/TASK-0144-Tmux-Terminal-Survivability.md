---
type: "[[task]]"
id: TASK-0144
aliases: ["TASK-0144"]
title: "tmux-backed terminal survivability — agents outlive the desktop app"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-20
source: ["[[ISS-0008-Terminal-Sessions-Die-With-App]]"]
parent: "FEAT-0007"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[TASK-0145]]", "[[ISS-0008]]"]
tests: []
---

# TASK-0144 — tmux-backed terminal survivability

## Goal

Workspace terminals must survive desktop-app death (ISS-0008: two unexplained app exits killed an in-flight hour-long Claude session). Each PTY becomes a **tmux client** attached to a named session (`cockpit-<workspace-id>`) on a dedicated socket (`-L cockpit`); the tmux server owns the shell. App death only detaches the client; relaunch runs `new-session -A` and lands back in the still-running session — an in-flight claude keeps working headless in between and is simply *there* again on restart.

## Design points

- Dedicated socket + generated conf (`-f cockpit.tmux.conf`: status off, history-limit 100k, escape-time 10) so the user's own tmux config/sessions are untouched.
- Instrumentation env (`ZDOTDIR`, `COCKPIT_INSTRUMENT_DIR`) passed via `new-session -e` (needs tmux ≥ 3.2) *and* client env; `COCKPIT_HOOK_URL` already flows through the `hook-env` file re-sourced per hook event, so surviving sessions automatically re-target the new sidecar port after an app restart.
- tmux binary discovery across `/opt/homebrew/bin`, `/usr/local/bin`, `/usr/bin`, `$PATH`; graceful fallback to the previous direct spawn when absent or too old (marker: `viaTmux` per PTY record).
- Explicit dispose (user closes the workspace terminal) kills the tmux session too; app quit (`shutdownAllTerminals`) kills only clients — that asymmetry is the feature.
- xterm scrollback from before a restart is not replayed (tmux redraws the live screen); tmux's own history holds the backlog.

## Verification

End-to-end without GUI: launch app → `tmux -L cockpit ls` shows the workspace session; kill the app with SIGKILL → session still listed, test process inside keeps running; relaunch → client reattaches to the same session.
