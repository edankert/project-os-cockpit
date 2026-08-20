---
type: "[[change]]"
id: CHG-20260820-The-Guard-Sends-The-Request
title: "The read-only guard sends the request — a loopback check that is present but dead now fails"
date: 2026-08-20
owner: user:edwin
phase: "[[PHASE-029-One-Tool-Two-Front-Doors]]"
related: ["[[TASK-0363-The-Read-Only-Guard]]", "[[FEAT-0083-The-Browser-Cockpit-Answers-Questions]]", "[[ISS-0249-Two-Check-Write-Paths-Reach-No-Front-Door]]", "[[REQ-0027]]", "[[RISK-0001-Render-Server-Exposure]]", "[[ADR-0010-What-The-Browser-Cockpit-Is-For]]"]

---

# The guard sends the request

## What changed

`tests/test_remote_peer_refusal.py` is new. **No production code changed** — the guard it exercises was already correct, and every one of its assertions passes at the commit before this one.

That is the point. The file exists to make a specific future failure loud.

## Why

The render server binds `0.0.0.0` so a tablet on the Wi-Fi can read the notes. The only thing separating that reader from a writer is a per-request peer check on the shared socket ([[REQ-0027]], [[RISK-0001]]).

`test_every_note_mutating_endpoint_requires_loopback` has guarded that since TASK-0280 and it is a good test: it reads the POST dispatch, so **a new route that forgets the guard fails by existing**. It stays.

But it decides by looking for the substring `_require_loopback` in the handler's source. Given a guard that is present and disabled —

```python
if False and not self._require_loopback():   # MUTANT
    return
```

— it passes. Executed, not argued:

| | old test | new test |
|---|---|---|
| dead guard on `/api/notes/mark-check` | **passed** | **failed** |

And the remote caller's reply under that mutant was not a silent write, it was:

```
400 {"ok": false, "error": "'' is not a verdict; expected one of
     clear, excused, failed, partial, pass, question, rerun"}
```

A dead guard parses the LAN caller's body *before* deciding whether to talk to them, and hands back the internal vocabulary on the way out. Only a real request can show that. All **27** guarded routes were confirmed to refuse before parsing — every one 403, none 400.

## What it asserts

- **27 of 32 POST routes** refuse a peer at `203.0.113.7` (RFC 5737 TEST-NET-3), over a real socket.
- **The other 5 stay reachable.** Pinned in both directions, because a guard that refused everything would pass a one-way test and break the reading surface: `cockpit.js` posts `/api/cockpit/tab-state` on a heartbeat from the tablet the bind exists for.
- **The fake peer is genuinely remote** — asserted absent from `_LOOPBACK_HOSTS`, and the set itself asserted, so widening it does not quietly turn the suite into a tautology.
- **The real predicate stays in the path.** The fixture overrides `client_address` on a handler subclass rather than stubbing `_is_loopback`, so the predicate still runs and still decides. A test that stubs the predicate cannot catch the predicate going wrong.
- **Both enumerations of the dispatch agree** — this file's `ast` walk and the sibling's regex are asserted equal, so neither can silently lose a route.
- **[[FEAT-0083]] criterion 4**, measured: `cockpit.js` fetches exactly `/api/cockpit/tab-state` and `/api/terminal`, and the write assertion runs against the *guarded set* rather than a hand-list.

Four mutants fired. A fifth was discarded for proving nothing — an edit that broke indentation and failed at import, which is a syntax error wearing a mutant's coat.

## What it does not do

It does not add authentication. [[ADR-0010]]: *"The loopback check is not a safety feature on top of an authorisation model. It **is** the authorisation model."* [[REQ-0034]] is still owed and still gates every actuating view in [[PHASE-029]].

## Also filed

Running the `note_writes` cross-check in reverse: `retire_check` and `cover_check` are complete write functions with no caller outside `tests/`. Not a security finding — unreachable from the dispatch is unreachable from the LAN. But [[TASK-0518]] asks whether 83 rested checks should retire, and nothing can call the function that retires one. [[ISS-0249]].

## Paths

- `tests/test_remote_peer_refusal.py` (new)
- `docs/issues/ISS-0249-Two-Check-Write-Paths-Reach-No-Front-Door.md` (new)
- `docs/features/browser-front-door/FEAT-0083-*.md`, `.../plan/tasks/TASK-0363-*.md`, `docs/phases/PHASE-029-*.md`
