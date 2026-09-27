---
type: "[[task]]"
id: TASK-0641
title: "The Tests pane lists Release test · <version> under Acceptance tests, then each platform with progress, then its sections with a status dot and done/total"
status: backlog
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

- [ ] While a release is open, the Tests pane shows "Release test · <version>" under "Acceptance tests", above "Feature tests" and "Regression tests", which stay where they are.
- [ ] Under it is one row per platform with a done/total count and a thin progress bar.
- [ ] Under each platform are its sections, each with a status dot and a done/total count. The dot is empty before any result, half filled when part done, filled when done, and red when the section holds a Fail, Question or Blocked result.
- [ ] The row for the page being read is highlighted.
- [ ] The Tests view's owned pages include the release test pages, so a write never lands the reader on the Tests landing (the `VIEW_OWNED_PAGES` guard from ISS-0263). A renderer test proves it.
- [ ] With no open release, the entry is absent.

## Steps

- [ ] Add the entry to the Tests pane tree.
- [ ] Add the release test routes to the Tests view's owned pages.
- [ ] Renderer tests for the dot states and the counts.
