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
updated: 2026-07-05
related: ["[[FEAT-0019-Agent-Hook-Ingestion]]", "[[PHASE-007-Agent-Instrumentation]]", "[[RISK-0001-Terminal-Exposure]]"]
mitigation:
  - "Per-spawn injection only for terminal instrumentation: generated settings/hooks files live under the app's own state dir and are passed via env/flags; ~/.claude is written ONLY by the explicit settings toggle (FEAT-0027) — marker-identified entries, one-time backup, surgical uninstall."
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
