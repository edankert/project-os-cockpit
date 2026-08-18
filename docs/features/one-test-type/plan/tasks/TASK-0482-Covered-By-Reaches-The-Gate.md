---
type: "[[task]]"
id: TASK-0482
aliases: ["TASK-0482"]
title: "`covered_by:` reaches the gate — a passing covering test settles the check it covers"
status: done
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0120-The-Automation-Path]]"]
parent: "[[FEAT-0120-The-Automation-Path]]"
effort: M
depends: ["[[TASK-0481-Retire-The-Check-Type-From-The-Cockpit]]"]
blocks: []
related: []
tests: []
---

# `covered_by:` reaches the gate

`Item.settled` becomes: the mark is settled, **or** `covered_by:` names a test that is `passing`. One clause, and it is the return on the whole phase.

**The direction is what keeps it safe.** A machine's exit code discharges a human's checkbox; a human's mark never writes a runner's status, so [[project-os-dev#ADR-0010]] is untouched.

**Name the consequence rather than discovering it** ([[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] records it): a *failing* covering test un-settles the check. The gate must then say which test and why — an acceptance row that goes red with no explanation is worse than one that was never covered. And a *stale* covering test is a third state: `passing` but last run before the change that invalidated the check, which `invalidated_by.date` versus `last_run` can already answer arithmetically.

Done when: a check with a passing covering test leaves the blocking set with no mark written; a failing one re-enters it naming the test; and the count of checks discharged this way is reported on the gate rather than inferred.

## Done

`Item.settled` gained one clause — settled if the mark is settled **or** `covered_by:` names a test that is `passing` — and `Item.covered_by_status` carries the resolved statuses.

**Resolved at load, never stored.** A remembered status is a claim about a run that happened once; what the gate needs is whether the covering test passes *now*. That single decision is also what makes a failing covering test un-settle the check: the same read, in the other direction.

**A directory read leaves it empty and falls back to the mark alone**, which is the safe direction — it can only ever under-settle, failing a gate closed rather than open. Guarded by `test_coverage_cannot_settle_without_an_index`.

**Four states, asserted end to end on real notes** (`test_a_passing_covering_test_settles_the_check`): uncovered and unwalked blocks; a `passing` cover settles it **with no mark written**; a `failing` cover puts it back in the gate; and a `ready` cover settles nothing — because *"not failing"* is not coverage, and `ready` means defined and never executed.
