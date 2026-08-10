---
type: "[[task]]"
id: TASK-0279
aliases: ["TASK-0279"]
title: "Ticking a criterion rewrites one line, in the validator's own shapes, with a witness"
status: done
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0059-The-Write-Service-Widens]]"]
parent: "[[FEAT-0059-The-Write-Service-Widens]]"
effort: M
depends: ["[[TASK-0278-The-Transition-Table-As-Data]]"]
blocks: []
related: ["[[REQ-0028-Evidence-Names-Its-Witness]]"]
tests: []
---

# The tick path

## Definition of Done

- [x] `POST /api/notes/tick`: locates the criterion by exact text within the criteria section, rewrites that line only.
- [x] Both forms: `- [x] … — evidence: <text> (user:…, date)` and `- [~] … — <reason>`, matching what REQ-BOXES/PHASE-BOXES parse — proven by running the real validator over a ticked fixture.
- [x] mtime precondition: a note edited since render refuses the tick loudly.
- [x] Ambiguous or missing criterion text is a 4xx; nothing is written.

## Done 2026-08-10

`stamp_tick` in `note_writes.py`, `POST /api/notes/tick` behind the same loopback check, allow-list and mtime precondition as every other write.

**The shapes are format strings, not literals.** `TICK_TEMPLATE` and `RECONCILE_TEMPLATE` sit beside each other so the writer and the validator cannot drift into disagreeing about a line only one of them produces.

**Proven against the real validator, per the DoD** — not against a hand-written regex. `test_a_tick_writes_the_shape_the_real_validator_parses` imports `validate_docs_bundled`, writes a tick, then asserts `CHECKED_RE` matches it *and* that `count_acceptance_boxes` counts it. A tick the validator cannot read is worse than no tick: it looks resolved and does not count toward REQ-BOXES.

**Ambiguity refuses rather than guesses.** Two criteria with identical prose is not a case to pick between — the mtime guard makes a *stale* match impossible to apply, and an ambiguous one would make a *wrong* match easy to apply. The refusal names the count.

**Indentation survives.** A nested criterion stays nested: the line's leading whitespace is preserved and exactly one line changes, asserted.
