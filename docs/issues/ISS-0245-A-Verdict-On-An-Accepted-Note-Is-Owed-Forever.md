---
type: "[[issue]]"
id: ISS-0245
aliases: ["ISS-0245"]
title: "A `changes-requested` verdict on an ADR, design, reference or requirement is owed forever — the obligation asks `is_completed` while the rest of the app asks `is_done_status`, and the two disagree on exactly those four"
status: open
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
source: ["independent review 2026-08-20"]
severity: high
component: cockpit
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0121-A-Review-Verdict-Is-Sticky]]", "[[REQ-0059-One-Predicate-Per-Question]]", "[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]", "[[ISS-0241-The-Section-Head-Restates-Its-Own-Arithmetic]]"]
tests: []
---

# Two predicates for one question, and they disagree on the four types that use `accepted`

## Problem

`_verdict_is_owed` (`cockpit.py:2414`) ends `return not statuses.is_completed(status)`. `is_completed` is a **band** test, and `band_of("accepted")` is **`active`**. Meanwhile `cockpit.is_done_status(note_type, status)` — the type-aware predicate the rest of the app uses, and the one `test_every_row_of_the_rehoming_table_is_reachable` asserts against — says `accepted` **is** terminal for the types that have it.

Measured 2026-08-20:

| type | status | `statuses.is_completed` | `cockpit.is_done_status` |
|---|---|---|---|
| `adr` | `accepted` | `False` | **`True`** |
| `design` | `accepted` | `False` | **`True`** |
| `reference` | `accepted` | `False` | **`True`** |
| `requirement` | `accepted` | `False` | **`True`** |
| `issue` | `fixed` | `True` | `True` |
| `feature` | `done` | `True` | `True` |

So for those four types the obligation **never clears**. A reviewer writes `changes-requested`, the author fixes everything, the note reaches its terminal status — and the row stays in `Needs you` for the rest of the record's life.

## This is [[ISS-0121]] on a second axis

That issue's whole subject is that `review_verdict` is sticky, and its fix was to discriminate on the subject's current status. The fix works for `issue`/`feature`/`change`, whose terminal statuses are in the `done` band, and silently does not work for the four whose terminal status is `accepted` — because it asks a band question about a type-specific state.

It is also [[REQ-0059]]'s forbidden shape exactly: **one question, two implementations**. `_covers_an_issue` was caught doing this a week ago and made to delegate. This is the same defect in the obligations path.

## How it surfaced, which is the part worth keeping

The independent reviewer stamped `review_verdict: changes-requested` on [[ADR-0040]]. Edwin then accepted the ADR, so it became `status: accepted` — and `test_every_row_of_the_rehoming_table_is_reachable` began failing with *"ADR-0040 is terminal but still counted as owing a re-review"*.

**The suite then went green because the reviewer flipped its own verdict to `approved` on the re-review pass** — which is a legitimate act, and it masked the defect. The reviewer said so explicitly and re-proved it in isolation: at `changes-requested` the test fails, at `approved` it passes. Without that note the failure would have read as *"the ADR should not have been accepted"* rather than *"the predicate is wrong"*, and the likely response would have been to un-accept a decision Edwin had made.

**A test that passes because a field was edited, rather than because the code was fixed, is the most expensive kind of green.**

## Expected

`_verdict_is_owed` asks the same question as the rest of the app: `is_done_status(note_type, status)`. That needs the note's **type**, which the current signature does not take — the change is real, not a one-word swap.

Both call sites (`cockpit.py:2537`, `:6685`) have the record in hand.

## Next Actions

- [ ] `_verdict_is_owed` takes the note type and delegates to `is_done_status`.
- [ ] A guard on the four disagreeing pairs specifically — the corpus contains `adr` at `accepted` today, so this one **can** be proved from real data rather than constructed input.
- [ ] Check the other readers of `statuses.is_completed` for the same substitution. `_section_head_label`'s merged-row count ([[ISS-0242]]) is a deliberate and correct use — it asks about a *test*, whose terminal statuses are all in the `done` band — but it was chosen without knowing this hazard existed, so it deserves the second look.
