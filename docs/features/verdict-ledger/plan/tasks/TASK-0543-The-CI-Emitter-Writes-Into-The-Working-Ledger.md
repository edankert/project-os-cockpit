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
review_date: 2026-08-20
review_verdict: approved
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
