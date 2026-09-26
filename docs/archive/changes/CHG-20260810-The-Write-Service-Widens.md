---
type: "[[change]]"
id: CHG-20260810-The-Write-Service-Widens
title: "Three verbs join note_writes — transition, tick and create — and the hardening suite found an endpoint that had been LAN-writable since FEAT-0011"
status: merged
reviewed_by: ""
review_date: ""
review_verdict: ""
date: 2026-08-10
owner: user:edwin
component: [note-writes, server]
related: ["[[FEAT-0059-The-Write-Service-Widens]]", "[[ISS-0129-Check-Toggle-Mutated-Notes-For-Any-LAN-Peer]]", "[[REQ-0026-Only-Human-Owned-Transitions]]", "[[REQ-0027-Every-Write-Guarded]]", "[[REL-0001-The-Human-Has-Levers]]"]
---

# The write service widens

## What changed

Three endpoints, all behind the guards `note_writes.py` already had:

| endpoint | what it does |
|---|---|
| `POST /api/notes/transition` | one human-owned lifecycle move |
| `GET /api/notes/actions` | what is legal for a note in its current state |
| `POST /api/notes/tick` | resolve one criterion, ticked with evidence or reconciled with a reason |
| `POST /api/notes/create` | file an issue from the template |

`HUMAN_TRANSITIONS` is DES-0005's matrix as data, keyed `(type, from-status)`. **Keyed by the note's *current* status**, so a stale renderer cannot replay an action that has since stopped being offered.

**`Defer` was added to the issue row**, per ADR-0020: 39 issues sit at `triage` across the fleet with a median age of 56 days, and the only verbs were accept and decline — so *"real, but not now"* had nowhere to go.

## The suite found two live defects before any guard was deliberately broken

**[[ISS-0129]] — `/api/notes/check-toggle` had no loopback check**, and writes note body text. Any peer that could reach the `0.0.0.0` render surface could tick or untick any checkbox under `docs/`, including the acceptance and exit criteria the validator reads as evidence. It predates `note_writes.py`, so it appeared in no hand-written list of write endpoints. REQ-0027 had required loopback-only since 2026-08-03; nothing enforced it.

It was found because the suite **enumerates the POST dispatch table** rather than listing endpoints. A list derived from `note_writes`' callers would not have contained it.

**A duplicate-id race.** Two creates against the same stale index compute the same id from different titles, so a *filename* existence check passes and two notes end up sharing an id. Collision is now detected on the id.

## And a third, found by dogfooding

Resolving REQ-0027's own criteria with the new tick path failed on the fourth: `_criterion_text` stripped everything after the first ` — `, looking for appended evidence, so **any criterion containing an em dash was unreachable**. The discriminator is now the box state — an unticked box has no resolution to strip. Regression test added.

Using a new write path on a real note, immediately, is what surfaced it. The fixture criteria had no em dashes.

## Contract

Unchanged and asserted: loopback-only, allow-listed fields or one located line, mtime preconditions, format-preserving, `SNAPSHOT.yaml` never written. No agent-owned transition is reachable — `done`, `fixed`, `merged`, `implemented`, `passing` and `verified` are asserted absent from the table.

REQ-0027 advanced to `implemented`, with its mtime criterion **reconciled rather than ticked**: create has nothing to precondition, and check-toggle still bypasses it (recorded, folded into TASK-0363).

## Paths

- `src/project_os_cockpit/note_writes.py` — `HUMAN_TRANSITIONS`, `legal_actions`, `stamp_transition`, `stamp_tick`, `create_issue`, `next_issue_id`
- `src/project_os_cockpit/server.py` — four routes, plus the loopback guard on `_serve_check_toggle`
- `tests/test_human_transitions.py` — 26 assertions, most of them refusals
