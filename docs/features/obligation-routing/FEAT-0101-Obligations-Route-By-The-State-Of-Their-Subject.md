---
type: "[[feature]]"
id: FEAT-0101
aliases: ["FEAT-0101"]
title: "Obligations route by the state of their subject — a judgment asks while the thing it attaches to is in flight, and the quiet it leaves behind is inspectable"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
reviewed_by: "model:claude-opus-5"
review_date: 2026-08-16
review_verdict: approved
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin 2026-08-16: 'the items which need my attention are still a little bit invisible in the tool, hidden by all the other stuff which is mainly handled by the LLM'", "Edwin 2026-08-16, on deferring requirements: 'it sounds like the suggested option is a lot better in that only requirements for the phase will ask for attention, can we do this to other items as well (probably not issues)?'"]
goal: "Take what needs a person from one undifferentiated number down to the items whose subject is actually being worked — measured 64 to 31 in your-trainer — by routing each obligation to the phase that owns its subject and letting it ask only while that subject is in flight, with everything it quiets still on screen as a collapsed line carrying its reason."
requirements: []
tasks: ["[[TASK-0423-An-Obligations-View-Is-Decided-Per-Item]]", "[[TASK-0424-The-In-Flight-Predicate]]", "[[TASK-0425-The-Quiet-Is-On-Screen]]"]
design: ""
release: ""
depends: ["[[ADR-0028-Work-Has-Three-Phases]]"]
related: ["[[ADR-0028-Work-Has-Three-Phases]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[FEAT-0102-Publication-Becomes-A-View]]", "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"]
tests: ["[[TST-0025-Obligation-Routing-Is-Per-Item-And-Complete]]", "[[TST-0026-The-In-Flight-Rule-Against-The-Live-Fleet]]"]
---

# Obligations route by the state of their subject

## The problem, measured

`../your-trainer` asks a person for 64 things. Of those:

- **26 requirement approvals — 23 attach to features still in `backlog`**, and 21 of the 26 belong to a phase literally named `PHASE-999-Future`. The record already says *future*; the badge asks anyway.
- **15 manual tests to run — 10 verify features that are `done`** or are system-wide. They have been at `ready` for four to seven months, and `last_run` is empty on every one of the 15.
- 22 issues at triage, which are genuinely owed.
- 1 commit to push, which is genuinely owed.

Applying [[ADR-0028]]'s rule: **64 → 31**, and the 31 are distributed across three phases instead of piled into one number.

## What this builds

**1. Routing is decided per item** ([[TASK-0423]]). `Obligation.view` is a fixed string per note type today, and `counts_by_kind`/`owed_items` both do `out[ob.view]`. It becomes derivable from the record. This deliberately breaks the invariant at `obligations.py:34` — *"one type, one view"* — and the safety property that replaces it is the one that already holds: one item still yields one row, and `counts_by_kind` stays asserted against `owed_items`, so a badge and its page cannot disagree.

**2. The in-flight predicate** ([[TASK-0424]]). For a requirement, the subject is the feature its `implements:` names. For a test, the features its `verifies:`/`features:` name — or a release, once [[FEAT-0102]] gives releases a rung. In flight means that subject is at a working status; terminal or `backlog` means resting.

The discriminator is the **feature's** status, not the phase's. `PHASE-019` is `active` while holding two features already `done`; `PHASE-017`/`PHASE-018` read `planned` while holding `done` features; 19 features carry no phase at all and three of twelve repos have no `PHASE-*` notes. Phase is what the reader *sees*, never what the rule reads.

**3. The quiet is on screen** ([[TASK-0425]]). Whatever the rule silences collapses into a line that says how many and why, grouped by phase where one exists:

```
Needs you · 3
  ⌄ 21 more · PHASE-999 Future     (no feature in flight)
     1 more · PHASE-015, PHASE-018
```

This is not decoration. Edwin's complaint is that owed work is invisible; derived silence that cannot be opened is the same failure with the opposite sign.

## Acceptance criteria

- [x] An obligation's view is derived from the item, and a type or note-less source with **no routing rule fails a test** — the completeness burden `obligations.py` already carries for undeclared types, extended to routing — `Obligation.route` + `view_for()`; `test_every_kind_routes_somewhere` walks the corpus and fails a kind that routes nowhere
- [x] `counts_by_kind` remains derived from the same walk as `owed_items`, and the existing assertion that the page and the badge are one computation still holds — stronger than asked — `counts_by_kind` is now DERIVED from `owed_items` rather than a second pass asserted equal (`test_the_page_and_the_badge_are_one_walk`)
- [x] A requirement whose `implements:` feature is `backlog`, `done`, `cancelled` or `superseded` does not count; one whose feature is `planned`, `doing` or `review` does — parametrised over doing/planned/backlog/done/cancelled in `test_a_requirement_asks_while_its_feature_is_in_flight`
- [x] A manual test at `ready` counts when a feature it verifies is in flight, and does not when every one of them is terminal — `test_a_manual_test_asks_while_a_feature_it_verifies_is_in_flight` + `..._rests_when_every_subject_is_terminal`
- [x] `deferred` still wins over the derived rule — an explicitly deferred requirement stays quiet **even when its feature moves to `doing`** — `test_deferred_beats_the_rule_even_when_the_feature_is_doing` — and it never enters the rule at all, because `deferred` is not an owed status for its type
- [x] An issue at `triage` is unaffected. The count of 22 in `your-trainer` is the same before and after — 22 before and after on the live sidecar; `test_triage_is_owed_in_every_phase` also asserts `issue` is absent from `SUBJECT_FIELDS`
- [x] Everything the rule quiets is reachable in one click from a collapsed line stating the count and the reason — `suppressed_group()`; walked live — `Quiet · 23 · PHASE-015, PHASE-018, PHASE-999`, each row carrying its subject and that subject's status
- [x] **No note changes address.** A `TST-*` stays in the Tests view whichever phase owes it; only its obligation row routes. Asserted: a test whose subject is a release is still listed in the Tests navigator, and its row appears under Publication — [[ADR-0025]]'s shortcut, not a move — `test_routing_moves_the_row_and_never_the_note` asserts the whole test corpus is still listed in the Tests navigator
- [x] Measured against `your-trainer`: total 64 → **31**, requirements 26 → 3, tests 15 → 5, issues 22 → 22, push 1 → 1 — **exact**: 31 total — requirement 3, issue 22, test 5, unpushed commit 1; and 31 owed + 33 suppressed = 64
- [x] Measured against a repo with no `PHASE-*` notes (`edankert.com`, `obsidian-supernote-sync`, `project-os`): routing is correct and no code path requires a phase to exist — `test_a_repo_with_no_phases_routes_and_labels_without_inventing_one`; walked against all three
- [x] A requirement or test that names **no** subject at all is treated explicitly rather than falling through — its behaviour is chosen, written down, and tested — chosen, written down and tested: it ASKS. `test_an_obligation_naming_no_subject_still_asks`, plus the undeclared-status and dangling-subject siblings

## Notes

**The last criterion is where this will go wrong if it goes wrong.** `TST-0001` and `TST-0002` verify nothing — `system-wide`, no features named. Under a naive "is the subject in flight" test they silently become never-owed, which is a way of losing two tests rather than quieting them. The choice needs to be deliberate: a subject-less obligation most likely keeps asking, because nothing can prove it is resting.

**Not a second obligation vocabulary.** The predicate lives in `obligations.py` beside the ones already there. `cockpit.py`'s digest and landing payloads read the registry and are not to grow a rule of their own — [[ISS-0159]] is what that costs.

## Delivered 2026-08-16

**64 → 31 on `your-trainer`, exactly as predicted**, and the arithmetic closes: 31 owed + 33 suppressed = 64. Requirements 26 → 3, tests 15 → 5, issues 22 unchanged, unpushed commit 1 unchanged. Walked against a live sidecar on the built bundle, not only in-process.

### The first `RESTING_STATES` was hand-listed, and wrong within the hour

It named the terminal statuses of **features** — `done`, `cancelled`, `superseded` — and a test's subject can equally be a requirement or an issue, whose terminals are `implemented`, `retired` and `fixed`. Those fell through to the unrecognised-status branch and asked forever: the first measurement came out at **8 owed tests where the rule should leave 5**, and all three extras were that one gap (`TST-0001`/`TST-0002` via `REQ-*` at `implemented`, `TST-0009` via `ISS-0191` at `fixed`).

It is now derived from `statuses.COMPLETED_STATUSES`, so a terminal status added upstream is resting on arrival rather than becoming a permanent question. `test_the_terminal_statuses_of_every_subject_type_rest` pins it.

### Two surfaces were computing owed-ness with their own predicate

The suite caught both the moment the rule changed, which is the registry's whole purpose working:

- `_owed_flag()` took no index, so it could not apply the rule and marked rows the badge did not count — the exact drift its own docstring warns about, reintroduced by an omitted argument. It now takes the index, and every call site passes one.
- The Tests navigator's `Needs a run` group read `_owed_flag`, so it disagreed with its own badge (2 against 1). Fixed by the same change, and suppressed tests get a **`Resting · no feature in flight`** group rather than falling through to `Never verified` — that group is a statement about *evidence*, and evidence is not why these are quiet.

### `counts_by_kind` is now derived rather than asserted equal

It used to be a second walk with a test asserting the two agreed — a property that has to be *maintained*. It is now computed from `owed_items`, so the disagreement is unrepresentable rather than merely absent. Note-less obligations were already counted this way; now every kind is.

Ten mutations, each chosen to defeat a guard. One was a silent no-op from bad shell escaping and was re-run with an apply-check before being believed — a mutation that did not apply is not evidence, which is [[ISS-0171]]'s lesson.
