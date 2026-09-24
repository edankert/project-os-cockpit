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
updated: 2026-09-23
related: ["[[FEAT-0019-Agent-Hook-Ingestion]]", "[[PHASE-007-Agent-Instrumentation]]", "[[RISK-0001-Terminal-Exposure]]", "[[ISS-0312]]", "[[CHG-20260916-Show-Codex-session-state-and-temperature-in-cockpit]]"]
mitigation_tasks: ["[[TASK-0633]]", "[[TASK-0634]]", "[[TASK-0635]]", "[[TASK-0636]]", "[[TASK-0637]]"]
mitigation:
  - "Per-spawn injection only for terminal instrumentation: generated settings/hooks files live under the app's own state dir and are passed via env/flags; user agent configuration is written ONLY by the explicit agent-specific settings toggle (FEAT-0027) — marker-identified entries, one-time backup, surgical uninstall."
  - "Treat /api/agent-hook payloads as untrusted: validate shape, cap size, never render content as HTML, rate-limit per source."
  - "Bind the ingestion endpoint loopback-only (same boundary as the terminal endpoint, see RISK-0001)."
  - "Version-pin against hook schema drift: tolerate unknown events/fields, log-and-drop rather than error."
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
