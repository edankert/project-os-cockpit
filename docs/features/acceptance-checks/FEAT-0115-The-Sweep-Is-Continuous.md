---
type: "[[feature]]"
id: FEAT-0115
aliases: ["FEAT-0115"]
title: "The sweep is continuous — invalidation happens where work lands, in one action, and a feature says its acceptance impact was considered"
status: superseded
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
source: ["Edwin 2026-08-17: 'the acceptance tests need to be re-checked and any functionality touched which could impact an existing check should be un-checked and new checks should be created'", "Edwin 2026-08-17: 'the acceptance-tests should constantly be kept up to date and the human should be able to tick them off as features appear/change'", "TESTING.md rules — the documented process this gives a surface to"]
goal: "TESTING.md rule 3 becomes performable instead of merely documented: invalidating a check names the change and the reason in one write, a feature's close-out offers a batched sweep — mark existing checks needs-re-run and author new ones, one Save, one commit — and the feature records that its acceptance impact was considered, in one authored line with three honest states."
requirements: []
tasks: ["[[TASK-0466-Verdict-Writes-On-Notes]]", "[[TASK-0467-The-Impact-Sweep-At-Close-Out]]", "[[TASK-0468-The-Considered-Obligation]]", "[[TASK-0519-Withdraw-The-Sweep]]"]
design: ""
release: ""
depends: ["[[FEAT-0113-The-Check-Type-And-The-Migration]]"]
related: ["[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0028-Work-Has-Three-Phases]]", "[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]", "[[PHASE-035-Acceptance-Checks-Are-Notes]]"]

---

# The sweep is continuous

## The measurement this stands on

The rule already exists — TESTING.md: *"Any code change must uncheck all Tier 1 and Tier 2 tests whose scope overlaps with the changed code"* — and the corpus shows both that it is practised and how it fails without tooling. Practised: commit `a4577c01`, *"cover TASK-0383..0387 + uncheck overlapping rows"* — six checks added, three invalidated, one commit, by hand. Failing: **57 rows carry a hand-written `RE-RUN (…)` annotation and 54 of them are still ticked** — people annotate instead of unchecking, because unchecking destroys the record that the check was ever verified and there is nowhere to say why. The invalidation half of the rule is being documented, not performed.

## The three states, and why not a boolean

`acceptance_impact:` on the feature: a **date** (swept then), **`none — <reason>`** (considered, nothing to do — discharged forever), or **absent** (not yet swept — owed while the feature is in flight, per [[ADR-0028-Work-Has-Three-Phases]]'s routing). A boolean would collapse *nothing to do* into *not done* and nag forever, which is the [[ADR-0027-The-Registry-Counts-What-Needs-A-Person]] failure. The feature authors *that* the sweep happened, one line, never a list of checks; the checks author *what it did* — `invalidated_by:` names the change. Neither restates the other's fact.

## Acceptance criteria

- [ ] Needs-re-run is one action on a check: clears the mark and writes `invalidated_by:` (change id required, refused without one — the same discipline `[-]` has), one write.
- [ ] A feature reaching `done` offers the sweep: the checks in its touched areas, batch-invalidate plus batch-author (name, tier, area inherited, `covers:` prefilled), one Save, one commit — `a4577c01`'s shape, reproduced by tooling.
- [ ] The sweep's close writes `acceptance_impact:` on the feature; a feature in flight without it appears as an obligation on the features view; `none — reason` discharges permanently; no per-check row appears on any badge anywhere.
- [ ] A pass records its date, and a check whose pass predates its `invalidated_by:` change is computably stale — the 60-versus-113 gap becomes arithmetic instead of hand-annotation.

## Closed 2026-08-18

Every task scope-resolved and the linked tests `passing` — the feature had sat at `review` since its build leg finished on 2026-08-17, which is the state PHASE-035 could not close through.

**And it is closed knowing what came next.** [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] superseded this phase's own [[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]] one day after it was accepted, so parts of what this feature built have already been replaced. That is not a reason to leave it open: what it delivered was delivered, the record of *why the sibling type existed* is what makes ADR-0031 legible, and a feature left at `review` because its decision moved on is a phase that can never close.

## Reopened 2026-08-18 — to be withdrawn ([[ADR-0036]])

Edwin: *"I would like to remove the sweep functionality, until we find a need for it later."*

Reopened rather than left `done` with a task hanging off it, because the feature is being changed and `done` would be false while that is true. Reopening is cheap and honest; the alternative was a withdrawal task homed under a feature it has nothing to do with.

**Re-homed to [[PHASE-037]]** in the same move, because [[PHASE-035]] is `done` and a reopened child would have held it open — the validator caught that within a minute, which is the `PHASE-CHILDREN` gate doing exactly its job.

The reasoning is in [[ADR-0036]]. The short version: the problem this was built for — 54 ticked rows carrying a hand-written `RE-RUN` — is **no longer in the corpus**, `mark: rerun` and `invalidated_by:` are both 0 in every repo, and what remains is an obligation whose common case is answering *"nothing to do"*. Five of the six features owing a sweep on the day of the decision had been created that afternoon.
