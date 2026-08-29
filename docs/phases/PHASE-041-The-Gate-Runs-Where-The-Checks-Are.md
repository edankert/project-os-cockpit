---
type: "[[phase]]"
id: PHASE-041
aliases: ["PHASE-041"]
title: "The gate runs where the checks are, and the fleet stops drifting"
status: done
order: 41
owner: user:edwin
created: 2026-08-29
updated: 2026-08-29
goal: "Put the acceptance gate in the repos that hold the checks — migrating each fleet repo onto the upstream validator one at a time, cheapest first — and leave behind a drift check that fails the build when the next divergence opens, so this is the last time the fleet has to catch up."
features: ["[[FEAT-0143-The-Fleet-Runs-One-Validator]]"]
requirements: []
tasks: ["[[TASK-0579-Count-The-Flood-By-Rule]]", "[[TASK-0580-The-Migration-Is-A-Tool-Not-A-Session]]", "[[TASK-0581-Migrate-Obsidian-Supernote-Sync]]", "[[TASK-0582-Migrate-Your-Health]]", "[[TASK-0583-Migrate-Your-Sudoku]]", "[[TASK-0584-Migrate-Your-Trainer]]", "[[TASK-0585-Drift-Is-Measured-Not-Noticed]]", "[[TASK-0586-Your-Trainer-Scopes-Its-Release]]"]
issues: ["[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]"]
related:
  - "[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]"
  - "[[FEAT-0142-A-Release-Says-What-Is-In-It]]"
  - "[[ADR-0037-A-Verdict-Is-An-Event]]"
  - "[[ADR-0034-Three-Axes-Not-One-Word]]"
  - "[[ISS-0208-Retire-The-Tier-Rule]]"
tags: [tooling, acceptance, fleet]
---

# The gate runs where the checks are

## Goal

Put the acceptance gate in the repos that hold the checks — migrating each fleet repo onto the upstream validator one at a time, cheapest first — and leave behind a drift check that fails the build when the next divergence opens, **so this is the last time the fleet has to catch up.**

## Where this came from

[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]] decided that a release selects its features and its acceptance checks follow that selection. [[FEAT-0142-A-Release-Says-What-Is-In-It]] built it and is `done`. Two of its three preconditions — [[ISS-0206-A-Check-Cannot-Belong-To-A-Release]] and [[ISS-0210-The-Release-Page-Offers-Sixty-Live-Marks]] — are `fixed`.

The third, [[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]], is open, and ADR-0040 ordered it **ahead of the build**. It was not done ahead of the build. So a decided, built, closed feature reaches none of the repos it was built for, and has since the day it shipped.

`your-trainer` supplied the worked cost on 2026-08-29. Asked to do exactly what ADR-0040 describes — bind features and checks to `REL-0013` (v2.1.7) and walk only what its Android diff touches — it could not. The scoping was done by hand from a `git diff`, mapping 14 changed Kotlin files onto `area:` groupings by judgement, and the result written as a markdown table: **32 checks of 623**, as prose that nothing can query or validate. The documented alternative is `release-verification/SKILL.md` §68 — *"Tier 1 + Tier 2 tests must ALL be checked"* — which is **555 checks, 110 of them `todo`**, and is the reason nobody runs it.

## What the fleet actually looks like

Measured 2026-08-29. Divergence is `diff` against upstream `project-os`, whitespace-normalised, counting differing lines.

| repo | notes | acceptance checks | divergence | 2026-08-18 | gate |
|---|---|---|---|---|---|
| `obsidian-supernote-sync` | 88 | 0 | 782 | 690 | **0** |
| `your-sudoku` | 604 | 59 [^n] | 784 [^d] | 690 | **0** |
| `your-health` | 782 | 0 | 817 | 725 | **0** |
| `your-trainer` | 2519 | **628** [^n] | 784 [^d] | 690 | **0** |

[^n]: **Corrected at close, 2026-08-29.** Counting notes whose frontmatter carries `level: acceptance`, `your-sudoku` holds **57** and `your-trainer` **625** — not 59 and 628. Both figures were inherited from [[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]] and repeated here, in [[TASK-0583-Migrate-Your-Sudoku]], in [[TASK-0584-Migrate-Your-Trainer]] and in `your-trainer`'s migration commit message without being recomputed. The fleet total is **682** across these four and **716** across all twelve repos, not 669. Found by independent review.

[^d]: **The method label is wrong, not the number.** 784 is a raw `diff` line count; whitespace-normalised (`diff -w`) the same comparison gives **776**, which is what every other table in this note, in ISS-0209's close-out and in the commit messages reports. `your-health` (817) and `obsidian-supernote-sync` (782) are identical under both. So the *"grew ~93 lines in eleven days"* reading rests on 784 against a 690 whose own method is now unknown; the direction holds and the magnitude is ±8.

Two facts set the shape of this phase.

**Divergence is uniform (782–817) but corpus size varies 29×.** The cost is not the validator diff; it is reconciling every rule that diff turns on, and that scales with notes. Ordering by divergence would be ordering by the wrong number.

**The divergence grew ~93 lines in eleven days, uniformly**, while nobody did anything wrong. That is a fleet drifting from an upstream that keeps moving. A one-shot catch-up regresses, which is why the drift check is in the goal rather than in a follow-up.


## The census — step 0, run 2026-08-29

Upstream `validate-docs.py --repo-root <repo>`, report-only, against each fleet repo. Each repo's **own** validator passes with 0 errors today, so every number below is a rule the repo does not yet run.

| repo | notes | upstream errors | `PARENT-BACKLINK` | `SNAPSHOT-MEMBERSHIP` | anything else |
|---|---|---|---|---|---|
| `obsidian-supernote-sync` | 88 | 16 | 12 | 4 | **0** |
| `your-health` | 782 | 271 | 257 | 14 | **0** |
| `your-sudoku` | 604 | 194 | 186 | 8 | **0** |
| `your-trainer` | 2519 | 605 | 589 | 16 | **0** |
| **total** | 3993 | **1086** | **1044** | **42** | **0** |

**The step-0 hedge was right and the phase is cheaper than its own estimate.** This note said the census *"may well show the reconciliation is two or three mechanical rules, which would change everything below."* It is **two**, they are **100%** of the errors, and they are the *same relationship seen from its two ends* — a feature's `tasks:` not naming the tasks that declare it as `parent:`. One operation over the notes answers both, and `sync-snapshot.py` carries it into the snapshot.

So the scope stands, the ordering stands, and the per-repo cost is not "reconcile every rule the diff turns on". It is one reconciliation, run four times, at 12 / 257 / 186 / 589 findings.

### And the divergence number was answering a different question

`sync-project-os.sh --dry-run` reports `validate-docs.py` as **DIVERGED** in all four repos and skips it — which is the mechanism that kept the fleet behind while routine syncs reported success. But measured against each repo's **own recorded baseline** rather than upstream HEAD, the local delta is small, and almost none of it is local:

| repo | vs upstream HEAD | vs its own baseline | added since baseline | of those, absent from upstream HEAD |
|---|---|---|---|---|
| `obsidian-supernote-sync` | 782 | 28 | 23 | **0** |
| `your-health` | 817 | 21 | 16 | 4 (comment wording) |
| `your-sudoku` | 776 | 100 | 79 | 32 |
| `your-trainer` | 776 | 100 | 79 | 32 |

The 32 in `your-sudoku` and `your-trainer` are [[ADR-0030]]'s `CHK` prefix and `checks` collection — which [[ADR-0031]] **retired**, folding `check` into `test` at `level: acceptance`. Upstream carries the replacement; the fleet carries the thing it replaced. So `--force` discards nothing that upstream does not already supersede, and the census run is the proof rather than the argument: upstream's rules executed against these corpora report those two rules and nothing else.

### One correction to the finding this phase inherited

`VERIFY-ACCEPTANCE` is a **warning** upstream, grandfathered until **2026-11-20**, and it fires **10** times against `your-sudoku` — `FEAT-0025` against `TST-0028..0033`, and `FEAT-0028` against `TST-0018..0021`. [[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]] counts *"six"*, which is `FEAT-0025`'s share alone. After the migration those findings will **fire and not block** until November. Installing the gate and having it gate are two dates; the exit criterion below is written against the first, and the second is a fact to record rather than work to do.

## Scope

**Step 0 — count the flood before choosing anything.** ISS-0209 records that copying upstream's validator into `your-sudoku` produced *"a flood"* — `SNAPSHOT-MEMBERSHIP` on eight features, `PARENT-BACKLINK` on every task in FEAT-0001 — but nobody counted it. Run each upstream validator against each fleet repo in report-only mode and record the error count **by rule**. Cheap, and it converts this phase's estimate into a table. It may well show the reconciliation is two or three mechanical rules, which would change everything below.

**Then migrate, cost-ascending, value deliberately last:**

1. `obsidian-supernote-sync` — 88 notes, 0 checks. Gains nothing directly; that is the point. The rehearsal that proves the route end-to-end at 3% of the hard repo's size.
2. `your-health` — 782 notes, 0 checks. Second rehearsal, now at real corpus scale.
3. `your-sudoku` — 604 notes, 59 checks. First repo where the gate does something: its six FEAT-0025 findings start firing in its own pre-commit.
4. `your-trainer` — 2519 notes, 628 checks. 91% of the fleet's checks, and the only repo where release-scoped verification currently pays. Attempted last, with the route proven three times.

**And leave the guard behind:** a drift check reporting each fleet validator's divergence from upstream, failing past a threshold, so the number is measured continuously rather than when someone notices.

## Out of Scope

- **Backporting only the acceptance rules into each fleet validator.** ISS-0209 lists this as option 2 and judges it *"a patch that makes option 1 harder later."* It is out of scope by decision, not by omission — it will look attractive around repo 3, when the `your-trainer` reconciliation is in view, and taking it means the gate arrives while the divergence keeps growing underneath. That is today's situation with extra steps.
- **The ledger migration itself** ([[ADR-0037-A-Verdict-Is-An-Event]]). Distinct work; this phase makes it reachable in the fleet rather than performing it.
- **New upstream rules.** Upstream will keep moving during this phase; the drift check is how that is absorbed, not a freeze.

## Exit Criteria

- [x] The by-rule error count is recorded for all four repos, from a report-only run against the upstream validator. **Done 2026-08-29 ([[TASK-0579-Count-The-Flood-By-Rule]]) — see 'The census' below.**
- [x] `_acceptance_is_settled` runs in every repo holding acceptance checks — `your-sudoku` and `your-trainer` at minimum. **All four, 2 occurrences each.**
- [x] `your-sudoku`'s six FEAT-0025 findings either fire in its own pre-commit or are fixed (inherited from ISS-0209). **They fire. There are ten — the six plus `FEAT-0028` against `TST-0018..0021` — and they are warnings until upstream's grandfather window closes on 2026-11-20.**
- [x] A drift check reports each fleet validator's divergence and fails past a stated threshold. **`tools/scripts/fleet-drift.py` ([[TASK-0585-Drift-Is-Measured-Not-Noticed]], [[TST-0081-The-Drift-Check-Fails-When-The-Fleet-Falls-Behind]]). It gates on missing upstream RULE CODES rather than line count — see below — and it cannot run in CI, which is stated in the tool rather than papered over.**
- [x] Divergence is measured once more at close and recorded, showing it closed rather than paused. **782 / 817 / 776 / 776 → 0 / 0 / 0 / 0.**
- [~] `your-trainer` can scope a release's acceptance checks from its own `REL-*` note — the thing it could not do on 2026-08-29 — with `REL-0013`'s hand-written 32-of-623 table replaced by something derived. **Partly: 13 of the 32 are derived; the other 19 cannot be, and that limit is now measured and filed rather than assumed away ([[ISS-0258-A-Release-Cannot-Derive-What-It-Broke]]). See below.**

## Notes

**Sequencing.** Do not start with `your-trainer` because it is the one that hurts. Its 628 checks are the prize, but 2519 notes is where an unrehearsed migration stalls, and a stalled first attempt is what parked this in `PHASE-999-Future` for a quarter already.

**Timing.** The cheapest moment to run the first migration is the moment divergence is smallest. That was eleven days ago; it is today rather than next month.

**Precondition now cleared.** ISS-0209 recorded `your-sudoku` as the only clean candidate, and `your-trainer` as carrying *"59 dirty files belonging to another agent's work while it waits."* That work has landed. All four repos have clean trees as of 2026-08-29, so option 1's "cleanest first" is a choice among four rather than a constraint of one.


## Closed 2026-08-29

[[CHG-20260829-The-Fleet-Runs-One-Validator]]. One feature, eight tasks, two tests, three issues filed. All four migrations committed **locally**; nothing pushed.

| repo | errors under upstream's rules | after | gate | divergence before | after |
|---|---|---|---|---|---|
| `obsidian-supernote-sync` | 16 | **0** | 0 → **2** | 782 | **0** |
| `your-health` | 271 | **0** | 0 → **2** | 817 | **0** |
| `your-sudoku` | 194 | **0** | 0 → **2** | 776 | **0** |
| `your-trainer` | 605 | **0** | 0 → **2** | 776 | **0** |

### Three things this phase learned that its plan did not contain

**A report-only census counts the rules that can fire *against the corpus as it stands*.** `your-trainer`'s reconciliation armed a second rule: `VERIFY` reads a feature's `tasks:` from the **snapshot**, so with those lists absent it had nothing to walk and reported nothing during the census. Filling them in — the migration's entire content — produced **15** findings, three features closed while tasks in their scope are open. The census's *"nothing else at all"* was true and was **not a prediction**. Recorded in `your-trainer`'s `tools/GRANDFATHERED.yaml` (155 → 158) rather than guessed at.

**The drift check gates on rule codes, not on lines, and the difference is load-bearing.** `project-os-cockpit` is 1105 lines from upstream and *ahead* of it — new rules are authored here and upstreamed. A line-count threshold would fail the one repo doing the right thing and be switched off within a week. Missing **rule codes** separates behind from ahead exactly: after this phase the four migrated repos and the cockpit are missing **0** of upstream's 52, and the six repos holding no acceptance checks are each missing **10** ([[ISS-0259-Six-Fleet-Repos-Run-Ten-Fewer-Rules]]).

**The drift check cannot run in CI, and the tool says so.** What it measures is drift between *local working copies of sibling repos*; a GitHub runner checks out one repo and has no fleet. A CI job could only ever report "nothing to compare", which is the reports-success-because-it-could-not-look shape this phase exists to remove. Its home is `tools/hooks/pre-commit.local` — tracked here, installed by hand, and `.git/hooks/` is not tracked, so a fresh clone has no gate until somebody installs it. That is a real limit of the guard and is written in its header rather than left to be discovered.

### The sixth criterion, and why it is `~` rather than `[x]`

`REL-0013` needs **32** of `your-trainer`'s 625 checks. **13** are now derived from the note's own `features:` — they had been unreachable because all thirteen were authored for `FEAT-0104` on 2026-08-17 and every one said `covers: FEAT-0011`, so the query returned zero and the table was written by hand *because the query looked empty rather than wrong*. That is fixed and it is a data defect, not a missing tool.

The other **19** are not derivable and no field carries the relation. `features:` answers *what did this release build?*; those nineteen answer *what did this release break?* — checks whose subject the diff overlaps without the release owning the feature they cover. Filed as [[ISS-0258-A-Release-Cannot-Derive-What-It-Broke]] against [[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]'s model rather than worked around in the release note.

### The goal sentence is not fully met, and no `[x]` claims it is

This phase's goal says *"leave behind a drift check that **fails the build** when the next divergence opens, **so this is the last time the fleet has to catch up**."* Exit criterion 4 is narrower — *"reports … and fails past a stated threshold"* — and that is met: `fleet-drift.py` exits 1 for a gated repo that is behind, and [[TST-0081-The-Drift-Check-Fails-When-The-Fleet-Falls-Behind]] exercises the failing branch.

**But nothing runs it.** `.git/hooks/pre-commit.local` does not exist in this repo or in any fleet repo; `tools/hooks/pre-commit.local` is tracked here and installed by hand in three lines; `.git/hooks/` is not tracked, so a fresh clone has no gate. And it cannot run in CI by construction — it compares local working copies and a runner has one repo. So *"the last time the fleet has to catch up"* is **not** guaranteed by anything that shipped: what shipped is a check that will say so, once somebody installs it or runs it.

Stated here rather than left in the tool's header, because a reader of this phase should not have to open a hook to find out whether the guard is armed. Raised by independent review, which found the goal and the criterion saying different things.

**The three issues this phase filed are homed in [[PHASE-999-Future]], not here.** They are follow-ups it produced rather than work it owes: leaving them under a `done` phase fires `PHASE-CHILDREN`, and reopening the phase to hold them would make a closed migration look permanently unfinished. Each names this phase in `related:` so the trail back is intact.

Recording it as half-met is the point. Closing this box on 13 of 32 would be the overclaim [[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]] closed on removing.
