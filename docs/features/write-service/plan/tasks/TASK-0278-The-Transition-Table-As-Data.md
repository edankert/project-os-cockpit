---
type: "[[task]]"
id: TASK-0278
aliases: ["TASK-0278"]
title: "The human-owned transition table as one data structure, and the endpoint that consults it"
status: done
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0059-The-Write-Service-Widens]]"]
parent: "[[FEAT-0059-The-Write-Service-Widens]]"
effort: M
depends: []
blocks: ["[[TASK-0279-The-Tick-Path]]"]
related: ["[[DES-0005-The-Actuator-Grammar]]"]
tests: []
---

# The transition table as data

## Definition of Done

- [x] One dict in `note_writes.py`, beside `DECIDE_TRANSITIONS`, mapping (type, from-status) → the actions a human may take, exactly [[DES-0005]]'s matrix.
- [x] `POST /api/notes/transition` performs one; `GET /api/notes/actions` reports what is legal (with `disabled`+`reason` where a gate blocks) so the renderer never restates vocabulary.
- [x] Every status named in the table exists in `statuses.py`; guarded by a vocabulary test in the ISS-0023 style.
- [x] An agent-owned transition in the request is a 4xx naming the ownership rule.

## Done 2026-08-10

`HUMAN_TRANSITIONS` in `note_writes.py`, keyed `(type, from-status) -> ((verb, to-status), …)`, exactly DES-0005's matrix. `GET /api/notes/actions` reports what is legal; `POST /api/notes/transition` performs one, behind the same loopback check, mtime precondition and allow-list every other write uses.

**Keyed by the note's *current* status**, so a stale renderer cannot replay an action that has since stopped being offered — the failure mode a table keyed only by type would have.

**`Defer` was added to the issue row**, per [[ADR-0020]]'s amendment: 39 issues sit at `triage` across the fleet with a median age of 56 days, and the only verbs were accept and decline, so *"real, but not now"* had nowhere to go. `deferred` was already legal in `STATUSES.md` and already carried a mark in [[DES-0004]].

### Guarded by refusal, not by offer

`tests/test_human_transitions.py` — eight assertions, and the ones that matter test what the table **will not** do:

- no close-out status (`done`, `fixed`, `merged`, `implemented`, `passing`, `verified`) is reachable from any entry
- a note in the wrong state is refused, with `REQ-0026` named in the message
- a status outside `statuses.VOCABULARY` is refused
- a stale `mtime` refuses and writes nothing
- a legal write leaves the **body byte-identical** and touches only `status:` and `updated:`

The offer is visible on screen; the refusal is not, which is why it is what the tests assert.
