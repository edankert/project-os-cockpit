---
type: "[[task]]"
id: TASK-0543
aliases: ["TASK-0543"]
title: "The CI emitter appends observed-coverage entries into the working ledger for its platform"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-21"
reviewed_by: model:claude-opus-5
review_date: 2026-08-21
review_verdict: changes-requested
review_response: "2026-08-21: the `--by` filter is gone from the invalidation set and the failing branch's asymmetry is documented as the decision it is, with tests constructing a `manual` and a `migration` verdict for both directions."
review_response_date: 2026-08-21
parent: "[[FEAT-0138-Coverage-Is-Observed-Not-Declared]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# The emitter

## Definition of Done

- [x] A green CI run appends one `method: automated` entry per covered check, with `by:` naming the test and `date:` the run — `.github/workflows/observed-coverage.yml`, `test_a_green_run_appends_one_automated_entry_per_covered_check`.
- [x] A failing test emits `mark: fail` with the failure as the reason, or emits nothing — **decided, and neither**: it emits an **invalidation**. The reasoning is below; `test_a_failing_covering_test_invalidates_rather_than_emitting_fail`.
- [x] The platform comes from the run's target — the observing job runs on `macos-latest` and emits `--platform macos`, because this repo's ledger is `WORKING-macos.json` and emitting macos verdicts from a linux runner would be a false statement about where the evidence came from.
- [x] **Deleting a covering test puts its check back on the run list — proved**, in this repo, by construction: `test_deleting_the_covering_test_puts_its_check_back_on_the_run_list`. [[ISS-0209]]'s limit stands and is stated below.

## Notes

Criterion 4 is the whole point of Stage 2 and the one thing a standing field could not do.

**The limit, and it must not be papered over:** [[ISS-0209]] — the acceptance gate runs in **no repo that holds a check**. Until that is resolved this emitter runs here and nowhere the data lives, so criterion 4 is proved in `project-os-cockpit` only. State that; do not report the fleet as covered.

The failing-test decision matters more than it looks. Emitting `fail` puts a machine-driven population into the release gate — the behaviour change [[ADR-0031]] recorded as a risk rather than discovering later. Same call, same place to record it.

## Re-homed 2026-08-20 — the parent moved and this did not

[[FEAT-0138]] was re-homed from [[PHASE-999]] into [[PHASE-037]] on 2026-08-20 (Edwin). **Its tasks stayed behind**, so a task pointed at a parking-lot phase while the feature it delivers pointed at an active one.

That is not cosmetic: `PHASE-CHILDREN` gates a phase on **notes naming it in `phase:`**, so for as long as this task named `PHASE-999` it was invisible to the gate on the phase that actually owns its work — and `PHASE-999` is never closed, so it was invisible to every gate. A child in a parking lot cannot hold anything open.

The phase's own widening note records the same class of miss one level up: *"FEAT-0138 also pointed at PHASE-999 without ever being listed in it, which is why nothing flagged it."*

**The consequence is deliberate.** [[PHASE-037]] now cannot close while this task is unresolved. That is the honest reading of Edwin's re-homing: if the feature belongs to this phase, so does the work that delivers it.

## Independent review — fresh-context pass, 2026-08-20 (`4521a7a`)

Separate session, `model:claude-opus-5`, starting from the notes and the diff with no access to the author's reasoning. Same model family as the author, recorded in `reviewed_by`; the independence claimed here is **context**, not weights ([[project-os-dev#ADR-0013]]).

**Verdict: approved.** The consequence the note claims was constructed and watched rather than reasoned about.

Materialised `HEAD` into a scratch tree, set `PHASE-037` to `done` in **both** the phase note and `SNAPSHOT.yaml` — `effective_status` reads the snapshot, so editing the note alone leaves the rule silent, which is worth knowing before anyone tries to reproduce this — and ran the validator:

```
ERROR [PHASE-CHILDREN] PHASE-037 is 'done' but 14 item(s) still name it as their phase
without a resolved status: … TASK-0542 (backlog), TASK-0543 (backlog); …
```

So the claim holds exactly: both tasks are now inside the gate on the phase that owns their work, and `PHASE-037` cannot close while either is unresolved. `PHASE_RESOLVED["task"]` is `{done, cancelled, superseded}` and `backlog` is not in it; `CLOSED_PHASE_STATUSES` is `("done", "superseded")` and `PHASE-999` is `planned`, so the note's *"a child in a parking lot cannot hold anything open"* is accurate rather than rhetorical.

The `SNAPSHOT.yaml` half was checked separately: both entries carry `phase: "[[PHASE-037-…]]"`, and `sync-snapshot.py` does propagate `status` and not `phase`, so the hand edit was necessary. `TASK-0541` keeping `PHASE-038` is consistent with it being `done`.


## Built 2026-08-21

`tools/scripts/emit-coverage.py`, reading the declarations and the run's **JUnit XML** — which pytest writes with `--junitxml` and gradle writes natively, so the two toolchains [[TASK-0542]] names need no shared library here either.

### The failing-test decision, made rather than defaulted

This task named two options and the answer is a third, so the reasoning is recorded rather than the choice.

**`mark: fail` is wrong.** `fail` is a *walk* verdict in the blocking vocabulary, so emitting it would put a machine-driven population straight into the release gate — the behaviour change [[ADR-0031]] recorded as a risk rather than discovering later.

**Emitting nothing is wrong too.** It leaves the last green run's `pass` standing over a test that now fails, which is the stale-verdict shape this whole phase exists to remove.

**An invalidation says exactly what is true**: the evidence for that verdict no longer holds. The check goes back on the run list without anybody asserting a walk that never happened. `ledger.resolve` already clears a standing verdict on an invalidation, so no new vocabulary was needed — [[ADR-0037]] decision 6's `invalidated_by` is precisely this event.

### The defect that would have made the whole feature a no-op

The first cut computed the invalidation set as *declared but not observed*. **Deleting the test deletes the declaration too** — so the check left the set that could be invalidated and stayed settled forever. That is `covered_by:`'s silent rot reproduced exactly, inside the tool built to end it.

It is read from the **ledger** now: *this emitter said a machine covered it — did a machine cover it this time?* Caught by `test_deleting_the_covering_test_puts_its_check_back_on_the_run_list`, which **failed on its first run**, which is the only reason it is not still there.

### Three properties worth naming

- **Only this emitter's own verdicts are invalidated.** A person's `manual` walk and a `migration` backfill are not the emitter's to overturn: it observes runs, and it has observed nothing about those.
- **Every declaring test must pass.** A check covered by five tests is covered by all five; reporting it as passing because four did is the overclaiming this phase spent itself removing.
- **It appends only when the answer changes.** The ledger is an event log and an event is a change; an identical re-append on every green run would grow the file and record nothing.
- **A skipped test is not observed.** `@Ignore` is the case [[FEAT-0138]] names beside delete and rename, and it produces an invalidation, not a pass.

### The limit, stated and not papered over

[[ISS-0209]]: the acceptance gate runs in **no repo that holds a check**. The emitter runs here and nowhere the fleet's data lives, so criterion 4 is proved in `project-os-cockpit` **only**. The fleet is not covered and nothing in this task or its workflow claims it is.

### It does not push

The emitter writes the working ledger and stops; the workflow prints the diff and never commits. A commit is local and reversible; a push is publishing, and in this project publishing is a person clicking something. `test_it_does_not_push` and `test_ci_does_not_push_the_ledger`.

## Independent review — 2026-08-21

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `f5ca55b..07602db`; the author's reasoning trace was not available to it. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — same model as the author, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant rather than read.


**Verdict: changes-requested.** The inversion is the right design, the removal of `covered_by:` is safe and honestly measured, and the headline criterion is genuinely proved. Two defects remain in the emitter, one of them the same class of silent rot this feature exists to end.

### What survived refutation

- **The `covered_by:` removal is safe.** Re-measured across all 12 `SNAPSHOT.yaml`-bearing repos under `~/Dev/repos/`, against `git archive HEAD` as well as the working tree: **671 acceptance checks at HEAD**, of which 635 carry the key and **every single value is the literal `[]`**. Zero non-empty values anywhere, in either tree. No `.base` view, no `.ts`/`.js`, and no script *reads* the field — the only code touching the name refuses it (`LEDGER_MOVED_FIELDS`) or strips it. Removing it changes no repo's gate, exactly as claimed.
- **The headline criterion is proved, not asserted.** `test_deleting_the_covering_test_puts_its_check_back_on_the_run_list` settles a check by a run, deletes the test file, runs again, and asserts the check is blocking. That is a real construction.
- **A `manual` walk survives the stale path.** Constructed: a `method: manual` verdict, then the covering test deleted. The emitter printed *"nothing changed"* and the verdict stood.

### Finding 1 (medium) — the invalidation set is keyed on `--by`, so renaming the CI job makes every prior verdict permanently un-invalidatable

`plan()` computes:

```python
stale = sorted(check for check, verdict in current.items()
               if verdict.method == "automated" and verdict.by == by
               and check not in passing and check not in failing)
```

`by` comes from `--by`, and `.github/workflows/observed-coverage.yml` passes the literal `"ci:observed-coverage"` — a string tied to the workflow's name.

Constructed and executed: settle a check with `--by ci:test`; delete the covering test; run again with `--by ci:renamed-job`. Output was *"nothing changed (0 check(s) observed passing)"* and the check stayed **settled and non-blocking**, with no covering test in the repo.

This note already records catching this class once — *"the invalidation set was computed from the declarations, so deleting the test … removed the check from the set that could be invalidated"*. Keying on `by` is the same defect through a different field: the set that can be invalidated depends on something that can change independently of the evidence. Renaming a CI job is an ordinary edit, and the failure is silent and permanent.

### Finding 2 (medium) — *"Only this emitter's own verdicts"* is false on the failing branch

`plan()`'s docstring states: *"**Only this emitter's own verdicts.** A person's `manual` walk and a `migration` backfill are not the emitter's to overturn."* The `failing` loop in `main()` carries no `method`/`by` filter at all:

```python
for check, tests in sorted(failing.items()):
    if check not in current:
        continue
    ... _ledger.append(..., invalidated_by=run, ...)
```

Constructed: a `method: manual`, `by: user:edwin` verdict, then a run in which a declaring test fails. The emitter invalidated the person's hand walk and the check became blocking.

The *behaviour* is defensible — the evidence is contradicted, and invalidating is the conservative move. The **documented claim is not**, and nothing tests it: `tests/test_observed_coverage.py` never constructs a `manual` or `migration` verdict. Either narrow the code to match the docstring or narrow the docstring to match the code, and add the case.

### Finding 3 (low) — the documentation impact list is short by two files

The `CHG` note's impact list names neither:

- `tools/instructions/TAXONOMY.md:61`, which still states *"a `passing` test named in another's `covered_by:` settles it"*. This commit deleted `_resolve_coverage`, so that sentence is now false. It is template-owned and present in four fleet repos, so the fix belongs upstream — but it should be *named*.
- `tools/scripts/migrate-acceptance-checks.py:149`, which still writes `covered_by: []` into every note it emits while `LEDGER_MOVED_FIELDS` refuses the field in any ledger-keeping repo. Pre-existing rather than introduced here, but this change is what strands it, and eight of twelve repos have not migrated.
