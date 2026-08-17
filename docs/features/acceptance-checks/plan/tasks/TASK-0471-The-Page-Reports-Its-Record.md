---
type: "[[task]]"
id: TASK-0471
aliases: ["TASK-0471"]
title: "The release page reports its record — the note reachable, still-owed counted honestly, prose rendered as prose, confidence rolled up"
status: done
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
source: ["[[FEAT-0116-A-Release-Can-Be-Finished]]"]
parent: "[[FEAT-0116-A-Release-Can-Be-Finished]]"
effort: S
depends: []
blocks: []
related: ["[[FEAT-0110-Still-Owed-By-A-Shipped-Release]]"]
tests: []
---

# The page reports its record

Four small reads, three of them storage-independent and ready any time:

- **The note is a row.** `note · docs/releases/REL-0012-v2.1.6.md`, both release pages — the authored record is currently unreachable from the only view about it.
- **Still owed, counted honestly.** REL-0010's heading says 11; the truth is 1 open + 2 done + 8 unknowable. The heading carries the split, open sorts first, age stays.
- **Prose `tests_verified` reads as prose.** 11 of the corpus's 15 entries are recorded claims ("Unit tests: 614 tests, all passing") and render today as broken links — *"not in this corpus"*. A claim renders as a claim.
- **Confidence, rolled up** (needs the migrated fields): of the checks touching what shipped — N automated, M partial, K manual, derived from `automation:`, never authored twice. Edwin asked *"is this a feature stat"* — it is not; it is a check property rolled up.

## Done when

- [ ] All four appear on the appropriate page states, and none invents a number the record does not hold.
