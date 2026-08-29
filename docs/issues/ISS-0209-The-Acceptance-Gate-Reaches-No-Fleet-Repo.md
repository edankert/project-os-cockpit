---
type: "[[issue]]"
id: ISS-0209
aliases: ["ISS-0209"]
title: "The acceptance gate runs in no repo that holds acceptance checks — the fleet validators are ~690 lines behind upstream and cannot be synced without a migration"
status: fixed
owner: user:edwin
created: 2026-08-18
updated: "2026-08-29"
fixed_in: "[[CHG-20260829-The-Fleet-Runs-One-Validator]]"
severity: high
component: tooling
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
related: ["[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ISS-0208-Retire-The-Tier-Rule]]", "[[PHASE-036-One-Human-Walk]]"]
---

# The gate is in the wrong repos

`VERIFY-ACCEPTANCE` and `_acceptance_is_settled` exist in `project-os-cockpit`'s validator and — since `project-os@61c5c92` — in upstream's. They occur **zero** times in `your-sudoku`, `your-trainer`, `your-health` and `obsidian-supernote-sync`.

**Those are the repos that hold the 669 acceptance checks.** `your-sudoku` has six true `VERIFY-ACCEPTANCE` findings (FEAT-0025 against TST-0028..0033) that fire in no pre-commit and in no CI. The gate is installed everywhere except where the thing it gates lives.

Raised by all three independent reviews of [[PHASE-036-One-Human-Walk]]; the third called it one of a pattern with the uncommitted upstream validator and the uncommitted `kind:` removals — *"work that exists on the authoring machine and nowhere else"*. Those two are now committed. This one is not, because it is not a commit.

## Why it was not just synced

Measured 2026-08-18, not assumed. The fleet validators diverge from upstream by **690 lines** (`your-sudoku`, `your-trainer`, `obsidian-supernote-sync`) and **725** (`your-health`). Copying upstream's validator into `your-sudoku` — the one repo with a clean tree — and running it produced a **flood** of errors it currently passes: `SNAPSHOT-MEMBERSHIP` on eight features, `PARENT-BACKLINK` on every task in `FEAT-0001`, and more. The repo would have been unable to commit anything.

So the fleet validators are not behind by the acceptance gate. They are behind by **every upstream rule added since they were last synced**, and pulling one pulls all of them. That is a migration per repo — reconcile the notes each new rule reports — and `your-trainer` carries 59 dirty files belonging to another agent's work while it waits.

## Options

1. **Sync and migrate, one repo at a time**, cleanest first (`your-sudoku` is clean today). Honest, and the only route to the fleet actually sharing a gate.
2. **Backport only the acceptance rules** into each fleet validator. Cheap, gets the gate where the checks are, and widens the divergence it is a symptom of.
3. **Run the cockpit's validator over the fleet** from one place (`fleet_validate` already walks every repo) and treat *that* as the fleet gate, leaving each repo's own validator as the local pre-commit. Changes what "the gate" means rather than closing the gap.

Option 1 is right and expensive; option 2 is a patch that makes option 1 harder later.

## Done when

- [x] `_acceptance_is_settled` runs in every repo holding acceptance checks, by whichever route is chosen. **Done 2026-08-29 by option 1, all four repos.**
- [x] `your-sudoku`'s six FEAT-0025 findings either fire in its own pre-commit or are fixed. **They fire — and there are ten, not six.** See the correction below.
- [x] The divergence number is measured again and recorded, so the next reviewer sees whether it is closing or growing. **Re-measured 2026-08-29 — it is growing.** See below.

## Re-measured 2026-08-29 — the gap is widening, and the stated blocker has cleared

Same method as 2026-08-18: `diff` of each fleet validator against upstream `project-os`, whitespace-normalised, counting differing lines; `grep -c '_acceptance_is_settled'` for the gate.

| repo | validator | differing lines vs upstream | 2026-08-18 | change | gate | tree |
|---|---|---|---|---|---|---|
| `your-trainer` | 1881 | **784** | 690 | +94 | **0** | clean |
| `your-sudoku` | 1881 | **784** | 690 | +94 | **0** | clean |
| `your-health` | 1828 | **817** | 725 | +92 | **0** | clean |
| `obsidian-supernote-sync` | 1817 | **782** | 690 | +92 | **0** | clean |
| `project-os` (upstream) | 2585 | — | — | — | 2 | — |
| `project-os-cockpit` | 3498 | — | — | — | 3 | — |

**Two findings, and the second is the one that changes what is schedulable.**

**The divergence grew by ~93 lines in eleven days**, uniformly across all four repos — which is what a fleet drifting from an upstream that keeps moving looks like, rather than any one repo falling behind. At this rate the migration cost rises by roughly the size of the original acceptance-gate backport every fortnight. The issue's own framing holds and hardens: *"the fleet validators are not behind by the acceptance gate. They are behind by every upstream rule added since they were last synced."*

**Every fleet repo now has a clean tree.** This note recorded that `your-sudoku` was the only clean candidate and that *"`your-trainer` carries 59 dirty files belonging to another agent's work while it waits."* That work has landed. `your-trainer` shows two modified files at time of measurement — a `versionCode`/`versionName` bump from a release build and one draft `REL-*` note, both same-day and both the release pipeline's own — not a foreign 59-file working set.

So the precondition that made option 1 (*"sync and migrate, one repo at a time, cleanest first"*) a one-repo experiment no longer binds. All four are candidates today, and the cheapest moment to run the first migration is the moment the divergence is smallest — which was eleven days ago, and is today rather than next month.

The gate is still absent from all four (`0` occurrences), so nothing about the finding itself has changed.

### Measured from `your-trainer`, as a worked example of the cost

`your-trainer` was asked on 2026-08-29 to do exactly what [[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]] decided and [[FEAT-0142-A-Release-Says-What-Is-In-It]] built: bind features and acceptance checks to a release (`REL-0013`, v2.1.7), and walk only the checks its Android diff actually touches.

It could not. Lacking the gate, the scoping was done by hand — reading `git diff v2.1.6..HEAD`, mapping 14 changed Kotlin files onto `area:` groupings by judgement, and writing the resulting **32 checks out of 623** into the release note as a markdown table. That table is prose: not queryable, not validated, and stale the moment anything moves. The documented alternative, `release-verification/SKILL.md` §68, is *"Tier 1 + Tier 2 tests must ALL be checked"* — **555 checks, 110 of them currently `todo`** — which is the gate the repo actually has and the reason nobody runs it.

That is the cost of this issue stated in one repo's units: a decided, built, `done` feature reaching none of the repos whose checks it was built to scope.

## The phase is the remaining obstacle

`phase: PHASE-999-Future` means this cannot be scheduled, and it is the only one of ADR-0040's four preconditions still open ([[ISS-0206-A-Check-Cannot-Belong-To-A-Release]] and [[ISS-0210-The-Release-Page-Offers-Sixty-Live-Marks]] are `fixed`; [[FEAT-0142-A-Release-Says-What-Is-In-It]] is `done`).

It is left at `PHASE-999` here deliberately rather than re-homed, because **neither open phase fits and forcing one would be worse than the parking**. `PHASE-028-Borrowed-Capability` is a standing survey of capability taken from adjacent tools; this is a migration of our own. `PHASE-004-Embedded-Terminal` is `done` and reopened only as the terminal's standing home.

**Resolved 2026-08-29:** [[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]] was opened for exactly this — a fleet-sync migration, one repo at a time, cheapest first, with a drift check left behind so the catch-up does not recur. This issue moved out of `PHASE-999-Future` into it and is schedulable.


## Resolved 2026-08-29 — option 1, all four repos, and three corrections to this note

[[CHG-20260829-The-Fleet-Runs-One-Validator]], [[FEAT-0143-The-Fleet-Runs-One-Validator]], [[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]].

| repo | errors under upstream's rules | after | gate before | after | divergence before | after |
|---|---|---|---|---|---|---|
| `obsidian-supernote-sync` | 16 | **0** | 0 | **2** | 782 | **0** |
| `your-health` | 271 | **0** | 0 | **2** | 817 | **0** |
| `your-sudoku` | 194 | **0** | 0 | **2** | 776 | **0** |
| `your-trainer` | 605 | **0** | 0 | **2** | 776 | **0** |

**Correction 1 — the migration was two rules, not a reconciliation per repo.** This note said the fleet validators *"are behind by every upstream rule added since they were last synced, and pulling one pulls all of them. That is a migration per repo."* The premise is right and the estimate was not. Counted rather than assumed ([[TASK-0579-Count-The-Flood-By-Rule]]): **1086 errors, 100% of them `PARENT-BACKLINK` (1044) and `SNAPSHOT-MEMBERSHIP` (42)** — one relationship seen from its two ends, answered by one operation run four times. Nothing else fired at all. Had the flood been counted on 2026-08-18 this would not have waited eleven days.

**Correction 2 — the divergence number was answering a different question.** The 690→784 figures this note tracks are against upstream **HEAD**, and the growth is *upstream moving*. Against each repo's own recorded sync baseline the local delta was **21–100 lines**, and of the lines added downstream since baseline, 0 / 4 / 32 / 32 were absent from upstream HEAD — the 32 being [[ADR-0030]]'s `CHK`/`checks` collection, which [[ADR-0031]] retired. So `--force` replaced a hand-applied backport with the thing that superseded it, and discarded nothing.

**Correction 3 — the check counts this note originated are wrong, and they propagated.** *"the 669 acceptance checks"* in the opening paragraph, and `your-sudoku`'s 59 / `your-trainer`'s 628 quoted from it in [[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]], [[TASK-0583-Migrate-Your-Sudoku]], [[TASK-0584-Migrate-Your-Trainer]] and one migration commit message, were repeated rather than recomputed. Counting notes whose frontmatter carries `level: acceptance`: `your-sudoku` **57**, `your-trainer` **625**, these four repos **682**, all twelve **716**. Found by independent review, 2026-08-29.

**Correction 4 — `VERIFY-ACCEPTANCE` is a warning until 2026-11-20, and it fires ten times, not six.** This note counts *"six true `VERIFY-ACCEPTANCE` findings (FEAT-0025 against TST-0028..0033)"*. Upstream reports **ten** against `your-sudoku` — those six plus `FEAT-0028` against `TST-0018..0021` — and `your-trainer` reports **19**. All of them are warnings inside upstream's grandfather window ending **2026-11-20**. So the gate is installed and reporting today, and *blocking* is a second date. The "done when" box above reads as one event and is two.

## One thing the census could not have predicted, recorded because it will recur

`your-trainer`'s reconciliation **armed a second rule**. `VERIFY` reads a feature's `tasks:` from the **snapshot**; with those lists absent it had nothing to walk, so it reported nothing during the census. Filling them in made it report **15** findings — `FEAT-0098` done 2026-07-05 with 11 tasks still `doing`, `FEAT-0083` with 3, `FEAT-0086` with 1.

Those are real, and they are `your-trainer`'s to settle rather than this migration's to guess at. Added to that repo's `tools/GRANDFATHERED.yaml` (155 → 158) with the reason written beside them.

The general lesson, which belongs on any future census: **a report-only run counts the rules that can fire against the corpus as it stands. Fixing rule A can arm rule B.** The census's "nothing else at all" was true and was not a prediction.
