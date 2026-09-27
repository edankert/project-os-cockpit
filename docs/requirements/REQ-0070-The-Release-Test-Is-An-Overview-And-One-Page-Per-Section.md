---
type: "[[requirement]]"
id: REQ-0070
title: "The release test is reached from the Tests pane, opens on a platform overview, and shows one section per page"
status: implemented
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-27
updated: 2026-09-27
source: ["Edwin, 2026-09-27: approved the example page in docs/features/release-test/__attachments__/release-test-example/index.html"]
priority: high
reviewed_by: "model:claude-opus-5-5 (FEAT-0155 review, two rounds)"
review_date: 2026-09-27
review_round: 2
review_verdict: approved
approved_by: "user:edwin"
approved: 2026-09-27
scope: "The release test in the cockpit's Tests pane, for any project-os workspace with an open release and a ledger"
acceptance: ["The Tests pane lists the release test per platform and per section, with progress", "A platform opens on its overview", "A section page shows what changed, then Setup folded, then grouped checks", "Each check is one action, one expected result and its test tag"]
implements: "[[FEAT-0155-The-Release-Test-Goes-Section-By-Section]]"
verifies: []
related: ["[[REQ-0066-The-Release-Walk-Keeps-Observation-Context]]", "[[REQ-0067-The-Walk-Keeps-Required-Actions-And-Only-Relevant-Setup]]", "[[SUR-0001-The-Tests-View]]"]
tests: []
---

# The release test is an overview and one page per section

## Statement

The cockpit must list the release test in the Tests pane, open each platform on an overview, and show each section on its own page. A section page must show what changed first, Setup folded second, and the checks third. Each check must be one action line and one expected line.

This replaces the one-action-at-a-time rule of [[REQ-0066-The-Release-Walk-Keeps-Observation-Context]] and [[REQ-0068-The-Walk-Records-One-Clear-Observation-At-A-Time]], which are superseded when [[FEAT-0155-The-Release-Test-Goes-Section-By-Section]] lands. [[REQ-0067-The-Walk-Keeps-Required-Actions-And-Only-Relevant-Setup]] still applies to what Setup and the "Start:" lines contain.

## Acceptance Criteria

- [x] The Tests pane lists the release test per platform and per section, with progress — evidence: `cockpit._release_test_group` and `rtRefreshPane` ([[TASK-0641-The-Release-Test-In-The-Tests-Pane]]); [[TST-0092-A-Release-Test-Section-Is-Tested-From-The-Tests-Pane]] step 1, 2026-09-27.
- [x] A platform opens on its overview — evidence: `~release-test/<platform>` draws the overview ([[TASK-0642-The-Platform-Overview-Continue-And-Needs-You]]); TST-0092 step 2.
- [x] A section page shows what changed, then Setup folded, then grouped checks — evidence: [[TASK-0643-The-Section-Page-And-Its-Results]]; TST-0092 step 4.
- [x] Each check is one action, the expected line of each part it cites, and its tags (corrected on review, 2026-09-27: a step may cite several parts) — evidence: TASK-0643 and the pilot, [[TASK-0645-Pilot-The-Equipment-Section-Then-The-Rest]]; TST-0092 step 4.

## Traceability

- Implements: [[FEAT-0155-The-Release-Test-Goes-Section-By-Section]].
- Verified by: [[TST-0092-A-Release-Test-Section-Is-Tested-From-The-Tests-Pane]] and the desktop renderer tests the tasks add.

## Approved and implemented, 2026-09-27

Edwin approved the release test page after using it in the desktop app: *"It looks great, I think we can now fully close out the cockpit phase-0010 and the release test functionality."* Every criterion above is met; the release test itself was tested end to end as [[TST-0092-A-Release-Test-Section-Is-Tested-From-The-Tests-Pane]].
