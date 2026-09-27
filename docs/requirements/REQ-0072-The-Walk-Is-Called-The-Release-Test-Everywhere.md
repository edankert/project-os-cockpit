---
type: "[[requirement]]"
id: REQ-0072
title: "The walk is called the release test everywhere in the cockpit, internal names included, and old walk links still open it"
status: implemented
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-27
updated: 2026-09-27
source: ["Edwin, 2026-09-27, decision D1: walk becomes release test, sitting becomes section, survey becomes what changed, and the mark shown to a person becomes result, internal names included, 'to avoid confusion later on'"]
priority: medium
scope: "Routes, API paths, payload functions, the bundled generator's file name, labels, CSS classes, browser storage keys, tests and live notes in this repository"
acceptance: ["No code name, route, label or storage key uses the old words", "Live notes use the new words; closed ADRs, change notes and archived notes are unchanged", "Ledger values are unchanged", "Old ~walk addresses open the new page and saved progress carries over"]
implements: "[[FEAT-0155-The-Release-Test-Goes-Section-By-Section]]"
verifies: []
related: ["[[RISK-0011-Renaming-The-Walk-Drops-Links-And-Saved-Progress]]", "[[ADR-0039-Three-Sections-Derived-Not-Filed]]"]
tests: []
---

# The walk is called the release test everywhere

## Statement

The cockpit must use one set of words for testing a release by hand: release test, section, what changed, result and check. The old words (walk, sitting, survey, and mark or verdict as shown to a person) must not remain in routes, API paths, payload functions, file names, labels, CSS classes, storage keys, tests or live notes. The stored ledger values stay as they are. A link to an old `~walk/<platform>` address must still open the release test for that platform, and results saved in the browser under the old keys must carry over.

"Live notes" means notes that are not closed or archived. Closed ADRs, change notes and archived notes are history and keep their words. A note's file name and ID do not change, so existing links keep working; its title and prose do.

## Acceptance Criteria

- [x] No code name, route, label or storage key uses the old words — evidence: `tests/test_release_test_names.py` searches `src/` and `desktop/src/` ([[TASK-0639-Rename-The-Walk-To-The-Release-Test]]).
- [x] Live notes use the new words; closed ADRs, change notes and archived notes are unchanged — evidence: TASK-0639, and the sweep of 45 live notes in 89e4655, 2026-09-27.
- [x] Ledger values are unchanged — evidence: `ledger.py` keeps its result values; a new entry stores them under `result` and every reader still accepts `mark` (TASK-0639).
- [x] Old ~walk addresses open the new page and saved progress carries over — evidence: The redirect in `navigateToInner` and the storage move (TASK-0639, [[TASK-0644-Retire-The-Walk-Page-In-The-Publication-View]]); TST-0092 step 9.

## Traceability

- Implements: [[FEAT-0155-The-Release-Test-Goes-Section-By-Section]].
- Verified by: tests added in [[TASK-0639-Rename-The-Walk-To-The-Release-Test]].

## Approved and implemented, 2026-09-27

Edwin approved the release test page after using it in the desktop app: *"It looks great, I think we can now fully close out the cockpit phase-0010 and the release test functionality."* Every criterion above is met; the release test itself was tested end to end as [[TST-0092-A-Release-Test-Section-Is-Tested-From-The-Tests-Pane]].
