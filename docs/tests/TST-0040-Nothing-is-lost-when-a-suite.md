---
type: "[[test]]"
id: TST-0040
aliases: ["TST-0040"]
title: "Nothing is lost when a suite becomes notes — parity, both annotation positions, and two shapes at their own refs"
status: passing
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
last_verified: 2026-08-17
last_run: 2026-08-17
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
scope: feature
verifies: ["[[FEAT-0113-The-Check-Type-And-The-Migration]]"]
automated: true
command: ".venv/bin/pytest tests/test_check_migration.py -q"
requirements: []
related: ["[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]"]
---

# Nothing is lost when a suite becomes notes

Automated, in `tests/test_check_migration.py`.

The migration's only real risk is a silent one. [[ISS-0175]] is this project's record of what assuming costs: a mapping that "obviously" held drifted by 37 rows on the one corpus it ran against.

## What it pins

**That every row survives with its verdict**, compared pairwise through the real reader after the real script has run — not by trusting the script's own "parity OK".

**That the blocking number does not move** across the cut, asserted in its own right rather than inferred from the rows.

**That legacy marks normalise without changing a verdict.** `~` → `/` and `F` → `!` are spelling changes; the classification is asserted beside them.

**That `RE-RUN (…)` becomes a field from BOTH positions the fleet writes.** 28 of the 54 end the line and 26 sit mid-sentence; handling only the first would leave 26 checks carrying the annotation twice.

**That a check nobody can classify BLOCKS.** Added after a mutation setting the fallback to Tier 3 survived the entire suite — dropping the row and defaulting it to Tier 3 are the same failure, and the first implementation did the first while its comment warned about the second.

**That the source is deleted only after parity is green**, driven by breaking the writer rather than by trusting statement order.

**That `suite_at` reads file-shape at a pre-migration tag and note-shape after**, in two subprocesses rather than N.

## Adequacy

Seven mutations run against this module; all killed. The two that survived first — the tier fallback and the parity-before-delete ordering — are named above.

## Amended 2026-08-17 — the guard that was missing

`test_a_ref_read_survives_non_ascii_prose` was added after the note-shape ref read shipped a defect this module did not catch: `git cat-file --batch` sizes are **bytes** and the walk sliced characters, so `../your-trainer` read back **314 of 579** checks with no error and the gate would have under-reported at every post-migration ref.

Adequacy: the guard fails against the shipped implementation and **the other sixteen tests here pass against it**, which is the measurement that matters — the module was comprehensively blind to the one thing that could quietly shrink a release gate.
