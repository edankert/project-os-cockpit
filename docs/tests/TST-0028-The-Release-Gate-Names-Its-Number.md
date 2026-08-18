---
type: "[[test]]"
id: TST-0028
aliases: ["TST-0028"]
title: "The release gate names its number and stays one obligation — 60 is stated, never summed, and it asks only while a release is `draft`"
status: passing
covers: ["[[FEAT-0102-Publication-Becomes-A-View]]"]
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0102]] acceptance criteria", "Edwin 2026-08-16: 'I am also afraid that this could overwhelm my attention'"]
scope: system
level: integration
entrypoint: ""
command: ".venv/bin/pytest tests/test_release_gate_campaign.py -q"
last_verified: ""
issues: ["[[ISS-0173-The-Suites-Own-Ids-Are-Written-In-A-Form-Nothing-Reads]]"]
tasks: ["[[TASK-0429-The-Gate-Is-A-Campaign]]"]
artifacts: []
evidence: []
last_run: "2026-08-16T00:00Z"
exit_code: 0
adequacy: ""
mutation_score: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[ADR-0028-Work-Has-Three-Phases]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ISS-0141]]"]
---

# The release gate names its number

## Purpose

The gate is the whole reason [[PHASE-034]] exists, and it is the thing most likely to be rebuilt into the wall it replaced. This pins both halves: it must **state** 60, and it must never **sum** to 60.

## Procedure

1. A repo with a `draft` release and unchecked Tier 1/2 rows. Expect: the gate contributes exactly **one** obligation.
2. The same repo with the release `released`. Expect: **zero** obligations. The rows still render on the rung; they ask for nothing.
3. No release note at all, unchecked rows present. Expect: zero obligations, rows visible.
4. The badge total, digest and fleet card for that repo. Expect: each rises by at most **1** between steps 2 and 1 — never by 60. Asserted as a bound, not a spot value, so a future kind cannot slip 60 in behind it.
5. The gate surface states the unchecked count directly. Expect: the number `60` present as a number, not `306/347` requiring subtraction.
6. Rows group by environment read from the suite's own table. Expect: grouping present; a suite without such a table groups by section and says which it used.
7. Tier 3 present and non-gating.
8. A `- [~]` reconciled row: counted and named, never folded into `checked`. The denominator is what the document holds.
9. A repo with no suite. Expect: *never instantiated*, and **not** *nothing blocking*.
10. A row opens the suite at its section.
11. The gate's rule sentence is the contract's words as shipped by the server, with the local reconciliation clause beside rather than folded into it.
12. With [[ISS-0173]] landed: a section heading naming ids in bare form resolves them, and a heading naming an id inside prose does not become a false ref.

## Notes

Step 4 is the guard against this feature's own worst outcome. The first proposal would have taken `your-trainer`'s card from 64 to 124 in answer to a complaint about noise; a bound rather than an equality means the assertion still bites if someone later routes the rows individually.

Step 9 restores a distinction `gate_payload` reports and a surface can easily lose. Every repo had no suite until 2026-08-10, and a gate reading *nothing blocking* is exactly what made it look like it worked for the years it could not fire.
