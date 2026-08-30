---
type: "[[issue]]"
id: ISS-0264
aliases: ["ISS-0264"]
title: "A check must be marked twice before it settles — the write endpoint answers `ok` about 50 ms before the watcher refreshes the index, so the repaint that follows the response reads the pre-write state"
status: fixed
owner: user:edwin
created: 2026-08-30
updated: 2026-08-30
reviewed_by: model:claude-opus-5
review_date: 2026-08-30
review_verdict: changes-requested
severity: high
component: server
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
fixed_in: "[[TASK-0590-A-Write-Is-Readable-When-It-Answers]]"
source: ["Edwin, 2026-08-30: 'I need to do the check twice before the feature/acceptance test dissappears.'"]
related: ["[[ISS-0263-A-Write-Evicts-The-Reader-From-The-Checks-Page]]", "[[ISS-0262-Marking-A-Check-Clears-The-Filter-You-Are-Walking]]"]
---

# `ok` was true and the next read disagreed

## Measured, on a scratch repo built for it

| | |
|---|---|
| `POST /api/notes/mark-check` returns | **1 ms**, `ok: true` |
| re-read issued the moment it resolves | **still `mark: todo`** |
| index catches up at | **~50 ms** |

The renderer repaints as soon as the POST resolves, so it lost that race every time. The first tick appeared to do nothing; the second showed the first one's result — which is exactly *"I need to do the check twice."*

## Cause

The index is refreshed by the **watcher**, asynchronously: the server writes the note, `watchdog` notices, the bus carries a `FileEvent`, and `Index.invalidate` re-parses. The write endpoint takes no part in that and answers immediately.

So the API told the truth about the disk and a lie about itself: `ok` for a write that its own next read could not see.

## Fix

`_reindex(*note_ids)` on the handler, calling `Index.invalidate` on the written note's path **before** the response — a synchronous re-parse of one path, the same call the watcher subscriber makes when it arrives late. Wired into `mark-check` and `retire-check`.

Not fixed in the client. A delay or retry there would have to guess the watcher's latency, and every other consumer would still be told `ok` about something it could not read.

## Why it surfaced only now

It was always there and [[ISS-0263]] was hiding it. Until that was fixed, marking a check **navigated the reader away** to the Tests landing, so the stale repaint was never seen — arriving back at `~checks` later re-fetched, by then long past 50 ms. Fixing the eviction left the reader looking at the page that had lost the race.

Three defects on one keystroke, found in the order they masked each other: [[ISS-0262]] cleared the filters, [[ISS-0263]] evicted the reader, and this one made the write invisible.

## Latent elsewhere, and not fixed here

Every other write endpoint has the same shape — `release-contents`, `release-verified`, `release-prepare`, `mark-released`, the status writes. None was reported and none is fixed, because making them all reindex means deciding what each one touched, and a guess there is worse than the race. Filed rather than swept in.

## Independent review, 2026-08-30 — changes-requested

The cause and the placement are right — fixing it at the endpoint rather than with a client delay is the correct call, and `C1` (removing the `mark-check` reindex) fails both tests as claimed. Two findings. [[ISS-0266]] — the retire-check reindex is unguarded: removing it fails nothing, while TASK-0590 says *"Removing the `_reindex` call fails both"*. [[ISS-0270]] — *"Filed rather than swept in"* names a note that does not exist, and the enumeration of the other write endpoints is short by about a dozen. One observation, not a finding: in a repo that keeps a ledger the mark routes to `record_verdict`, which writes the ledger and not the check note, so `_reindex(check_id)` invalidates a path that was not written — harmless today because `ledger.load` reads from disk on every call, and worth knowing before that changes.

Reviewed from a clean context (the notes and the diff, no authoring transcript) by `model:claude-opus-5`, the same model family as the author and a different session. Mutants were applied one at a time in a worktree at `c861414` and the full suite re-run; corpus figures were recomputed against `git archive fb99a751`, the `../your-trainer` state as of these commits.
