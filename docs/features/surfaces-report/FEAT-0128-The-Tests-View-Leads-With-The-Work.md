---
type: "[[feature]]"
id: FEAT-0128
aliases: ["FEAT-0128"]
title: "The tests view opens on what is owed and tracks progress, instead of on 579 rows of inventory"
status: doing
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
requirements: ["[[REQ-0047-The-View-Opens-On-What-Is-Owed]]"]
tasks: ["[[TASK-0508-Collapse-Resting-To-A-Line]]", "[[TASK-0509-Tier-Sections-Collapse-To-Tracking-Lines]]", "[[TASK-0510-Feature-Tests-Lead]]", "[[TASK-0513-The-Checks-Page-Is-A-Flat-List-Per-Tier]]", "[[TASK-0520-Group-The-Suite-By-Surface]]", "[[TASK-0549-One-Grouping-Key-And-It-Is-The-Id]]", "[[TASK-0550-The-Nav-Groups-By-Surface]]", "[[TASK-0551-A-Percentage-Where-The-Reader-Is-Working]]"]
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
