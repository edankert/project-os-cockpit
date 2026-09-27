---
type: "[[requirement]]"
id: REQ-0071
title: "A result is recorded on the check where it was seen, with a reason for anything but Pass, and every count on screen follows at once without moving the reader"
status: draft
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-27
updated: 2026-09-27
source: ["Edwin, 2026-09-27: approved the example page in docs/features/release-test/__attachments__/release-test-example/index.html"]
priority: high
scope: "Results on the release test's section page, the existing ledger write path, and the overview that summarises them"
acceptance: ["All seven results are offered, Pass and Fail in one tap", "Every result but Pass needs a reason before it is saved", "Results reach the ledger through the existing write path with unchanged stored values", "Pane, overview, Continue and Needs you update at once and the reader stays in place", "Continue names and opens the next check with no result", "A check that cannot be done yet is greyed with why and a suggested result"]
implements: "[[FEAT-0155-The-Release-Test-Goes-Section-By-Section]]"
verifies: []
related: ["[[REQ-0068-The-Walk-Records-One-Clear-Observation-At-A-Time]]", "[[REQ-0069-The-Walk-Resumes-With-Valid-Evidence]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]", "[[ISS-0263-A-Write-Evicts-The-Reader-From-The-Checks-Page]]"]
tests: []
---

# A result is recorded on the check where it was seen

## Statement

The section page must let a person give each check one of seven results where they read it. Pass and Fail must take one tap. Partial, Question, Blocked, N/A and Excused must be one more tap away, each with a one-line meaning. Every result except Pass must carry a reason. Results must reach the release ledger through the existing write path. The pane, the overview, the Continue button and Needs you must show the new result without a reload, and the reader must stay where they were.

[[REQ-0069-The-Walk-Resumes-With-Valid-Evidence]] still applies: saved results survive a restart, and a check whose words changed does not inherit an old result.

## Acceptance Criteria

- [ ] All seven results are offered, Pass and Fail in one tap — evidence: pending ([[TASK-0643-The-Section-Page-And-Its-Results]]).
- [ ] Every result but Pass needs a reason before it is saved — evidence: pending ([[TASK-0643-The-Section-Page-And-Its-Results]]).
- [ ] Results reach the ledger through the existing write path with unchanged stored values — evidence: pending (ledger-copy test in [[TASK-0643-The-Section-Page-And-Its-Results]]).
- [ ] Pane, overview, Continue and Needs you update at once and the reader stays in place — evidence: pending ([[TASK-0642-The-Platform-Overview-Continue-And-Needs-You]], [[TASK-0643-The-Section-Page-And-Its-Results]]).
- [ ] Continue names and opens the next check with no result — evidence: pending ([[TASK-0642-The-Platform-Overview-Continue-And-Needs-You]]).
- [ ] A check that cannot be done yet is greyed with why and a suggested result — evidence: pending ([[TASK-0643-The-Section-Page-And-Its-Results]]).

## Traceability

- Implements: [[FEAT-0155-The-Release-Test-Goes-Section-By-Section]].
- Verified by: [[TST-0092-A-Release-Test-Section-Is-Tested-From-The-Tests-Pane]] and the desktop renderer tests the tasks add.
