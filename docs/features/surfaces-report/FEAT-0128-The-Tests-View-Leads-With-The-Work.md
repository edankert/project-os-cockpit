---
type: "[[feature]]"
id: FEAT-0128
aliases: ["FEAT-0128"]
title: "The tests view opens on what is owed and tracks progress, instead of on 579 rows of inventory"
status: doing
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
requirements: ["[[REQ-0047-The-View-Opens-On-What-Is-Owed]]"]
tasks: ["[[TASK-0508-Collapse-Resting-To-A-Line]]", "[[TASK-0509-Tier-Sections-Collapse-To-Tracking-Lines]]", "[[TASK-0510-Feature-Tests-Lead]]", "[[TASK-0513-The-Checks-Page-Is-A-Flat-List-Per-Tier]]", "[[TASK-0520-Group-The-Suite-By-Surface]]", "[[TASK-0549-One-Grouping-Key-And-It-Is-The-Id]]", "[[TASK-0550-The-Nav-Groups-By-Surface]]", "[[TASK-0551-A-Percentage-Where-The-Reader-Is-Working]]", "[[TASK-0552-The-navs-surfaces-get-their-own-address-and-their-ow]]", "[[TASK-0553-A-surface-row-draws-its-progress-and-a-payload-field]]", "[[TASK-0554-A-surface-carries-no-test-status]]", "[[TASK-0555-The-check-id-renders-once-at-the-start-and-is-select]]", "[[TASK-0556-Incomplete-First]]"]
tags: [feature]
---

# 579 rows is an inventory, not an answer

Edwin: *"the feature tests are shown below those sections, even though I think these sections should be clearly at the forefront. Note: there is no point showing all the tests inside the left hand Tier x - sections. But it would be nice to show a tracking line how many tsts have been completed and how many tests will need to be rerun."*

Three changes, none of which removes information:

**`Resting · no feature in flight` collapses to one line.** It exists for a real reason ([[ADR-0028]]) — telling *"nobody owes this yet"* apart from *"nobody got round to it"* — and that reason survives a `<details>`. 10 rows in `your-trainer`, 3 here.

**Tier sections collapse to their tracking line.** The headers already carry `306/347`; what they should also carry is the re-run count, which is computable today because `rerun` is a mark. `Tier 1 — 306/347 walked · 12 need re-run · 29 to walk`.

**Feature tests lead.** They are the substance of the view and they currently sit below three flat groups.

## Acceptance

- [ ] Resting is one collapsed line.
- [ ] Tier sections show a tracking line and expand on demand.
- [ ] Feature tests come first.

## Criteria re-read 2026-08-20 — two met, one with a question

- *Tier sections show a tracking line and expand on demand* — met. Every section head carries its count and `default_open: False`.
- *Feature tests come first* — met, and guarded by `test_exactly_one_group_per_test`.
- *Resting is one collapsed line* — **the mechanism exists and its population is empty in both repos.**

### The open question

The group is built (`cockpit.py`, `key: "suppressed"`, `label: "Quiet · N · no feature in flight"`, `reason: "no feature in flight"`) and [[TASK-0508]] is `done`. But it renders in **neither** corpus today:

| repo | suppressed groups |
|---|---|
| `project-os-cockpit` | none |
| `your-trainer` | none |

This note recorded **"10 rows in `your-trainer`, 3 here"** when it was written. Both are now zero.

**Two readings, and they are not equivalent.** Either the corpus moved — those subjects came into flight or reached a terminal status, which would make zero correct — or the predicate stopped firing, which is the defect this phase has found five times.

**Not resolved, and deliberately not ticked.** A criterion whose subject cannot be produced on either corpus is exactly the shape that gets ticked on the strength of the code existing. Whoever closes this feature has to construct the case — a check whose subject is `backlog` — and watch the group appear.
