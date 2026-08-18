---
type: "[[test]]"
id: TST-0027
aliases: ["TST-0027"]
title: "The ladder is non-empty in every repo — every rung a repo reaches is present, every rung it cannot is absent, and an unknown count is never a zero"
status: passing
covers: ["[[FEAT-0102-Publication-Becomes-A-View]]"]
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0102]] acceptance criteria"]
scope: system
level: integration
entrypoint: ""
command: ".venv/bin/pytest tests/test_publication_ladder.py -q"
last_verified: ""
issues: []
tasks: ["[[TASK-0426-The-Ladder-As-Data]]", "[[TASK-0427-The-Publication-View]]", "[[TASK-0428-The-Release-Rung]]"]
artifacts: []
evidence: []
last_run: "2026-08-16T00:00Z"
exit_code: 0
adequacy: ""
mutation_score: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[ADR-0028-Work-Has-Three-Phases]]", "[[FEAT-0100-Unpushed-Work-Needs-A-Person]]"]
---

# The ladder is non-empty in every repo

## Purpose

The Publication view's whole justification over a `Releases` view is that it is never empty: a `Releases` mode would be blank in 9 of 12 repos, and the ladder is universal. That claim is a property of the payload and is asserted here.

Hybrid: the four shapes are pinned on fixture repos, because they must hold whatever the fleet looks like next month; the non-emptiness sweep runs across the discovered fleet, because that is the claim.

## Procedure

**The four shapes, on fixtures.**

1. Backup remote, 0 ahead. Expect: push rung present and clear.
2. No remote at all. Expect: push rung **absent**, not present-at-zero. Repo still reaches rung 1 and the view reads as complete.
3. Deploy remote, no upstream, `ahead is None`. Expect: one row saying the count cannot be taken. Never a zero, on this payload or any surface reading it.
4. Deploy remote with commits. Expect: counted, named, reason present as data, and **no action offered**.
5. No `REL-*` notes and no tags. Expect: release rung reported unreached, not as an empty list.
6. A `draft` release and a `released` one. Expect: distinguishable in the payload.
7. A tag with no release note, and a note with no tag. Expect: both shown as themselves.
8. Unreadable git dir / detached HEAD / no tags. Expect: the repo yields what it can and does not raise; one bad repo must not take the fleet pass down.

**The sweep, across the discovered fleet.**

9. For every repo under `~/Dev/repos` carrying a `SNAPSHOT.yaml`: the ladder payload is non-empty. Expect: 12 of 12.
10. Rung coverage matches the measurement: 12 reach commit, 8 push, 2 deploy, 3 release. Expect: agreement, or a recorded reason the fleet moved.
11. No route reachable from the Publication view can push a deploy remote. Expect: enumerated and refused, the same way `test_every_note_mutating_endpoint_requires_loopback` enumerates.

## Notes

Step 3 is the one with history. `ahead is None` was coerced to zero on two renderer surfaces after the first repair fixed only Python, and all three surfaces silently reported nothing owed against a real repo with a real remote. It is asserted on the payload **and** on what the view renders.

Step 9 must fail if a repo yields an empty ladder, not skip it. A sweep that quietly skips the repo it cannot read is how "non-empty in every repo" becomes true of the repos it looked at.
