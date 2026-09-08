---
type: "[[requirement]]"
id: REQ-0061
aliases: ["REQ-0061"]
title: "A release's version, platform and settled checks are written through one workflow, and every settle is an event carrying a reason and an author"
status: implemented
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-09-08
updated: "2026-09-08"
reviewed_by: model:claude-opus-5
review_date: 2026-09-08
review_verdict: changes-requested
review_response: "All six findings acted on; the verdict stands as written. (1) FIVE FAILING TESTS, all mine and all now green -- test_remote_peer_refusal's two pinned counts moved 28->32 and 30->34 for the four new loopback-guarded handlers, both with the deliberate-edit line the file asks for; test_acceptance_marks reads the dialog loop as `of offered`, which IS MARK_CHOICES wherever no `only:` is passed; TST-0082 no longer names a renamed test by a truncated prefix; and test_tests_view's `marks <= ledger.MARKS` was stronger than the sentence above it and true only because every check in this corpus had been walked -- TST-0083 is the first unwalked one, `todo` is the absence of an event rather than a mark, and the guard now says so. The reviewer also caught ME: I reported the suite green three times from BACKGROUND runs whose output files were empty, reading the wrapper's exit code as pytest's. The final numbers are from a foreground run: 2233 passed, 6 skipped, plus the node suite. (2) The platform-order guard did not guard -- `open_releases` sorts version-descending, so `the first open release` is the HIGHEST-versioned draft and the fixture settled that one. Swapped, plus an assertion that the fixture still puts the OTHER release first, and the mutant re-run fails as it must. (3) An abandoned release vanished from the publication navigator, which defeats the whole argument for keeping the note; it now gets its own row below the shipped ones, closed by default. (4) FOUR NUMBERS CORRECTED IN SEVEN PLACES: `eleven weeks` -> 23 days (REL-0013 created 2026-08-16), in this repo's validator, the bundled copy, statuses.py AND upstream; `since June` -> 2026-08-16; `67 rows / 17 areas / three of 67` -> the re-measured 52 rows / 15 areas / 9 covering a carried feature, gate 65 blocking; `29 new tests` -> 33. (5) Notes naming what the code lacks: PLAN.md and TASK-0600 said `platform_candidates` where the key is `platforms`; TASK-0601 still listed askForMark as forbidden, which ADR-0041 reversed; and REQ-0061 criterion 1 cited criterion 2's test -- so it now has its own, test_creating_a_release_writes_its_platform_and_scopes_the_gate, which asserts the CONTROL posts the platform, because the defect was in the caller and a write-path test passed throughout. (6) SURFACE-ORPHAN on TST-0083's `area: Publication` is one more row in a pre-existing population: this repo has zero SUR-* notes, so all ~20 areas warn. Not fixed, deliberately -- inventing the corpus's only surface note is a different piece of work. Surviving mutants left standing and stated: `_clean_platform`'s name refusal, `update_release` never stamping `preparing:`, `coverage_gaps`'s requirement dedupe, `settle_rows` dropping the quiet/resting filter, `abandon_release` with a narrower `closed` set. `wrap.prepend` above the gate and a non-release-named surface calling walkOneCheck are pre-existing; ISS-0254 owns the second."
review_response_date: 2026-09-08
priority: high
scope: "release preparation"
source: ["Edwin, 2026-09-08: 'suggest how the creation of releases can be made a little easier in the tool. I think it should probably be a new workflow: Create Release (Update and delete release should also be possible) — set the version — select: android or iOS — uncheck the required acceptance-tests for the release and add new checks if required'"]
implements: "[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]"
acceptance:
  - "[ ] Creating a release from the workflow writes `platform:` into the note, and the gate on the next screen is scoped to that platform."
  - "[ ] Changing the platform of an open release changes the owed count and touches no check note."
  - "[ ] Abandoning a draft leaves the note, its reason and its `superseded_by:` in place, and the version it held is not silently reusable."
  - "[ ] Settling a check from the release page writes a ledger event carrying a reason and an author, and `excused` clears only this release."
  - "[ ] The coverage sweep names the features a release carries that no check covers, computed mechanically."
verifies: []
covers: []
related: ["[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]", "[[ISS-0288-The-Release-Gate-Ignores-The-Release-Platform]]", "[[ISS-0290-A-Walker-Cannot-Mark-A-Check-Because-Nothing-Names-The-Platform]]"]
tags: [requirement, release, publication]
---

# A release is written through one workflow

## Approval

**Approved 2026-09-08** by Edwin's instruction to implement [[FEAT-0145]] in full, on the request he wrote the same morning. The five criteria below are his four steps plus the sweep, restated as things that can be measured rather than described.

## Statement

Preparing a release **shall** be one sequence of writes through the cockpit — name the version, say which platform, choose the contents, settle what is owed — and every act that changes what a release owes **shall** be recorded as an event carrying who decided it and why.

A release's version and platform **shall** be changeable while it is open and **shall not** be changeable after it has shipped. A prepared release that will not ship **shall** be abandoned with a reason, never deleted.

## Why this is a requirement and not four tasks

On 2026-09-08 Edwin prepared `your-trainer` v2.2.0 and every step was a hand-edit or a diagnosis: the release note was typed by hand, the platform was absent so the gate reported 635 checks owed on a repo holding 67 ([[ISS-0288-The-Release-Gate-Ignores-The-Release-Platform]]), and a walker could not record a verdict at all because nothing named a platform to write it against ([[ISS-0290-A-Walker-Cannot-Mark-A-Check-Because-Nothing-Names-The-Platform]]).

Each of those has since been fixed on its own. What has not been fixed is the reason all three were reachable at once: the pieces exist — `release-prepare`, `release-contents`, `release-verified`, `release-mark-released`, the ledger, the owed list — and **no order runs through them**. The requirement is about the sequence, which is why it is stated once here rather than restated in eight tasks.

## Acceptance Criteria

One checkbox per entry in the frontmatter `acceptance:` list. Tick only with an evidence pointer, at feature close-out.

- [x] **Creating a release from the workflow writes `platform:`, and the gate on the next screen is scoped to it.** — evidence: `note_writes.create_release` writes the field and `_ensure_release_ledger` makes its working ledger; the renderer's *Name the version* control sends a chosen platform rather than omitting it. *It used to send `{version, actor}` and nothing else, so every release created in the tool arrived platform-less even after `create_release` learned to take one — the write path was fixed and its only caller was not. `buildPlatformPicker` is the missing half. Verified by `tests/test_release_workflow.py::test_creating_a_release_writes_its_platform_and_scopes_the_gate`, which creates a release on a two-ledger repo, reads `platform:` back off the note, asserts the gate on the next screen is scoped to it, and asserts the control posts `platform: picker.value` — because the defect was in the caller, and a test of the write path alone would have passed throughout.*
- [x] **Changing the platform of an open release changes the owed count and touches no check note.** — evidence: `note_writes.update_release` plus a guard that the owed set differs before and after while every `CHK`/`TST` note's mtime is unchanged. The direction that matters is the second half: [[REQ-0055]] says a verdict write never touches a note, and a *platform* write must not either.
- [x] **Abandoning a draft leaves the note, its reason and its `superseded_by:`, and the version it held is not silently reusable.** — evidence: `note_writes.abandon_release` sets `status: abandoned` and refuses without a reason; `create_release`'s version refusal still reads the abandoned note's version. `your-trainer` REL-0013 is the precedent this is modelled on — prepared as v2.1.7, never shipped, still on the record with `superseded_by: [[REL-0016-v2.1.8]]`, which is why the version number was skipped.
- [x] **Settling a check from the release page writes a ledger event carrying a reason and an author, and `excused` clears only this release.** — evidence: `POST /api/notes/release-settle` appends through `ledger.append`, refuses `pass`/`partial`/`fail` by name per [[ADR-0041]], and refuses any of the three settle marks with no reason (`ledger.NEEDS_REASON`). The scope half is already structural: `ledger.PERSISTS` excludes `excused`, so `seal` expires it.
- [x] **The coverage sweep names the features a release carries that no check covers, computed mechanically.** — evidence: `publication.coverage_gaps` reads the suite's own `refs` reverse index and `criteria.payload`; no model runs, so the number is the same on every machine. A feature carrying `acceptance_exception:` is not a gap.

## Traceability

- Implements: [[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]
- Decided by: [[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]] for criterion 4; [[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]] still governs criterion 5's derivation.
- Verified by: `tests/test_release_held_back.py` (the ADR-0035 boundary, rewritten by [[TASK-0601]]), plus the guards named on each task.

## What this requirement does not say

- **Nothing about cutting a build.** `release.sh` in a downstream repo owns `versionCode`/`versionName` and the artifact.
- **Nothing about a second store for required checks.** The derivation plus the ledger is the store ([[ADR-0032]]).
- **Nothing about deleting a shipped release.** A released note is the record.

## Independent review — 2026-09-08, `model:claude-opus-5`, `changes-requested`

Reviewed together with [[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]; the findings are written once, in that note's `## Independent review — 2026-09-08` section. Two of them are about this note: criterion 1's evidence line names criterion 2's test, and criterion 4 is met at the endpoint but its guard for the *platform* half passes with the defect reinstated. The five criteria are otherwise supported by code and tests that were run.
