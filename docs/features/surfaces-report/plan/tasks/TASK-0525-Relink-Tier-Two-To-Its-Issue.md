---
type: "[[task]]"
id: TASK-0525
aliases: ["TASK-0525"]
title: "Restore the `ISS-*` link on the 73 Tier 2 checks that lost it"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
parent: "[[FEAT-0131-The-Suite-Is-Refined]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Restore the `ISS-*` link on the 73 Tier 2 checks that lost it

TESTING.md already requires it — each Tier 2 test *"references the \`ISS-*\` that created it"*. Measured 2026-08-18: **85 of 158 do**, so 73 have lost the one field that says why they exist.

This is what makes Tier 2 groupable by issue rather than by 46 one-off scenario names, and it is the prerequisite for [[TASK-0526]] — a check cannot rest with its issue if it does not name one.

**Per check, from the note's own text.** A Tier 2 check whose issue cannot be identified is a finding, not a blank to fill: it may be the evidence that the check should be retired ([[TASK-0518]]).

## The premise is refuted, 2026-08-20 — they never had it

This task says the 73 *"have lost"* the field. **They did not lose it. It was never written.**

The pre-migration `docs/tests/ACCEPTANCE_TESTS.md` survives in `your-trainer`'s history (deleted at the migration; last living revision recovered with `git show`). Its Tier 2 section splits exactly:

| Tier 2 headings | count | rows under them |
|---|---|---|
| naming an `ISS-*` — e.g. `## 2.1 Family License on Cold Start (ISS-0108)` | 31 | **85** |
| naming none | 21 | **73** |
| | 52 | **158** |

Those three numbers are the ones this task already carries — *"85 of 158 do, so 73 have lost"* — and they line up with the note corpus at `HEAD` exactly: 158 `tier: 2` checks, 85 with an `ISS-*` in `covers:`, 73 without. **73 is also basis-independent**: the working tree has 164 / 91 / 73.

So the migration was **lossless**. It carried the heading's issue into `covers:` wherever the heading had one, and wrote nothing where it did not, which is the correct behaviour. An attempted excavation by the [[TASK-0517]] method recovered **0 of 73**, and that zero is the evidence rather than a failure of the method: the document cannot supply what it never held.

## What this task actually is

Not a restoration — **original research**. For each of 73 checks, decide from its own text which issue it guards, or that it guards none. The task's own last line already anticipated this: *"A Tier 2 check whose issue cannot be identified is a finding, not a blank to fill: it may be the evidence that the check should be retired ([[TASK-0518]])."* That is now the whole of it, not the tail.

**Left open deliberately.** Filling 73 `covers:` entries by inference would put a guessed link on a check that gates a release, and the guess would be indistinguishable from a recovered one the moment it was written. That is the shape this phase exists to remove.

## Consequence for [[TASK-0526]]

A Tier 2 check can only rest with its issue if it names one, so *rest-with-issue* reaches **85 of 158 today** and cannot reach the other 73 until this is done. Not a blocker for building it — the mechanism is [[ADR-0028]]'s in-flight rule and needs no new code — but its coverage must be stated rather than assumed, or the surface will look like it quieted everything it could.

## Read individually 2026-08-20, on Edwin's instruction — and 67 of the 73 need nothing

He chose *read each and decide*, with a table to approve before anything is written. Reading them collapses the task a second time.

### They are not regression checks

**All 73 derive to the `feature` section** — verified 73 of 73. [[ADR-0039]] derives a check's section from `covers:`, and **35 of the 73 name a `FEAT-*`** directly, 15 name only a `TASK-*`, 17 name something else, and 6 name nothing at all *(corrected after independent review: the note first said **67**, which is `73 − 6` — the count naming **any** subject, not the count naming a feature. The load-bearing claim is unaffected, because the section is derived from the absence of an `ISS-*` rather than from the presence of a `FEAT-*`)* — usually a `TASK-*` beside it. Read, they are feature verification: *Ramp Warmup Rendering*, *Cue Display*, *Cue Auto-Dismiss*, *No Cue in Free Ride*. Not guards over fixed defects.

For comparison, the 91 that **do** name an issue derive to `regression` (86) and `automated` (5) — correctly, and by the same rule.

So `tier: 2` on these 73 is **dead metadata**. [[ISS-0208]] retired the tier rule and [[ADR-0039]] replaced it with derivation; the section they land in is already right, and the field that said otherwise is the one that stopped being read.

**Assigning an `ISS-*` to a check that verifies a feature would be inventing a defect to justify a tier that no longer exists.** That is the opposite of what this task wanted.

### Six name nothing at all, and they are exactly the six that gate

Of the 73, six carry no `covers:` — and those same six are the only ones blocking, through `blocking_for`'s fail-closed clause (*a check nobody can attribute cannot be discharged by finishing any particular item*).

| id | check | surface |
|---|---|---|
| `TST-0434` | Fresh Install Add Rider | Riders & profiles |
| `TST-0435` | Family Tier Add Rider | Riders & profiles |
| `TST-0436` | No Sessions Message | History & analytics |
| `TST-0444` | HRM Reset on User Switch | Hardware |
| `TST-0445` | HRM Prompt After User Switch | Hardware |
| `TST-0446` | HRM Reconnect on Switch Back | Hardware |

Read, none is a regression guard either — they are empty-state and user-switch behaviours whose `covers:` was never filled.

**Proposed, awaiting approval:** give each the feature it verifies — `FEAT-0002` (rider profiles) for TST-0434/0435, `FEAT-0060` (history) for TST-0436, `FEAT-0007` (device pairing) for TST-0444/0445/0446. That moves them off the fail-closed path into Feature tests. **No issue is invented for any of them.**

Nothing has been written. The table above is the approval this task's own instruction asked for.

## Independent review — third pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`, reviewing `6cc7f72..HEAD`. Verdict: **changes-requested**. Every claim below was re-measured or re-executed.

**The premise refutation is correct and reproduces exactly.** At `your-trainer` HEAD: 158 `tier: 2` checks, **85** with an `ISS-*` in `covers:`, **73** without; working tree 164 / 91 / **73**. The basis-independence of 73 is real and is the right thing to have noticed. The excavation recovering 0 of 73 is consistent with a lossless migration.

**The load-bearing claim holds**: all **73** derive to the `feature` section under `ADR-0039` — verified through `section_of` at both bases, 73/73.

**But *"67 of the 73 name a `FEAT-*`"* does not.** Parsed with YAML rather than a regex, at both bases: of the 73, **35** name a `FEAT-*`, 26 name a `TASK-*`, and **6** carry an empty `covers:`. 67 is almost certainly `73 − 6` — the count naming *any* subject — described as though it were the count naming a feature.

That matters because 67 is the number the closure rests on: *"67 of the 73 need nothing"*. The conclusion may well survive on the section derivation, which is verified — but as written the note justifies it with a figure that is not what it says it is, and the reader cannot tell which of the two readings was actually used to decide.


## Approved and applied 2026-08-20 — and the effect was not the one this note claimed

Edwin approved the table. All six now name the feature they verify, committed in `your-trainer` (`0dad8104`), bare-id form to match the house convention.

**But two claims above are false, and were caught only by measuring before writing rather than after.**

> *"those same six are the only ones blocking, through `blocking_for`'s fail-closed clause"*
> *"That moves them off the fail-closed path into Feature tests"*

Re-measured at the time of writing:

| | before | after |
|---|---|---|
| suite blocking | 59 | **59** |
| of the six, blocking | **0** | 0 |
| section | `feature` | `feature` |
| `CHECK-SUBJECT` warnings | 44 | **38** |

**None of the six was blocking.** All carry `mark: done`, so they already cleared the gate. And they were already in the `feature` section, because a check with no `covers:` **defaults** there — which is exactly what the `CHECK-SUBJECT` warning says: *"its section cannot be derived and it defaults to a feature check."*

Repo-wide, **79** checks carry no `covers:` at all; **2** of those block and 77 are cleared by their mark. So the fail-closed clause is real and this note attributed the wrong population to it.

**What the change actually bought**, which is duller and true: six `CHECK-SUBJECT` warnings cleared, the record now says what each check verifies, and if one of those marks is ever invalidated the check has a subject for [[ADR-0040]]'s selection-subtracts rule to reach.

The decision was right for reasons the note stated correctly — they are feature behaviours, no issue should be invented — and it was *sold* on an effect that had not been re-measured since it was first written. The proposal was put to Edwin carrying that error.
