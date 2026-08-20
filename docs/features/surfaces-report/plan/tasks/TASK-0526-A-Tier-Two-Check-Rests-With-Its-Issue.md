---
type: "[[task]]"
id: TASK-0526
aliases: ["TASK-0526"]
title: "A Tier 2 check goes quiet when the issue it guards is closed, and wakes when the issue reopens"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
parent: "[[FEAT-0131-The-Suite-Is-Refined]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# A Tier 2 check rests with its issue

Edwin: *"there should be very few tier-2 items active at any given time, so should not overwhelm."*

**This reconciles a contradiction rather than inventing a rule.** `TESTING.md` says Tier 2 is *"kept permanently"*; Edwin says few should be active. Both are right, and they are about different things — the check is **kept**, and it is not **asked about**.

That is exactly [[ADR-0028]]'s in-flight rule, which already quiets a test whose subject is not in flight. What is new is the subject: the acceptance suite has never read an `ISS-*` as one.

So there is no new mechanism to build. `covers:` names the issue, the in-flight rule reads it, and a closed issue's guard rests — **visible, counted, not owed**. It wakes if the issue reopens, which is the case a permanent-retirement rule could not express and is the reason this is resting rather than retiring.

Depends on [[TASK-0525-Relink-Tier-Two-To-Its-Issue]]: a check cannot rest with its issue if it does not name one.

**Measured 2026-08-20, and the dependency is a ceiling rather than a gate.** 85 of 158 Tier 2 checks name an `ISS-*`; the other 73 never did — the pre-migration document's Tier 2 headings split 31-with / 21-without, holding exactly 85 and 73 rows. So this can be built now and will reach **85 of 158**, and the remaining 73 are waiting on original research rather than on a relink. The surface must say which, or it will look like it quieted everything it could.

## Done when

- [ ] A Tier 2 check whose `covers:` names a `fixed` issue is quiet.
- [ ] Reopening the issue wakes it, without an edit to the check.
- [ ] Nothing is deleted and nothing is hidden — the check is still listed, still counted, still walkable.

## Done 2026-08-20

`obligations.ids_are_settled` plus a `resting` bucket in `gate_payload`, rendered as a collapsed **Resting · N — the issue each guards is closed** group beside `Quiet`.

**Its own group, not folded into `Quiet`.** The two rest for opposite reasons — subject *not built* against subject *finished* — and a reader who cannot tell them apart cannot tell a screen nobody has written from a defect nobody needs to re-check. Every row names the issue and its status, so the silence can be inspected ([[ADR-0028]] decision 5).

### Measured on `your-trainer` (working tree, 2026-08-20)

| | rows |
|---|---|
| blocking | 59 |
| …of those, in the regression section | 14 |
| …of those, with **every** `ISS-*` closed → **resting** | **11** |
| displayed gate groups (`New` + `Chronic`) before | 39 |
| after | **28** |

No resting row appears in a delta group as well — asserted, because a row in two places is [[ISS-0068]] and a row in neither is worse.

### The regression restriction is the whole safety of it, and the mutant proves the number

A feature check whose `FEAT-*` is `done` is the ordinary state of every settled feature in the repo. Dropping `section_of(i) == SECTION_REGRESSION` was executed: **34 rows rest instead of 11** — three times as many, and the gate stops meaning anything. A regression check's subject is the *defect* it guards, and a closed defect is exactly the condition under which nobody needs to re-walk it.

### Two guards, and the second one only worked on the second attempt

`is_done_status`, never the band test — `band_of("accepted")` is `active`, so a band predicate would never rest a check guarding an `adr` or a `requirement`. That is [[ISS-0245]], fixed hours earlier.

**The first version of that guard asserted `"is_done_status" in source` and the mutant passed**, because the `from .cockpit import is_done_status` line satisfies it. A guard satisfied by an *import* tests nothing. It now asserts the **call** and the **absence** of `is_completed`, and the same mutant fails.

### Coverage, stated rather than assumed

This reaches **85 of 158** Tier 2 checks — the ones that name an issue. The other 73 never did ([[TASK-0525]]), so they cannot rest until that research is done. The surface must not read as though it quieted everything it could.

## Independent review — third pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`, reviewing `6cc7f72..HEAD`. Verdict: **approved**. Every claim below was re-measured or re-executed.

Every figure reproduces on `your-trainer`'s working tree with an indexed loader: `blocking=59`, `quiet=20`, regression checks among the blocking **14**, of which **11** have every `ISS-*` closed and rest — so the gate reads 48. The dependency ceiling is stated correctly too: 85 of 158 Tier 2 checks name an issue, and the surface says so rather than looking as though it quieted everything it could.

**The safety argument is measured, not asserted.** Dropping `section_of(i) == SECTION_REGRESSION` was re-executed here: **34** rows rest instead of 11 — the note's number exactly — and the mutant is caught by `test_a_regression_guard_rests_when_its_issue_closes`. Replacing `ids_are_settled` with `True` is caught by the same guard.

`ids_are_settled` delegating to `is_done_status` rather than the band test, explicitly because `ISS-0245` had just been found, is the right lesson applied in the right direction.
