---
type: "[[issue]]"
id: ISS-0319
aliases: ["ISS-0319"]
title: "Every new cockpit terminal inherits the environment of the Claude session that started the cockpit's tmux server"
status: fixed
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[TST-0094-A-Claude-Session-In-A-Cockpit-Terminal-Reports-Through-The-Plugin]], step 7"]
reported_by: agent
question: ""
severity: medium
component: desktop
parent: ""
related: ["[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]", "[[RISK-0004-Hook-Injection-Surface]]"]
tests: ["[[TST-0094-A-Claude-Session-In-A-Cockpit-Terminal-Reports-Through-The-Plugin]]"]
---

# Every new cockpit terminal inherits the environment of the Claude session that started the cockpit's tmux server

## Problem

A new terminal opened in the cockpit starts with environment variables that belong to a different, older Claude session. Every Claude session started in a cockpit terminal is therefore told it is the child of that other session. The kill switch `COCKPIT_NO_INSTRUMENT=1` also fails: a terminal opened with it still loads the cockpit plugin.

The cause is the cockpit's tmux server (`tmux -L cockpit`). A tmux server copies the environment of whatever first started it, and gives that copy to every session it creates afterwards. The current server (pid 1833) was started on 2026-10-11 at 10:42 by a cockpit app that had itself been launched from a Claude session inside a cockpit terminal. So the server's environment holds that session's `CLAUDECODE`, `CLAUDE_CODE_SESSION_ID`, `CLAUDE_PID`, `CLAUDE_CODE_MESSAGING_SOCKET`, and the your-trainer terminal's `ZDOTDIR` and `COCKPIT_INSTRUMENT_DIR`.

With instrumentation on, the app passes `-e ZDOTDIR=…` and the other instrument variables to `tmux new-session` (`desktop/src/ipc/terminal.ts`), which hides the wrong `ZDOTDIR`. The Claude variables are never overridden. With the kill switch on, the app passes nothing, so a new terminal loads your-trainer's generated `.zshrc`, which adds the plugin path to `CLAUDE_CODE_PLUGIN_DIRS`. That `.zshrc` checks `COCKPIT_NO_INSTRUMENT` itself, but the variable never reaches the shell, because tmux does not pass the client's environment to a new session.

> [!quote] As reported — 2026-10-14 (user:edwin)
> I have restarted, echo $CLAUDE_CODE_PLUGIN_DIRS does print something

## Repro

1. Start the cockpit app from a shell that has `CLAUDECODE=1` and a `ZDOTDIR` set, for example from a Claude session in a cockpit terminal, at a moment when no `tmux -L cockpit` server is running.
2. Quit the app; the tmux server keeps running.
3. Start the app from a clean environment with `COCKPIT_NO_INSTRUMENT=1`.
4. Close a project terminal with its restart button and run `echo $CLAUDE_CODE_PLUGIN_DIRS`.

## Expected

The variable is empty. A new terminal carries no other Claude session's variables, whether or not instrumentation is on.

## Actual

The variable holds the plugin path. `tmux -L cockpit show-environment -g` lists `CLAUDECODE=1`, `CLAUDE_CODE_CHILD_SESSION=1`, `CLAUDE_PID=1247`, `CLAUDE_CODE_SESSION_ID=177b9b4e-…`, and `ZDOTDIR` pointing at `instrument/e1c3057519152987/zdotdir` (your-trainer).

## Evidence

- The your-applications.com terminal was recreated at 13:00:36 on 2026-10-14 under an app started at 12:56 with only `HOME`, `PATH`, `SHELL`, a few basics and `COCKPIT_NO_INSTRUMENT=1`. Its tmux session environment holds only `SSH_AUTH_SOCK`; the plugin path came from the server's global environment.
- This repository's Claude process (pid 43803, started 12:44 under the instrumented app) has `CLAUDECODE=1`, `CLAUDE_PID=1247` and `CLAUDE_CODE_SESSION_ID=177b9b4e-…` in its starting environment (`ps -E -p 43803`). Pid 1247 is a separate `claude --dangerously-skip-permissions` still running.
- What Claude Code does differently when it believes it is a child session has not been checked.

## Decision

Edwin, 2026-10-14, chose to fix it now, inside FEAT-0156: [[TASK-0652-A-New-Cockpit-Terminal-Starts-Without-Another-Sessions-Variables]].

## Next Actions

- [x] When the app spawns a tmux session, remove inherited Claude, tmux and instrument variables from the server's global environment (`tmux set-environment -g -u …`), or start the server with a clean environment.
- [x] Rerun TST-0094 step 7 after the fix. It passed at 13:19.
