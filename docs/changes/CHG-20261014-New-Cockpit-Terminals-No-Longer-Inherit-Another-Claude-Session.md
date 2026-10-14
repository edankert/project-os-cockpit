---
type: "[[change]]"
id: CHG-20261014-New-Cockpit-Terminals-No-Longer-Inherit-Another-Claude-Session
title: "A new cockpit terminal no longer inherits another Claude session's variables, and the kill switch holds"
status: merged
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[TASK-0652-A-New-Cockpit-Terminal-Starts-Without-Another-Sessions-Variables]]"]
commit: ""
pr: ""
impacts: ["desktop/src/ipc/terminal.ts", "desktop/tests/terminal-inherited-env.test.mjs", "desktop/tests/terminal-history.test.mjs"]
platforms: [macos]
issues: ["[[ISS-0319-Every-Cockpit-Terminal-Inherits-The-Environment-Of-The-Claude-Session-That-Started-Tmux]]"]
features: ["[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TST-0094-A-Claude-Session-In-A-Cockpit-Terminal-Reports-Through-The-Plugin]]", "[[RISK-0004-Hook-Injection-Surface]]"]
---

# A new cockpit terminal no longer inherits another Claude session's variables

## Summary

A Claude session started in a new cockpit terminal is no longer told it is the child of some other Claude session. With `COCKPIT_NO_INSTRUMENT=1`, a new terminal no longer loads the cockpit plugin.

Before this change, the cockpit's tmux server handed every new terminal the environment it was started with. When the app had been launched from a Claude session in a cockpit terminal, that environment held the session's identity (`CLAUDECODE`, `CLAUDE_PID`, `CLAUDE_CODE_SESSION_ID`, its messaging socket and token) and another terminal's `ZDOTDIR`. The tmux server keeps running across app restarts, so the leak lasted until the server ended. On 2026-10-14 the server had been carrying one session's variables since 11 October.

## What changed

- Before it opens a terminal, the app removes these variables from the environment it spawns the terminal with: the twelve Claude Code sets for its own child processes, `TMUX` and `TMUX_PANE`, and any `ZDOTDIR` or `COCKPIT_INSTRUMENT_DIR` pointing into the cockpit's instrument folder. It also takes the cockpit plugin out of an inherited `CLAUDE_CODE_PLUGIN_DIRS`, keeping the person's own entries.
- Before it creates a tmux session, it removes the same variables from the running tmux server's global environment (`tmux set-environment -g -u`). So a server started by a launch that carried them is cleaned without ending any session.
- A terminal already open keeps what it started with until it is restarted.

## What a person notices

- `echo $CLAUDE_CODE_PLUGIN_DIRS` in a new terminal is empty when the app runs with `COCKPIT_NO_INSTRUMENT=1`.
- `env | grep CLAUDE` in a new terminal shows only what the person set themselves.

## Verification

- `desktop/tests/terminal-inherited-env.test.mjs`: three tests. Built without the cleaned spawn environment, one fails; built without the tmux server cleanup, another fails. The desktop suite passes 196 tests; `npm run typecheck` is clean.
- TST-0094 step 7 passed at 13:19 in a restarted project-os-deck terminal.

## Not changed

The external hook in `~/.claude/settings.json` (FEAT-0027) still reports every Claude session on the machine, including one in a cockpit terminal under the kill switch. That hook is a separate, opt-in path, and the kill switch has never covered it.
