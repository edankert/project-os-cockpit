---
type: "[[task]]"
id: TASK-0514
aliases: ["TASK-0514"]
title: "A `SUR-*` note type, with template, schema entry and validator support"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
parent: "[[FEAT-0130-Surfaces-Are-A-First-Class-Type]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# A `SUR-*` note type, with template, schema entry and validator support

Template-owned, so it lands upstream in `project-os` FIRST and syncs down — the lesson of the `kind:` removal, which took three passes because six repos held the edit on disk and in no commit.

## Done 2026-08-20 — upstream first

`docs/__templates__/surface.md` and the `TAXONOMY.md` entries landed in `~/Dev/repos/project-os` and were copied down byte-identical; a test fails if they drift. That order is the task's own instruction and the lesson of the `kind:` removal, *"which took three passes because six repos held the edit on disk and in no commit."*

Validator support in all three copies — upstream's and both of the cockpit's:

| | |
|---|---|
| `ID_PREFIXES` | `SUR` added, so a `SUR-*` id resolves |
| `COLLECTION_TYPE` | `surfaces -> {"surface"}` |
| `ALLOWED_STATUS` | `active`, `retired`, `superseded` |
| `counters` | `SUR: 1` |

### A surface is not *done*

It exists until the product stops having it. `retired` says the place is gone; `superseded` says another surface took it over and names which. **`done` is the value somebody will reach for and it is the one that is wrong**, so it is the mutant: adding it to the allowed set fails two tests.

No new vocabulary — [[project-os-dev#ADR-0008]] collapsed 64 status values to 53, and a new type is not a reason to reopen that.

### The template refuses to list its own coverage

The checks covering a surface are **derived from `area:`**, and the `## Coverage` section says so instead of leaving a tempting empty list. A second, hand-maintained copy of a relationship is what [[project-os-dev#ADR-0032]] spent a decision removing — and this type exists precisely so the name is written **once**.

Measured, which is the case for the type at all: **94 distinct `area:` strings across `your-trainer`'s 581 checks**, every one typed by hand on every check that touches it.

### [[SUR-0001]] exists, and it is this phase's own surface

The tests view — the one four of [[PHASE-037]]'s issues are about. It states its **boundaries**, which is the field that stops a surface absorbing its neighbours: not the release page ([[ADR-0035]] exists because those two were confused), and not the obligations badge ([[ADR-0027]]'s question, with its own registry).

A type with no instance is a schema nobody has tested, so this is one rather than a fixture.

### What this does NOT do

**Nothing reads `area:` as a `SUR-*` link yet.** A check still carries the string, and the type is defined beside it. Making the two meet is [[TASK-0515]] (mapping `your-trainer`'s 94 areas onto a set of surfaces) and [[TASK-0516]] (rendering them). This task is the schema, and claiming more would be the overclaiming this phase exists to remove.

## The template is untracked upstream — added 2026-08-20

*"`docs/__templates__/surface.md` and the `TAXONOMY.md` entries **landed** in `~/Dev/repos/project-os`"* is how this note put it, with no caveat. Independent review checked: `surface.md` is **untracked** there and `TAXONOMY.md` is **modified and uncommitted**. Nothing has landed in the sense a downstream repo can receive — `sync-project-os.sh` copies from a checkout, and an untracked file in the source is not part of any commit a fleet repo could sync.

The test that guards this compares the two files **byte for byte on disk**, so it passes exactly as well against an untracked upstream file as against a committed one. It is the right test for drift and it says nothing about durability.

**And `your-trainer`'s fifteen `SUR-*` notes are in no commit either** — `git log --all -- 'docs/surfaces/*'` there returns nothing. The type is real and committed here; every instance of it, everywhere, is a working tree.

## Independent review — third pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`, reviewing `6cc7f72..HEAD`. Verdict: **approved**. Every claim below was re-measured or re-executed.

The `SUR-*` type is wired into the validator and the vocabulary is guarded: adding `done` to the surface status set fails `test_the_type_is_wired_into_the_validator` and `test_an_illegal_surface_status_is_refused`. The reasoning for `active`/`retired`/`superseded` — a surface is not *done*, it exists until the product stops having it — is sound, and adding no new vocabulary respects `ADR-0008`.

The join in `surface_coverage` is on the exact title string, and in `your-trainer` it is currently perfect: 15 `SUR-*` titles, 15 `area:` values, no orphan on either side. The docstring is honest that a surface matching no `area:` reads as zero because it genuinely covers nothing.

See `TASK-0515` for the two checks that carry `area: ""` and therefore sit on no surface at all — that is a gap in the migration's reach, not in this type.
