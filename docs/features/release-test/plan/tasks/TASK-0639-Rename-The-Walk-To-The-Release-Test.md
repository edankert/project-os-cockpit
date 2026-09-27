---
type: "[[task]]"
id: TASK-0639
title: "Rename the walk to the release test in routes, the API, the payload, the bundled generator, labels, CSS, storage keys, tests and live notes"
status: done
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

- [x] The page's address is `~release-test/<platform>` and its API is `/api/cockpit/release-test`. `~walk` and `~walk/<platform>` open the new address instead of an empty page. `~release-test[/<platform>[/<section>]]` in the renderer; `/api/cockpit/release-test` in the server; `~walk` redirects through `rtAddressFor`, proven by `desktop/tests/release-test.test.mjs`.
- [x] `acceptance.walk_payload` is renamed, and so are the renderer's walk functions, types and CSS classes. Labels a person reads say "release test", "section", "what changed" and "result". `walk_payload` is replaced by `release_test_payload`; the old page's 70 renderer functions, its types, state and 357 lines of CSS are removed, not renamed (they were unreachable once the route moved, and `test_surface_ownership` refuses unreachable functions). `walkOneCheck`, which `~checks` still uses, is `markOneCheck`. Visible labels say tested, release test and result.
- [x] The bundled generator `walk_sheet_bundled.py` has the new name project-os-dev gives its generator, and `tests/test_walk_bundle.py` (renamed with it) still proves the copy is byte-identical. `release_test_bundled.py`; `tests/test_release_test_bundle.py` asserts it byte-identical to `tools/scripts/release-test.py`.
- [x] The five browser storage keys (`cockpit:walk-focus`, `walk-completed`, `walk-place`, `walk-steps`, `walk-evidence`) are renamed. A value found under an old key is moved to the new key once, then the old key is removed. A renderer test proves a result saved under the old key is still shown. `rtMigrateStorage` moves each once and removes the old key; `rtCarryWalkMarks` carries a saved step result onto the printed check with the same tags. Both are proven in `release-test.test.mjs`.
- [x] The obligation links in `src/project_os_cockpit/obligations.py` and `cockpit.py` ("Walk them") point at the new address and use the new words. `obligations.py` acts on `~release-test`; `cockpit.py`'s gate row reads "Test them" and links to `~release-test/<platform>`.
- [x] A test searches `src/` and `desktop/src/` for the old words in the old sense and fails on any hit outside a redirect or migration table. `tests/test_release_test_names.py`: identifiers, string literals, CSS and HTML, with comments and docstrings left as history. Allowed: the redirect, the storage migration, the OLD-NAME label, the DOM's TreeWalker and five ordinary-English traversals, each named.
- [x] Live notes use the new words: SUR-0004's title and prose, `docs/GLOSSARY.md`, `docs/references/COCKPIT-API.md`, `docs/references/TESTING-MODEL.md`, `docs/reference/cockpit-capability-register.md`, `docs/tests/acceptance/WALK.md` and `README.md`, and PHASE-043's title. File names and IDs of existing notes do not change. Closed ADRs, change notes and archived notes are not edited. SUR-0004 (title and body), GLOSSARY, COCKPIT-API.md (the new route documented), TESTING-MODEL.md, the capability register (three rows replace six), RELEASE-TEST.md and PHASE-043's title. README.md had none. File names and IDs are unchanged.
- [x] The ledger's stored values are unchanged. New entries use the key `result`, and every reader accepts `mark`. `ledger.py` writes `result` and reads `result` or `mark`; `test_the_ledger_reads_both_keys_and_writes_result`.
- [x] "Feature tests", "Regression tests" and "Automated tests" are called test kinds in code and live notes (`section_of`, `SECTION_FEATURE`, `MANUAL_SECTIONS` and the like become `kind_of`, `KIND_FEATURE`, `MANUAL_KINDS`), so "section" means only a release test section. `kind_of`, `KIND_FEATURE`, `KIND_REGRESSION`, `KIND_AUTOMATED`, `MANUAL_KINDS`, `KIND_ORDER`, `KIND_LABELS`, `kind_label` and the private names, in `src/`, `tests/` and the two scripts that import them.
- [x] The full Python suite and the desktop suite pass. Python: 2,140-odd passed, 6 skipped, none failing after the old walk tests were removed (they tested the removed payload). Desktop: 158 passed.

## Steps

- [ ] Wait until project-os-dev has renamed its generator (project-os-dev FEAT-0040 and ADR-0050, the release test generator, the vocabulary decision and the release-prep skill), then sync it, so the bundled copy and its name arrive together.
- [ ] Rename the server route, the payload function and its tests.
- [ ] Rename the renderer's route handling, functions, CSS classes and labels; add the `~walk` redirect and the storage-key migration.
- [ ] Rename the words in the live notes listed above.
- [ ] Write a change note naming the old and new addresses.

## Notes

Template-owned files (`tools/instructions/TESTING.md` "The walk", `tools/skills/walk-procedure/`, `docs/__templates__/walk.md`, `tools/scripts/walk-sheet.py`) are renamed upstream in project-os-dev and arrive here by `sync-project-os.sh`. They are not edited here by hand.

Every fleet repository carries a copy of the cockpit under `tools/cockpit/`, which still links to `~walk` until the next cockpit release reaches it. The `~walk` redirect covers those links, and the release note links in Your Trainer such as `REL-0017-v2.2.0.md`.

The word "section" already has a meaning in this repository. [[ADR-0039-Three-Sections-Derived-Not-Filed]] calls "Feature tests", "Regression tests" and "Automated tests" sections, and the code says `section_of`, `SECTION_FEATURE` and `MANUAL_SECTIONS`. After the rename, the Tests pane would show both kinds of "section" under "Acceptance tests". Edwin decided on 2026-09-27 to rename the old meaning: those three become "test kinds" in code and notes (`kind_of`, `KIND_FEATURE`, `MANUAL_KINDS` and the like), and the release test's groups are plain `section`. The ledger's stored key becomes `result`, and every reader keeps accepting `mark`.

## Close-out, 2026-09-27

- The template sync ran twice: the first run used the old sync script, which left the old skill's generated copies (project-os-dev sync behaviour, not a defect).
- `validate_docs_bundled.py` was re-copied from the synced validator; it was a verbatim copy of the old one. The validator's new OLD-NAME code got a readable label in `validation-rows.ts`.
- The cockpit's `SCHEMAS.md` is merge-owned; its change, section-order, what-changed and procedure sections were taken from the template by hand, and its own test and surface wording updated.
- The old page's removal is TASK-0644's code half, done here because the dead-code test would not let the page stay unreachable.
