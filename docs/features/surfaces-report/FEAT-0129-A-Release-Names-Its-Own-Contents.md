---
type: "[[feature]]"
id: FEAT-0129
aliases: ["FEAT-0129"]
title: "A release names its own contents — features and phases are chosen, not only derived — and the gate scopes to them"
status: doing
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
requirements: ["[[REQ-0048-A-Release-Can-Be-Composed]]"]
tasks: ["[[TASK-0511-A-Picker-Writes-Features-And-Phases]]", "[[TASK-0512-The-Gate-Scopes-To-The-Release]]", "[[TASK-0557-One-Release-Per-Platform]]", "[[TASK-0558-A-Release-Composes-Its-Contents]]"]
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
- [ ] **One preparing release per platform**, and two on one platform is an error — the state [[ADR-0037]]'s ledger cannot represent, since sealing assigns one working ledger to one release. *Edwin, 2026-08-19: two concurrent releases on a platform are a branch, not a schema problem.*
- [ ] **A feature in two open releases on the same platform is an error; across platforms it is the normal case.** The obvious version of this rule — any two open releases — is wrong the first time a feature ships to both, which is where it is going ([[ISS-0236]]).

## Independent review — fourth pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`. Verdict: **approved**. Re-measured or re-executed, not read.

All six criteria trace to mechanisms I have now re-executed:

1. add/remove features and phases — `release_contents`, 5 refusal mutants, all caught.
2. a phase contributes rather than stores — mutant caught by three tests.
3. with contents named, the gate reports what blocks *this* release — `blocking_minus` wired through `release_payload`; 59 → 58 when `FEAT-0047` is held back.
4. **no named contents keeps derived behaviour** — the one flagged, and it is the strongest of the six: `blocking_minus(None)` and `blocking_minus(set())` both return exactly `blocking()` (59 on the live corpus), and removing the `if not deselected: return base` short-circuit fails **14** tests, so it is load-bearing rather than a convenience.
5. one preparing release per platform — 3 mutants, all caught.
6. same-platform clash is an error, cross-platform is normal — 2 mutants, caught, including the per-contributed-feature case that names the member rather than the phase.

Status is `doing` with the boxes unticked, which is right — the criteria are met in mechanism, and nothing here ticked itself.
