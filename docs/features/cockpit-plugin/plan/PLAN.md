---
type: "[[plan]]"
title: "Delivery plan: Claude sessions report through the cockpit plugin"
status: active
owner: user:edwin
created: 2026-10-14
updated: 2026-10-14
source: ["[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]"]
implements: ["[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]"]
related: ["[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]", "[[RISK-0004-Hook-Injection-Surface]]", "[[REQ-0019-Agent-Fleet-Visibility]]"]
---

<!-- Plans deliberately carry no `id:` / `aliases:`; see docs/__templates__/plan.md. -->
# Delivery plan: Claude sessions report through the cockpit plugin

A Claude session in a cockpit terminal will report to the sidecar through a plugin that Claude Code loads, instead of through four files the shell generates. The sidecar receives the same JSON it receives today, so nothing in the sidecar's state machine or in the renderer changes. The work is three tasks.

## Where the plugin lives

The plugin is the folder `desktop/plugin/claude-code/`. The application runs from `desktop/` (`electron .`), so the shell finds the plugin at `app.getAppPath()/plugin/claude-code` and needs no copy step. A packaged build would put the folder inside an `.asar` archive, which Claude Code cannot read; packaging is parked ([[FEAT-0007]], TASK-0065), and the shell maps `app.asar` to `app.asar.unpacked` so the path is right if packaging resumes with the folder unpacked.

## How each event reaches the sidecar

Claude Code 2.1.299's mod interface fires a `classic.<Event>` event wherever it would run a settings hook of that name, whether or not a settings hook is configured. Its input is the JSON a command hook reads on stdin. So nine of the ten events are forwarded unchanged, and the sidecar cannot tell them from the shell script's posts. This was checked against the type declarations Claude Code 2.1.299 writes (`claude-code.d.ts`, `ClassicEventOf`, `ClassicHookInputs`), not against the web page.

| Event the sidecar reads | Mod event | What the plugin posts | Fields the sidecar reads (`agent_hooks.py` `ingest`) |
| --- | --- | --- | --- |
| SessionStart | `classic.SessionStart` | the input unchanged | `session_id`, `cwd`, `transcript_path` |
| UserPromptSubmit | `classic.UserPromptSubmit` | the input unchanged | `prompt` |
| PreToolUse | `classic.PreToolUse` | rebuilt: its input is the tool call (`tool`, the tool's arguments), not the stdin shape, so the plugin writes `hook_event_name`, `session_id`, `cwd`, `tool_name` and `tool_input` itself | `tool_name`, `tool_input.file_path` / `path` |
| PostToolUse | `classic.PostToolUse` | the input unchanged | `tool_name`, `tool_input` |
| Notification | `classic.Notification` | the input unchanged | `notification_type`, `message` |
| PermissionRequest | `classic.PermissionRequest` | the input unchanged | `tool_name` |
| Stop | `classic.Stop` | the input unchanged | `message` (absent in today's stdin too) |
| SubagentStart | `classic.SubagentStart` | the input unchanged | `agent_type`, `agent_id` |
| SubagentStop | `classic.SubagentStop` | the input unchanged | `agent_type`, `agent_id` |
| SessionEnd | `classic.SessionEnd` | the input unchanged, awaited for at most one second because the process is exiting | none beyond the session |
| Statusline (the cockpit's own name) | `session.measure` | rebuilt from Claude Code's measurement into today's status-line shape | `cost.total_cost_usd`, `cost.total_duration_ms`, `context_window.used_percentage`, `context_window.context_window_size`, `rate_limits.five_hour` / `seven_day` `.used_percentage` and `.resets_at` |

**Two fields the status line carried are not available.** `session.measure` reports cost in dollars only, so `total_lines_added` and `total_lines_removed` are no longer posted. Nothing displays them: `renderer.ts` declares them in `AgentCostSnapshot` and reads neither. `total_duration_ms` is computed from `$.session.usage().startedAt`. [[REQ-0019-Agent-Fleet-Visibility]] asks for cost, context and rate limits, and all three keep every field that is drawn.

**When the cost figures arrive.** The status-line script posted at most once every five seconds whenever Claude Code redrew the status line. `session.measure` fires after each main-thread turn and when a rate-limit window moves a whole point. The rail's figures therefore update at the end of a turn rather than during it.

Every post carries `"_cockpit_plugin": true` and `"agent": "claude"`, and goes to `$COCKPIT_HOOK_URL/api/agent-hook`. The plugin reads that address from the workspace's `hook-env` file on each post, because the sidecar can respawn on a new port. A post is not awaited by the hook (except SessionEnd), and a failure is swallowed, so a stalled sidecar never slows a tool call.

## The decisions on the feature's three open questions

1. **The dedup window, given FEAT-0027's user hook: option (b).** The plugin marks its posts. When the sidecar has seen a marked post for a session, it ignores an unmarked Claude post for that session. The two-second window stays: it still catches the double capture from a terminal opened before this change, whose shell keeps the old wrapper until it is closed. This matches the feature note's recommendation and changes nothing the user consented to.
2. **An older Claude Code: no fallback.** Claude Code before 2.1.287 ignores the plugin, and the session is not instrumented. The installed version is 2.1.299, and the plugin's own test runs against 2.1.299 in CI. A warning in the terminal when the installed Claude Code is older is filed as a follow-up issue, not built here, because nothing on this machine can reach that case today.
3. **Where the plugin lives:** `desktop/plugin/claude-code/`, above.

## Delivery sequence

1. **The plugin** ([[TASK-0649-The-Cockpit-Plugin-Posts-Every-Claude-Event-To-The-Sidecar]]). The folder, its manifest and its hooks module, which posts the table above. It passes `claude plugin validate`, and its `*.test.ts` pass under `claude plugin test`. A live run of `claude -p` with the plugin loaded and a stand-in sidecar shows the posts arriving.
2. **The shell loads it** ([[TASK-0650-The-Shell-Loads-The-Plugin-And-Stops-Generating-Claude-Files]]). `agent-instrument.ts` stops writing `claude-settings.json`, the Claude `hook-forward.sh` and `statusline.sh`, and drops the `claude` wrapper from the generated `.zshrc`. The `.zshrc` appends the plugin's folder to `CLAUDE_CODE_PLUGIN_DIRS` after the user's own `.zshrc` has run, once, keeping any value the user set. With `COCKPIT_NO_INSTRUMENT=1` the variable is not set. Files an earlier version wrote are left in place, because a terminal opened before the update still runs `claude --settings <that file>`, and Claude Code refuses to start when the file is missing.
3. **The sidecar, CI and the record** ([[TASK-0651-The-Sidecar-Prefers-The-Plugin-And-CI-Checks-It]]). The plugin claim in `agent_hooks.py`; a CI step that installs Claude Code 2.1.299 and runs `claude plugin validate` and `claude plugin test`; the capability register row and the change note; RISK-0004 updated; the acceptance check set to `active`.

## What the implementation must not do

- Write anything under `~/.claude` ([[RISK-0004-Hook-Injection-Surface]]).
- Change what Codex sessions receive: the zdotdir, `hook-env`, `codex-hook-forward.sh` and `codex-launch.sh` stay as they are.
- Answer, deny or rewrite anything in a Claude session. Every hook in the plugin passes the event on unchanged; drawing, submitting and answering are FEAT-0157 to FEAT-0159.
