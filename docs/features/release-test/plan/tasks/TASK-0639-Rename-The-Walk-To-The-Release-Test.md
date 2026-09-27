---
type: "[[task]]"
id: TASK-0639
title: "Rename the walk to the release test in routes, the API, the payload, the bundled generator, labels, CSS, storage keys, tests and live notes"
status: backlog
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-27
updated: 2026-09-27
source: ["Edwin, 2026-09-27, decision D1"]
parent: "[[FEAT-0155-The-Release-Test-Goes-Section-By-Section]]"
effort: "L"
due: ""
depends: []
blocks: ["[[TASK-0640-The-Release-Test-Payload]]"]
related: ["[[REQ-0072-The-Walk-Is-Called-The-Release-Test-Everywhere]]", "[[RISK-0011-Renaming-The-Walk-Drops-Links-And-Saved-Progress]]", "[[ADR-0039-Three-Sections-Derived-Not-Filed]]"]
tests: []
---

# Rename the walk to the release test

## Definition of Done

- [ ] The page's address is `~release-test/<platform>` and its API is `/api/cockpit/release-test`. `~walk` and `~walk/<platform>` open the new address instead of an empty page.
- [ ] `acceptance.walk_payload` is renamed, and so are the renderer's walk functions, types and CSS classes. Labels a person reads say "release test", "section", "what changed" and "result".
- [ ] The bundled generator `walk_sheet_bundled.py` has the new name project-os-dev gives its generator, and `tests/test_walk_bundle.py` (renamed with it) still proves the copy is byte-identical.
- [ ] The five browser storage keys (`cockpit:walk-focus`, `walk-completed`, `walk-place`, `walk-steps`, `walk-evidence`) are renamed. A value found under an old key is moved to the new key once, then the old key is removed. A renderer test proves a result saved under the old key is still shown.
- [ ] The obligation links in `src/project_os_cockpit/obligations.py` and `cockpit.py` ("Walk them") point at the new address and use the new words.
- [ ] A test searches `src/` and `desktop/src/` for the old words in the old sense and fails on any hit outside a redirect or migration table.
- [ ] Live notes use the new words: SUR-0004's title and prose, `docs/GLOSSARY.md`, `docs/references/COCKPIT-API.md`, `docs/references/TESTING-MODEL.md`, `docs/reference/cockpit-capability-register.md`, `docs/tests/acceptance/WALK.md` and `README.md`, and PHASE-043's title. File names and IDs of existing notes do not change. Closed ADRs, change notes and archived notes are not edited.
- [ ] The ledger's stored values are unchanged.
- [ ] The full Python suite and the desktop suite pass.

## Steps

- [ ] Wait until project-os-dev has renamed its generator (project-os-dev: release test generator, vocabulary ADR and release-prep skill, ID to follow), then sync it, so the bundled copy and its name arrive together.
- [ ] Rename the server route, the payload function and its tests.
- [ ] Rename the renderer's route handling, functions, CSS classes and labels; add the `~walk` redirect and the storage-key migration.
- [ ] Rename the words in the live notes listed above.
- [ ] Write a change note naming the old and new addresses.

## Notes

Template-owned files (`tools/instructions/TESTING.md` "The walk", `tools/skills/walk-procedure/`, `docs/__templates__/walk.md`, `tools/scripts/walk-sheet.py`) are renamed upstream in project-os-dev and arrive here by `sync-project-os.sh`. They are not edited here by hand.

Every fleet repository carries a copy of the cockpit under `tools/cockpit/`, which still links to `~walk` until the next cockpit release reaches it. The `~walk` redirect covers those links, and the release note links in Your Trainer such as `REL-0017-v2.2.0.md`.

The word "section" already has a meaning in this repository. [[ADR-0039-Three-Sections-Derived-Not-Filed]] calls "Feature tests", "Regression tests" and "Automated tests" sections, and the code says `section_of`, `SECTION_FEATURE` and `MANUAL_SECTIONS`. After the rename, the Tests pane would show both kinds of "section" under "Acceptance tests". This is an open question for Edwin, recorded on the feature. Until he answers, the new code names the release-test kind `release_section` and leaves ADR-0039's names alone.
