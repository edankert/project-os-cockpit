---
type: "[[plan]]"
title: "Plan — validator errors as session work"
status: done
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
parent: "[[FEAT-0051-Validator-Errors-As-Session-Work]]"
---

# Plan

Three tasks, sequenced so each is useful alone.

1. **[[TASK-0252]]** — the data. Subscribe the renderer's existing `EventSource` to `cockpit:validation` and prime it with one fetch. Pure plumbing; the endpoint, the event and the connection all exist already.
2. **[[TASK-0253]]** — the surface. Rows in `#agent-strip-detail`, in the grammar the work rows already use. Depends on 0252.
3. **[[TASK-0254]]** — the promotion. A close-out step and its guard; independent of the two above, and the only one that touches documentation rather than code.

## The decision this plan rests on

**Which errors need a human is measured, not classified.** An error still standing when the session ends needs one. No lookup table of error codes — a table would have to be kept in step with the validator's rules, and [[ISS-0023]] / [[ISS-0024]] are both records of exactly that going wrong.

## Two things to watch

**Rows must not double as a second badge.** The session panel answers *what*; the rail badge answers *which project*. If a row simply restates the count we have rebuilt what [[ISS-0068]] deleted. Each row carries a code, a message and a destination — information the badge cannot hold.

**`METRICS` is noisy by construction.** The counts go stale the moment a note is written and are corrected by `sync-snapshot.py` at pre-commit. Under this design that is fine — it appears as a row and closes on its own, which is exactly what a session work item does. It should **not** be filtered out: hiding a real check result because it is usually benign is the [[ISS-0065]] failure of teaching a reader to ignore a surface.
