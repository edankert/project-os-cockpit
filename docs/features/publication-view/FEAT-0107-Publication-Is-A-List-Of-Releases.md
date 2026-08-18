---
type: "[[feature]]"
id: FEAT-0107
aliases: ["FEAT-0107"]
title: "Publication is a list of releases — one navigator of releases, one page each, and the record the repo already keeps finally read"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin 2026-08-16: 'I don't understand the functionality and we have gone around numerous times now'", "Edwin 2026-08-16: 'what do we need to do for a release, what tests need to pass, what documentation needs to be updated etc … all that should be available on the publication view and previous releases should be available with the functionality that was in the release, the tests and the documentation which was used as part of the publication'", "Edwin 2026-08-16: 'acceptance-tests is one document which moves between releases and the release notes capture the acceptance tests executed and reasons why not'", "Independent review of PHASE-034, 2026-08-16 — changes-requested on the phase and five of six features"]
goal: "Replace nine concepts with two — a list of releases and a page per release — and read the record this repo has been keeping by hand for twelve releases: the suite snapshot each one shipped against, the tests it verified, what it shipped with unfixed, and its platform artifacts."
requirements: []
tasks: ["[[TASK-0442-The-Cut]]", "[[TASK-0443-Releases-Are-The-Navigator]]", "[[TASK-0444-A-Shipped-Release-Shows-Its-Own-Record]]", "[[TASK-0445-Capture-At-Ship]]"]
design: ""
release: ""
depends: []
related: ["[[ADR-0028-Work-Has-Three-Phases]]", "[[FEAT-0102-Publication-Becomes-A-View]]", "[[FEAT-0103-The-Gate-Is-Walkable]]", "[[FEAT-0106-The-Release-Page]]", "[[ISS-0177-An-Exception-Mark-Drops-A-Check-With-No-Justification]]", "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"]

---

# Publication is a list of releases

## Why this supersedes most of what came before

Five rounds, six features, and Edwin asked the same question at the start and at the end: *see and go through the acceptance tests for a release.* An independent review returned `changes-requested` on the phase and five of six features, and found the reason:

> **Every one of Edwin's three complaints is already written down in this repo as an unticked acceptance criterion on a feature that was closed anyway.**

[[FEAT-0104]] says the stepper is removed — unticked. [[FEAT-0106]] says nothing pops a dialog — unticked. [[FEAT-0105]] is `done` at **0 of 8** criteria; [[FEAT-0106]] at **0 of 9**. Three times a replacement was added and the thing it replaced was left running.

## What the record already holds, and nothing reads

This is the part that changes the design from *build* to *read*. `your-trainer` has kept all of it by hand:

| what Edwin described | where it already is |
| --- | --- |
| "the acceptance-tests document moves between releases" | `ACCEPTANCE_TESTS.md` living, plus `ACCEPTANCE_TESTS_v2.1.0.md` and `ACCEPTANCE_CHECKLIST_v2.1.1.md` as shipped snapshots |
| "the release notes capture the acceptance tests executed" | `tests_verified:` — REL-0012 names its snapshot and two `TST-*` notes |
| "and reasons why not" | `## Known issues (shipping with)`, in 6 of 12 notes |
| "external release notes, Play or other platform texts" | 7 files, `REL-####-vX.Y.Z-<kind>.xml`, beside the notes |

`tests_verified` is read by nothing. The artifacts are read by nothing. `changes:` on the release template is empty in every repo.

## The shape

**Navigator: releases.** Newest first, each with its content nested — the precedent Features already sets by nesting requirements, plan and tasks under a feature. No rungs-as-groups, no gate group, no `Needs you`.

**Page, next release:** what has accumulated, and the **living** suite with its outstanding count, opening `ACCEPTANCE_TESTS.md` where the 542 checkboxes already work.

**Page, shipped release:** the record *as it stood* — the snapshot `tests_verified` names, the note's own known-issues section, and the artifacts beside it. Not today's gate recomputed, which is what it does now.

Commit, push and deploy go back to `~history` and the overview, where they already worked. The ladder metaphor is what turned a list of releases into seven groups.

## Acceptance criteria

- [x] Publication's navigator lists releases and nothing else — 12 groups on your-trainer, every key `release-*` or `stale-*`
- [x] Selecting the mode opens a page in the centre pane — Publication joins `VIEW_LANDING_RELS` and `MODES_WITH_VIRTUAL_LANDING`, which it never did — joined `MODES_WITH_VIRTUAL_LANDING` and gained a `loadWsNav` branch mirroring Intent's — it was the only badge-bearing view without one
- [x] `~walk`, `renderAcceptanceWalkPage`, `buildAcceptanceWalker` and the walk-check pass/fail path are **deleted**, with their tests — deleted by TASK-0442
- [x] `prepare_release`, `promptPrepareRelease` and `~prepare-release` are **deleted**; the version field on the page is the only way to start a release — all three gone; the version field on the page is the only way in
- [x] The `release-gate` navigator group is **deleted** — the suite is reachable from the page and from Tests, where it already lived — gone — the suite is reachable from the page and from Tests
- [x] `_needs_you_group` no longer runs on publication — `publication` is in `_VIEWS_THAT_ALREADY_GATHER`
- [x] A shipped release lists what it shipped — `contents.ids` is rendered, not dropped ([[FEAT-0106]] P3) — `contents.ids` renders; REL-0012 shows its frozen feature
- [x] A shipped release shows the tests **it** verified, from `tests_verified:`, and never today's gate — `tests_verified` read — REL-0012 shows its snapshot and two TST notes; `gate` is `{}` for a shipped release
- [x] A shipped release shows its platform artifacts, found by the filename convention — `play store listing` on REL-0012, by the convention ADR-0028 now blesses
- [x] `~release/<id>` is reachable by clicking a release, not only by typing — every navigator group's `url` is `~release/<id>`
- [x] A release with no `tests_verified` says *not recorded* rather than showing nothing — and offers `Record what it verified` — five of twelve are empty
- [x] At ship, the cockpit asks for the suite snapshot and writes `tests_verified` — it does not write files unasked — `record_verification` writes only the answer given; `test_recording_writes_only_what_it_was_given` asserts no file is created
- [x] Every criterion here is ticked with evidence before this feature reaches `done`, which is the thing that did not happen five times — this list

## Notes

**Not in scope: documentation state.** Edwin named it — *"what documentation needs to be updated"* — and it maps to `changes:` on the release template, empty in every repo. Deriving it from CHG notes since the last release is a real design question, not a lookup, and it is deferred rather than guessed at.

**The artifact convention needs blessing, not inferring.** `REL-####-vX.Y.Z-<kind>.xml` holds across seven files and exists nowhere but in Edwin's habit. Reading it means agreeing it — an amendment to [[ADR-0028]], not a regex somebody wrote.


## Delivered 2026-08-16

**Publication is a list of releases.** Twelve groups on `your-trainer`, every one a release, each opening its own page. The ladder is gone; commit, push and deploy are back on `~history` and the overview where they already worked.

**The record was already there.** REL-0012 has been carrying its snapshot (`ACCEPTANCE_CHECKLIST_v2.1.1`), two `TST-*` notes, a known-issues table and a play-store listing since July. Reading it took no new mechanism — `tests_verified:` was in the template, the artifacts follow a convention seven files deep, and the known-issues heading is in half the notes. Three sections on the page, no new fields.

### Two bugs found while wiring it

1. **`_set_field` quotes everything**, so `tests_verified: ["[[X]]"]` was written as a *string containing a list* and parsed back as one opaque value — a release reported nothing it had verified. It now takes `quote=False` for list-valued fields.
2. **A shipped release was showing today's gate**, recomputed. It shows its own snapshot instead, and `gate` is empty for anything `released` (review finding P5).

### What this feature deliberately did not do

**Documentation state.** Edwin named it and it maps to `changes:`, empty in every repo in the fleet. Deriving it from `CHG-*` notes since the last release is a design question, and inventing a fourth mechanism for something the record may already answer is what this phase spent five rounds doing.
