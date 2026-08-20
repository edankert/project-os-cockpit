---
type: "[[requirement]]"
id: REQ-0049
aliases: ["REQ-0049"]
title: "A surface exists whether or not a test names it, and the suite groups by a controlled vocabulary"
status: implemented
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
priority: medium
scope: "surfaces"
implements: "[[FEAT-0130-Surfaces-Are-A-First-Class-Type]]"
acceptance:
  - "[x] A surface is a note. It exists, and is listed, with zero tests naming it. — SUR-0001 is this repo's only surface and nothing covers it; tests/test_surface_type.py::test_surfaces_have_a_home_on_the_design_view asserts it is listed, ::test_a_surface_with_no_checks_is_visible_as_such asserts surface_coverage(index) == {SUR-0001: 0}"
  - "[x] The consolidated set for your-trainer is small enough to hold in the head — a target of 12-15, not 76 — and every original area maps onto one, with the mapping recorded rather than inferred. — 76 -> 15 over 579 checks; the mapping is recorded in TASK-0515 'The mapping as applied, recorded', 75 one-to-one rows plus the parking bay's 66 notes named individually"
  - "[x] Surfaces are visible on the design view, beside the other things that bound the project. — tests/test_surface_type.py::test_surfaces_have_a_home_on_the_design_view; dropping the group fails it and three others (mutant executed, TASK-0516 fourth-pass review)"
  - "[~] No check loses its history in the consolidation: the original `area:` string is preserved on the note. — RECONCILED: the property holds, the instrument does not. The original is recoverable for every one of the 579 checks from the mapping recorded on TASK-0515; it is NOT on the note, and the migration wrote it nowhere. See 'Criterion 4, reconciled' below."
covers: []
related: ["[[DES-0012-Tests-In-Two-Flows]]", "[[TASK-0515-Consolidate-Your-Trainer-Surfaces]]", "[[TASK-0516-Surfaces-On-The-Design-View]]"]
tags: [requirement]
---

# A surface exists on its own

Criterion 4 is the constraint on criterion 2. Consolidating 76 strings into ~13 is a **lossy rename** unless the original is kept — and the original is the only evidence of what a check was originally filed under. `your-trainer`'s suite is 579 notes; a mapping applied without preserving the source is not reversible by reading.

Criterion 1 is the whole point of the type. A string cannot be absent; a note can.

## Acceptance criteria

- [x] A surface exists with zero tests. — `SUR-0001`, listed on the design view with `surface_coverage(index) == {"SUR-0001": 0}`; `tests/test_surface_type.py::test_surfaces_have_a_home_on_the_design_view` and `::test_a_surface_with_no_checks_is_visible_as_such`.
- [x] A consolidated set of 12-15, mapping recorded. — **15** surfaces from **76** original `area:` values over **579** checks; the mapping is recorded in [[TASK-0515]] (*"The mapping as applied, recorded"*), 75 one-to-one rows plus the parking bay's 66 notes named individually.
- [x] Visible on the design view. — [[TASK-0516]]; `tests/test_surface_type.py::test_surfaces_have_a_home_on_the_design_view`, and dropping the group fails four tests (mutant executed at that task's fourth-pass review).
- [~] The original `area:` preserved. — **Reconciled, not met as written.** See below.

## Criterion 4, reconciled — the property holds and the instrument does not

**What the criterion asks for was not built.** The migration overwrote `area:` in place on 579 notes. It wrote the original into no field and into no body line, and [[TASK-0515]] said it had ("*the original string is preserved on each note*") in a sentence written **before** the work and never re-read after it. That sentence is now corrected on the task.

**What was built instead is a single recorded mapping**, added to [[TASK-0515]] on 2026-08-20: 75 of the 76 original values map one-to-one onto a surface, and the 76th — `Moved from Tier 1 / Tier 2 — Fully Automated`, the parking bay — fans out across 13 surfaces and so is recorded **note by note**, all 66. Every check's original string is therefore recoverable by reading, which is the property the body of this requirement argues for: *"a mapping applied without preserving the source is not reversible by reading."*

**Why one table rather than 579 fields, stated so it can be argued with.** A `prior_area:` on every note is a second, permanent encoding of a fact that is true once — the shape [[ADR-0032]] spent a decision removing, and the shape [[ADR-0037]] removed seven fields for. It would also need a schema entry in three validators and would be read by nothing. The single table is one copy, in the note that made the decision, and it does the reversal the criterion protects.

**What it costs, honestly.** The table lives in `project-os-cockpit` and the notes live in `your-trainer`, so a reader of a single check cannot see where it came from without crossing repos. That is a real loss against the criterion as written, and it is the reason this is `[~]` rather than `[x]`. **If Edwin wants the field, the mapping now exists to write it from** — which it did not before, and that was the urgent part: the originals survived only in an uncommitted working-tree diff.

## Independent review — fresh-context pass, 2026-08-20 (`b4b9c50` / `4521a7a`)

Separate session, `model:claude-opus-5`, starting from the notes and the diff with no access to the author's reasoning. Same model family as the author, recorded in `reviewed_by`; the independence claimed here is **context**, not weights ([[project-os-dev#ADR-0013]]).

**Verdict: approved.** The citations were checked by mutation rather than by reading, and the `[~]` is a real reconciliation.

- **Criterion 3's** claim *"dropping the group fails it and three others"* is exact: removing the `surfaces` entry from the design view's constraints loop fails **four** tests — `::test_surfaces_have_a_home_on_the_design_view`, `::test_a_surface_with_no_checks_is_visible_as_such`, `::test_the_count_is_not_sent_on_a_field_no_renderer_draws`, `::test_a_covered_surface_drops_off_the_head_count`.
- **Criterion 1's** cited tests both fail when `surface_coverage` is stubbed to `{}`, so neither is citing a property it does not assert.
- **Criterion 2's** figures (76 -> 15 over 579, the mapping recorded on [[TASK-0515]]) were re-derived independently and match in every cell.
- **Criterion 4 is a legitimate `[~]`, not closure by fiat.** It says *"not met as written"* in its own words, separates the property from the instrument, argues the alternative against [[ADR-0032]] and [[ADR-0037]], and states the cost — a reader of a single check must cross repos. It does not tick, and it names what would have to be built. That is what a reconciliation is supposed to look like.

One caveat inherited rather than introduced: the mapping this criterion now rests on is recorded against `49cf2ce9`, which [[TASK-0515]] mislabels as `HEAD`. The table is correct; the pointer to how to reproduce it is not.
