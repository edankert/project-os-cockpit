---
type: "[[change]]"
id: CHG-20261014-Claude-Sessions-Report-Through-The-Cockpit-Plugin
title: "A Claude session in a cockpit terminal reports through a plugin, and your own Claude status line is back"
status: merged
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[TASK-0649-The-Cockpit-Plugin-Posts-Every-Claude-Event-To-The-Sidecar]]", "[[TASK-0650-The-Shell-Loads-The-Plugin-And-Stops-Generating-Claude-Files]]", "[[TASK-0651-The-Sidecar-Prefers-The-Plugin-And-CI-Checks-It]]"]
commit: ""
pr: ""
impacts: ["desktop/plugin/claude-code/.claude-plugin/plugin.json", "desktop/plugin/claude-code/hooks/hooks.json", "desktop/plugin/claude-code/hooks/register.ts", "desktop/plugin/claude-code/tests/cockpit.test.ts", "desktop/plugin/claude-code/tsconfig.json", "desktop/src/ipc/agent-instrument.ts", "desktop/tests/claude-plugin-shell.test.mjs", "desktop/tests/codex-shell-exit.test.mjs", "src/project_os_cockpit/agent_hooks.py", "tests/test_agent_hooks.py", "tests/test_agent_instrument.py", ".github/workflows/observed-coverage.yml", "docs/reference/cockpit-capability-register.md"]
platforms: [macos]
issues: []
features: ["[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TST-0094-A-Claude-Session-In-A-Cockpit-Terminal-Reports-Through-The-Plugin]]", "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]", "[[RISK-0004-Hook-Injection-Surface]]"]
---

# A Claude session in a cockpit terminal reports through a plugin

## Summary

In a cockpit terminal opened after this change, Claude Code draws your own status line again, and `claude` runs whatever it runs in any other terminal. The rail dot, the agent row, and the cost, context and rate-limit figures still work. They now arrive through a plugin that Claude Code loads, `desktop/plugin/claude-code/`, instead of through files the cockpit generated for every project.

Three things a person notices:

- **Your status line is your own.** The cockpit used to replace it with `model · $cost` so it could read cost and context from it. It no longer does.
- **A `claude` alias now applies in cockpit terminals.** The cockpit used to unalias `claude` and run its own wrapper. On this machine the alias adds `--dangerously-skip-permissions`, so a cockpit terminal's `claude` now starts with that flag, as it does everywhere else.
- **The cost figures update when a turn ends.** The status line posted every five seconds during a turn. Claude Code's measurement fires after each turn, and when a rate-limit window moves a whole point.

A terminal opened before the change keeps the old wrapper until it is closed. Its generated files are left in place for it, because Claude Code refuses to start when the settings file it was given is missing.

## Impact

- **New: the plugin**, `desktop/plugin/claude-code/`. Its module hooks Claude Code's `classic.<Event>` events, whose input is the JSON a settings hook reads on stdin, and posts nine of them unchanged to `/api/agent-hook`. PreToolUse is rebuilt into that shape, because its mod event hands over the tool call itself. Cost, context and rate limits come from `session.measure` and are posted as the cockpit's own `Statusline` payload. The address is read from the workspace's `hook-env` on every post. Every hook passes its event on and decides nothing.
- **Changed: `desktop/src/ipc/agent-instrument.ts`.** It stops writing `claude-settings.json`, the Claude `hook-forward.sh` and `statusline.sh`. The generated `.zshrc` no longer wraps or unaliases `claude`; it appends the plugin's folder to `CLAUDE_CODE_PLUGIN_DIRS` once, after your own `.zshrc` has run. Codex's files are byte-identical to before.
- **Changed: `src/project_os_cockpit/agent_hooks.py`.** The plugin marks its posts with `_cockpit_plugin`. Once a session has sent a marked post, an unmarked Claude post for it is dropped. That is FEAT-0027's opt-in external hook capturing the same event a second time. The two-second duplicate window stays, for terminals opened before the change.
- **New CI step** in `observed-coverage`: install Claude Code 2.1.299, then `claude plugin validate` and `claude plugin test` on the plugin. Either failing fails the build.
- **Two status-line fields are no longer sent:** `total_lines_added` and `total_lines_removed`. Claude Code's measurement does not carry them, and nothing in the cockpit displays them.
- **Register:** `shell.agents.claude-plugin` is new, and `shell.agents.usage` gains a dated line.

## What was checked

- **A real session, headless.** `claude -p` on Haiku with the plugin loaded and a stand-in sidecar on port 18766. The stand-in received SessionStart, UserPromptSubmit, PreToolUse, Statusline, PostToolUse, Stop, Statusline and SessionEnd, each marked. The Statusline posts carried real figures: $0.0035, a 1,000,000-token window at 3%, the five-hour window at 4% and the seven-day window at 40%, with reset times. Fed to `AgentSessionTracker.ingest`, the eight posts gave busy, waiting and idle at the expected events, the prompt, the Bash tool and the whole cost snapshot.
- **A real session, interactive.** Claude Code started in a private tmux in this repository with the plugin loaded. It asked nothing about the plugin, drew its own bottom line, and the stand-in received SessionStart and Statusline at start and SessionEnd at `/exit`. Loading the folder interactively made Claude Code write `tsconfig.json` and `.claude-plugin/types/` into it. The types folder ignores itself; `tsconfig.json` only extends it and is committed.
- **The plugin's own tests:** 10 pass under `claude plugin test`, including with an empty HOME and no login, as on a CI runner.
- **The shell:** `desktop/tests/claude-plugin-shell.test.mjs`, 6 tests, in a real zsh with a stand-in HOME, including that HOME's `.claude` keeps its bytes and modification times. Node suite: 193 pass.
- **The sidecar:** a new tracker test; `tests/test_agent_hooks.py`, 28 pass.

## What was not checked

- **The running cockpit application.** The acceptance check, [[TST-0094-A-Claude-Session-In-A-Cockpit-Terminal-Reports-Through-The-Plugin]], is Edwin's to run after a rebuild and restart.
- **The CI step on GitHub.** It was run locally with an empty HOME; it has not run on a runner, because nothing is pushed.

## Test adequacy

Each test was shown to fail when the code it guards is broken:

- **Plugin, seven breakages, each turning at least one test red:** the kill switch ignored; Stop not forwarded; the mark dropped; any host accepted; SessionEnd not awaited; rate limits dropped; PreToolUse's tool name wrong.
- **Shell, two breakages of the built file:** assigning instead of appending, and no duplicate guard. Each failed one test.
- **Sidecar, one breakage:** the claim's drop removed. The new test failed.

The tests also found one defect, fixed before this note: SessionEnd's one-second limit ended at once when Claude Code's clock could not start a sleep, so the post was never awaited.
