---
type: "[[test]]"
id: TST-0014
aliases: ["TST-0014"]
title: "Dispatch ledger, queue-requests, status-aware verbs, CLI"
status: passing
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
scope: feature
kind: automated
level: integration
entrypoint: ".venv/bin/python -m pytest tests/test_dispatch_ledger.py"
features: ["[[FEAT-0025-Dispatch-Runtime]]", "[[FEAT-0026-Verb-Polish]]"]
tasks: ["[[TASK-0135]]", "[[TASK-0136]]", "[[TASK-0137]]"]
---

# TST-0014 — Dispatch ledger + verbs

## What it verifies

`tests/test_dispatch_ledger.py` (7 tests): pending dispatches stamp the next session that starts (and attach directly to a live one); `dispatch_history` reports pending vs session-bound entries with live flag and cost; `POST /api/cockpit/dispatch` validates and normalises IDs; `GET /api/cockpit/dispatch-requests` hands CLI requests off exactly once; `/api/render` carries `dispatch_history` only for dispatched notes; default `when:` lists encode the lifecycle (no implement-on-done, no close-out-on-backlog) and always-on entries stay `when`-less; YAML `when` passthrough normalises case; `cockpit dispatch` posts `{id, enqueue, verb, agent}`.

## Evidence

- 2026-07-06: `7 passed`; full suite `186 passed, 1 skipped`.
- 2026-07-06: live smoke against this repo's docs — dispatch record → requests handoff (once-only) → `dispatch_history` pending entry on TASK-0115's render payload.
