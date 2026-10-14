---
type: "[[task]]"
id: TASK-0649
aliases: ["TASK-0649"]
title: "The cockpit plugin posts every Claude event the sidecar reads, and cost, context and rate limits"
status: done
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]], candidate tasks 1-4"]
parent: "[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]"
effort: "M"
due: ""
depends: []
blocks: ["[[TASK-0650-The-Shell-Loads-The-Plugin-And-Stops-Generating-Claude-Files]]"]
related: ["[[RISK-0004-Hook-Injection-Surface]]"]
tests: []
---

# The cockpit plugin posts every Claude event the sidecar reads

A plugin folder in this repository that Claude Code can load. Once loaded in a session whose environment names a cockpit workspace, it posts to the sidecar the same JSON the generated shell scripts post today.

## Definition of Done

- [x] `desktop/plugin/claude-code/` holds `.claude-plugin/plugin.json`, `hooks/hooks.json` and a hooks module.
- [x] The module forwards the ten events in the plan's table, and posts cost, context and rate limits from `session.measure` as a `Statusline` payload.
- [x] It reads the sidecar's address from `$COCKPIT_INSTRUMENT_DIR/hook-env` on every post, and posts nothing when `COCKPIT_NO_INSTRUMENT` is set or the address is missing.
- [x] Every hook passes its event on unchanged; none decides, rewrites or waits on the sidecar (SessionEnd waits at most one second).
- [x] `claude plugin validate desktop/plugin/claude-code` reports no error.
- [x] `claude plugin test desktop/plugin/claude-code` passes tests that fail when a post is dropped, when the kill switch is ignored, or when the address is read once instead of per post.
- [x] A live `claude -p` run with the plugin loaded and a stand-in sidecar receives SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop, SessionEnd and Statusline, recorded in this note.

## Steps

- [x] Write the manifest and the module against `claude-code.d.ts` as Claude Code 2.1.299 writes it.
- [x] Write the tests with the `claude-code/testing` kit.
- [x] Run validate, test and the live run.

## Result, 2026-10-14

- **Files.** `desktop/plugin/claude-code/.claude-plugin/plugin.json`, `hooks/hooks.json`, `hooks/register.ts` and `tests/cockpit.test.ts`.
- **Validate.** `claude plugin validate desktop/plugin/claude-code` passes on Claude Code 2.1.299, with one warning (no `author` in the manifest). It also reports a fact worth keeping: where an organization manages Claude Code, the `classic.*` hooks of a plugin a person installs do not run. That does not apply on this machine; it is recorded in [[RISK-0004-Hook-Injection-Surface]].
- **Event names must be literal.** The validator refuses `on(event, ...)` in a loop, so each of the eight forwarded events has its own `on('classic.<Event>', forward)` line.
- **Type check.** `tsc` against the 2.1.299 declarations, with the header's tsconfig kept outside the plugin folder: no errors.
- **Tests.** `claude plugin test desktop/plugin/claude-code`: 10 pass. Seven deliberate breakages each turned at least one test red: the kill switch ignored, Stop not forwarded, the mark dropped, any host accepted, SessionEnd not awaited, rate limits dropped, and PreToolUse's tool name wrong.
- **One defect found by the tests and fixed.** SessionEnd's one-second limit was a race between the post and `$.clock.sleep`. When the sleep could not start, its rejection ended the race at once and the post was never awaited. The sleep's rejection now waits for the post instead.
- **Live run.** `claude -p` on Haiku in a scratch folder, with `CLAUDE_CODE_PLUGIN_DIRS` naming the plugin, `COCKPIT_INSTRUMENT_DIR` naming a folder whose `hook-env` pointed at a stand-in sidecar on port 18766, and one allowed `cat`. The stand-in received, in order: SessionStart, UserPromptSubmit, PreToolUse (Bash, with its command), Statusline, PostToolUse, Stop, Statusline, SessionEnd. Every post carried `_cockpit_plugin: true`. The Statusline posts carried real figures: cost $0.0035, context window 1,000,000 at 3%, five-hour window at 4% and seven-day at 40%, each with its reset time.
- **The sidecar reads them as before.** The same eight posts fed to `AgentSessionTracker.ingest` gave busy, busy, busy, waiting and idle at the expected events, one prompt, the Bash tool, the full cost snapshot, and an ended session.
