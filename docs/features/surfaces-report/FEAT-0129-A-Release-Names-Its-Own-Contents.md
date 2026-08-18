---
type: "[[feature]]"
id: FEAT-0129
aliases: ["FEAT-0129"]
title: "A release names its own contents — features and phases are chosen, not only derived — and the gate scopes to them"
status: doing
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
requirements: ["[[REQ-0048-A-Release-Can-Be-Composed]]"]
tasks: ["[[TASK-0511-A-Picker-Writes-Features-And-Phases]]", "[[TASK-0512-The-Gate-Scopes-To-The-Release]]"]
related: ["[[ISS-0206-A-Check-Cannot-Belong-To-A-Release]]", "[[FEAT-0125-The-Release-Page-Reports-What-Holds-It]]"]
tags: [feature]
---

# Choosing what ships

Edwin: *"on the release view I would like to be able to select the features and/or phases to add to a release."*

Today a release's contents are **derived** — *"32 features unshipped since REL-0012"* — or **frozen** at `Mark released`. There is no middle state, which is the state a person preparing a release is actually in: `REL-0013` is `preparing: 2026-08-16` with `features: []` and 32 derived rows.

The field already exists and is already used: `REL-0001` carries 27 `features:` entries. What is missing is a way to put them there other than by hand.

**This is the one item here that is new scope rather than a fix**, and it unlocks the other half of [[FEAT-0125]]: once a release names its features, `blocking_for(subjects)` scopes the gate to them, and *"what holds this release"* stops meaning *"what holds any release"*. It also bears on [[ISS-0206]] — a check that cannot be scoped to a release — without resolving it: choosing features narrows the gate honestly, where inventing a `release:` field on a check would encode something derivable.

## Acceptance

- [ ] A preparing release can add and remove features and phases, written to its note.
- [ ] Adding a phase adds its features, and says so rather than storing a second encoding.
- [ ] With contents named, the gate reports what blocks *this* release.
- [ ] A release with no named contents keeps today's derived behaviour.
