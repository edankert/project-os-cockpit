---
type: "[[test]]"
id: TST-0012
aliases: ["TST-0012"]
title: "Scoped stats payload + cache"
status: passing
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
scope: feature
kind: automated
level: integration
entrypoint: ".venv/bin/python -m pytest tests/test_stats_scope.py"
features: ["[[FEAT-0023-Overview-Scopes]]"]
tasks: ["[[TASK-0128]]"]
---

# TST-0012 — Scoped stats

## What it verifies

`tests/test_stats_scope.py` (4 tests) covers `stats_payload(index, scope=…)`: hero/phases/activity filtered to the phase with inheritance via parent feature and `features:`-link fallback (tests/changes), `exit_criteria` parsed from the phase note's Exit Criteria section only (Notes section excluded), `scope` block contents, `None` for unknown scopes (endpoint 404), `Index.generation` incrementing on invalidation, and the endpoint cache serving stale-until-invalidated then refreshing after `invalidate()` bumps the generation.

## Evidence

- 2026-07-06: `4 passed`; full suite `175 passed, 1 skipped`.
- 2026-07-06: live check against this repo's docs — `?scope=PHASE-007` returned 5 features / 17 tasks (11 done) / 6 exit criteria / scoped recent feed; unknown scope → 404.
