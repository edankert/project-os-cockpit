---
type: "[[issue]]"
id: ISS-0008
aliases: ["ISS-0008"]
title: "Embedded terminal agents die with the desktop app — no survivability or reattach after an app exit"
status: fixed
severity: high
component: terminal
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
parent: "[[FEAT-0007-Desktop-Shell]]"
related: ["[[ISS-0007-Stale-Url-Cross-Workspace-Poisoning]]"]
---

# ISS-0008 — embedded terminal agents do not survive app exits

## Problem

Observed 2026-07-18/19: the desktop app terminated twice without the user quitting (once SIGKILL-class, once a clean exit-0 whose trigger could not be determined from logs — not window-all-closed, which keeps the app alive on macOS, and no crash report). Each embedded terminal PTY is a child of the Electron main process, so an app exit SIGHUPs every in-flight agent session. A killed hour-long Claude session in `your-sudoku` could not be recovered: the process was gone and `claude --resume <id>` reports "No conversation found" (its transcript was absent from `~/.claude/projects` — an upstream Claude Code anomaly on top of the cockpit-side death; both sudoku transcripts from that day were missing while other projects' persisted). The only recovery was the project-os docs the session had already written.

## Impact

Losing the app loses every running agent across all workspaces at once. With dispatch (FEAT-0025) making the cockpit the primary way to run agents, this turns any app crash/quit into a multi-workspace work stoppage and, when transcripts are also unavailable, unrecoverable conversation loss.

## Fix (TASK-0144 + TASK-0145, 2026-07-19)

All three directions implemented (see [[CHG-20260719-Terminal-Survivability-And-Identity-Guard]]): terminals are tmux clients on a dedicated `-L cockpit` socket (tmux ≥ 3.2, installed via Homebrew; `COCKPIT_NO_TMUX=1` or missing tmux falls back to direct spawn), so app death detaches instead of killing and relaunch reattaches via `new-session -A`; `before-quit` warns when a busy/needs-input agent sits in a fallback terminal (tmux-backed agents survive quits — no dialog); fallback spawns print a display-only `claude --resume <id>` hint when the session index shows a recent unended session. Survivability verified end-to-end through the exact node-pty spawn path: client killed → session and its process kept running → reattach replayed the live screen. Quit-guard dialog and death hint ride on the TST-0011 manual sweep (TASK-0145 stays `doing` until then).

### Original fix directions (for the record)

1. **tmux-backed PTYs:** spawn each workspace terminal inside a named tmux session (`cockpit-<workspace-id>`); the app's PTY attaches rather than owns. App death detaches; relaunch reattaches — the agent keeps running headless in between. tmux availability check with graceful fallback to today's direct spawn.
2. **Quit guard:** `before-quit` prompt when any workspace agent-state is busy/needs-input ("2 agents are running — quit anyway?"), so graceful quits at least become deliberate.
3. **Post-restart recovery surface:** on launch, detect sessions the tracker marked live-but-unended (no `SessionEnd`, app-exit inside the decay window) and show a "resume `claude --resume <id>`?" affordance in that workspace's terminal — works only when the transcript survived, so pair with 1.
