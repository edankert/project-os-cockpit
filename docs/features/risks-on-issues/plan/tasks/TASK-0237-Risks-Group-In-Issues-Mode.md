---
type: "[[task]]"
id: TASK-0237
aliases: ["TASK-0237"]
title: "Risks group in the Issues nav mode, bucketed by severity"
status: done
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: []
parent: "[[FEAT-0047-Risks-On-The-Issues-Surface]]"
effort: S
depends: []
blocks: ["[[TASK-0238-Risks-Tile-Destination]]", "[[TASK-0245-Drop-Relocated-Groups]]"]
related: ["[[ISS-0063-Dead-Stat-Tiles]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
---

# TASK-0237 — Risks in the Issues mode

## Definition of Done
- [ ] `_issues_groups` emits risk records alongside issues, bucketed by `severity:`
- [ ] Risk rows carry `type: "risk"` so the existing risk shield icon distinguishes them
- [ ] A corpus with no risks renders identically to today
- [ ] Every `[[risk]]` note in this corpus appears

## Steps
- [ ] Read `index.notes_by_type("risk")` in `_issues_groups`, filtered through `_platform_match`
- [ ] Emit risks as their own severity-labelled groups (e.g. `Risks · high`) rather than mixing them into the issue buckets — same surface, visibly not the same thing
- [ ] Keep `_SEVERITY_RANK` ordering
- [ ] Test: risk count in the payload equals `notes_by_type("risk")`; no-risk corpus unchanged

## Notes

Deciding between "mixed into the severity buckets" and "own groups": own groups. Mixing would make the Issues count in the stat tile disagree with what the pane shows, and a risk is not triaged the way an issue is.
