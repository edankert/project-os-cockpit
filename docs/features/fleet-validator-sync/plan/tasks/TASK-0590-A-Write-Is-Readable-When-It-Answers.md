---
type: "[[task]]"
id: TASK-0590
aliases: ["TASK-0590"]
title: "The check-write endpoints re-index before they answer, so a mark is readable by the request that follows it"
status: done
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
owner: user:edwin
created: 2026-08-30
updated: "2026-08-30"
source: ["[[ISS-0264-A-Write-Is-Not-Readable-By-The-Next-Request]]"]
parent: "FEAT-0143"
effort: ""
due: ""
depends: ["TASK-0589"]
blocks: []
related: ["[[ISS-0262-Marking-A-Check-Clears-The-Filter-You-Are-Walking]]", "[[ISS-0263-A-Write-Evicts-The-Reader-From-The-Checks-Page]]"]
tests: []
---

# A write is readable when it answers

## What changed

`_reindex(*note_ids)` on the request handler — `Index.invalidate` on the written note's path, before the response — called by `_serve_mark_check` and `_serve_retire_check`.

## Guards

`tests/test_mark_check_is_readable.py`, two of them, and **no watcher runs in these tests**. That is what makes them sharp: nothing but the endpoint can make the write visible, so the guard cannot be masked by a filesystem event arriving in time on a fast machine.

The second pins the **order** — reindex before the response — because reindexing after it still passes a functional test while losing the race in the app, where the client is already fetching.

Removing the `_reindex` call fails both. Run, not assumed.

## Reproduced before it was fixed

A scratch repo with one check and a real sidecar: POST returned in 1 ms with `ok: true`, an immediate re-read still said `mark: todo`, and the index caught up at ~50 ms. After the fix the same script reads `settled` with no delay. That measurement is what turned a fourth guess into a cause.
