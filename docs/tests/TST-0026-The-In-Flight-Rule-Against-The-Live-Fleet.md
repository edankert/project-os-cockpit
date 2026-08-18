---
type: "[[test]]"
id: TST-0026
aliases: ["TST-0026"]
title: "The in-flight rule against the live fleet — the 64 to 31 claim is measured on the real corpus, and a repo with no phases routes correctly"
status: passing
covers: ["[[FEAT-0101-Obligations-Route-By-The-State-Of-Their-Subject]]"]
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0101]] acceptance criteria — the numbers are claims about twelve real repos"]
scope: system
level: system
entrypoint: "the discovered fleet under ~/Dev/repos"
command: ""
last_verified: "2026-08-16"
issues: []
tasks: ["[[TASK-0424-The-In-Flight-Predicate]]"]
artifacts: []
evidence: []
last_run: "2026-08-16T00:00Z"
adequacy: ""
mutation_score: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TST-0025-Obligation-Routing-Is-Per-Item-And-Complete]]", "[[ADR-0028-Work-Has-Three-Phases]]"]
---

# The in-flight rule against the live fleet

## Purpose

[[FEAT-0101]]'s central claim is a number: `your-trainer` goes from 64 owed to 31. That is a statement about a real corpus and cannot be verified by a fixture. This walks it.

Manual because the subject is twelve repositories on Edwin's disk whose contents change daily. Its value is the comparison, not a fixed expected number — a claim that has drifted is re-measured, not re-asserted.

## Steps

1. Record the baseline before the change: for `your-trainer`, the badge total and its breakdown by kind. Expect: 64 total — 26 requirement, 22 issue, 15 test, 1 unpushed commit.
2. Apply the change and re-read the same payload. Expect: 31 total — 3 requirement, 22 issue, 5 test, 1 unpushed commit.
3. Confirm the issue count is **identical** across steps 1 and 2. Expect: 22 both times — the rule must not touch triage.
4. Expand the suppressed line and count its rows. Expect: exactly 33, and the line's stated count equals the rows it expands to.
5. Confirm every suppressed row is reachable in one click and shows its subject and that subject's status.
6. Read the same payload for each of the three repos with no `PHASE-*` notes — `edankert.com`, `obsidian-supernote-sync`, `project-os`. Expect: routing succeeds, no code path requires a phase, and no empty or invented phase label appears in the suppressed line.
7. Read it for the remaining repos and record each before/after total. Expect: no repo's total **rises**.
8. Confirm the badge, the landing page, the digest and the fleet card agree for `your-trainer` after the change. Expect: one number in four places.

## Notes

Step 7 is the phase's stated bar: *"it must not make the number bigger."* A repo whose total rises is a finding regardless of what else improved.

Step 8 exists because this feature touches the one property the registry was built to guarantee. Four surfaces read one walk, and per-item routing is precisely the kind of change that could give one of them a different answer without anything failing.
