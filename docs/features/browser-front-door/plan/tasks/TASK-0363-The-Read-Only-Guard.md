---
type: "[[task]]"
id: TASK-0363
aliases: ["TASK-0363"]
title: "A test asserts every actuating endpoint refuses a non-loopback peer, and fails when a new one forgets"
status: done
phase: "[[PHASE-029-One-Tool-Two-Front-Doors]]"
owner: user:edwin
created: 2026-08-09
updated: "2026-08-20"
source: ["[[REQ-0032-Two-Front-Doors-Agree-Or-Differ-On-The-Record]]", "[[RISK-0001-Render-Server-Exposure]]"]
parent: "[[FEAT-0083-The-Browser-Cockpit-Answers-Questions]]"
effort: S
due: ""
depends: []
blocks: ["[[TASK-0361-The-Overview-On-The-Reading-Surface]]", "[[TASK-0362-The-Design-Register-Read-Only]]"]
related: []
tests: []
completed: 2026-08-20
---

# The read-only guard

## Definition of Done
- [x] Every write endpoint is enumerated from one place and asserted to refuse a non-loopback peer — evidence: `tests/test_remote_peer_refusal.py`, 27 guarded routes, all 403 over a real socket
- [x] Adding a write endpoint without the check fails the test — enumerated, not hand-listed — evidence: `test_every_note_mutating_endpoint_requires_loopback` (TASK-0280) already did this; both enumerations are now asserted equal
- [x] The test states the threat model it guards in one sentence, naming [[RISK-0001]] — evidence: the module docstring's opening paragraph

## Steps
- [x] Enumerate the POST routes from `server.py`'s dispatch rather than restating them, so a new route joins the suite by existing — done with `ast`, and cross-asserted against the sibling test's regex
- [x] Assert refusal with a simulated non-loopback peer address — a handler subclass reports RFC 5737 `203.0.113.7`; `_is_loopback` still runs and still decides
- [x] Cross-check against `note_writes`' documented callers — 19 routes call it, all 19 guarded, none unguarded; the reverse walk found [[ISS-0249]]

## Notes
**This lands before the two porting tasks, not after.** It is the guard that makes widening the reading surface safe, and a guard written after the widening has already been trusted once.

The measured hazard is specific: mode 1 is served on `0.0.0.0` so a tablet can read, and the only thing separating reading from writing is a per-request peer check on the shared socket. That check is correct today. Nothing currently fails if someone adds an endpoint and omits it.

## Done 2026-08-20 — and the guard was already half-built

**Most of this task existed before it was opened.** `test_every_note_mutating_endpoint_requires_loopback` (TASK-0280, in `tests/test_human_transitions.py`) already enumerates the POST dispatch, already fails when a new route forgets the guard, and already names the five runtime-only exemptions individually with a check that each really writes nothing under `docs/`. That is the second DoD bullet, complete, months old. It stays exactly as it is.

**What was missing is the first bullet's second half — *"asserted to refuse"*.** That test decides by reading source text: it asserts the substring `_require_loopback` appears somewhere in the handler body. It has never sent a request.

### The mutant that separates them

A guard that is *present in the source and never fires*:

```python
if False and not self._require_loopback():   # MUTANT
    return
```

| | `test_every_note_mutating_endpoint_requires_loopback` | `test_remote_peer_refusal.py` |
|---|---|---|
| dead guard on `/api/notes/mark-check` | **passed** | **failed** |

And the failure is worse than a missing 403. The remote peer got back:

```
400 {"ok": false, "error": "'' is not a verdict; expected one of
     clear, excused, failed, partial, pass, question, rerun"}
```

— so a disabled guard does not merely permit the write. It parses the LAN caller's body first and hands back the API's internal vocabulary on the way to rejecting it. The refusal has to come *before* the parse, and only a request can show that it does. All 27 guarded routes were confirmed to refuse before parsing: every one returned 403, not 400.

### What was verified, not assumed

- **27 of 32 POST routes guarded**, 5 open. The open set is asserted to be exactly the five runtime-only endpoints and pinned in **both** directions — `/api/cockpit/tab-state` must keep answering a remote peer, because `cockpit.js` posts it on a heartbeat from the tablet the `0.0.0.0` bind exists for. A guard that refused everything would pass a one-directional test and break the reading surface.
- **The fake peer is real.** `203.0.113.7` (RFC 5737 TEST-NET-3) is asserted absent from `_LOOPBACK_HOSTS`, and the set itself is asserted, so widening it to something absurd fails there rather than quietly making every other assertion a tautology.
- **The predicate stays in the path.** The fixture overrides `client_address` on a handler subclass rather than monkeypatching `_is_loopback`, so the real predicate still runs and still consults the real set. A test that stubs the predicate cannot catch the predicate going wrong — `test_design_bench.py:2443` takes the stub route for one endpoint, which is why this one does not.
- **Three further mutants fired**: `_is_loopback` forced true (2 tests failed), `_require_loopback` forced false (the loopback-still-works test failed, naming all 27 routes), and both enumerations of the dispatch are asserted equal so neither can silently lose a route.
- **A fourth "mutant" was not one** — an edit that broke indentation and failed at import. Recorded because it proves nothing and was nearly counted.

### The cross-check found something the task was not looking for

Walking `note_writes` callers in reverse: `retire_check` and `cover_check` are complete write functions with **no caller outside `tests/`**. Not a security finding — unreachable from the dispatch is unreachable from the LAN, so they are the safest things in the module. But [[TASK-0518]] asks whether 83 rested checks should retire, and the function that performs a retirement cannot be called by anything. Filed as [[ISS-0249]].

### Why the sibling test is not replaced

Neither subsumes the other, and the failure modes are opposite. Delete this file and a guard can rot into a no-op. Delete the sibling and a new route never appears here at all — this one only tests what the dispatch already routes. Both are kept, and the two enumerations now assert each other.
