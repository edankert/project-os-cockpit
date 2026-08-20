---
type: "[[change]]"
id: CHG-20260820-The-Guard-Sends-The-Request
title: "The read-only guard sends the request — a loopback check that is present but dead now fails"
date: 2026-08-20
owner: user:edwin
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
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
- **[[FEAT-0083]] criterion 4**, measured: `cockpit.js` reaches **five** `/api/` endpoints plus the `/_events` SSE stream (`tab-state`, `terminal`, `cockpit/validation`, `cockpit/nav`, `cockpit/context`), and **exactly one of them is a POST** — `/api/cockpit/tab-state`, which is on the runtime-only open list. *(This line first said **two**, and it was wrong — see the correction section below.)*

Four mutants fired. A fifth was discarded for proving nothing — an edit that broke indentation and failed at import, which is a syntax error wearing a mutant's coat.

## What it does not do

It does not add authentication. [[ADR-0010]]: *"The loopback check is not a safety feature on top of an authorisation model. It **is** the authorisation model."* [[REQ-0034]] is still owed and still gates every actuating view in [[PHASE-029]].

## Also filed

Running the `note_writes` cross-check in reverse: `retire_check` and `cover_check` are complete write functions with no caller outside `tests/`. Not a security finding — unreachable from the dispatch is unreachable from the LAN. But [[TASK-0518]] asks whether 83 rested checks should retire, and nothing can call the function that retires one. [[ISS-0249]].

## Paths

- `tests/test_remote_peer_refusal.py` (new)
- `docs/issues/ISS-0249-Two-Check-Write-Paths-Reach-No-Front-Door.md` (new)
- `docs/features/browser-front-door/FEAT-0083-*.md`, `.../plan/tasks/TASK-0363-*.md`, `docs/phases/PHASE-029-*.md`

## Independent review 2026-08-20 — changes requested

Recorded here as provenance rather than as a discharged obligation: [[ADR-0023]] exempts `CHG-*` notes from the review gate. This one was read because its claims are the claims under test.

**What reproduced, independently measured.** 27 of 32 POST routes refuse `203.0.113.7` with exactly `403 {"ok": false, "error": "mutations are loopback-only"}`, none with 400 — and the five open ones *do* return 400 to the same body, which is what makes "refuses before parsing" observed rather than argued. The headline mutant passes the old test and fails the new one, with the verdict-vocabulary 400 as quoted. `_LOOPBACK_HOSTS` is exactly the asserted frozenset. The fixture keeps the real predicate in the path. The two dispatch parses agree, and the agreement check was proved able to fire against a branch padded past the regex's window. `retire_check` and `cover_check` have no caller in `src/`. And **"no production code changed" is true** — the commit touches six notes and one new test file, nothing under `src/`.

**Wrong: "`cockpit.js` fetches exactly `/api/cockpit/tab-state` and `/api/terminal`."** It also reaches `/api/cockpit/validation`, `/api/cockpit/nav` and `/api/cockpit/context` through `fetchJson`, and opens `EventSource("/_events")` — all unconditional on page load. The measurement saw only literals written inside `fetch(`, which is not how this file calls its read APIs.

**Overstated: "Four mutants fired."** They did. Two more that ought to fire do not:

- a guard that is **called and its result ignored** — the third case the new file's own docstring names as what the sibling misses — passes all eight tests while a remote peer's write lands on disk (`status: triage` → `status: "open"`, with the 403 still returned to the caller);
- a new unguarded route whose handler is not named `_serve_*` is invisible to both enumerations and to the sibling test.

Both executed. Details in [[TASK-0363]]'s review section.

## Correction — independent review, same day

The review of this change found **two blocking defects in it**, and the first is the one this file was written to prevent.

### 1. A guard whose answer is discarded refuses the caller and writes anyway

```python
self._require_loopback()          # answer thrown away
```

The peer at `203.0.113.7` receives `403 mutations are loopback-only`. The note on disk goes `status: triage` → `status: "open"`. **Refusal real. Write real.** All eight tests in the new file passed. The sibling passed. All 1965 passed.

The module docstring above names three failure modes as its reason to exist — a guard assigned to a variable, called behind a false condition, or *"called it and ignored the result."* I executed the first two and shipped without executing the third. **A test file whose subject is checks that cannot fire, containing a check that could not fire.** Fourth time this phase, same shape.

The cause is exact and worth keeping: **every assertion in this file reads a status code**, and `_require_loopback` responds *before* it returns `False` — so the 403 is already on the wire when its answer is dropped. [[REQ-0027]] is about the write, not the reply, and I was asserting the reply.

Fixed with a **second predicate for the second question** ([[REQ-0059]]) — not *"does the guard fire?"* but *"is its answer used?"*. Answered statically over all 27 call sites: a discarded result is an `ast.Expr` wrapping the call and there is no other way to spell it. The reviewer's mutant now fails; the other eight tests still pass, which confirms their blindness rather than excusing it.

### 2. "`cockpit.js` fetches exactly two endpoints" was false — it is five

The measurement read `fetch("…")` **call sites**. The file's own idiom is `fetchJson(url)`. It reaches `/api/cockpit/validation`, `/api/cockpit/nav`, `/api/cockpit/context`, `/api/terminal` and `/api/cockpit/tab-state`, plus an `EventSource("/_events")`.

The wrong number reached three notes. Worse, the claim built on it was hollow: *"a ported view calling a read API shows up here"* did not hold — `fetchJson("/api/cockpit/stats")`, which is literally what [[TASK-0361]] will do, kept all eight tests green. The inventory now reads **string literals**, and that mutant fails.

Criterion 4's substance survives: no `note_writes`-backed route appears in the client in any form, and the client makes exactly **one** POST.

### 3. Two further holes, both mine, both fixed

- Both enumerations required the handler to be named `_serve_*`, so neither could see `/api/notes/backdoor → self._handle_backdoor()`. They could not disagree about a route they both missed. The parse now takes any `self.<method>()` in the branch.
- `assert len(guarded) >= 25` was a floor two below the actual 27. Two routes could lose their guard and the sweep would still pass over a quietly smaller domain. It is now an exact partition asserted to cover the dispatch.

### What the reviewer confirmed

Claims 1, 2, 3 and 5 reproduced exactly, including the verdict-vocabulary 400 — and **stronger than argued**: the five *open* routes return 400 to the same empty body while the 27 return 403, so refusal-before-parsing is *observed*, not inferred.

### The honest summary

This change was committed with a green suite, a green validator, `HEAD passes the full CI step set`, and four mutants I had run myself. **None of that caught a defect that lets a write land while the caller is told it was refused.** A 20-minute review did, and it cost no blocked time because it ran in the background.
