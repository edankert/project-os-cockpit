---
type: "[[issue]]"
id: ISS-0249
aliases: ["ISS-0249"]
title: "`retire_check` and `cover_check` are complete write paths that no front door reaches — the answer to TASK-0518 has nowhere to be recorded"
status: fixed
owner: user:edwin
created: 2026-08-20
updated: "2026-08-21"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
source: ["[[TASK-0363]] cross-check against `note_writes`' callers, 2026-08-20"]
severity: medium
component: cockpit
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[TASK-0518-Review-Tier-Two-For-One-Time-Fixes]]", "[[FEAT-0131-The-Suite-Is-Refined]]", "[[ADR-0035-A-Release-Page-Reports]]", "[[TASK-0363-The-Read-Only-Guard]]"]
tests: []
---

# Two write paths, no caller

## What was measured

[[TASK-0363]]'s last step is *"cross-check against `note_writes`' documented callers"*. Walking the POST dispatch with `ast` and resolving every `note_writes.*` call inside each handler gives a clean answer to the question the task asked — **19 routes call `note_writes`, all 19 are loopback-guarded, and no unguarded route calls it at all.**

The same walk, run in reverse, answers a question the task did not ask. Of `note_writes`' public functions, these have **no caller anywhere outside `tests/`**:

| function | what it writes | reached by |
|---|---|---|
| `retire_check` | sets a check to `retired`, optionally promoting its replacement | nothing |
| `cover_check` | writes `covered_by:` on a check | nothing |

`resolve_note` is an internal helper used inside `note_writes` itself, and `legal_actions` / `next_issue_id` / `next_release_id` / `read_design_comments` are reads. Those four are accounted for. `retire_check` and `cover_check` are not: they are **writes**, they are tested (`tests/test_checks_view.py` exercises both, including their refusals), and no HTTP route, no renderer control and no CLI path invokes either.

## Why this is not merely tidy-up

**It is the missing half of a decision already on the table.** [[TASK-0518]] asks whether any of the 83 rested regression checks should *retire* rather than rest. Whatever the answer is, there is no way to record it: the function that performs a retirement exists and is correct, and nothing can call it. The decision would have to be executed by hand-editing 83 notes — which is the failure mode [[ADR-0009]] exists to prevent, since a hand edit is a write the record cannot attribute.

The same holds for `cover_check`: [[FEAT-0131]]'s premise is that the suite gets refined, and `covered_by:` is how one check subsumes another. `ledger.py:318` documents the guard `cover_check` applies. The guard is live prose about a function nothing calls.

## Why nothing flagged it

A write path with no caller is invisible to every check this repo runs. The validator walks *notes*, not code. The loopback enumeration walks the *dispatch*, so a function absent from the dispatch is absent from its domain by construction — it cannot report what it cannot see. And the tests pass, because the tests call the functions directly.

This is the [[REQ-0059]] shape once more, from a new angle: the guard's question is *"does every routed write check its caller?"*, and **"is every write routed?"** is a different question that nothing was asking.

## Not a security finding

Worth stating plainly, because the issue arrives out of a security cross-check. Unreachable from the dispatch means unreachable from the LAN: these two functions are the *safest* things in `note_writes`. The defect is that a capability was built and never connected, not that it is exposed.

## Options

1. **Wire both into `~checks`** behind the existing `_require_loopback` guard, as two more verdict-style actions. Smallest change; puts the retirement lever where the checks already are.
2. **Wire `retire_check` only**, and leave `cover_check` until [[FEAT-0131]] needs it. Answers [[TASK-0518]] without building ahead of a decision.
3. **Delete both** and their tests, on the grounds that a capability nobody asked for is debt. Rejected on sight for `retire_check` — [[TASK-0518]] is exactly someone asking for it — but it is the honest option for `cover_check` if the suite is never refined that way.

Recommendation: **option 2**, and take `cover_check` up with [[FEAT-0131]]. `retire_check`'s caller should land with [[TASK-0518]]'s answer rather than before it, so the button and the decision arrive together.

## Links

- Found by: [[TASK-0363]] — the read-only guard's `note_writes` cross-check
- Blocks the execution of: [[TASK-0518]]

## Independent review 2026-08-20 — approved

Fresh context, separate session; same model family, recorded in `reviewed_by`. Reproduced from scratch rather than read.

Walking `_route_post` with `ast` and resolving `note_writes.<fn>` calls per handler gives **19 routes calling `note_writes`, all 19 guarded, none unguarded** — exact.

The reverse walk over all 29 public `note_writes` functions confirms the table. `retire_check` and `cover_check` are the only two with no caller anywhere in `src/`, including inside `note_writes` itself. The four the note sets aside are accounted for as it says: `resolve_note` has 13 internal uses, `next_issue_id` and `next_release_id` one each, `read_design_comments` is called from `cockpit.py` — and every remaining public function is called from `server.py`. The only other references to the two are `tests/test_checks_view.py` and the prose at `ledger.py:318`. "Not a security finding" is right for the reason given, and the options are stated fairly.

**One correction.** `related:` links `[[TASK-0518-Rest-Or-Retire]]`, but that note is `TASK-0518-Review-Tier-Two-For-One-Time-Fixes.md` and its `aliases:` carry only `TASK-0518`. The validator resolves the reference by ID, so nothing errors; a reader clicking it lands nowhere.


## Fixed 2026-08-21 — one wired, one deleted, and the general form guarded

**`retire_check` was wired.** `POST /api/notes/retire-check`, loopback-guarded like the other 27, and a `Retire` control beside the mark on `~checks`. The dispatch partition test moved 27 -> 28 deliberately, and the sweep drives the new route over a real socket and requires a 403.

[[TASK-0518]] closed with *"retire nothing today"*, and this note's own recommendation was that the caller should land **with** that decision. It lands now for the reason that task records: *"if the answer here ever changes, there is no button to press."* A decision that changes later must not find that there is nothing to press.

**`cover_check` was deleted**, which is option 3 — and this note named the condition for it: *"the honest option for `cover_check` if the suite is never refined that way."* [[FEAT-0131]] — *the suite is refined* — closed `done` without ever needing it, so it never was. And [[FEAT-0138]]/[[REQ-0057]] end the field it wrote outright: nothing declares coverage in a note.

### The thing found while wiring it, which is this issue's point restated

`retire_check` wrote **`verdict_reason:`** — one of the seven fields [[ADR-0037]] moved into the ledger, and one this repo's validator **refuses** (`LEDGER-MOVED-FIELD`). So the function would have failed the commit it was part of, on its first real use, in a repo that keeps ledgers.

Nothing caught it, and nothing could: the unit tests call it directly and never validate the result, and every other check walks the corpus, which the function had never touched. **An unreachable write path is an untested one however many unit tests it has** — that is a sharper statement than the one this note filed, and it is the one the wiring produced.

The reason goes in the note **body** now (`## Retired <date>`), where a reader sees it.

`promote` went too. It wrote `tier: 3`, and [[ADR-0039]] decided there is no Tier 3 — `tier:` is read by no section and by no gate decision. A parameter whose only effect is a field nothing reads is a lever that moves nothing, and offering it from a front door would have been worse than leaving it unreachable.

### The general form, so the next one is caught by a test

`test_no_public_write_in_note_writes_is_unreachable` (`tests/test_checks_view.py`) walks `note_writes` with `ast`, takes every public function that calls `_write` — **13 of them** — and requires each to be named somewhere other than its own definition.

That is the question this issue found nobody was asking. The loopback enumeration walks the **dispatch**, so a function absent from it is absent from that rule's domain *by construction*: it cannot report what it cannot see. *"Is every write routed?"* is a different question, and it has a test now.

### Correction applied

`related:` linked `[[TASK-0518-Rest-Or-Retire]]`, a slug that note does not carry. It resolves by ID so nothing errored; a reader clicking it landed nowhere. Now `[[TASK-0518-Review-Tier-Two-For-One-Time-Fixes]]`.
