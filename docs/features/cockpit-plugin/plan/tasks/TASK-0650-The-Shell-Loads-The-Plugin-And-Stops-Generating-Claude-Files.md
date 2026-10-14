---
type: "[[task]]"
id: TASK-0650
aliases: ["TASK-0650"]
title: "The shell loads the plugin through CLAUDE_CODE_PLUGIN_DIRS and stops generating the Claude files"
status: done
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]], candidate task 5"]
parent: "[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]"
effort: "S"
due: ""
depends: ["[[TASK-0649-The-Cockpit-Plugin-Posts-Every-Claude-Event-To-The-Sidecar]]"]
blocks: []
related: ["[[RISK-0004-Hook-Injection-Surface]]"]
tests: []
---

# The shell loads the plugin and stops generating the Claude files

A cockpit terminal's zsh puts the plugin's folder on `CLAUDE_CODE_PLUGIN_DIRS`, and the shell no longer writes a Claude settings file, hook script or status-line script.

## Definition of Done

- [x] `ensureInstrumentation` no longer writes `claude-settings.json`, `hook-forward.sh` or `statusline.sh`, and the generated `.zshrc` no longer defines a `claude` function or unaliases `claude`.
- [x] The generated `.zshrc`, after sourcing the user's `.zshrc`, appends the plugin's folder to `CLAUDE_CODE_PLUGIN_DIRS`, keeps a value the user set, and does not add the folder a second time in a nested shell.
- [x] With `COCKPIT_NO_INSTRUMENT=1` nothing is generated and the variable is not set.
- [x] Files an earlier version wrote are left in place (the reason is in the plan).
- [x] The Codex files and the Codex wrapper are byte-identical to before.
- [x] A node test runs the generated startup files in a real zsh with a stand-in HOME and shows the variable's value, the kill switch, and that HOME's `.claude` is byte-identical afterwards.
- [x] `tests/test_agent_instrument.py` guards the new wrapper-free `.zshrc` instead of the old wrapper.

## Steps

- [x] Change `desktop/src/ipc/agent-instrument.ts` and its header comment.
- [x] Update the node and Python tests.

## Result, 2026-10-14

- **`desktop/src/ipc/agent-instrument.ts`.** `claudeSettings`, `statuslineScript` and the Claude half of the forwarder are gone; `CLAUDE_HOOK_EVENTS` with them. `claudePluginDir()` returns `<app path>/plugin/claude-code`, or nothing when that folder has no `plugin.json`. The generated `.zshrc` appends the folder to `CLAUDE_CODE_PLUGIN_DIRS` after sourcing the user's `.zshrc`, inside a `case` that skips the append when the folder is already there.
- **A `claude` alias now runs inside cockpit terminals.** The old `.zshrc` unaliased `claude` so its wrapper could run. With no wrapper, the user's alias is left alone, so in a cockpit terminal `claude` now does what it does in any other terminal. On this machine that alias adds `--dangerously-skip-permissions`.
- **Codex is unchanged, byte for byte.** The old build and the new build were each run against a scratch folder. `codex-hook-forward.sh`, `codex-launch.sh`, `.zshenv` and `.zprofile` compare equal, once the scratch path is masked.
- **Tests.** `desktop/tests/claude-plugin-shell.test.mjs`, six tests, runs the built module and the generated startup files in a real zsh with a stand-in HOME. Two deliberate breakages of the built file (assigning instead of appending, and no duplicate guard) each failed one test. `desktop/tests/codex-shell-exit.test.mjs` gained `getAppPath` in its stand-in `app`. `tests/test_agent_instrument.py` now guards against the wrapper returning. The node suite is 193 passing.
