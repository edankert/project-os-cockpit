---
type: "[[issue]]"
id: ISS-0245
aliases: ["ISS-0245"]
title: "A `changes-requested` verdict on an ADR, design, reference or requirement is owed forever — the obligation asks `is_completed` while the rest of the app asks `is_done_status`, and the two disagree on exactly those four"
status: fixed
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
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

## Fixed 2026-08-20

`_verdict_is_owed` takes the note type and delegates to `is_done_status`. Both call sites have the record in hand. `note_type` defaults to `None` and falls back to the band test, so a caller that cannot supply one degrades rather than raises.

**The green is now the code's, not a field's.** The decisive check is the one the reviewer described: with `ADR-0040`'s verdict set back to `changes-requested`, `test_every_row_of_the_rehoming_table_is_reachable` **passes**. Before the fix it failed. That is the difference between a defect repaired and a symptom edited away.

Two guards, both proved on the mutant that restores `statuses.is_completed`:

- `test_a_verdict_on_an_accepted_note_stops_being_owed` asserts the four pairs **by name**, and asserts the premise as well — that the two predicates genuinely split on exactly those. A guard testing `issue`/`feature` would have passed against the bug for the same reason the original code did.
- `test_the_owed_verdict_predicate_has_one_implementation` reads the source, because the two predicates agree on every pair this corpus holds except those four: a second implementation would pass the behavioural test for months.

## Next Actions

- [x] `_verdict_is_owed` delegates to `is_done_status`.
- [x] A guard on the four disagreeing pairs, provable from real data.
- [x] Checked the other readers of `statuses.is_completed`. [[ISS-0242]]'s merged-row count in `_section_head_label` is the one that deserved the second look, and it is **correct — but not for the reason I first wrote down.**

  The first version of this line claimed the two predicates *"cannot disagree"* on a test. **They do**, on exactly one value: `is_completed("retired")` is `True` (the `archived` band) while `is_done_status("test", "retired")` is `False`. Caught by running it rather than by reasoning about it, in the note whose entire subject is a predicate claim that was not checked.

  It is nevertheless unreachable **and** the band answer is the right one:

  - `_tests_groups` routes any status in `_RESOLVED_NOT_PASSING` — `retired`, `canceled`, `cancelled`, `obsolete`, `superseded` — to the `Retired` bucket **before** the feature/regression buckets exist, so a retired test never enters the merge and the disagreeing branch never runs.
  - And if it ever did, `is_completed` gives the answer the head wants: a retired test is **not outstanding work**. Swapping to `is_done_status` there would make it outstanding, which is wrong.

  So: left alone, with the reason stated and the near-miss recorded. `_section_head_label`'s merged-row count ([[ISS-0242]]) is a deliberate and correct use — it asks about a *test*, whose terminal statuses are all in the `done` band — but it was chosen without knowing this hazard existed, so it deserves the second look.

## Independent review — third pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`, reviewing `6cc7f72..HEAD`. Verdict: **approved**. Every claim below was re-measured or re-executed.

The defect my second pass surfaced is fixed correctly and the fix is guarded where it matters. `_verdict_is_owed` now delegates to `is_done_status`, and `test_a_verdict_on_an_accepted_note_stops_being_owed` asserts **all four** disagreeing pairs by name — `adr`, `design`, `reference`, `requirement` at `accepted` — which is the entire population where the two predicates split. A guard testing only `issue`/`feature` would have passed against the bug for the same reason the original code did; this one cannot.

`test_the_owed_verdict_predicate_has_one_implementation` reads the function body with the docstring stripped, so the delegation cannot be satisfied by a comment. The `note_type=None` fallback keeps the old band test for callers without a record, and both real call sites pass one.

The docstring names the masking honestly — the suite went green when the reviewer updated its own verdict — which is the right way to record it.
