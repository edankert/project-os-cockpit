---
type: "[[task]]"
id: TASK-0111
aliases: ["TASK-0111"]
title: "Validation health endpoint — run validate-docs on watcher events, cache result, SSE notify"
status: done
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-17
parent: "FEAT-0018"
tests: ["[[TST-0016]]"]
---

# Validation health endpoint

## Definition of Done
- [x] Server locates `tools/scripts/validate-docs.py` in the browsed repo root (fallback: the cockpit's own bundled copy) and runs it against that repo, capturing structured results (code, message, involved ID when parseable, repo-relative path).
- [x] Result is cached; watcher file events under `docs/` or on `SNAPSHOT.yaml` schedule a debounced (~1s) re-run.
- [x] `/api/cockpit/validation` returns `{ok, errors, warnings, checked_at}` with the standard `X-Cockpit-Schema` header.
- [x] A validation-state change (ok↔failing, or error-set delta) is announced on the existing SSE channel so clients refresh without polling.
- [x] No new Python dependencies; validator invoked as subprocess or imported module, never reimplemented.

## Notes
- Parse the validator's `ERROR [CODE] message` lines; IDs are extractable with the same `PREFIX-####` regex the index already uses.
- Exit code 2 (missing python3/SNAPSHOT) renders as "unavailable", distinct from both healthy and failing.

## Verification (2026-07-17)
- Implemented in `src/project_os_cockpit/validation.py` (`ValidationRunner`: locate → subprocess → parse → cache → debounced re-run → `cockpit:validation` ControlEvent) with the bundled fallback at `src/project_os_cockpit/validate_docs_bundled.py` (verbatim copy of `tools/scripts/validate-docs.py`); endpoint + wiring in `server.py` (`_serve_cockpit_validation`, `DocsServer.validation`, non-recursive SNAPSHOT.yaml observer — the main watcher only covers `docs/`).
- Verified by [[TST-0016]] (`tests/test_validation.py`, 11 passed incl. burst-coalescing debounce guard added at independent review; full suite 201 passed / 1 skipped) with mutation-run adequacy evidence, plus a manual curl against this repo's own docs: `200`, `X-Cockpit-Schema: 3`, `state: "ok"`, PATH-ALIAS warning parsed.
