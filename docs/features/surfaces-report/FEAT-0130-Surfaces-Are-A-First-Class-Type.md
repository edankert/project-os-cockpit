---
type: "[[feature]]"
id: FEAT-0130
aliases: ["FEAT-0130"]
title: "A surface is a note, not a string retyped on every check — so an untested surface is visible rather than absent"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
requirements: ["[[REQ-0049-A-Surface-Exists-Whether-Or-Not-A-Test-Names-It]]"]
tasks: ["[[TASK-0514-The-Surface-Note-Type]]", "[[TASK-0515-Consolidate-Your-Trainer-Surfaces]]", "[[TASK-0516-Surfaces-On-The-Design-View]]"]
related: ["[[DES-0012-Tests-In-Two-Flows]]", "[[ISS-0250-A-Surface-Rename-Silently-Orphans-Its-Checks]]"]
tags: [feature]
---

# A surface is a thing, not a string

Edwin: *"The surface ticket types are great but where should they be visible, probably in the design?"*

Today `area:` is **free text retyped on every check**. `your-trainer` has 76 distinct values for 579 checks, including `"Moved from Tier 1 / Tier 2 — Fully Automated"`, which is a migration bucket wearing a surface's clothes. Nothing can answer *which surfaces have no coverage*, because a surface only exists if a check happens to mention it.

A `SUR-*` note makes the surface exist first. Then:

- **An untested surface is visible** — a row with no checks, rather than nothing at all.
- **The suite groups by a controlled vocabulary** rather than by whatever was typed.
- **A release can report per surface**, which is what [[DES-0012]] D1 and the progress bars need.

## Where it is visible

**The design view**, per Edwin. That view already holds what bounds the project — ADRs, risks, the glossary — and a surface is exactly that: a standing statement of what the application *is made of*, independent of any one feature. Tests then reference it; the design view owns it.

## Consolidation is part of the feature, not after it

76 is not a vocabulary, it is a list. Edwin's own examples: `Per-Rider Data Export` → `Data Import/Export`; `Workout Loop/Repeat` → a generic `Workouts`; `HR Zone Lock` → `HR Zones`. The target is a set a person can hold in their head — roughly 12–15 for `your-trainer` — and the mapping is a judgement per area, recorded.

## Acceptance

- [x] A `SUR-*` note type exists with a template and schema entry. — [[TASK-0514]]; `docs/__templates__/surface.md` byte-identical to upstream's, `SUR` in `ID_PREFIXES`, `surfaces -> {"surface"}` in `COLLECTION_TYPE`, statuses `active`/`retired`/`superseded`. `tests/test_surface_type.py::test_the_type_is_wired_into_the_validator`, `::test_a_surface_note_validates`, `::test_the_template_is_template_owned_and_identical_upstream`. Mutant: adding `done` to the surface status set fails two tests.
- [x] `your-trainer`'s 76 areas map onto a consolidated set, each mapping recorded. — [[TASK-0515]]; **76 -> 15** over **579** checks, and the mapping is recorded in that note's *"The mapping as applied, recorded"* section: 75 one-to-one rows plus the parking bay's 66 notes named individually. *(The mapping was **not** recorded until 2026-08-20 — the table the task carried was a superseded proposal whose surface names do not exist in `your-trainer`, and the only copy of what was applied was an uncommitted diff. That is the last thing this criterion was waiting on.)*
- [x] Surfaces appear on the design view. — [[TASK-0516]]; `tests/test_surface_type.py::test_surfaces_have_a_home_on_the_design_view` asserts the `surfaces` group and its members. Mutant: dropping the group fails four tests.
- [x] A surface with no checks is visible as such. — `Surfaces · 1 with no checks` on the group head; `tests/test_surface_type.py::test_a_surface_with_no_checks_is_visible_as_such`, with `::test_a_covered_surface_drops_off_the_head_count` proving the count moves and `::test_the_count_is_not_sent_on_a_field_no_renderer_draws` proving it did not go somewhere undrawn.

## Closed 2026-08-20 — and what it leaves

The type exists, the vocabulary is controlled, `your-trainer`'s 76 hand-typed strings are 15 surfaces, and an uncovered surface has a row. All three tasks are `done` and independently reviewed.

**Two things are deliberately not claimed.**

**A check still does not *link* to a surface.** `area:` is a string that now happens to equal a surface's title, and `surface_coverage` joins on that string. Renaming a surface therefore orphans its checks in silence, and an orphaned surface renders identically to a genuinely uncovered one — the same row this feature exists to produce. Filed as [[ISS-0250]] with the measurement that makes a fix affordable: the join is currently **perfect**, 15 titles against 15 area values with no orphan on either side.

**The original `area:` is not on the note.** [[REQ-0049]] criterion 4 asks for it and the migration wrote it nowhere; it is reconciled `[~]` there against the recorded mapping, with the cost stated. The record now exists to write the field from if Edwin wants it.
