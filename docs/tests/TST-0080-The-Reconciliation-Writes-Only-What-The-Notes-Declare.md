---
type: "[[test]]"
id: TST-0080
aliases: ["TST-0080"]
title: "The backlink reconciliation writes only what the notes declare — it is idempotent, it never invents membership, and removal is reported before it happens"
status: active
covers: ["[[TASK-0580]]"]
owner: user:edwin
created: 2026-08-29
updated: 2026-08-29
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
source: ["[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]"]
scope: system
level: unit
entrypoint: ""
command: ".venv/bin/pytest tests/test_fleet_migration.py -q"
last_verified: ""
issues: ["[[ISS-0209]]"]
tasks: ["[[TASK-0580]]"]
artifacts: []
related: ["[[FEAT-0143]]"]
---

# The reconciliation writes only what the notes declare

Automated, in `tests/test_fleet_migration.py`.

## What it pins

**That the direction is note → feature, and only that direction.** `PARENT-BACKLINK` and `SNAPSHOT-MEMBERSHIP` are one relationship seen from two ends, and [[ADR-0009]] settles which end authors it: the note. The reconciliation reads every task's `parent:` and writes the feature's `tasks:`. A test asserts the reverse never happens — a `tasks:` entry that no task claims is **reported**, never quietly kept and never quietly dropped.

**That a second run is a no-op.** The tool has to be safe to run on a repo somebody already ran it on, because that is what the fifth repo will look like. Idempotence is asserted by running it twice against the same fixture and requiring the second run to report zero writes and leave the bytes identical.

**That a dangling parent is not membership.** A task declaring `parent: FEAT-9999` where no such feature exists must not create an entry, must not crash, and must appear in the report. This is the case where "fix the errors" and "make the validator quiet" come apart.

**That the frontmatter survives the rewrite.** The corpus being edited is 3993 notes across four repos, hand-written over months. A YAML round-trip that reorders keys, drops comments, or reflows a hard-wrapped string is a silent 3993-file diff wearing a one-line change's clothes. The test asserts that reconciling a note whose `tasks:` is already correct changes **no bytes at all**, which is the only formulation that catches a reformatter.

## What it does not pin

It does not assert that the migration makes any particular repo green — that is each migration task's own definition of done, verified by running the validator there. This module tests the operation, on fixtures it owns.
