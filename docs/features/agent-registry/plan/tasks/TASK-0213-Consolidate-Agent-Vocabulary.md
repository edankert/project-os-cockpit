---
type: "[[task]]"
id: TASK-0213
title: "Consolidate the agent vocabulary into one served registry (ISS-0032)"
status: done
phase: "[[PHASE-999]]"
owner: user:edwin
created: 2026-07-27
updated: 2026-07-27
source: ["[[ISS-0032]]"]
parent: "[[FEAT-0025]]"
effort: "M"
due: ""
depends: []
blocks: []
related: ["[[ISS-0023]]", "[[TST-0019]]"]
tests: []
---

# Consolidate the agent vocabulary (ISS-0032)

## Definition of Done

- [x] `src/project_os_cockpit/agents.py` is the single declaration of dispatchable agents, in the shape `statuses.py` uses for statuses — evidence: `agents.py`; `AGENTS` + `AGENT_IDS`, with `resolve_dispatch_agent` returning None rather than a sibling
- [x] The registry is **served**, not restated: the renderer and main process consume it rather than declaring their own union — evidence: `GET /api/cockpit/agents` (`server.py:_serve_cockpit_agents`); renderer `loadAgentRegistry()` + `resolveDispatchAgent()`; `test_renderer_resolves_through_the_registry`
- [x] A queued item for an unrecognised agent no longer fails validation and vanish on restart — evidence: `dispatch-queue.ts` validates shape only; `test_queue_validator_does_not_check_membership`, and the inversion run confirms restoring the membership check fails it
- [x] The two coercions (`renderer.ts:5989`, `main.ts:232`) reject or preserve an unrecognised agent instead of relabelling it `claude` — evidence: `renderer.ts` agent-set now rejects via `resolveDispatchAgent`; `main.ts` preserves `currentAgent` verbatim; `test_no_agent_coercion` over both files
- [x] The agent radio menu is built from the registry, not from two literal entries — evidence: `main.ts` iterates `menuAgents` from the payload; `test_main_builds_the_menu_from_the_payload`
- [x] `cli.py`'s `--agent` accepts the registry's ids rather than a hardcoded list — evidence: `choices=list(agents.AGENT_IDS)`; `test_registry_is_the_only_python_declaration`
- [x] Dispatchable (closed) and recordable (open) stay separate: a record or signal from an agent the cockpit cannot launch is still accepted and still displays under its own name — evidence: `agent_hooks.py`/`server.py` untouched and still preserve any string; `test_ingestion_paths_do_not_gate_on_dispatchability` asserts neither imports `is_dispatchable`; `label_for('kimi') == 'kimi'`
- [x] A parity test in TST-0019's shape parses every surface and fails if one restates or drops a member — evidence: `tests/test_agent_vocabulary.py`, 16 tests; adequacy verified by reverting all six fixes one at a time, each caught by the matching test
- [x] The full suite passes — evidence: 330 passed, 1 skipped; `tsc --noEmit` clean; desktop bundle rebuilt so the stale-build guard passes

## Steps

- [x] Write `agents.py` with the registry and the resolve/label helpers
- [x] Serve it from the sidecar and consume it in the renderer + main process
- [x] Open the queue validator; keep the shape checks, drop the membership check
- [x] Replace the coercions
- [x] Write the parity test, and verify it FAILS when a surface is reverted

## Result

Nine sites reduced to one declaration plus a served payload. The real defect — the queue discarding a third agent's work on restart — is fixed and guarded.

One thing found while writing the test: the first version of `test_queue_validator_does_not_check_membership` failed against the *comment* explaining the old code. A check that reads prose fires on the explanation of a fix rather than on the defect, so every pattern check now runs through `_code_only()`. Worth recording because the comments in these files deliberately quote what they replaced.

## Notes

Blocks adding Kimi as a dispatch target. Doing it in the other order would have turned a latent queue-validation bug into silent loss of queued work.

The distinction the fix rests on: **dispatchable is closed, recordable is open.** The ingestion path (`agent_hooks.py`, `server.py`, `cli.py signal`) was already correct and freeform — it must stay that way. A session record naming an agent the cockpit cannot launch is legitimate history, not bad data.
