---
type: "[[risk]]"
id: RISK-0004
aliases: ["RISK-0004"]
title: "Hook injection modifies agent CLI configuration surfaces"
status: open
severity: medium
likelihood: medium
owner: user:edwin
created: 2026-07-05
updated: "2026-10-14"
related: ["[[FEAT-0019-Agent-Hook-Ingestion]]", "[[PHASE-007-Agent-Instrumentation]]", "[[RISK-0001-Terminal-Exposure]]", "[[ISS-0312]]", "[[CHG-20260916-Show-Codex-session-state-and-temperature-in-cockpit]]", "[[PHASE-046-A-Claude-Session-Talks-To-The-Cockpit-Through-A-Plugin]]", "[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]]", "[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]]", "[[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]]"]
mitigation_tasks: ["[[TASK-0633]]", "[[TASK-0634]]", "[[TASK-0635]]", "[[TASK-0636]]", "[[TASK-0637]]"]
mitigation:
  - "Per-spawn injection only for terminal instrumentation: Claude Code loads the cockpit plugin from CLAUDE_CODE_PLUGIN_DIRS (FEAT-0156) and Codex gets generated hooks files under the app's own state dir, passed via env/flags; user agent configuration is written ONLY by the explicit agent-specific settings toggle (FEAT-0027) — marker-identified entries, one-time backup, surgical uninstall."
  - "Treat /api/agent-hook payloads as untrusted: validate shape, cap size, never render content as HTML, rate-limit per source."
  - "Bind the ingestion endpoint loopback-only (same boundary as the terminal endpoint, see RISK-0001)."
  - "Version-pin against hook schema drift: tolerate unknown events/fields, log-and-drop rather than error; CI validates and tests the Claude plugin on the Claude Code version it declares (2.1.299)."
  - "Honest UX for the Codex one-time trust prompt — never auto-approve trust on the user's behalf."
  - "Kill switch: a single setting disables all injection, reverting to voluntary cockpit-signal behaviour."
---

# RISK-0004 — Hook injection surface

## Hazard

FEAT-0019 injects lifecycle-hook configuration into Claude Code and Codex sessions spawned in the embedded terminal, and opens a new unauthenticated localhost endpoint (`/api/agent-hook`) that those hooks POST to. Three failure modes: (1) injection leaks into the user's own agent configuration or subtly changes agent behaviour outside the cockpit (e.g. a stray settings write, or hook latency slowing every tool call); (2) the endpoint trusts payloads it shouldn't — any local process can POST fabricated agent state, or a hostile payload could be rendered into the UI; (3) upstream hook/notify schemas are version-unstable, so a CLI update silently breaks ingestion and the cockpit shows stale or wrong agent state (worse than no state — the user trusts a green dot).

## Likelihood

Medium — hook schemas have already churned across CLI versions in 2026, and config-surface accidents are easy to make when generating per-spawn files.

## Severity

Medium — no data loss, but wrong agent-state display undermines the core promise of the phase, and mutating a developer's `~/.claude` would be a serious trust breach.

## Mitigations

See frontmatter `mitigation` list. The kill switch and the never-touch-user-config rule are the two non-negotiables; schema-drift tolerance (log-and-drop unknown events) keeps a CLI upgrade from breaking the cockpit. Verification: a test asserting `~/.claude` / `~/.codex` mtimes are untouched by a spawn-instrument-teardown cycle, plus endpoint fuzz tests for malformed payloads.

The 2026-09-16 Codex follow-up uses one per-launch command hook for each lifecycle event. The hook posts to the workspace sidecar and returns no approval decision. It does not bypass Codex hook trust or write user configuration. Hook payloads contain session ids and may contain prompts; the sidecar clips stored prompts, and the project-state file stores only agent, state, message, time, and a bounded set of session statuses. A live walkthrough must confirm that trust review and user/project hooks all behave as documented.

The command path in a Codex hook is parsed twice: TOML reads the string, then a shell runs the decoded command. Quoting only for TOML left the path under `Application Support` split at its space. The generated command now retains shell quotes inside the TOML string, and a test runs that decoded command through `/bin/sh` ([[CHG-20260916-Fix-Codex-status-and-Needs-You-feed]]).

### Codex account quota contract (2026-09-16)

[[TASK-0628]] also depends on the installed CLI's documented app-server account API. Schema drift, missing login, or a CLI absent from the GUI environment can prevent quota reads. The reader accepts only a numeric weekly percentage from the general Codex bucket, bounds stdout and process lifetime, discards raw account fields, and shows no invented zero on failure. It starts no thread, sends no prompt, requests no login, and writes no CLI configuration. Last-known values retain their original capture age; unavailable data never becomes a fresh measurement.

### Codex parity mitigations — 2026-09-23

- [[TASK-0633]] verifies real trust and state transitions in isolated application/workspace state. Preserve the user's active sessions and real configuration.
- [[TASK-0634]] confirms installed payloads and parent/child identity before mapping subagent stop or interruption to state. Queue release must follow the parent lifecycle.
- [[TASK-0635]] adds the Codex consent path. Test preservation of unrelated entries, malformed configuration refusal, backup, repeated enable, surgical removal, sidecar absence and duplicate suppression in disposable configuration.
- [[TASK-0636]] observes usage only through a supported read-only path. Bound process/output lifetime, do not retain credentials in evidence, and never create or resume a thread or send a keep-warm request.
- [[TASK-0637]] reports the actual enforcement boundary. Missing reviewer identity cannot become a claim of enforced tool budgets.

The external hook exception applies only when the person deliberately enables that agent's settings toggle. Launching an embedded session must still leave both real user configuration directories unchanged.

## September 23 mitigation evidence

The Codex installer preserves unrelated handlers and refuses malformed configuration; tests use disposable homes. Normal hook trust was observed in real embedded and external Codex launches. Interruption stays held after a real late background tool completion, and child events preserve parent identity. Duplicate embedded/external forwarding is covered by the ingestion fixture. Production user configuration was not changed. The remaining live and shared-parser checks are recorded under ISS-0312.

## Claude sessions report through a plugin — 2026-10-14

[[FEAT-0156-Claude-Sessions-Report-Through-The-Cockpit-Plugin]] replaced the Claude half of the generated files with a plugin, `desktop/plugin/claude-code/`, that Claude Code loads from `CLAUDE_CODE_PLUGIN_DIRS`. What that changes for this risk:

- **Nothing is written under `~/.claude` to load it.** The variable is set by the cockpit terminal's generated `.zshrc`, appended to any value the user set. `desktop/tests/claude-plugin-shell.test.mjs` runs the generated startup files in a real zsh with a stand-in HOME and asserts that HOME's `.claude` folder has the same bytes and modification times afterwards. That is this risk's verification test, now run on every node suite.
- **The plugin runs inside Claude Code's process, with no sandbox.** Every hook in it passes its event on unchanged and decides nothing. It reads two environment variables and one file (`hook-env`), and posts only to a loopback address; any other address in `hook-env` is refused. `claude plugin validate` lists exactly these calls.
- **A version pin against interface drift.** The mods interface shipped in v2.1.287 and may change between releases. The plugin is tested on Claude Code 2.1.299; the `observed-coverage` workflow installs that version and runs `claude plugin validate` and `claude plugin test`, failing the build on either. A Claude Code older than 2.1.287 ignores the plugin, and the session is simply not instrumented (filed as a follow-up for a visible warning).
- **One condition that silently stops it.** `claude plugin validate` reports that where an organization manages Claude Code, the `classic.*` hooks of a plugin a person installs do not run. Every lifecycle event the cockpit reads is one of those. This does not apply on this machine; on a managed machine the plugin would have to be listed in managed settings.
- **Generated files from before the change are left in place**, not deleted. A terminal opened before the update still runs `claude --settings <that file>`, and Claude Code refuses to start when the file is missing.
- **The kill switch still holds.** With `COCKPIT_NO_INSTRUMENT=1` nothing is generated and the variable is not set; the plugin also checks the variable before every post.

## The plugin starts to submit prompts — planned 2026-10-14

[[FEAT-0158-A-Dispatched-Prompt-Is-Submitted-Not-Typed]] gives the plugin its first act that is more than passing an event on: it submits a dispatched prompt with `$.prompt.submit`, and it may stop its own submission from a `prompt.submit` hook when the person cancels. It also runs a one-second `$.clock.every` poll of the sidecar. What that changes for this risk:

- **More of the mods interface is depended on.** `$.prompt.submit`, `turn.start`, `turn.complete`, `prompt.submit` and `$.clock.every` join the calls CI already tests on Claude Code 2.1.299. The plugin's tests cover each one, so a change in their meaning fails the build rather than the session.
- **The hook still never turns a `deny` into an `allow`.** Its one new answer is `{ drop }`, for this plugin's own cancelled prompt, and it lets every other prompt through unchanged.
- **The new hazard is not here.** A sidecar route that takes prompt text is [[RISK-0012-A-Local-Request-Can-Put-A-Prompt-Into-A-Claude-Session]].
