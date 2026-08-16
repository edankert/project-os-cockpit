---
type: "[[feature]]"
id: FEAT-0103
aliases: ["FEAT-0103"]
title: "The gate is walkable — declare the next release, see the checks that gate it, and walk them one at a time with a record of who walked what"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
reviewed_by: "model:claude-opus-5"
review_date: 2026-08-16
review_verdict: changes-requested
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin 2026-08-16, after PHASE-034 shipped: 'Don't understand I still don't seem to be able to see and execute the current set of acceptance tests for the next release?'", "Edwin's original report, 2026-08-16: 'it is not really clear how I should execute'"]
goal: "Close the half of the original report that [[FEAT-0102]] left open: a person can say which release they are preparing, see the individual checks that gate it rather than a count, reach any of them in one click, and walk a section one check at a time with pass/fail and evidence recorded against a witness."
requirements: []
tasks: ["[[TASK-0430-The-Suite-Is-Addressable]]", "[[TASK-0431-Declare-The-Next-Release]]", "[[TASK-0432-The-Gate-Lists-Its-Checks]]", "[[TASK-0433-The-Acceptance-Walker]]"]
design: ""
release: ""
depends: ["[[FEAT-0102-Publication-Becomes-A-View]]"]
related: ["[[ADR-0028-Work-Has-Three-Phases]]", "[[FEAT-0102-Publication-Becomes-A-View]]", "[[FEAT-0063]]", "[[ISS-0172-A-Manual-Test-With-Subsections-Has-No-Runnable-Steps]]", "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"]
tests: ["[[TST-0029-The-Walker-Ticks-What-It-Walked]]", "[[TST-0030-Walking-A-Release-Gate-End-To-End]]"]
---

# The gate is walkable

## Why this exists

[[FEAT-0102]] shipped and Edwin said: *"Don't understand I still don't seem to be able to see and execute the current set of acceptance tests for the next release?"*

He is right, and the mis-scope is precise. His original report had two halves — *not clearly visible* and *not clear how I should execute*. [[ISS-0172]] fixed **execute** for `TST-*` notes. For the acceptance suite, [[FEAT-0102]] built only the **counter**.

What the Publication view gives him today:

- `Release gate · 60 unchecked`, expanding to **17 rows that are area names, not checks** — `Trainer Compatibility Verification · 20 unchecked`
- each linking to `docs/tests/ACCEPTANCE_TESTS.md` **at the top**, where section 1.25 begins at line 522 of 1082, after 327 other checkboxes
- and, because nothing is `draft`, the gate reads *"no release in preparation"* and asks for nobody

So there is no *current set*, no list of *the checks*, and no way to *walk* one. The exit criterion [[FEAT-0102]] met — *"reachable from a surface that names the number"* — was too weak, and meeting it exactly is how the phase closed with the reported problem still standing.

**What already works, and is worth stating** so this feature does not rebuild it: `POST /api/notes/check-toggle` handles any `.md` under `docs/`, and the rendered suite carries **542 live checkboxes**. Ticking is not the missing piece. Seeing, reaching, and recording are.

## What this builds

**1. The suite is addressable** ([[TASK-0430]]) — a check can be named, found and written by a stable address rather than by a global checkbox index that shifts whenever the file is edited.

**2. Declare the next release** ([[TASK-0431]]) — create a `REL-*` at `draft` from the cockpit. That is what makes 60 unchecked rows *the current set for the next release* rather than a standing property of a checklist.

**3. The gate lists its checks** ([[TASK-0432]]) — the 60, by name, each reaching its own section anchor. The anchors already exist (`#125-trainer-compatibility-verification`) and nothing uses them.

**4. The walker** ([[TASK-0433]]) — the stepper shape the `TST-*` runner already has, over a section's unchecked rows: one check at a time, pass / fail / skip, evidence, and a tick written back with a witness.

## Acceptance criteria

- [x] A person can declare the release they are preparing, and the gate then names it — `Release gate · 60 unchecked · preparing 2.1.7` — `POST /api/notes/release-prepare` -> `Prepare release…` on the gate summary. Walked live: declared 2.1.7 and the label became `Release gate · 4 unchecked` with the obligation firing
- [x] The gate lists the **individual checks**, not only area counts, and the number it states equals the number of rows it lists — `test_the_gate_lists_individual_checks_not_area_counts` + `test_the_stated_number_equals_the_rows_listed`
- [x] A check row reaches **its own section** in the suite, not the top of the file — `Item.anchor`, slugified with markdown's OWN function — verified character-for-character against the live render
- [x] A section can be walked: one check at a time, with pass / fail / skip and an evidence field — `~walk` / `~walk/<section>`, the TST stepper's shape reused
- [x] A passed check is **ticked in `ACCEPTANCE_TESTS.md`** and carries a dated witness — `REQ-0028`'s rule that acceptance names who stood behind it, which is why PHASE-022's twelve rounds left only a chat transcript — walked live: `- [x] **Alpha:** … _(walked 2026-08-16 · user:edwin — resistance responded at 200W)_`
- [x] A failed check stays **unticked** and records what went wrong. A walk that fails is evidence of a defect, not of progress — walked live: `- [ ] **Beta:** … _(FAILED 2026-08-16 · user:edwin — ERG never engaged)_`, and the blocking count did not fall for it
- [x] A check is addressed by **section and ordinal**, never by a global checkbox index — an index shifts when anything above it is edited, and a walker that writes the wrong row is worse than one that writes nothing — `acceptance.locate`; `test_editing_a_row_above_does_not_move_the_target` is the assertion a global-index walker fails and nothing else catches
- [x] An `mtime` guard refuses a stale write, as every other write path in `note_writes` does — `test_a_stale_write_is_refused`
- [x] Walking is loopback-only (`REQ-0027`), and the walker adds no route that can publish anything — `test_every_note_mutating_endpoint_requires_loopback` enumerates the dispatch table, so both new routes are covered by existing
- [x] Ticking a `- [~]` reconciled row is refused — that mark means settled by decision, and a walker must not silently convert it into a walked check ([[ISS-0141]]) — `test_a_reconciled_row_is_refused`
- [x] The gate still contributes **one** obligation, never sixty ([[ADR-0028]]); listing the checks must not put them back on a badge — `test_the_gate_still_contributes_one_obligation_never_sixty`, and TST-0028's bound assertion still passes unchanged

## Notes

**Not a second runner.** The `TST-*` stepper (`buildTestRunner`) is the desk's one piece of genuine machinery. This reuses its shape and, where it can, its code — a second stepper with its own vocabulary is [[ISS-0023]] with a different noun.

**Not in scope: cutting the release.** Declaring `draft` says *I am preparing this*. Shipping it stays a person's act elsewhere ([[ADR-0022]]), and this feature adds no path that publishes.


## Delivered 2026-08-16

Walked end to end against a throwaway repo, driving the real endpoints: declared 2.1.7, gate went `4 unchecked · no release in preparation` -> `4 unchecked` **and asking**, then pass / fail / skip on three checks left the suite exactly as designed and the count at 3. Both refusals fired through the live server.

### I rebuilt something that already existed

`note_writes.create_release` **has existed since TASK-0316** — it scaffolds a release note as a `draft` and its docstring already quotes the same `STATUSES.md` line I quoted. I wrote a second function with the same name, which silently shadowed it and broke four `test_unreleased.py` tests. The suite caught it; I did not.

The duplicate is gone and the real one is extended instead, with an optional `version` plus the two guards this feature needs — refuse a version at or below the newest `released`, and refuse a second release in preparation. The existing caller is unchanged, which is the point: `version` was `""` in every note it had ever written, because the unreleased card drafts from the done-but-unshipped set and does not know the number.

**What I should have done** is search `note_writes` for the capability before writing it. The module is 1800 lines and I had read three of its functions.

### One test's slice was over-broad, and my buttons found it

`test_the_jump_suppresses_the_arriving_landing_rather_than_racing_it` asserts every `navigateTo('~…')` inside `loadWsNav` is landing-suppressed. Its slice runs to the next top-level `async function`, so it takes in the plain `function`s after it — including `renderNavGroup`. The gate's controls are the first **click handlers** to land in that window, and a click cannot lose a load-time race. The test now excludes click handlers, with the reason written down.

### Ten mutations, all defeated

Including the two that matter most: `fail` ticking the row, and addressing by global index instead of section-and-ordinal.
