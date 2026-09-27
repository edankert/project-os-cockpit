---
type: "[[task]]"
id: TASK-0641
title: "The Tests pane lists Release test · <version> under Acceptance tests, then each platform with progress, then its sections with a status dot and done/total"
status: done
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-27
updated: 2026-09-27
source: ["Edwin, 2026-09-27: approved example page"]
parent: "[[FEAT-0155-The-Release-Test-Goes-Section-By-Section]]"
effort: "M"
due: ""
depends: ["[[TASK-0640-The-Release-Test-Payload]]"]
blocks: ["[[TASK-0644-Retire-The-Walk-Page-In-The-Publication-View]]"]
related: ["[[SUR-0001-The-Tests-View]]", "[[REQ-0070-The-Release-Test-Is-An-Overview-And-One-Page-Per-Section]]", "[[ISS-0263-A-Write-Evicts-The-Reader-From-The-Checks-Page]]"]
tests: []
---

# The release test in the Tests pane

## Definition of Done

- [x] While a release is open, the Tests pane shows "Release test · <version>" under "Acceptance tests", above "Feature tests" and "Regression tests", which stay where they are. `_release_test_group`, inserted straight after `Needs you`, above the test kinds. The pane has no "Acceptance tests" heading to nest it under, so it sits where the example puts it relative to its neighbours.
- [x] Under it is one row per platform with a done/total count and a thin progress bar. "Android · 25/355" with the bar, on your-trainer.
- [x] Under each platform are its sections, each with a status dot and a done/total count. The dot is empty before any result, half filled when part done, filled when done, and red when the section holds a Fail, Question or Blocked result. `dot` on each section row (`empty`, `part`, `done`, `bad`), drawn by `buildNavRow`; the page redraws the dots, bars and counts after every result (`rtRefreshPane`).
- [x] The row for the page being read is highlighted. Rows carry the page address as `data-rel`, which the pane already highlights.
- [x] The Tests view's owned pages include the release test pages, so a write never lands the reader on the Tests landing (the `VIEW_OWNED_PAGES` guard from ISS-0263). A renderer test proves it. `VIEW_OWNED_PAGES.tests` holds `~release-test`; renderer test in `release-test.test.mjs`.
- [x] With no open release, the entry is absent. No section order or no open release gives no group; `test_no_section_order_means_no_release_test_group`.

## Steps

- [ ] Add the entry to the Tests pane tree.
- [ ] Add the release test routes to the Tests view's owned pages.
- [ ] Renderer tests for the dot states and the counts.

## Close-out, 2026-09-27

Seen in a browser on a copy of your-trainer through `desktop/harness/live-harness.html`: the group, the counts and the highlighted row.
