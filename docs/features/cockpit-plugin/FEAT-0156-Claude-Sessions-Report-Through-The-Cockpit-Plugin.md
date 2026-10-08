---
type: "[[feature]]"
id: FEAT-0156
aliases: ["FEAT-0156"]
title: "Claude Code sessions report to the cockpit through a plugin the shell loads, instead of through generated shell files and the status line"
status: backlog
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-08
updated: 2026-10-08
source:
  - "Edwin 2026-10-08: 'Plan the implementation in a new phase.' (Claude Code mods shipped in v2.1.287)"
  - "[[REFERENCE-FUNCTION-HOOKS-REVIEW]], 'What it would change for the cockpit'"
goal: "A Claude session in a cockpit terminal reports its lifecycle, cost, context and rate limits to the sidecar through a plugin Claude Code loads, so the shell stops generating Claude settings and hook scripts and stops taking over the user's status line."
requirements: []
tasks: []
release: ""
acceptance_exception: ""
acceptance: ""
design: ""
related:
  - "[[FEAT-0019-Agent-Hook-Ingestion]]"
  - "[[FEAT-0027]]"
  - "[[RISK-0004-Hook-Injection-Surface]]"
  - "[[REQ-0019-Agent-Fleet-Visibility]]"
  - "[[FEAT-0157-The-Project-State-Sits-Above-The-Claude-Prompt]]"
  - "[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]"
  - "[[FEAT-0159-A-Permission-Prompt-Is-Answered-From-The-Cockpit]]"
---

# Claude sessions report through the cockpit plugin

**Not started.** Filed at `backlog` in the planned [[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]. It is the first of the phase's four features, and the other three need the plugin it creates.

## Goal

A Claude session started in a cockpit terminal shows the same rail dots, agent rows, cost, context and rate limits as today. The difference is how they arrive. Today the shell generates a `claude` wrapper, a settings file with ten command hooks, a forwarding script and a status-line script for every workspace (`desktop/src/ipc/agent-instrument.ts:1-30`). After this feature, the shell sets one environment variable, and a plugin that Claude Code loads posts the same payloads to `/api/agent-hook`. The user's own status line works again, because the cockpit no longer replaces it.

## Findings

- **What is generated today, and what stays.** `agent-instrument.ts` writes, per workspace: a zdotdir whose `.zshrc` wraps both `claude` and `codex`, `claude-settings.json`, `hook-forward.sh`, `statusline.sh`, `codex-hook-forward.sh`, `codex-launch.sh` and `hook-env`. Only the Claude pieces go: the `claude` function in `.zshrc`, `claude-settings.json`, the Claude `hook-forward.sh` and `statusline.sh`. The zdotdir, `hook-env` and both Codex files stay, because Codex still uses them.
- **The ten events.** `CLAUDE_HOOK_EVENTS` (`agent-instrument.ts:36-47`) is SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Notification, PermissionRequest, Stop, SubagentStart, SubagentStop and SessionEnd. Each needs a mod event that carries the same information, or stays a plain command hook inside the plugin's `hooks.json`. The mapping has to be checked against the mods reference page before any code; Notification and PermissionRequest are the two most likely to have no direct mod event.
- **The status line was a telemetry channel.** `statusline.sh` POSTs cost, context and rate limits, debounced to one every five seconds, and `agent_hooks.py:7` calls the result a "cockpit-defined" `Statusline` event. `session.measure` and `$.session.usage()` carry the same numbers. The plugin should post them as the same `Statusline` payload, so nothing in the sidecar or the renderer changes and [[REQ-0019-Agent-Fleet-Visibility]] keeps every field.
- **The sidecar's address changes.** The sidecar can respawn on a new port, which is why `hook-env` is rewritten. The plugin has to read the current address on each post (from `hook-env` or the discovery file), not once at session start.
- **Loading without touching `~/.claude`.** `CLAUDE_CODE_PLUGIN_DIRS` loads a plugin directory with no install step, so [[RISK-0004-Hook-Injection-Surface]]'s rule holds by construction. The shell must append to any value the user already set, not replace it. The plugin ships inside the cockpit app; it is not installed into any fleet repo.
- **The kill switch.** `COCKPIT_NO_INSTRUMENT=1` must mean the variable is not set at all, and the plugin must also honour it at runtime, as the scripts do today (`agent-instrument.ts:63,87,105,189`; `terminal.ts:168`).
- **The two-second dedup window.** `agent_hooks.py:60-67` drops a payload identical to one seen within 2 s. It exists because a cockpit-terminal session with [[FEAT-0027]]'s opt-in user hook enabled fires both paths. Replacing the cockpit's own path with a plugin does not remove that second path: the user hook lives in `~/.claude/settings.json` and fires in every terminal. So the window can only go once one of the options in the open questions below is chosen.
- **Version.** Mods shipped in v2.1.287; the installed version on 2026-10-08 is 2.1.292. A hook has a 10 s limit, and waiting inside a mods API call does not count toward it.

### Candidate tasks, minted when this feature starts

1. Check the event mapping against the mods reference, and write it down as a table in the plan: each of the ten events, its mod event or command hook, and the payload fields the sidecar reads.
2. Create the plugin directory with `hooks/hooks.json` and `register.ts`, passing `claude plugin validate`.
3. Post the lifecycle events to `/api/agent-hook` with the existing payload shape, re-reading the sidecar address per post.
4. Post cost, context and rate limits from `session.measure` / `$.session.usage()` as the existing `Statusline` payload.
5. Make the shell set `CLAUDE_CODE_PLUGIN_DIRS` for cockpit terminals, honour the kill switch, and stop generating the Claude files.
6. Remove the dedup window, or narrow it, according to the decision on the open question.
7. Run `claude plugin validate` and `claude plugin test` in CI against the pinned version; extend RISK-0004's `~/.claude` mtime test to the plugin path.

## Open questions

1. **What happens to the dedup window, given FEAT-0027's user hook?** Options: (a) keep the window; (b) the plugin marks its posts, and the sidecar ignores a user-hook post for a session the plugin has already claimed; (c) FEAT-0027's toggle installs the plugin user-wide instead of a command hook, which writes to `~/.claude` under the same consent gate it uses today. Recommendation: (b), because it removes the duplicate without changing what the user consented to.
2. **What if Claude Code is older than the pinned version?** Options: fall back to the shell-script path, or start the session uninstrumented with a visible warning. A fallback keeps two paths alive, which is what the phase is removing. Recommendation: no fallback; warn on the rail.
3. **Where does the plugin live in this repository?** For example `desktop/plugin/claude-code/`, copied into the app bundle at build. To be settled in the plan.

## Links

- Phase: [[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]
- Review this follows: [[REFERENCE-FUNCTION-HOOKS-REVIEW]]
- Code: `desktop/src/ipc/agent-instrument.ts`, `desktop/src/ipc/terminal.ts`, `src/project_os_cockpit/agent_hooks.py`
