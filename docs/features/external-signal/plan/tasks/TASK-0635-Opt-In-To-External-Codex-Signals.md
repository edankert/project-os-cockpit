---
type: "[[task]]"
id: "TASK-0635"
title: "Opt in to Codex signals from external terminals"
status: "doing"
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: "user:edwin"
created: "2026-09-23"
updated: "2026-09-23"
source: ["User request, 2026-09-23", "docs/reference/codex-parity-review-2026-09-23.md"]
parent: "[[FEAT-0027]]"
effort: "M"
depends: ["[[TASK-0634]]"]
blocks: []
related: ["[[ISS-0312]]", "[[RISK-0004]]"]
tests: ["[[TST-0011]]", "[[TST-0015]]"]
---

# Opt in to Codex signals from external terminals

## Definition of Done

- [x] Add a separate Codex external-terminal setting, disabled by default, with an explanation of the configuration it changes.
- [x] Install and remove only cockpit-owned native Codex hook entries. Preserve unrelated hooks, settings, authentication and normal hook trust review. Refuse malformed configuration without replacing it.
- [x] Prove enable, repeated enable, disable and restart against disposable home/config fixtures, including paths with spaces and pre-existing user hooks.
- [x] Prove external signals reach the correct workspace with and without a sidecar. Simultaneous embedded and external events must not duplicate activity or queue delivery.
- [x] Extend TST-0015 and the external-session TST-0011 procedure. Record live coverage separately from fixture coverage; never enable instrumentation in the real user configuration as an automatic test step.

## Steps

- Confirm the installed behavior and capture a minimal reproduction.
- Deliver only this task's bounded result and record verification evidence.
- Update ISS-0312 and the parent plan before moving focus.

## Notes

The user request authorizes implementation of the opt-in capability; only a deliberate settings action enables it in the user home. Reuse the existing external-session discovery and decay paths. Codex global configuration format must be verified before choosing the editor.

The source request and scope decision are recorded verbatim in [[ISS-0312]]. [[RISK-0004]] covers schema drift, configuration preservation and event identity. No new dependency or endpoint is authorized by this task.

## Handoff, 2026-09-23

The separate setting is implemented. Disposable configuration tests cover enable, refresh, removal, user handlers, malformed input and quoted paths; Python tests cover fallback, interruption and duplicate delivery. The real external Codex CLI completed EXTERNAL_CODEX_OK through the isolated setting. An isolated app restart preserved the enabled setting; disabling it through Settings removed the entries. Production opt-in remains untouched.

See [the verification report](../../../../reference/codex-parity-verification-2026-09-23.md). Keep this task doing because its linked TST-0011 manual gate remains open. Fresh independent review is owed before FEAT-0027 closes.
