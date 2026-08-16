---
type: "[[plan]]"
title: "Plan — FEAT-0102 Publication becomes a view"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
source: []
implements: ["[[FEAT-0102-Publication-Becomes-A-View]]"]
related: ["[[ADR-0028-Work-Has-Three-Phases]]", "[[ISS-0173-The-Suites-Own-Ids-Are-Written-In-A-Form-Nothing-Reads]]", "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"]
---

# Plan — FEAT-0102 Publication becomes a view

## Delivery sequence

1. **[[TASK-0426]] — the ladder as data.** One payload, every rung, every repo. **First**, because the view's whole claim is that it is never empty, and that is a property of the data across twelve repos rather than of a renderer. Provable before anything is drawn.
2. **[[TASK-0427]] — the view.** The nav mode over that payload, with `~history` re-homed inside it rather than replaced.
3. **[[TASK-0428]] — the release rung.** `REL-*` notes and tags, which nothing reads today. Independent of 4 and can land alone: three repos gain a rung, nine correctly show it unreached.
4. **[[TASK-0429]] — the gate as a campaign.** The acceptance suite attached to the release rung, one obligation when a release is `draft` and zero otherwise.

4 needs 3 — the gate hangs on a rung that must exist first. 2 needs 1. 3 needs 1 and can run beside 2.

## Dependencies

[[ADR-0028]] accepted. [[ISS-0173]] should land before 4: without it every blocking row resolves to zero refs, and the gate would be designed against a corpus where no row can name its subject.

[[FEAT-0101]] is **not** a hard dependency, but the two meet at [[TASK-0429]] — a test's subject gains a second kind (a release) once this lands, which is why [[TASK-0424]]'s predicate takes a subject rather than a feature.

## The measurements this feature stands on

Taken 2026-08-16 across all twelve discovered repos. They are claims about the world, and if they have drifted by the time this is built, the design is re-checked rather than the numbers re-stated:

- rung coverage: commit 12/12, push 8, deploy 2, versioned release 3
- live: 7 unpushed commits across 4 repos; your-applications.com 34 undeployed; your-trainer 11 `REL-*` + 12 tags
- your-trainer's gate: 60 unchecked Tier 1/2 in 17 sections, top two carrying 33
- `edankert.com` — deploy remote, no upstream, `ahead is None`: the rung is reachable and its count is unknown, which must render as a row and not a zero

## How this is verified

[[TST-0027]] walks the ladder across every discovered repo and asserts non-emptiness and correct degradation — the claim that cannot be made from fixtures. [[TST-0028]] asserts the gate names its number, contributes one obligation while a release is `draft` and none otherwise, and that no path from this view can push a deploy remote.
