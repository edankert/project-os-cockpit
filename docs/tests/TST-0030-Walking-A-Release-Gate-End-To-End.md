---
type: "[[test]]"
id: TST-0030
aliases: ["TST-0030"]
title: "Walking a release gate end to end — declare a release, see its checks, walk a section, and watch the count fall"
status: ready
covers: ["[[FEAT-0103-The-Gate-Is-Walkable]]"]
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0103]] — the criterion that cannot be met from a payload"]
scope: system
level: system
entrypoint: "Publication → Release gate, against a throwaway repo"
command: ""
last_verified: "2026-08-16"
issues: []
tasks: ["[[TASK-0433-The-Acceptance-Walker]]"]
artifacts: []
evidence: []
last_run: "2026-08-16T00:00Z"
adequacy: ""
mutation_score: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TST-0029-The-Walker-Ticks-What-It-Walked]]"]
---

# Walking a release gate end to end

## Purpose

The reported failure was about what a person can see and do, and neither is provable from a payload. This is the walk.

**Against a throwaway repo**, not `your-trainer`: walking real checks would tick real acceptance rows for a real product, which is Edwin's claim to make and not a test's.

## Steps

1. Open Publication in a repo with a suite and no release in preparation. Expect: the gate names its number and says *no release in preparation*, and asks for nobody.
2. Declare a release. Expect: the gate names it — `preparing <version>` — and the obligation appears.
3. Expect the gate to list **individual checks**, not area counts, and its stated number to equal the rows shown.
4. Click a check. Expect: the suite opens **at that section**, not at the top of the file.
5. Start a walk on a section. Expect: one check on screen with its procedure text, and pass / fail / skip offered.
6. Pass one. Expect: the row is ticked in `ACCEPTANCE_TESTS.md` with a dated witness, and the gate's count falls by one on the badge and in the list.
7. Fail one, with a reason. Expect: the row stays unticked and carries what went wrong.
8. Skip one. Expect: nothing written.
9. Abort mid-walk. Expect: what was already recorded stays; nothing else is written.
10. Re-open Publication. Expect: the count reflects exactly what was walked.


## Retired 2026-08-16 — and the vocabulary has no word for it

Superseded with [[TST-0029]]: the end-to-end walk it describes is of a surface that no longer exists. The walk was performed and did pass — that is why this is superseded rather than deleted.

**`status: ready` is the closest honest value the vocabulary allows.** `STATUSES.md` gives a test `ready`, `passing`, `failing` and no terminal state — every other note type has one. `passing` would claim this verifies something that exists; `ready` says defined and not executed, which is true of a test whose subject was deleted. The supersession is carried by this section and by the links, which is what the vocabulary leaves available. Filed as [[ISS-0178]].
