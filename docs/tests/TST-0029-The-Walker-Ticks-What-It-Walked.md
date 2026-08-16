---
type: "[[test]]"
id: TST-0029
aliases: ["TST-0029"]
title: "The walker ticks what it walked and nothing else — pass writes a witness, fail stays unticked, skip writes nothing, and a stale or reconciled row is refused"
status: passing
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0103]] acceptance criteria"]
scope: system
kind: automated
level: integration
entrypoint: ""
command: ".venv/bin/pytest tests/test_acceptance_walker.py -q"
last_verified: ""
requirements: []
features: ["[[FEAT-0103-The-Gate-Is-Walkable]]"]
issues: []
tasks: ["[[TASK-0430-The-Suite-Is-Addressable]]", "[[TASK-0431-Declare-The-Next-Release]]", "[[TASK-0432-The-Gate-Lists-Its-Checks]]", "[[TASK-0433-The-Acceptance-Walker]]"]
artifacts: []
evidence: []
last_run: "2026-08-16T00:00Z"
exit_code: 0
adequacy: ""
mutation_score: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[ISS-0141]]", "[[ADR-0028-Work-Has-Three-Phases]]"]
---

# The walker ticks what it walked

## Purpose

A walker that writes the wrong row is worse than one that writes nothing, and a walker that ticks on failure manufactures the claim the suite exists to make. Both are silent. This pins the write.

## Procedure

1. A pass ticks the addressed row and appends a dated witness naming the actor.
2. A fail leaves the row `- [ ]` and records what went wrong.
3. A skip writes nothing at all — no tick, no annotation.
4. Address is section-and-ordinal. Editing a row **above** the target does not move which row is written.
5. The name is carried and compared: if the row at that address is not the row the caller named, the write is refused.
6. A `- [~]` reconciled row is refused. Settled by decision is not walked ([[ISS-0141]]).
7. A stale `mtime` is refused, as every other `note_writes` path refuses one.
8. Round-trip: parse, walk one check, re-parse — the unchecked count drops by exactly one.
9. Declaring a release creates `REL-*` at `draft`; a version at or below the newest `released` is refused; a second declaration while one is in preparation is refused.
10. With a release in preparation the gate names it and the obligation fires; with none it is zero.
11. The gate lists the individual checks and the number it states equals the rows it lists.
12. **The badge is still one, never sixty** — the bound `TST-0028` asserts, re-asserted here after the list lands.
13. Every new write route is loopback-only and enumerated.

## Notes

Step 4 is the one worth mutation-testing hardest: a global-index implementation passes every other step here and fails only this one, silently and against a real corpus.
