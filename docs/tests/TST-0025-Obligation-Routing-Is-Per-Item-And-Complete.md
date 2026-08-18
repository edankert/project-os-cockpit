---
type: "[[test]]"
id: TST-0025
aliases: ["TST-0025"]
title: "Obligation routing is per-item and complete — an unrouted kind fails, the in-flight rule behaves on constructed subjects, and `deferred` beats the rule in both directions"
status: passing
covers: ["[[FEAT-0101-Obligations-Route-By-The-State-Of-Their-Subject]]"]
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0101]] acceptance criteria"]
scope: system
kind: automated
level: unit
entrypoint: ""
command: ".venv/bin/pytest tests/test_obligation_routing.py -q"
last_verified: ""
issues: []
tasks: ["[[TASK-0423-An-Obligations-View-Is-Decided-Per-Item]]", "[[TASK-0424-The-In-Flight-Predicate]]", "[[TASK-0425-The-Quiet-Is-On-Screen]]"]
artifacts: []
evidence: []
last_run: "2026-08-16T00:00Z"
exit_code: 0
adequacy: ""
mutation_score: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[ADR-0028-Work-Has-Three-Phases]]"]
---

# Obligation routing is per-item and complete

## Purpose

Guards [[FEAT-0101]] against the two ways it can fail silently: a kind that routes nowhere and is therefore counted nowhere, and an in-flight rule that quiets more than it was asked to.

Constructed fixtures, deliberately — the fleet measurement is [[TST-0026]]'s job. These are the cases that must hold regardless of what any repo happens to contain today.

## Procedure

1. Every note type reachable in the corpus, and every note-less source, has a routing rule. A type with none fails — the completeness burden the registry already carries for undeclared types.
2. `counts_by_kind` is derived from the same walk as `owed_items`; the existing one-computation assertion still passes.
3. A requirement whose `implements:` feature is `doing` counts. Expect: owed.
4. The same requirement with its feature at `backlog`. Expect: not owed.
5. The same at `done`, `cancelled`, `superseded`. Expect: not owed.
6. A requirement naming two features, one `backlog` and one `doing`. Expect: owed — any subject in flight is enough.
7. A requirement at `deferred` whose feature is `doing`. Expect: **not** owed. The decision beats the default.
8. A manual test at `ready` verifying a `doing` feature. Expect: owed.
9. The same verifying only `done` features. Expect: not owed.
10. A manual test naming **no** subject at all. Expect: **owed** — nothing can prove a subject-less obligation is resting, and this is the direction that fails safely.
11. A subject at a status in neither the in-flight nor the resting list. Expect: owed, and the comment naming that choice is present.
12. An issue at `triage`. Expect: owed, unchanged by everything above.
13. A row suppressed by the rule appears in the suppressed line's payload and **not** in the badge, the digest or the fleet card; the line's stated count equals the number of rows it expands to.
14. The suppressed line is absent when nothing is suppressed.
15. A test whose subject is a release is **still listed in the Tests navigator**, and its obligation row appears under Publication. Expect: present in both. Routing moves the row, never the note — [[ADR-0025]]'s shortcut rather than a relocation.

## Notes

Steps 10 and 11 are the ones worth mutation-testing hardest. Both are cases where a plausible implementation silently quiets something, and neither shows up as a failure — only as a smaller number, which is what this whole feature is trying to produce.

Mutations are chosen by trying to defeat each guard, not by picking the one that was in mind while writing it. [[ISS-0171]] is what the other habit costs: two guards stayed green under the exact regression they named, after being mutation-tested.
