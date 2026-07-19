---
type: "[[test]]"
id: TST-0013
aliases: ["TST-0013"]
title: "Agent verb registry — defaults, YAML override, endpoint"
status: passing
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
scope: feature
kind: automated
level: integration
entrypoint: ".venv/bin/python -m pytest tests/test_agent_actions.py"
features: ["[[FEAT-0024-Agent-Verbs]]"]
tasks: ["[[TASK-0131]]"]
---

# TST-0013 — Verb registry

## What it verifies

`tests/test_agent_actions.py` (4 tests): every dispatchable type ships verbs with exactly one default and `{id}`/`{rel}` slots; `tools/adapters/cockpit/actions.yaml` replaces a type wholesale while invalid entries are dropped and untouched types keep the built-ins; malformed YAML falls back to defaults without erroring; `GET /api/cockpit/actions` serves the registry.

## Evidence

- 2026-07-06: `4 passed`; full suite `179 passed, 1 skipped`.
- 2026-07-06: live endpoint check — task: implement*/refine/review/close-out, issue: fix*/triage/reproduce, feature: break-down*/implement-next/refine/close-out, requirement: implement*/refine/verify, phase: groom*/status-sweep/close-out, risk: mitigate*/reassess.
