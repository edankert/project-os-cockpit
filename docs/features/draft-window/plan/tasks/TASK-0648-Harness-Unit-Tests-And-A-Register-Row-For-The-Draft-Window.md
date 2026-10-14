---
type: "[[task]]"
id: TASK-0648
aliases: ["TASK-0648"]
title: "Harness, unit tests and a register row for the draft window"
status: doing
phase: "[[PHASE-045-The-Cockpit-In-Layers]]"
owner: user:edwin
created: 2026-10-13
updated: 2026-10-13
source: ["[[REFERENCE-CAPABILITY-REGISTER]], rule 1: a change note that adds capability updates the register in the same commit"]
parent: "[[FEAT-0160-A-Draft-Window-Shows-What-Needs-You]]"
effort: "S"
due: ""
depends:
  - "[[TASK-0646-The-Draft-Window-Opens-From-The-Menu-And-Gathers-Every-Projects-Data]]"
blocks: []
related:
  - "[[TASK-0647-The-Draft-Windows-Page-Shows-Three-Areas-And-Opens-The-Present-Window]]"
  - "[[TST-0093-The-Draft-Window-Lists-Owed-Work-A-Phase-And-The-AIs]]"
tests: []
---

# Harness, unit tests and a register row for the draft window

The draft window's page can be opened in a browser without the application, its pure functions have unit tests that run in the existing node suite, and the capability register says the window exists.

## Definition of Done

- [x] A harness page under `desktop/harness/` loads the built draft page with a stand-in for the preload bridge and a fixture payload. The fixture has at least: two projects that owe something, one project that owes nothing, one project marked as not read, one project with no active phase, and sessions in each of the four states.
- [x] Unit tests under `desktop/tests/` cover the page's pure functions and the payload-shaping function of [[TASK-0646-The-Draft-Window-Opens-From-The-Menu-And-Gathers-Every-Projects-Data]]. They run against the built files, the way `desktop/tests/deep-link.test.mjs` does, and pass with `node --test desktop/tests/*.test.mjs`.
- [x] The tests assert behaviour and would fail if it broke. At the least: every owed row carries exactly one verb; a row's link is the `cockpit://` link the existing `parseCockpitLink` reads back to the same project and target; a project marked not read never produces "nothing is owed"; a phase with unticked exit criteria lists them under what still stands; a zero count becomes a sentence.
- [x] Each test's adequacy is shown once in the change note or the test file's header: the test fails when the function it guards is broken (`tools/instructions/TESTING.md`, "Test adequacy").
- [x] `docs/reference/cockpit-capability-register.md` has a new row with a new key and the date for the draft window, and a dated line under its maintenance log. If a read-only sidecar route was added, it has its own row.
- [x] A change note under `docs/changes/` describes the draft window, in the same commit as the register row.
- [x] [[TST-0093-The-Draft-Window-Lists-Owed-Work-A-Phase-And-The-AIs]] is set to `active`, with its Setup and Steps corrected to what was built.
- [ ] The whole suite is green: `python3 -m pytest -q`, `node --test desktop/tests/*.test.mjs`, `npm run typecheck` in `desktop/`, and `bash tools/scripts/validate-docs.sh`.

## Steps

- [x] Write the tests beside the pure functions as they are written in the other two tasks; this task is where they are completed and counted.
- [x] Build the harness from `desktop/harness/overview-harness.html`, the one that stubs payloads with fixtures.
- [x] Add the register row and the change note. Check the register's own detection command still reports no commit without a row.
- [ ] Bring the acceptance check to `active` and tell Edwin it is ready for him to test.

## Notes

- The acceptance check is Edwin's to perform. An agent does not record its result.
- The feature reaching `done` owes one independent review (`tools/instructions/QUALITY.md`, "Independent review"). That is close-out for the feature, after this task.
- No surface note (`SUR-*`) is planned for the draft window. This repository has one surface note for about fourteen screens ([[ISS-0306]]); adding the draft window's is part of that issue's work, not this task's. Until one exists the acceptance check's `area:` stays empty, because the validator reports an `area:` that no surface note carries (SURFACE-ORPHAN).

## State on 2026-10-13

Everything this task writes exists. The line about the whole suite is not ticked, and the task stays `doing`, because the node suite has not been run in place against a build of these sources.

- **Tests.** `desktop/tests/home-model.test.mjs`, 17 tests. They pass against a build made outside the repository. Run in place before a build, the file fails because `dist/renderer/home-model.js` does not exist yet.
- **One criterion reads differently in the tests.** "A phase with unticked exit criteria lists them under what still stands" is tested on the model's `stands` list and its sentence. "A zero count becomes a sentence" is tested through the empty-list sentence and the three exit-criteria sentences.
- **Adequacy.** Eleven deliberate breakages, each caught; listed in [[CHG-20261013-A-Draft-Home-Window-Opens-Beside-The-Present-One]].
- **Harness.** `desktop/harness/home-harness.html`, with `#dark` and `#empty`.
- **The acceptance check is `active` and is Edwin's to run** after `npm run build` and a restart.
