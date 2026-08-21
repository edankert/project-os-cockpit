---
type: "[[feature]]"
id: FEAT-0127
aliases: ["FEAT-0127"]
title: "Every row in the tests view is a test, and no unrecognised status reads as `Verified`"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-21"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
requirements: ["[[REQ-0046-The-Pass-Bucket-Is-Not-The-Else-Branch]]"]
tasks: ["[[TASK-0506-Verified-Stops-Being-The-Else-Branch]]", "[[TASK-0507-Level-The-Five-Mislevelled-Tests]]"]
issues: ["[[ISS-0212-Retired-Documents-Render-As-Verified-Tests]]", "[[ISS-0213-Acceptance-Tests-Carrying-Level-System]]"]
tags: [feature]
---

# The pass bucket stops being the else-branch

Two defects Edwin found under one sentence — *"not showing the correct TSTs"*.

**A run plan reads as a verified test.** `_tests_groups` ends in `else: verified`, so any status the chain does not name lands in the group that makes the strongest claim available. `your-trainer` has three `status: retired` documents there. The general fix is to stop treating `Verified` as the fallback; the specific fix is to stop typing documents as tests.

**Five acceptance tests carry `level: system`** and so route to a flat group rather than under a tier. That one is data, and it needs a judgement per note: three are named `…Acceptance`, two are not obviously acceptance tests just because they are manual.

## Acceptance

- [x] An unrecognised status is visible, not absorbed into `Verified` — [[TASK-0506]].
- [x] The three documents are no longer typed as tests — [[ISS-0212]].
- [x] The five levels are set deliberately, with reasoning recorded — [[ISS-0213]]'s judgement table. Applying three of them is Edwin's decision on another repo's gate and is parked with the issue.

## Done 2026-08-21

Both tasks are `done`, [[REQ-0046]] is `implemented`, and [[ISS-0212]] is `fixed`.

[[ISS-0213]] is **deferred under [[PHASE-999]]**, not closed over. Its finding belonged to this phase — *a frontmatter field, not the content, decides where a test appears, and nothing on screen says so* — and that finding is what [[TASK-0506]] and [[TASK-0507]] answered. What remains on it is a data edit in `your-trainer` whose cost the issue measures and Edwin has not ruled on, plus a 107-row note that should be split before it is relevelled. Neither is a rendering question and neither is this feature's to decide.
