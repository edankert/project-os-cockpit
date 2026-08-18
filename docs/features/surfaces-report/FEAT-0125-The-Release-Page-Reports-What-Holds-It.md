---
type: "[[feature]]"
id: FEAT-0125
aliases: ["FEAT-0125"]
title: "The release page reports what holds the release, and offers no control that changes a check"
status: doing
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
requirements: ["[[REQ-0044-A-Release-Page-Records-Nothing]]"]
tasks: ["[[TASK-0502-Delete-The-Actionable-Mark-On-Release-Rows]]", "[[TASK-0503-The-Gate-Band-Becomes-A-Breakdown]]", "[[TASK-0504-The-Release-Shows-Its-Open-Tests]]"]
issues: ["[[ISS-0210-The-Release-Page-Offers-Sixty-Live-Marks]]"]
related: ["[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]"]
tags: [feature]
---

# What holds this release

Three changes to one page, from [[ADR-0035]] and [[ISS-0210]].

**The control goes.** `gateMark`'s `actionable` parameter is deleted rather than set false everywhere — a parameter with one value is a decision waiting to be re-litigated by the next caller. The `quiet` and `stale` groups already render the token as a plain `<span>`; every group now does.

**The wall becomes a breakdown.** Sixty rows sorted by nothing but "blocks" is an inventory, not an answer. The page keeps its verdict line and its confidence roll-up, and replaces the list with counts per area or feature, each a link into `~checks` pre-filtered.

**The page gains what Edwin asked for**: the open `TST-*` rows for the features in the release. `blocking_for(subjects)` already scopes to a feature set — the production caller landed in [[PHASE-036]] — so the data path exists.

## Acceptance

- [ ] No release-page row can write a check.
- [ ] The blocking wall is replaced by a breakdown whose parts link to a filtered `~checks`.
- [ ] Open tests for the release's contents are shown.
