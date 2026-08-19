---
type: "[[adr]]"
id: ADR-0038
aliases: ["ADR-0038"]
title: "An automated test records that it is automated, not whether it passed — the suite is the verdict, and only a manual test carries one"
status: "accepted"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
decision_date: 2026-08-19
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
source: ["Edwin 2026-08-19: 'In general, the automated tests should record that they are automated, they do not need to record that they pass, there should be a rule which doesn't allow unit or automated regressions to fail (I think this is a general sw-dev rule). The tst does not need to record this, however for manual tests, we do need to record this.'"]
supersedes: ""
superseded: ""
related: ["[[project-os-dev#ADR-0010]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]", "[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]", "[[ISS-0237-An-Automated-Check-Still-Blocks-The-Manual-Walk]]", "[[ISS-0238-There-Is-Nowhere-To-Put-An-Automated-Check]]", "[[ISS-0239-The-Runner-Stamps-Failing-On-A-Missing-Device]]", "[[FEAT-0138-Coverage-Is-Observed-Not-Declared]]", "[[REQ-0057-Coverage-Is-Observed-From-A-Run]]", "[[DES-0012-Tests-In-Two-Flows]]"]
tags: [conventions, schema, testing]
decided_option: "3"
---

# The suite is the verdict

## Status

**Accepted 2026-08-19 by Edwin**, by directing implementation — *"Define the features/requirements/tasks etc .. to implement the discussed changes fully"*, then *"After creating the docs, then implement, test and independently verify the full implementation."* Not through the decision actuator, so the instruction is quoted here rather than a click being cited.

Accepted alongside [[ADR-0039]], which depends on it. [[PHASE-039]] is the body of work.

## Rule

A test note that declares a `command:` never holds `ready`, `passing` or `failing`, and carries no `last_run:` or `exit_code:`.

## Domain

Every `TST-*` note whose `command:` is non-empty — **139 fleet-wide** on 2026-08-19: `your-trainer` 91, this repo 38, `your-health` 6, `project-os-dev` 4. The predicate is the one `cockpit._is_manual_test` already uses (ADR-0034 decision 4), inverted; there is no second reading of a `kind:` or `automation:` field and no new field to keep in step.

## Conformance

`ACCEPTANCE-STATUS`, widened. The check already exists and already states this rule — it is an **error** today when a `level: acceptance` note holds `ready`/`passing`/`failing`, over the 89 automated notes that sit at that level. This decision changes its domain from `level: acceptance` to `command: non-empty`, which takes it from 89 notes to 139. `TEST-AUTOMATED-EVIDENCE` is the new sibling for `last_run:`/`exit_code:`.

**The rule is authoritative.** A note carrying a verdict is wrong, and the resolution is to remove the stamp, never to widen the rule. There is no case where an automated note's frontmatter is better evidence than the execution that would produce it.

## Context

### The rule already exists, over two-thirds of its own domain

This decision does not invent a constraint. It notices that the corpus enforces one already and cannot say why it stops where it does.

`ACCEPTANCE_FORBIDDEN_STATUSES` forbids `ready`, `passing` and `failing` on any `level: acceptance` note, as an **error**, because — in the words of the code — `passing` is "the review gate and the runner-only rule" and `ready` is the obligation registry's `Run`, and a note holding either "means the merge's central construction has failed" ([[ADR-0031]], [[ADR-0027]]).

Measured 2026-08-19: **89 of the 139 automated notes are at `level: acceptance`**, so on 64% of the domain the rule below is already law. The other 50 are the same kind of thing — a note naming a command a machine executes — and hold verdicts only because nothing stopped them.

### What is measured, fleet-wide, 2026-08-19

**786 test notes.** 139 automated, 647 manual. Of the manual ones, **582 are acceptance checks a person does, whose verdict lives in the ledger** ([[ADR-0037]]) and whose `status:` is `active` — not a verdict, and not read as one. That leaves **65 manual tests where `status:` genuinely records a human verdict**: 45 `passing`, 14 `ready`, 6 `retired`.

So `status:` as a verdict is load-bearing on **65 of 786 notes**, and Edwin's split names exactly those 65.

On the automated side the field is not merely redundant, it is barely populated in the direction that would matter:

| | notes | carry `passing`/`failing` | carry `last_run` | carry `exit_code` |
|---|---:|---:|---:|---:|
| project-os-cockpit | 38 | 37 | 38 | 29 |
| your-trainer | 91 | 2 | 2 | 69 |
| your-health | 6 | 6 | 6 | 6 |
| project-os-dev | 4 | 4 | 4 | 4 |
| **total** | **139** | **49** | **50** | **108** |

`your-trainer` is the shape of the problem: **69 notes carry an `exit_code` and 2 carry a verdict**. That is `run-tests.py` having written into notes where the validator forbids the value it wanted to write, leaving the residue behind after the verdict was rejected or reverted. The most-written field on the automated corpus is the one that means least.

### And the runner's own premise refutes it

[[project-os-dev#ADR-0010]] — *"Test status is stamped by execution, not asserted by an author"* — was decided on this evidence, quoted from `run-tests.py`'s docstring:

> Across 10 repos and 5,890 status writes that gate has never once observed a failure — `failing` was written zero times, 78% of test notes are born `passing`, and 99% never change again.

`failing` is **still** written zero times, one year of corpus later. The measurement is unchanged; only its reading is. ADR-0010 read "no failure was ever recorded" as *authors do not record failures* and moved the writer. The alternative reading — *a red automated test is not a state anybody records, because it is a state nobody ships* — fits the same number and costs a field instead of a mechanism.

Edwin's sentence is that reading: **"there should be a rule which doesn't allow unit or automated regressions to fail."** A red unit test is a broken build. Broken builds get fixed, not documented.

### What the stamp cannot do, and the command can

A stamped `passing` cannot notice that the test it stands for was renamed, deleted or `@Ignore`d. It goes on asserting a verdict about something that is no longer executed — and nothing anywhere returns to correct it.

A `command:` **stops resolving**. That is a signal the stamp structurally cannot produce, it is self-correcting, and it is the property [[FEAT-0138]] and [[REQ-0057]] are built on. Trading a claim that cannot go stale-visibly for one that can is the whole of this decision.

## Options

1. **Keep stamping.** [[project-os-dev#ADR-0010]] unchanged. Costs: the runner keeps writing a value the validator forbids on 89 of 139 notes, and [[ISS-0239]] stays a live data-loss path.
2. **Fix the classifier only.** [[ISS-0239]]'s own suggestion — teach the runner that a missing device is `unrunnable`, and guard the write. Treats the symptom: the verdict is still stored where it rots, and a better classifier still cannot notice a renamed test.
3. **An automated test records that it is automated and nothing else; a manual test records its verdict.** The forbidden-status rule widens from `level: acceptance` to `command:`, the runner reports instead of writing, and the `VERIFY` gate is discharged for an automated test by its command resolving.
4. **Delete `status:` from every test note.** Symmetrical and wrong: the 65 manual tests have no other place to put a verdict, and this is precisely the half Edwin says must keep recording.

## Decision

**Option 3.**

1. **A `command:` is the record.** It says a machine executes this, which is the durable fact. Whether the machine was happy last Tuesday is not.
2. **`run-tests.py` reports and does not write.** It keeps its three outcomes and its non-zero exit; it stops stamping `status:`, `last_run:` and `exit_code:`. CI failing is the signal, and it is louder than a note.
3. **The `VERIFY` gate is discharged for an automated test by its `command:` resolving**, not by a stamped status (`validate_docs_bundled.py:2141`). For a manual test the gate is unchanged: `passing`, and not stale.
4. **Manual tests are untouched.** All 65 of them keep `status:` and its staleness clock, because nothing else knows how a person's check went. The 582 ledger-tracked checks are likewise untouched — [[ADR-0037]] already moved their verdicts.
5. **[[ISS-0239]] is dissolved rather than fixed.** Its defect is that a non-result overwrites a verdict. Under this rule there is no verdict in the note to overwrite, and the misclassification degrades to a wrong line in a report. The classifier is still worth fixing; it is no longer worth a data-loss guard, and the "never overwrite a passing" rule that issue proposes is withdrawn — it would have blocked the runner from recording a genuine regression, which is the one thing [[project-os-dev#ADR-0010]] exists to do.
6. **[[ISS-0237]] gets its principle.** An automated check discharges the manual list because a machine executes it; that is this rule seen from the manual list's side rather than a separate argument.

## The limit, stated plainly

**This rule is exactly as good as the suite that enforces it, and in most of the fleet there is no suite.** [[ISS-0209]]: the acceptance gate executes in no repo that holds a check. "CI is green" is a guarantee in this repo, where CI executes the 38 automated notes on every push. In `your-trainer` — 91 automated notes, the largest population in the domain — it currently guarantees nothing, because nothing executes them on a schedule anybody watches.

Removing the stamp there does not create that gap; it stops the corpus from papering over it with 2 verdicts and 69 orphan exit codes. But this decision **must not be read as evidence that those 91 tests pass**, and the honest sequence is that [[ISS-0209]] is resolved for a repo before this rule is claimed to protect it.

## Alternatives

- Keep the stamp and add a freshness clock to it — a `last_run` older than N days stops discharging the gate. Rejected: it is a second staleness mechanism for a value that should not exist, and it still cannot see a renamed test.
- Store the verdict outside the note, per execution, as the acceptance ledger does ([[ADR-0037]]). Not rejected so much as **already true** — that is what CI is. Building a second ledger to hold what a CI execution already reports is the mechanism this decision removes.

## Consequences

- **A migration over 49 notes** — strip the verdict, `last_run` and `exit_code` from every automated note. 37 are in this repo and can land with the decision; 12 are in three other repos and land with the fleet sync. Preferred landing is zero-violation, so the widened check errors from day one rather than taking a warning tier ([[project-os-dev#ADR-0011]]); if the fleet cannot be swept in the same change, the check lands warning-first with a dated promotion and the 12 listed in `GRANDFATHERED.yaml`.
- **The Tests view's left-hand sections stop working**, and this is the visible half of the change. Every non-acceptance group in `_tests_groups` is a verdict state — `Failing`, `Stale`, `Never verified`, `Verified` — and an automated test will have none. Measured today: **all 37 of this repo's automated tests sit in one group, `Verified`, which is collapsed by default**; in `your-trainer`, 89 of 91 are scattered through the manual tier sections. There is nowhere in the nav that shows the suite as the suite. The replacement axis is *is it still wired*, not *did it pass* — designed separately.
- **`note_writes.py`'s `test-run` actuator changes meaning**: executing a test from the cockpit reports a result; it no longer transitions the note.
- **`TESTING-MODEL.md` line 49 is wrong on landing** — it documents `status:` as "written by the runner from the exit code" — and so is `run-tests.py`'s module docstring, which is the clearest statement of the position being reversed.
- **New failure mode, deliberately**: a `command:` that no longer resolves. It is the one thing an automated note can owe a person, it is invisible today, and it is the reason the nav needs a group for it.
