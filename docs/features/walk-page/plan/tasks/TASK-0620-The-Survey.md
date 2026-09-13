---
type: "[[task]]"
id: TASK-0620
aliases: ["TASK-0620"]
title: "The survey: the surfaces this release changed, derived from the ledger's invalidation events, rendered before any scripted check"
status: done
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-13
updated: 2026-09-13
source: ["[[FEAT-0149-The-Walk-Page]]", "Edwin, 2026-09-13: 'one thing I notice the tests do not suggest me doing is to look at the changed screens at all'"]
parent: "[[FEAT-0149-The-Walk-Page]]"
effort: M
due: ""
depends: ["[[TASK-0618-The-Walk-Payload]]", "[[TASK-0619-The-Walk-Page]]"]
blocks: []
related: ["[[ADR-0036-The-Sweep-Is-Withdrawn]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[DES-0012-Tests-In-Two-Flows]]"]
tests: ["[[TST-0088-The-Walk-Page-Hands-Over-The-Owed-Checks]]"]
tags: [task, acceptance, publication]
---

# The survey

## Why

The checks say what must be true. None of them says "open the screens this release touched and look". Edwin does that first, by habit, and the system never asks for it. The information to ask for it is already recorded: an invalidation is an event `{check, invalidated_by, date}` in the ledger ([[ADR-0037-A-Verdict-Is-An-Event]]), every check names a surface in `area:`, and [[DES-0012-Tests-In-Two-Flows]] made surface the suite's axis. Joining them gives the surfaces whose checks a change reopened and the change that did it. That is the survey, and it costs no new question at close-out, which is what [[ADR-0036-The-Sweep-Is-Withdrawn]] asked of any replacement: *"keyed on the surface a change touched, not on the feature."*

## Definition of Done

- [x] `walk_payload(...)["survey"]` is a list of `{"surface", "surface_note", "checks": [...], "changes": [{"id", "title", "reopened": str | None}], "gallery": str | None}` grouped by `area:`, in WALK.md's sitting order where the area is named and id order after.
- [x] A surface appears if and only if at least one owed check under it has an invalidation as its latest ledger event on this platform. Tested with a check whose invalidation was overtaken by a later `pass` (absent) and one whose latest event is the invalidation (present).
- [x] `changes` holds every distinct `invalidated_by` id across those events, resolved through the index to its title; an id the index cannot resolve is kept with `title: None`, never dropped.
- [x] `reopened` is the text under a `## Acceptance checks reopened` heading in the invalidating note when one exists, else `None`. Nothing else in the note is read.
- [x] `surface_note` is the `SUR-*` note whose title matches the area when the repo has one, else `None`.
- [x] `gallery` at the survey level is the `gallery:` field from WALK.md's frontmatter, verbatim, or `None`.
- [x] The page renders the survey as the first section, opening with the gallery command when present and the sentence "Before any check, open these screens and look", then one block per surface: the surface name (linked to its note where present), the owed checks under it as links, the changes with titles, and the reopened text quoted.
- [x] Against `your-trainer`'s open Android ledger, the survey's surfaces and change ids equal what `ledger.events_by_check` yields by hand; a test computes both.

## Steps

- [x] Read `ledger.events_by_check` (`src/project_os_cockpit/ledger.py`, from the `def events_by_check(` line): newest first per check, invalidations included. The survey's predicate is "first event in the list is an invalidation".
- [x] Implement the join in the bundled walk module so the template's markdown sheet and the cockpit's page agree; the cockpit adds only the index lookup for titles and `SUR-*` notes.
- [x] Read the reopened section with the same frontmatter-and-headings reader the row's `setup`/`steps`/`expect` use in [[TASK-0618-The-Walk-Payload]].
- [x] Add `buildSurveySection(survey)` beside `buildWalkPage` in `desktop/src/renderer/renderer.ts` and mount it above the sittings.
- [x] Tests in `tests/test_walk_survey.py`: the overtaken-invalidation case, the unresolved-id case, the reopened-section case, and the live-corpus comparison guarded by `../your-trainer/docs`.

## Notes

**Why the latest event decides.** A check invalidated by a task and then walked to `pass` is not owed and its surface has been looked at. A check invalidated after its last `pass` is owed because of that change, and the change is what the walker should look at first. `ledger.resolve` already implements last-event-wins for the gate; the survey uses the same reading so the two cannot disagree.

**What the survey does not do.** It does not scan the diff, does not read `PARITY_MATRIX.md`, and does not ask an agent at close-out which screens changed. The `## Acceptance checks reopened` section is quoted when present because thirty-three `your-trainer` notes already carry it by convention; whether the template makes it a section is project-os-dev FEAT-0029's decision, and the survey works without it.

## Done 2026-09-13

The survey is the first section of the walk and is derived in the bundled module: for every owed check whose latest ledger event is an invalidation, the surface it belongs to, the checks under it, and every `invalidated_by` id with its title and its quoted `## Acceptance checks reopened` section.

On `your-trainer`'s open Android release that is six surfaces and eleven tasks, five of the six resolving a `SUR-*` note. `tests/test_walk_survey.py` computes the same set from `ledger.events_by_check` and compares, so the corpus can move without the test becoming a claim about a number.

### What the cases turned out to be

- An invalidation a later `pass` overtook is **not** in the survey: the check is not owed and its surface has been looked at.
- An invalidation a later `fail` overtook is **not** in it either, and the check is still owed. Somebody has opened that screen; it is no longer news about a changed surface.
- An id the index cannot resolve is kept with `title: null` and named on the page as `(not in this repo)`. A cause the walker cannot trace is still the reason their check reopened.
- A change note resolves through the walk module's own second index, because `CHG` is not one of the validator's id prefixes and the note index holds no change note at all.
- A check with no `area:` is surveyed under `(no area on the check)` rather than dropped. A reopened check invisible on the survey is the one failure the survey exists to prevent.

**No new close-out obligation**, which is what [[ADR-0036-The-Sweep-Is-Withdrawn]] required of any replacement: every fact the survey prints was already in the ledger.
