---
type: "[[task]]"
id: TASK-0652
aliases: ["TASK-0652"]
title: "A new cockpit terminal starts without another Claude session's variables, and the kill switch holds"
status: done
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[ISS-0319-Every-Cockpit-Terminal-Inherits-The-Environment-Of-The-Claude-Session-That-Started-Tmux]]", "[[TST-0094-A-Claude-Session-In-A-Cockpit-Terminal-Reports-Through-The-Plugin]], step 7"]
parent: "[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]"
effort: "S"
due: ""
depends: []
blocks: []
related: ["[[ISS-0319-Every-Cockpit-Terminal-Inherits-The-Environment-Of-The-Claude-Session-That-Started-Tmux]]", "[[RISK-0004-Hook-Injection-Surface]]"]
tests: ["[[TST-0094-A-Claude-Session-In-A-Cockpit-Terminal-Reports-Through-The-Plugin]]"]
---

# A new cockpit terminal starts without another session's variables

Edwin, 2026-10-14: "can you quit the app and run in the normal way and then fix the issue." The issue is [[ISS-0319-Every-Cockpit-Terminal-Inherits-The-Environment-Of-The-Claude-Session-That-Started-Tmux]]. It is fixed inside FEAT-0156 because TST-0094 step 7, the kill switch, cannot pass while it stands.

## Definition of Done

- [x] The environment the app gives a terminal, through tmux or directly, carries none of the variables Claude Code sets for its own child processes, no `TMUX`/`TMUX_PANE`, and no `ZDOTDIR` or `COCKPIT_INSTRUMENT_DIR` pointing into the cockpit's instrument folder. The cockpit plugin's folder is removed from an inherited `CLAUDE_CODE_PLUGIN_DIRS`; the person's own entries stay.
- [x] Before it creates a tmux session, the app removes the same variables from the running tmux server's global environment, so a server started by a dirty app is cleaned without killing any session.
- [x] A node test shows both, and fails when either is removed.
- [x] `node --test desktop/tests/*.test.mjs`, `npm run typecheck` and `bash tools/scripts/validate-docs.sh` are green.
- [x] TST-0094 step 7 is rerun. It passed at 13:19 in project-os-deck: the variable was empty and the plugin reported nothing (TST-0094, run section).

## Result, 2026-10-14

- **The code.** `desktop/src/ipc/terminal.ts`: `inheritedValue` decides what each inherited variable becomes, `cleanEnv` applies it to the environment a terminal is spawned with, and `cleanTmuxServerEnv` applies it to the tmux server's global environment (`set-environment -g -u`, or `-g` with the plugin folder removed) before every `new-session`. A session already running keeps what it started with.
- **The variable list.** The twelve Claude variables are the ones found in the tmux server: Claude Code pid 1247 was started from a plain shell holding none of them, so it set all twelve for its child processes.
- **Tests.** `desktop/tests/terminal-inherited-env.test.mjs`, three tests. Built without `cleanEnv`, one fails; built without `cleanTmuxServerEnv`, another fails. `npm run typecheck` is clean and the desktop suite passes 196 tests. On a throwaway tmux server, a session created after `set-environment -g -u CLAUDECODE` no longer had the variable.
- **Live.** The app restarted on this build at 13:11 with `COCKPIT_NO_INSTRUMENT=1`. Afterwards `tmux -L cockpit show-environment -g` listed none of the variables; before, it listed fourteen.

The app was then restarted normally at 13:20 (`npm start`, clean environment, no kill switch).
