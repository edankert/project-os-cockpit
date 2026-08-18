---
type: "[[task]]"
id: TASK-0485
aliases: ["TASK-0485"]
title: "Backfill `automation:` and `covered_by:` from the 203 bodies that already name their covering test"
status: backlog
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0120-The-Automation-Path]]"]
parent: "[[FEAT-0120-The-Automation-Path]]"
effort: M
depends: ["[[TASK-0483-The-Covered-By-Action]]"]
blocks: []
related: []
tests: []
---

# Backfill automation from the prose

**203 of `your-trainer`'s 579 bodies carry the migration's parenthesised annotation** — 181 `(partially automated`, 22 `(automated`, zero `(fully automated` — and 221 mention automation at all, while `automation:` reads `manual` on 669 of 669 and `covered_by:` is `[]` on 669 of 669. The fact is in the corpus and in the wrong place; ADR-0030 defined the fields and the migration copied the annotation as text.

The annotations name real classes — `LicensingManagerTest`, `RiderCardTest`, `TrainerCompatibilityTestFailureModesTest`. **Those are JVM test classes, not `TST-*` ids**, so the backfill cannot simply write `covered_by:` and stop: either the class name is recorded in a form the gate can check, or a `TST-*` note is created for the class and named. Decide that before writing 203 notes, because the wrong choice is 203 notes of plausible-looking data the gate cannot use.

**Report what it could not resolve.** A backfill that silently skips is indistinguishable from one that found nothing.

Done when: every resolvable annotation is a field, the unresolvable ones are listed rather than skipped, and the blocking count on `your-trainer` is re-measured — 15 of its 60 blocking checks claim automation in prose today.
