---
type: "[[task]]"
id: TASK-0661
aliases: ["TASK-0661"]
title: "Every project's Codex hooks run one identical command, so trusting them once in Codex covers every project"
status: done
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[ISS-0322-Codex-In-A-Cockpit-Terminal-Reports-Nothing-To-The-Sidecar]], proposed fix 2", "Edwin 2026-10-14: 'yes, implement both parts'"]
parent: "[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]"
effort: "XS"
due: ""
depends: []
blocks: []
related: ["[[TASK-0660-A-Dispatch-Checks-What-Runs-In-The-Terminal-Before-Typing]]", "[[FEAT-0019]]"]
tests: []
---

# Every project uses one Codex hook command

Codex keeps one trust entry per hook event, `/<session-flags>/config.toml:<event>:0:0`, holding a hash of the hook's command (ISS-0322). Each project's command names its own instrument folder, `instrument/<workspace>/codex-hook-forward.sh`. So trusting the hooks in one project marks them modified in every other, and Codex leaves them out there until the person reviews them again. On 2026-10-14 they were trusted only in project-os-deck.

## What changes

- `agent-instrument.ts` writes one forwarder, `instrument/codex-hook-forward.sh`, and every project's `codex-launch.sh` points its ten hooks at it. The command string, and so each hash, is the same in every project.
- The forwarder finds the project's sidecar from `$COCKPIT_INSTRUMENT_DIR/hook-env`. Every cockpit terminal sets that variable, and Codex passes its session's environment to hooks (`codex-rs/hooks/src/engine/command_runner.rs`, `build_command`, tag `rust-v0.162.1`). Without it the event is dropped, as an unset address is today.
- The per-project forwarder is no longer written. An old one left on disk is harmless: nothing points at it.

The first Codex start after this change shows Codex's hook review once more, because the command changed. After that one review, no project asks again.

## Definition of Done

- [x] A test: two projects' generated `codex-launch.sh` files carry byte-identical hook flags.
- [x] A test: the shared forwarder posts to the address in `$COCKPIT_INSTRUMENT_DIR/hook-env`, and posts nothing without that variable or with `COCKPIT_NO_INSTRUMENT` set.
- [x] The existing `codex-shell-exit` test still passes.

## Result, 2026-10-14

- `agent-instrument.ts`: `instrumentRoot()`; the forwarder is written once to `instrument/codex-hook-forward.sh` and reads `$COCKPIT_INSTRUMENT_DIR/hook-env`; `codexHookArgs()` no longer takes a folder.
- Tests: `desktop/tests/codex-hook-command.test.mjs` (two projects' launchers carry identical hook flags with no project folder in them; the forwarder posts to the terminal's own sidecar, and posts nothing with no folder or with the kill switch). With the forwarder reading `hook-env` beside itself again, the second test fails. `codex-shell-exit.test.mjs` now runs its hook with `COCKPIT_INSTRUMENT_DIR`, as Codex does; `claude-plugin-shell.test.mjs` expects the forwarder at the root.
- Desktop suite: 210 passed.

The first Codex start in each terminal opened after this change shows Codex's hook review once, because the command changed.
