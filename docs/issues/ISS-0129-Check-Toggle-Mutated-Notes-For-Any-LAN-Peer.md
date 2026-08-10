---
type: "[[issue]]"
id: ISS-0129
aliases: ["ISS-0129"]
title: "`/api/notes/check-toggle` wrote to notes for any peer that could reach the 0.0.0.0 render surface — it predates note_writes.py and nothing enumerated it"
status: fixed
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["Session 2026-08-10: writing TASK-0280's hardening suite, which enumerates POST routes instead of listing them"]
severity: high
component: "server"
parent: ""
related: ["[[REQ-0027-Every-Cockpit-Write-Is-Guarded]]", "[[RISK-0001-Terminal-Exposure]]", "[[TASK-0280-Create-Issue-And-The-Hardening-Suite]]", "[[TASK-0363-The-Read-Only-Guard]]"]
tests: []
---

# check-toggle mutated notes for any LAN peer

## Problem

`POST /api/notes/check-toggle` toggles a task-list checkbox **in the source `.md`** (FEAT-0011 / TASK-0074). It had **no loopback check**.

The render server binds `0.0.0.0` deliberately, so a tablet on the same Wi-Fi can read the notes. The only thing separating that read surface from a write surface is a per-request peer check — and this endpoint never had one. Any peer able to reach the cockpit could tick or untick any checkbox in any note under `docs/`, including requirement acceptance criteria and phase exit criteria, which are exactly the boxes the validator reads as evidence.

## Why it was invisible

It **predates `note_writes.py`**. Every write added since inherits that module's discipline — field allow-lists, mtime preconditions, path canonicalisation, and `_require_loopback` at the endpoint. This one writes directly, so it was not in `note_writes`' orbit and appeared in no list of "the write endpoints".

[[REQ-0027]] has said *"No write endpoint is reachable from a non-loopback peer"* since 2026-08-03. The requirement was right; nothing enforced it.

## How it was found

Not by reading. [[TASK-0280]]'s hardening suite **enumerates the POST dispatch table** rather than listing endpoints by hand, precisely so a route that forgets the guard fails by existing. It failed on the first run, naming this endpoint.

That is the difference between a test that checks a mechanism and one that checks a property: a hand-written list of write endpoints would have been written from `note_writes`' callers and would not have contained this.

## Fix

`_require_loopback()` at the top of `_serve_check_toggle`, matching every other mutating endpoint. This is [[REQ-0027]] applied, not a new restriction.

`test_every_note_mutating_endpoint_requires_loopback` now guards the whole table, with three runtime-only endpoints exempted **by name** — and the exemption itself asserts the handler performs no note write, so exempting a fourth is a deliberate edit rather than a widening nobody notices.

## What this does not fix

The endpoint still bypasses `note_writes.py`'s other guards — no mtime precondition, no field allow-list (it edits body text, not frontmatter). Bringing it fully into that module is worth doing and is **not** this fix: the exposure was the loopback gap, and widening the change would have delayed closing it. Worth folding into [[TASK-0363]], which owns the read-only guard for [[PHASE-029]].
