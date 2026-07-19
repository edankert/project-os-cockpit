---
type: "[[task]]"
id: TASK-0128
aliases: ["TASK-0128"]
title: "Scoped stats endpoint + payload cache"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
parent: "[[FEAT-0023-Overview-Scopes]]"
effort: "M"
depends: []
blocks: ["[[TASK-0129]]"]
related: []
tests: ["[[TST-0012]]"]
---

# Scoped stats endpoint + cache

## Definition of Done
- [x] `stats_payload(index, scope="PHASE-####")` filters hero, status_mix, phases (single entry), and activity (weekly + recent) to items whose phase resolves to the scope (inheritance via parent feature preserved).
- [x] Scoped payload carries `scope: {id, title, status, rel}` and `exit_criteria: [{text, done}]` parsed from the phase note's Exit Criteria section checkboxes.
- [x] Unknown scope returns `scope: null` semantics (404 from the endpoint).
- [x] `Index.generation` increments on build + every invalidation; `/api/cockpit/stats` serves a cached payload (per scope) while the generation is unchanged.
- [x] Tests green (TST-0012).

## Steps
- [x] `scope` param threading: `_serve_cockpit_stats(query)` → `stats_payload`.
- [x] Filter step after `_phase_id_of` helpers; exit-criteria regex over `rec.body`.
- [x] Generation counter + cache dict in `_make_handler`.
- [x] Tests: scoped hero counts, exit criteria, cache-hit behaviour, unknown scope.

## Notes
Also fixes the "stats has zero caching" finding from the 2026-07-06 Overview review (fix 6).
