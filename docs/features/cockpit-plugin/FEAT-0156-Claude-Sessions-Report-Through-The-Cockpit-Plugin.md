---
type: "[[feature]]"
id: FEAT-0156
aliases: ["FEAT-0156"]
title: "Claude Code sessions report to the cockpit through a plugin the shell loads, instead of through generated shell files and the status line"
status: done
phase: "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]"
owner: user:edwin
created: 2026-10-08
updated: 2026-10-14
source:
  - "Edwin 2026-10-08: 'Plan the implementation in a new phase.' (Claude Code mods shipped in v2.1.287)"
  - "[[REFERENCE-FUNCTION-HOOKS-REVIEW]], 'What it would change for the cockpit'"
goal: "A Claude session in a cockpit terminal reports its lifecycle, cost, context and rate limits to the sidecar through a plugin Claude Code loads, so the shell stops generating Claude settings and hook scripts and stops taking over the user's status line."
requirements: []
tasks:
  - "[[TASK-0649-The-Cockpit-Plugin-Posts-Every-Claude-Event-To-The-Sidecar]]"
  - "[[TASK-0650-The-Shell-Loads-The-Plugin-And-Stops-Generating-Claude-Files]]"
  - "[[TASK-0651-The-Sidecar-Prefers-The-Plugin-And-CI-Checks-It]]"
  - "[[TASK-0652-A-New-Cockpit-Terminal-Starts-Without-Another-Sessions-Variables]]"
  - "[[TASK-0653-The-First-Reviews-Findings-Are-Fixed]]"
release: ""
acceptance_exception: ""
acceptance: "[[TST-0094-A-Claude-Session-In-A-Cockpit-Terminal-Reports-Through-The-Plugin]]"
design: ""
reviewed_by: ["model:claude-opus-5-5 (independent-reviewer, round 1, A)", "model:claude-opus-5-5 (independent-reviewer, round 1, B)", "model:claude-opus-5-5 (independent-reviewer, round 2)"]
review_date: 2026-10-14
review_verdict: approved
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

**Started 2026-10-14.** The first of [[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]'s four features; the other three need the plugin it creates. The plan, with the event mapping checked against Claude Code 2.1.299, is `plan/PLAN.md` beside this note. The work is three tasks: [[TASK-0649-The-Cockpit-Plugin-Posts-Every-Claude-Event-To-The-Sidecar]] (the plugin), [[TASK-0650-The-Shell-Loads-The-Plugin-And-Stops-Generating-Claude-Files]] (the shell) and [[TASK-0651-The-Sidecar-Prefers-The-Plugin-And-CI-Checks-It]] (the sidecar, CI and the record). The acceptance check is [[TST-0094-A-Claude-Session-In-A-Cockpit-Terminal-Reports-Through-The-Plugin]].

## State on 2026-10-14

**Done.** All four tasks are done. Edwin walked [[TST-0094-A-Claude-Session-In-A-Cockpit-Terminal-Reports-Through-The-Plugin]] in the running app, and all seven steps passed (ledger: pass on macOS). Its step 7, the kill switch, found [[ISS-0319-Every-Cockpit-Terminal-Inherits-The-Environment-Of-The-Claude-Session-That-Started-Tmux]]: the cockpit's tmux server handed every new terminal another Claude session's variables. [[TASK-0652-A-New-Cockpit-Terminal-Starts-Without-Another-Sessions-Variables]] fixed it inside this feature. Its independent review requested changes in round 1, which [[TASK-0653-The-First-Reviews-Findings-Are-Fixed]] made, and approved them in round 2. What changed is in [[CHG-20261014-Claude-Sessions-Report-Through-The-Cockpit-Plugin]] and [[CHG-20261014-New-Cockpit-Terminals-No-Longer-Inherit-Another-Claude-Session]].

## Verification

Full runs on 2026-10-14, after the round-1 fixes ([[TASK-0653-The-First-Reviews-Findings-Are-Fixed]]):

- `python3 -m pytest -q -p no:randomly`: 2144 passed, 11 skipped.
- `node --test desktop/tests/*.test.mjs`, after `npm run build`: 196 passed.
- `npm run typecheck` in `desktop/`: clean.
- `command claude plugin validate desktop/plugin/claude-code` with Claude Code 2.1.299 and an empty HOME: passed with warnings. They name the environment variables `register.ts` reads, the managed-settings limitation RISK-0004 records, and "gating hook without .catch" for each `classic.*` hook.
- `command claude plugin test desktop/plugin/claude-code`: 13 passed.
- `bash tools/scripts/validate-docs.sh`: OK.
- TST-0094: pass on macOS, walked by Edwin, 12:38 to 13:19.

## Acceptance Criteria

*Written on 2026-10-14 at the start of the independent review. The note had none: they restate the Goal, the plan's event table and its "must not do" list as checkable statements.*

1. Each of the ten Claude events in the plan's table reaches `/api/agent-hook` from the plugin, with the fields the sidecar reads. PreToolUse is rebuilt into the stdin shape, with `tool_input.file_path`.
2. Cost, context and rate limits reach the sidecar as the existing `Statusline` payload, built from `session.measure`.
3. The plugin reads the sidecar's address from the workspace's `hook-env` on every post, so a sidecar respawned on a new port still receives the next post.
4. A failed or slow post never blocks or fails a Claude hook; only SessionEnd is awaited, for at most one second.
5. Every hook passes the event on unchanged: the plugin never answers, denies or rewrites anything in the session.
6. A new cockpit terminal appends the plugin's folder to `CLAUDE_CODE_PLUGIN_DIRS` once, after the user's own `.zshrc`, keeping any value the user set.
7. The shell no longer writes `claude-settings.json`, the Claude `hook-forward.sh` or `statusline.sh`, and the generated `.zshrc` has no `claude` wrapper. The user's own status line is not replaced.
8. Codex is unchanged: the zdotdir, `hook-env`, `codex-hook-forward.sh` and `codex-launch.sh` are written as before.
9. With `COCKPIT_NO_INSTRUMENT=1` in the app's environment, a new terminal has no `CLAUDE_CODE_PLUGIN_DIRS` entry for the plugin, and the plugin posts nothing if it is loaded anyway.
10. A new cockpit terminal carries none of another Claude session's variables, whether they came from the app's own environment or from a running tmux server's global environment.
11. Once the sidecar has accepted a plugin-marked post for a session, it ignores an unmarked Claude post for that session; Codex posts and other sessions are unaffected.
12. Nothing is written under `~/.claude`.
13. CI runs `claude plugin validate` and `claude plugin test` against Claude Code 2.1.299 and fails the build when either fails.

## Review

**Round 1, 2026-10-14: `changes-requested`.** Two `independent-reviewer` subagents ran on the same packet, each in a fresh context, with 31 and 35 tool calls. Both ran on the same model as the author. A refutation with evidence from either reviewer stands.

| # | Criterion | Combined verdict | Evidence |
|---|---|---|---|
| 1 | The ten events reach the sidecar; PreToolUse is rebuilt | **refuted** (tests) | Wiring holds: `claude plugin validate` lists all ten `classic.*` hooks. But reviewer A removed the registrations of PostToolUse, Notification, PermissionRequest, SubagentStart and SubagentStop, and `claude plugin test` still passed 10 of 10. Reviewer B: no test raises those five events. |
| 2 | Cost, context and rate limits as the `Statusline` payload | holds | Both: the status-line test passes; B checked the rate-limit kinds against the generated types and `agent_hooks.py`. |
| 3 | The address is re-read on every post | holds | Both: the test moves the port from 8766 to 9100 between posts. |
| 4 | A post never blocks a hook; SessionEnd waits at most one second | **refuted** (tests and one path) | Reviewer A replaced the one-second race with `await posting`, and all 10 plugin tests passed. Reviewer B: when `$.clock.sleep` rejects, `postWithin` falls back to waiting for the post with no limit. |
| 5 | Every hook passes its event on unchanged | holds | Both: every handler returns `next(e)` with the original event. |
| 6 | The plugin is appended once, after the user's `.zshrc` | holds | B broke the `case` guard in the built `.zshrc` and the nested-shell test failed. |
| 7 | No Claude files are generated; the user's status line is kept | holds | Both: the shell test asserts the exact file list; TST-0094 step 4 passed. |
| 8 | Codex is unchanged | holds | Both expanded the old Codex template by hand and found it identical to the new one. |
| 9 | The kill switch, in the terminal and in the plugin | holds | Both: the kill-switch tests on each side pass; TST-0094 step 7 passed. |
| 10 | No other session's variables, from the app or the tmux server | holds | B disabled the variable check in the built `terminal.js` and both tests failed. Both: the list matches the variables a 2.1.299 session sets. |
| 11 | A claimed session ignores unmarked Claude posts | holds | Both removed the claim branch and the pytest failed (1 failed, 27 passed). |
| 12 | Nothing is written under `~/.claude` | holds | Both: the fingerprint test; the validator reports no environment writes. |
| 13 | CI runs the plugin checks against 2.1.299 | holds as written; not run | Nothing is pushed, so no CI run includes the step. A ran both commands in a clean worktree, without the gitignored types folder, and both passed. |
| T | TST-0094 fails when the behaviour breaks | holds in part | B: it failed on a real break (step 7, ISS-0319). A: no step raises a notification, a permission request or a subagent, so it would miss the gap in criterion 1. |

**Findings to fix, all in code this feature changed** ([[TASK-0653-The-First-Reviews-Findings-Are-Fixed]]):

1. No test raises five of the ten events (criterion 1).
2. No test holds SessionEnd to one second, and a failed sleep removes the limit (criterion 4).
3. An event the external hook (FEAT-0027) posts before the plugin is counted twice. The plugin's mark makes the two copies differ, so the two-second check no longer matches them (both reviewers).
4. The comment in `register()` says nine events above eight registrations (both reviewers).

**Observations answered without a change:**

- *The validator warns "gating hook without .catch" for each `classic.*` hook* (A). The generated types say that without a `.catch` "a failed hook is absent", so a throw passes the event on, which is the intended behaviour. The packet's summary of the warnings was incomplete.
- *The list of Claude variables a terminal drops is fixed* (A, B). It is the set Claude Code 2.1.299 sets for its child processes. A variable a later version adds would pass through; ISS-0319 records how the list was found.
- *TST-0094's step 7 expectation was reworded after the run* (B). It was. The original said the session would not appear in the cockpit at all. That was wrong whenever the user's own `~/.claude/settings.json` registers the external hook, which reports every Claude session on the machine. The run log records the evidence: no plugin mark, no cost figures, prompt only.
- *The node tests load `desktop/dist/`* (B). The author's counts came after `npm run build`; the review packet does not show that.
- *`claude plugin test` refuses the `claude --dangerously-skip-permissions` alias* (B). Run it as `command claude`.

**Round 2, 2026-10-14: `approved`.** One `independent-reviewer` subagent in a fresh context, 10 tool calls, on the diff since `f08f3b6`. It worked on copies of the files and changed nothing in the repository.

| # | Round-1 finding | Answer | Evidence |
|---|---|---|---|
| 1 | Five events untested | fixed | Each of the five registrations removed in turn; each removal failed "the other five events are posted with what the sidecar reads" (12 pass, 1 fail). |
| 2a | SessionEnd's one-second limit untested | fixed | The race replaced with `await posting`: both new SessionEnd tests failed. The wait doubled: the one-second test failed. |
| 2b | A failed sleep removed the limit | fixed | The old fallback restored: "a clock that cannot sleep ends the wait at once" failed. |
| 3 | An event the external hook posts first is counted twice | fixed | The mark put back into the comparison, the claim from a dropped copy removed, and a post remembered before the claim check: the new pytest failed each time. Checked against the real source: a claimed session drops the external hook's copy of a new prompt and keeps the plugin's. |
| 4 | The comment miscounts the events | fixed | It now says eight go through `forward` and SessionEnd is the ninth. |

**One observation, not a finding:** the `catch` branch in `postWithin`, taken only if `$.clock.sleep` throws before returning a promise, is not tested. Changing it to wait for the post leaves all 13 tests passing. The engine turns a throwing sleep handler into a rejected promise, which the tested branch covers, and nothing shows the sleep can throw directly. Left as it is.

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

**Answered 2026-10-14, each with the note's own recommendation** (the reasons are in the plan): (1) option (b), the plugin marks its posts and the sidecar ignores an unmarked Claude post for a session the plugin claimed, and the two-second window stays for terminals opened before the change; (2) no fallback, and the warning for an older Claude Code is a follow-up issue; (3) `desktop/plugin/claude-code/`.

1. **What happens to the dedup window, given FEAT-0027's user hook?** Options: (a) keep the window; (b) the plugin marks its posts, and the sidecar ignores a user-hook post for a session the plugin has already claimed; (c) FEAT-0027's toggle installs the plugin user-wide instead of a command hook, which writes to `~/.claude` under the same consent gate it uses today. Recommendation: (b), because it removes the duplicate without changing what the user consented to.
2. **What if Claude Code is older than the pinned version?** Options: fall back to the shell-script path, or start the session uninstrumented with a visible warning. A fallback keeps two paths alive, which is what the phase is removing. Recommendation: no fallback; warn on the rail.
3. **Where does the plugin live in this repository?** For example `desktop/plugin/claude-code/`, copied into the app bundle at build. To be settled in the plan.

## Links

- Phase: [[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]
- Review this follows: [[REFERENCE-FUNCTION-HOOKS-REVIEW]]
- Code: `desktop/src/ipc/agent-instrument.ts`, `desktop/src/ipc/terminal.ts`, `src/project_os_cockpit/agent_hooks.py`
