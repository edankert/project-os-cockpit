---
type: "[[task]]"
id: TASK-0111
aliases: ["TASK-0111"]
title: "Validation health endpoint — run validate-docs on watcher events, cache result, SSE notify"
status: backlog
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-05
parent: "FEAT-0018"
---

# Validation health endpoint

## Definition of Done
- [ ] Server locates `tools/scripts/validate-docs.py` in the browsed repo root (fallback: the cockpit's own bundled copy) and runs it against that repo, capturing structured results (code, message, involved ID when parseable, repo-relative path).
- [ ] Result is cached; watcher file events under `docs/` or on `SNAPSHOT.yaml` schedule a debounced (~1s) re-run.
- [ ] `/api/cockpit/validation` returns `{ok, errors, warnings, checked_at}` with the standard `X-Cockpit-Schema` header.
- [ ] A validation-state change (ok↔failing, or error-set delta) is announced on the existing SSE channel so clients refresh without polling.
- [ ] No new Python dependencies; validator invoked as subprocess or imported module, never reimplemented.

## Notes
- Parse the validator's `ERROR [CODE] message` lines; IDs are extractable with the same `PREFIX-####` regex the index already uses.
- Exit code 2 (missing python3/SNAPSHOT) renders as "unavailable", distinct from both healthy and failing.
