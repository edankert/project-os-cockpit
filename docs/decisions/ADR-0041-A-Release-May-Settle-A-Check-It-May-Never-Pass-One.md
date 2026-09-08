---
type: "[[adr]]"
id: ADR-0041
aliases: ["ADR-0041"]
title: "A release page may settle a check; it may never pass one — `na`, `excused` and `blocked` are decisions about scope and belong to the release, while `pass`, `partial` and `fail` are attestations and stay where the procedure is"
status: "accepted"
owner: user:edwin
created: 2026-09-08
updated: "2026-09-08"
decision_date: 2026-09-08
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
source: ["Edwin, 2026-09-08: 'uncheck the required acceptance-tests for the release and add new checks if required'", "Edwin, 2026-09-08: 'Implement FEAT-0145 fully'", "Edwin, 2026-08-18 (the constraint this amends): 'on the release view, I still see all these checks, I would suggest we show something different there and definitely do not allow these acceptance tests to be checked.'"]
supersedes: ""
superseded: ""
related: ["[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]", "[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]", "[[ISS-0254]]"]
tags: [decision, release, acceptance]
decided_option: "2"
---

# A release page may settle a check; it may never pass one

## Status

**Accepted 2026-09-08**, and it **amends [[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]** rather than superseding it. ADR-0035's rule holds for six of the seven marks and is narrowed for three; its note is unchanged apart from one line pointing here.

The authority is Edwin's own request of the same day — *"uncheck the required acceptance-tests for the release"* — and his instruction to build [[FEAT-0145-Preparing-A-Release-Is-One-Workflow]] in full. That is the same shape as [[ADR-0030]]'s acceptance: the decision is written down before the code lands, and the instruction to build is the acceptance.

## Context

[[ADR-0035]] removed every check-changing control from the release page on 2026-08-18. Three weeks later Edwin prepared `your-trainer` v2.2.0 by hand and asked for one of those controls back. Both are correct, and the reason they are both correct is that *"changing a check"* was one phrase covering two different acts.

### What ADR-0035 actually argued, in its own words

Two objections, and they are worth restating because neither is weak:

1. **The fastest way to unblock a release must not be ticking the rows that say it is not ready.** *"Offering the mark here inverts that: the fastest way to unblock a release becomes ticking the things that say it is not ready, on the page whose whole purpose is to report that it is not ready."*
2. **A mark is offered at the distance from the procedure where nobody can be walking it.** *"The release page shows the check's name and area, not its steps — so the control is offered at exactly the distance from the procedure where a person cannot be walking it."*

Sixty rows, sixty live `gateMark(item, releaseId, actionable=true)` buttons, on the one page whose subject was the sum. The control went, `actionable` was deleted rather than pinned to `false`, and `tests/test_release_held_back.py::test_no_write_path_to_a_check_appears_on_the_release_page` has guarded the result since — over every top-level function whose name mentions a release, discovered rather than enumerated, after independent review defeated two narrower versions of the same test.

### What FEAT-0145 asks for, and why it is not that

Edwin's sentence is *"uncheck the required acceptance-tests for the release"*. The verdict vocabulary [[ADR-0037]] built already contains the answer, and it contains **three different answers**:

| mark | what a person is saying | lifetime |
| --- | --- | --- |
| `na` | this check cannot apply on this platform, ever | permanent (`ledger.PERSISTS`) |
| `excused` | not walked this cycle, by decision | **this release only** — expires at the seal |
| `blocked` | could not be run; the rig was down | still blocks, deliberately |

None of those three is a claim that anything was verified. `excused` is *scoped to one release by construction* — it lives in that release's working ledger and `seal` expires it — so the release is not merely a convenient place to record it. **It is the only place where the question has an answer at all.** Asking *"is this check excused?"* away from a release is asking a question with no subject.

## The distinction this decision rests on

**An attestation says a procedure was walked. A settle says whether the procedure is in scope.**

- `pass`, `partial`, `fail` — somebody executed steps and reports what happened. These are ADR-0035's subject, and its two objections apply to them in full.
- `na`, `excused`, `blocked` — somebody decided this check does not apply, is not in this cycle, or could not be attempted. Nobody walked anything. There is no procedure to be at the wrong distance from.

`question` is the seventh mark and stays where it is: *"the check itself is not understood"* is a judgment about the procedure's text, made by somebody reading it.

### The two objections, answered one at a time

**Objection 1 — ticking the rows that block.** It does not reach the three settle marks, and the reason is structural rather than a matter of care:

- `blocked` **still blocks** (`ledger.BLOCKING`). Choosing it makes the number on screen go nowhere. That is a control a person cannot use to unblock a release, by design.
- `na` and `excused` clear, and both are in `ledger.NEEDS_REASON` — the write path refuses either without a written justification, and the justification lands in the ledger as a dated event with an author. A gate that shrinks with a name and a sentence beside every subtraction is the exact opposite of the silent shrink [[ADR-0040]] and [[TASK-0576]] were built to prevent.
- Nothing on the settle surface can write `pass`, `partial` or `fail`. The endpoint refuses those three **by name** and says why, so the objection is enforced by the server and not by whoever renders the next release surface.

**Objection 2 — the distance from the procedure.** This one is met by paying it rather than by arguing it away. FEAT-0145's step 3 requires the owed list on the release page to carry **each check's own procedure text**, grouped by area, beside the buttons. ADR-0035 recorded that the page *"shows the check's name and area, not its steps"*, and that sentence is a description of a payload, not a law. `Item.text` holds the steps and the release payload does not currently carry it; carrying it is part of the work ([[TASK-0602]]).

**Where the distance argument still wins**: a person walking a suite still goes to `~checks` or to the check's own note. This decision adds no `pass` button anywhere, and moves none.

## Options

1. **Leave ADR-0035 intact and put the settle marks on `~checks` instead.** Costs nothing to decide and keeps the guard as written. It also loses the thing Edwin asked for: `excused` means *not this cycle*, `~checks` does not know which release is being prepared unless it is told, and the surface that knows is the one we would be sending him away from. This is the state that produced the hand-preparation of v2.2.0.
2. **Narrow ADR-0035 to attestations, and let the release page settle scope.** The release page gains three controls, each demanding a reason; `pass`, `partial` and `fail` stay off it and are refused by name at the server. The guard narrows from *"no write path to a check"* to *"no attestation path to a check"*, which is a weaker universal claim and must be re-stated in the test rather than deleted from it.
3. **Add a per-release "required checks" list the person edits directly.** The shape Edwin's phrasing reads like on first pass. Rejected on [[ADR-0040]]'s ground and [[ADR-0032]]'s: it is a second, hand-maintained store of what the derivation already computes, and unticking a row there would leave no reason, no author and no date.

## Decision

**Option 2.**

1. A release page **may offer `na`, `excused` and `blocked`** on the checks that release owes, in bulk, each with a reason the write path requires.
2. A release page **may never offer `pass`, `partial` or `fail`.** `POST /api/notes/release-settle` refuses those three values by name, citing this decision, so the rule is enforced where the write happens rather than where the button is drawn.
3. Every settle is a `ledger.append` event on the release's platform, carrying `mark`, `reason`, `by` and the date. Nothing is written to a check note; [[REQ-0055]] is unchanged.
4. **The settle surface must render each check's procedure text.** A settle offered beside a name alone is ADR-0035's second objection, unpaid.
5. `question` is not offered on a release page. It is a judgment about the check's own wording, and it belongs where the wording is read.

## Alternatives

- Option 1 — no release-side settle at all. Rejected: `excused` has no meaning away from a release.
- Option 3 — an authored per-release required-check list. Rejected: a second store for a derived set.
- Offering all seven marks with a confirmation dialog. Rejected: a confirmation is not an argument, and ADR-0035's first objection is about which act is *cheapest*, not about which act is unguarded.

## Consequences

- **`test_no_write_path_to_a_check_appears_on_the_release_page` is rewritten, not deleted**, and is now `test_no_attestation_path_to_a_check_appears_on_the_release_page`. The narrowing is structural rather than a hole punched in a list of spellings, which matters because seven passes of independent review each defeated a looser version of that test:
  - `walkOneCheck`, `/api/notes/mark-check`, `/api/notes/retire-check`, `gateMark(`, `markGateRow(`, `checkMark(`, `markCheckRow(`, `retireCheckRow(` and `paintCheckList(` stay forbidden inside every release surface. `walkOneCheck` and `mark-check` stay forbidden even though the endpoint could in principle be sent `excused`: they are the path that offers all seven marks, and a release page reaching them is one refactor away from offering `pass`.
  - **`askForMark` is admitted, and checked on its argument.** One dialog, one reason field, one set of refusals — a second dialog built for the release page is how the two surfaces would come to disagree about what `excused` means. So the call is allowed and the test asserts its `only:` list is a non-empty subset of `{na, excused, blocked}`, the same treatment `buildCheckRow`'s `controls` argument already gets. A ban with a carve-out would be a list with a hole; a subset check catches `pass` however it is spelled.
  - The endpoints a release surface posts to are asserted as a set: `/api/notes/release-settle` present, `mark-check` and `retire-check` absent.
  - A second test pins the server half over `ledger.MARKS`, so a mark added to the vocabulary tomorrow is either declared a settle mark or refused — never quietly admitted because nobody updated a literal.

  [[ISS-0254]] still owns the durable form — a rule over the call graph rather than over spellings — and this decision makes that issue more valuable, not less.
- **The refusal is the load-bearing part.** If `release-settle` ever accepts `pass`, ADR-0035 is gone and nothing will say so. That refusal is the first thing to guard and the last thing to relax.
- **The reason requirement is not new and is now exercised.** `ledger.NEEDS_REASON` has demanded a justification for every mark but `pass` since [[ADR-0037]], and it was measured then as never having been enforced against anything — `verdict_reason:` was non-empty on 0 of 671 notes because nobody had ever written one of those marks. The release page is the surface that finally writes them.
- **`blocked` on a release page is a deliberately useless-looking control**, and somebody will eventually ask why it is there. It is there because *"the trainer is in the loft"* is a fact worth recording with a date and an author, and because a release that ships with it still blocking is a release that shipped knowing. Recording it must never clear it.
- **This is the second time a rule about the release surface has been narrowed by use.** [[ADR-0040]] narrowed *"a release is derived"*; this narrows *"a release records nothing"*. Both original rules were right about what they were written against. Neither was wrong enough to supersede.
