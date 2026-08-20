---
type: "[[issue]]"
id: ISS-0249
aliases: ["ISS-0249"]
title: "`retire_check` and `cover_check` are complete write paths that no front door reaches — the answer to TASK-0518 has nowhere to be recorded"
status: open
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
source: ["[[TASK-0363]] cross-check against `note_writes`' callers, 2026-08-20"]
severity: medium
component: cockpit
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[TASK-0518-Rest-Or-Retire]]", "[[FEAT-0131-The-Suite-Is-Refined]]", "[[ADR-0035-A-Release-Page-Reports]]", "[[TASK-0363-The-Read-Only-Guard]]"]
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
