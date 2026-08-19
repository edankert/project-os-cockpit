---
type: "[[plan]]"
title: "Plan — a test says who executes it"
status: draft
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
source: []
implements: ["[[FEAT-0139-The-Suite-Is-The-Verdict]]", "[[FEAT-0140-Sections-Are-Derived-Not-Filed]]", "[[FEAT-0141-The-Contract-Says-It-Upstream]]"]
related: ["[[ADR-0038-The-Suite-Is-The-Verdict]]", "[[ADR-0039-Three-Sections-Derived-Not-Filed]]"]
---

# Plan — a test says who executes it

[[PHASE-039-A-Test-Says-Who-Executes-It]]. Three features, three requirements, seventeen tasks, two decisions.

**Nothing here starts until [[ADR-0038]] and [[ADR-0039]] are accepted.** Both read `proposed`.

## Order, and why

**1. [[FEAT-0141]] — upstream first.** [[TASK-0573]] and [[TASK-0574]] before any code, for the reason [[FEAT-0134]] put its upstream task first: the instruction file is what a fresh agent reads, and a corpus migrated ahead of its contract is a corpus nobody can check. It is also the cheapest leg to reverse.

**2. [[FEAT-0139]] — the verdict.** [[TASK-0559]] (the runner stops writing) is first and independent; it removes the source of new bad data before [[TASK-0562]] cleans the old. Landing the migration first would let the next execution re-stamp what was just stripped.

**3. [[FEAT-0140]] — the sections.** Depends on nothing in 0139 except the vocabulary, but placed after it because [[TASK-0571]]'s gate delta must be measured against a corpus that has stopped moving.

## The three risks, named

- **[[TASK-0571]] is the only task that changes what a release is allowed to do.** `your-trainer` goes from 68 open to 59. Measured per repo before it lands, as every [[PHASE-038]] gate change was.
- **[[TASK-0570]] carries debt that must not grow.** 68 checks cannot name the issue they verify. Grandfathered by ID with a promotion date; the authoring rule is what stops instance 69.
- **[[TASK-0566]] cannot be proved from the corpus.** Zero of 139 commands fail to resolve, so a test over today's data passes whether or not the code works. Constructed input, and the mutant must fail.
