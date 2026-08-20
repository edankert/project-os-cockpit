---
type: "[[adr]]"
id: ADR-0039
aliases: ["ADR-0039"]
title: "Three sections, derived and not filed — a check is re-checked when behaviour changes, done once when it verifies a fix, or executed by CI, and `tier:` says none of it"
status: "accepted"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
decision_date: 2026-08-19
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
source: ["Edwin 2026-08-19: 'On the verification tests ... these are the tests which have been automated. Can we just make one section and call it automated tests and move all automated tests there, it doesn't matter why they were automated? On the regression tests, these only exist to test issues which were fixed but which we do not expect to be re-occuring and which need to either be tested manually once or otherwise have an automated test. The Feature tests are really the acceptance tests which need to be un-checked set to todo when functionality is changed which warrants a genuine re-check.'"]
supersedes: ""
superseded: ""
related: ["[[ADR-0038-The-Suite-Is-The-Verdict]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ISS-0208-Retire-The-Tier-Rule]]", "[[ISS-0237-An-Automated-Check-Still-Blocks-The-Manual-Walk]]", "[[ISS-0238-There-Is-Nowhere-To-Put-An-Automated-Check]]", "[[FEAT-0138-Coverage-Is-Observed-Not-Declared]]", "[[DES-0012-Tests-In-Two-Flows]]"]
tags: [acceptance, conventions, schema, testing]
decided_option: "3"
---

# Three sections, derived and not filed

## Status

**Accepted 2026-08-19 by Edwin**, by directing implementation, and with two clauses settled in the same exchange: the `Broken command` section takes that name (*"Let's use 'Broken command' as the section. I am happy with the other sections"*), and *run* stays in the documents but leaves the UI.

## Amended before acceptance, 2026-08-19

**`tier:` is deleted, not kept.** As first written this decision retained `tier:` to carry the Tier 1 / Tier 2 distinction and answer [[ISS-0238]]'s question about what a tier means on an automated check. Edwin: *"I agree we either delete the distinction or we model this correctly"* — and then supplied the use case that settles it, below under *The case that settled it*.

Option 4 was rejected as *"too far for now"* on the ground that Tier 1 and Tier 2 have different lifetimes and that difference has to live somewhere. It does live somewhere: **`covers:` already carries it**, and `tier:` was a fourth axis restating part of a field [[ADR-0034]] had already made authoritative. Decisions 3 and 4 below are what changed; decisions 1, 2 and 5 stand as written.

## Context

`TESTING.md` defines three tiers, and each is described by **why a check was created**. Two of the three have since come to mean something else, and the corpus says so plainly.

### What the tiers hold, measured 2026-08-19

| | checks | automated | open | of which automated |
|---|---:|---:|---:|---:|
| Tier 1 · Feature tests | 349 | 17 | 43 | 4 |
| Tier 2 · Regression tests | 164 | 5 | 25 | 5 |
| Tier 3 · Verification tests | 68 | **67** | 0 | 0 |

`your-trainer`; this repo holds 27 + 7 and `your-sudoku` 51 + 5, all manual, no Tier 3 at all. **Nine of the 68 checks blocking `your-trainer`'s release are executed by a machine**, which is [[ISS-0237]].

### Tier 3 is not a tier, it is a destination

`TESTING.md` calls Tier 3 *temporary* — one-time checks for a specific build, removed after a verified release. Its **Unit test replacement** rule is the one that actually fires: *"When unit tests are written that cover the same logic as an acceptance test, the acceptance test can be moved from Tier 2 to Tier 3… Remove after the next release."*

So Tier 3 is where automated checks are parked on their way to deletion, and 67 of its 68 members got there that way. The label says *temporary*; the population is *permanently automated*. Those are opposite claims about the same 67 notes.

The damage is recorded in the notes: all 67 read `area: "Moved from Tier 1 / Tier 2 — Fully Automated"` — **a section heading from a deleted document, not a place in the application** ([[ISS-0235]] drew exactly this distinction) — and `tier: 3`, and `covers: []`. The original areas are not in the notes. They are in `your-trainer`'s git history, first move `d69cf23c` on 2026-04-18 (*"move 10 fully-automated rows to Tier 3"*) and several since, so recovering them is archaeology across commits rather than a field rename. [[ISS-0238]] called it *authoring, not migration*; it is closer to *excavation*.

### And filing is the mechanism that failed

A check reached Tier 3 because a person moved it. That is the same shape of defect [[ADR-0038]] removed from the verdict: a standing claim, written once, that nothing returns to correct. Rename the covering test and the check stays filed under *Fully Automated* forever, verified by nothing.

### Tier 2 was never permanent in practice

`TESTING.md` says Tier 1 and Tier 2 are *"never removed"*. But its own Unit test replacement rule moves Tier 2 checks out, and Edwin's account of what a regression check is for does not describe something re-checked forever at all: **a fixed bug we do not expect to recur, needing either one manual check or an automated test.** A thing you expect to regress gets a machine watching it forever. A thing you do not gets checked once.

Reading Tier 2 as permanent is what makes 25 checks sit open in a repo where nobody intends to check them again.

## Options

1. **Leave the tiers as written.** Costs: 67 notes keep a temporary label over permanent content, nine automated checks keep blocking a release, and the *permanent* reading keeps 25 Tier 2 rows open indefinitely.
2. **Re-tier by hand.** Give the 67 real areas and correct their tiers. Fixes today's data and rebuilds the same trap: the next automated check is filed by a person and rots the same way.
3. **Three roles, and the automated one is derived.** Tier 1 is re-checked whenever behaviour changes, Tier 2 is a queue that empties, and Automated tests is not a tier anybody files into — a check appears there because it carries a `command:`, and leaves when it stops carrying one.
4. **Delete `tier:` entirely** ([[ISS-0208]]'s direction), deriving every distinction it carried from fields that already exist. **Taken on amendment** — see decision 4. It was first rejected as too far, on a premise that turned out to be false: that the Tier 1 / Tier 2 difference had nowhere else to live.

## Decision

**Option 3.**

### 1. Feature tests. Re-checked when behaviour changes.

Unchanged, and now the only tier with this property: **never removed, and un-checked when a change overlaps its scope.** `TESTING.md`'s *When to uncheck* rule stops naming Tier 2 and becomes Tier 1's defining behaviour. The machinery already exists — `mark: rerun` as the explicit act, computed `stale` for a tick standing over overtaken evidence, `invalidated_by:` carrying the change id — and the tier header already reports both counts.

### 2. Regression tests. A queue that empties.

A regression check guards a fixed bug **we do not expect to recur**. It is discharged one of two ways, and then it is done:

- **done once**, and it stays settled — a later code change does **not** re-open it; or
- **given a `command:`**, after which it renders under Automated tests and CI re-runs it forever.

`TESTING.md`'s *"kept permanently / never removed"* is rewritten for Tier 2. The note is still never deleted (`LIFECYCLE.md`); what changes is that a settled Tier 2 check stops being owed.

**This is the clause that carries risk**, and it is stated so it can be argued with: if a bug we did not expect to recur does recur, nothing re-opens its check automatically. The answer is that such a bug files a new issue, and a bug that recurs is by definition one we should have expected — which is what a `command:` is for.

### 3. Automated tests — derived from `command:`, filed by nobody.

**A check renders under Automated tests when its `command:` is non-empty, and nowhere else.** Not a `tier:` value, not a move, not a migration.

- **Nothing is filed and nothing is deleted.** Removal-after-release goes; a check that has been automated is kept, because a kept check with a resolving command is self-correcting and a deleted one is a one-way door ([[ISS-0238]], [[FEAT-0138]]).
- **A check that stops carrying a command falls back to the section its `covers:` implies** (decision 4), so nothing has to remember where it came from.
- **`area:` must name a place in the application**, and the 67 notes reading a deleted document's section heading are wrong on their face. They are repaired or emptied, not left.
- **It is one section regardless of why the check was automated**, which is Edwin's point exactly: promoted from Tier 1, replaced from Tier 2, or born with a command — the reader is asking *does a machine do this*, and there is one answer.

### 4. `tier:` is deleted. What it said is derived from `covers:` and `command:`.

[[ADR-0034]] fixed three axes — `level` says what a test exercises, `command:` says who runs it, `covers:` says what it gates — and *"no axis implies another"*. `tier:` was a fourth, and it restated part of the third.

| what the check covers | what it claims | a change invalidates it? | section |
| --- | --- | --- | --- |
| a `FEAT-*` | *the system does X* — a standing claim about behaviour | **yes** | Feature tests |
| an `ISS-*` | *this defect was fixed* — a claim about a past event | **no** | Regression tests |
| *(carries a `command:`)* | CI re-runs it | n/a — never stale | Automated tests |

**The middle row is the load-bearing one, and it is not a policy choice.** A later change can falsify *"the app does X"*. Nothing a later change does can falsify *"this bug was fixed in this build"* — a one-time check is not re-checkable even in principle, so *never invalidated* is a property of what it asserts rather than a rule imposed on it. That is why this can be derived at all.

**One authoring rule makes it total: a check that is not a standing behaviour claim must name the `ISS-*` it verifies.** Enforceable at write time, which is what stops the debt growing.

**The debt, measured 2026-08-19:** 68 of `your-trainer`'s 164 Tier 2 checks name **no `ISS-*` anywhere in the note** — not in `covers:`, not in the body. A further 5 name one outside `covers:` and are a scripted repair. Deriving today would silently reclassify those 68 as behaviour checks and put them back on the list at every overlapping change, which is the exact behaviour this decision removes. So they are **grandfathered by ID with a dated promotion** ([[project-os-dev#ADR-0011]]), not migrated by guess. `covers:` on the legacy corpus records *provenance* — 35 point at a `FEAT-*`, 17 at `PHASE-013`, 26 at a `TASK-*` — which is the same conflation [[ISS-0235]] found between what a check verifies and what it came out of.

### 5. The group that asks is called `Needs you`.

`Needs a run` becomes `Needs you`, matching every other view ([[ADR-0025]], `_needs_you_group`). The existing comment argues a specific name *"says more than 'needs you'"*; consistency across the nav is the better argument, and the group already carries `needs_human: true`, so the look and feel is unchanged.

### The case that settled it

Edwin, 2026-08-19: *"there was an issue in android which we fixed and we quickly need to make sure this was fixed (db version moved, or obfuscation issue) this should never reapear and should not become an acceptance test when delivering similar iOS features."*

**Neither half needs a tier, and one half a tier could never have provided.**

- *Never reappears* is already the default. The check covers its `ISS-*`, so nothing invalidates it — and under [[ADR-0037]] decision 7 a `pass` **survives the seal** (`PERSISTS = {pass, partial, na}`), so it carries into the next release instead of being re-asked.
- *Not inherited by iOS* is `na` in the iOS ledger — *"a statement about the check and the platform"*, which persists identically. It is asked once ever, not once per release. **A tier is a property of the check; this is a fact about check × platform**, and a scalar on the note cannot hold it. That is [[ISS-0236]]'s observation one level down.

**Stated against the corpus rather than around it: this use case has zero instances.** All 68 Tier 3 checks are parking-bay residue, including the single manual one — `TST-0591` carries the same `area: "Moved from Tier 1 / Tier 2 — Fully Automated"` as the 67. And **no ledger entry exists anywhere in the fleet**; `na` and the persistence rule are implemented, validated and reachable, and have never executed. This part of the decision therefore cannot be proved from data and must be proved on constructed input.

## What `TESTING.md` must say

The instruction file is template-owned; canonical is `~/Dev/repos/project-os/tools/instructions/TESTING.md`, and these edits land there and sync down.

1. **Tier 3 § replaced** by Automated tests, defined by `command:` and explicitly permanent. *Unit test replacement* stops ending in removal — it ends in a `command:`.
2. **Tier 2 §** loses *"kept permanently"*; gains the two discharges and the statement that a settled regression check is not re-opened by later change.
3. **§ When to uncheck** narrows from *"all Tier 1 and Tier 2 tests"* to Tier 1.
4. **§ When to remove** loses the Tier 3 clause, leaving nothing that removes a check.
5. **The tier vocabulary goes.** *Acceptance test tiers* is replaced by the three sections and the rule that derives them; `tier:` stops being a field anyone writes. The words *feature test* and *regression test* stay — they are good names for what the sections hold.

**`STATUSES.md` is corrected by the same change.** Its line 144 attributes *"never removed, only deprecated"* to `TESTING.md` as a rule about any test, while `TESTING.md` scopes it to Tier 1 and Tier 2 and removes Tier 3. That is the upstream ambiguity [[ISS-0238]] flagged; once nothing removes a check the two documents agree, and the attribution becomes true rather than merely uncontradicted.

**Fleet state before the sync**, measured 2026-08-19: `project-os-cockpit`, `your-trainer` and `your-sudoku` are byte-identical to upstream. `your-health` and `project-os-dev` are stale by the same 26 lines — a plain sync, no conflict.

## Alternatives

- **Keep Tier 3 and add an `automated: true` flag.** A second field answering a question `command:` already answers — the exact defect [[ADR-0034]] decision 4 removed, re-introduced one level down.
- **Let an automated check keep displaying under its tier, marked.** Considered and rejected against Edwin's *"it doesn't matter why they were automated"*: the mark would be the answer to the only question being asked, rendered as an annotation on a grouping that answers a different one.

## Consequences

- **The release gate drops from 68 open to 59** in `your-trainer` the moment Automated tests is derived — the nine automated checks in Tiers 1 and 2 stop being owed. Measured per repo before landing, as every [[PHASE-038]] gate change was. Zero change in this repo and `your-sudoku`, which hold no automated checks.
- **Tier 2's 25 open checks each need a disposition** — do it once, or give it a command. That is a real body of work and it does not happen by re-labelling.
- **The 67 areas are still wrong** and this decision does not fix them; it removes the reason they were destroyed. Excavating them from `your-trainer`'s history is a separate task with a real cost, and emptying the field is the honest alternative to inventing 67 areas.
- **`tier:` stops being written and stops being read.** 671 notes carry one; the field is left in place and ignored rather than stripped in the same change, so a bad derivation is recoverable. Removing it is a later, separate migration once the sections have been read against for a while.
- **`GATING_TIERS = (1, 2)` and `PERMANENT_TIERS` go with it.** Gating becomes: an unsettled manual check blocks, an automated one never enters the manual list. That is one rule where there were two constants and a tier test.
- **68 checks are grandfathered, by ID and with a promotion date.** They are the ones that cannot name the issue they verify. This is debt that cannot grow, because the authoring rule refuses new instances.
- **A new obligation exists, and it is called `Broken command`**: an automated test whose `command:` no longer resolves. Named by Edwin, 2026-08-19, over *Unwired* — the state has a plain description and does not need an image. Measured 2026-08-19 across all 139 automated notes fleet-wide, **zero** currently fail to resolve — so this cannot be proved from the corpus and must be proved on constructed input, which is [[FEAT-0138]]'s acceptance criterion 4.

## Measurement basis, corrected 2026-08-20 after a second independent review

**Every number in the Context section above was taken from `your-trainer`'s WORKING TREE**, which carried 588 uncommitted files at the time. Against `HEAD` — what a fresh clone has, and what any other machine sees — the corpus is different, and the difference is the whole automated population:

| | Tier 1 | Tier 2 | Tier 3 | carrying a `command:` |
| --- | ---: | ---: | ---: | ---: |
| working tree | 349 | 164 | 68 | **89** (17 / 5 / 67) |
| `HEAD` | 349 | 158 | **74** | **0** |

**At `HEAD` no acceptance check in `your-trainer` is automated at all.** So the sentence *"67 of its 68 members got there that way"* describes uncommitted work, and the release-gate consequence runs the other way: **62 → 68**, six Tier 3 checks entering rather than nine automated ones leaving.

**None of this changes the decision.** The argument was never the count — it was that Tier 3's *label* and its *population* were opposite claims, that filing is what rotted, and that a check a machine executes should be derived rather than moved. Those hold at either basis, and the `HEAD` figures make the second half of the same rule visible instead: 74 one-time checks that nobody automated and nobody completed are owed, which is decision 2 applied to the tier decision 3 retires.

**What it does change is what a reader should expect on landing.** In `your-trainer` today this adds six checks to the gate; it removes nine only once that repo's uncommitted work is committed. Recorded in [[CHG-20260820]] and [[ISS-0240]].
