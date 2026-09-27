---
type: "[[requirement]]"
id: REQ-0070
title: "The release test is reached from the Tests pane, opens on a platform overview, and shows one section per page"
status: draft
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-27
updated: 2026-09-27
source: ["Edwin, 2026-09-27: approved the example page in docs/features/release-test/__attachments__/release-test-example/index.html"]
priority: high
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

- [ ] The Tests pane lists the release test per platform and per section, with progress — evidence: pending ([[TASK-0641-The-Release-Test-In-The-Tests-Pane]]).
- [ ] A platform opens on its overview — evidence: pending ([[TASK-0642-The-Platform-Overview-Continue-And-Needs-You]]).
- [ ] A section page shows what changed, then Setup folded, then grouped checks — evidence: pending ([[TASK-0643-The-Section-Page-And-Its-Results]]).
- [ ] Each check is one action, one expected result and its test tag — evidence: pending ([[TASK-0643-The-Section-Page-And-Its-Results]], [[TASK-0645-Pilot-The-Equipment-Section-Then-The-Rest]]).

## Traceability

- Implements: [[FEAT-0155-The-Release-Test-Goes-Section-By-Section]].
- Verified by: [[TST-0092-A-Release-Test-Section-Is-Tested-From-The-Tests-Pane]] and the desktop renderer tests the tasks add.
