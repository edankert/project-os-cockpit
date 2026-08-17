---
type: "[[task]]"
id: TASK-0458
aliases: ["TASK-0458"]
title: "Six marks, Minimal's, with `~` and `F` read forever as aliases"
status: done
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin 2026-08-17: 'can we use the commonly used checkbox values like they are defined here https://minimal.guide/checklists together with their styling'", "Edwin 2026-08-17: 'I confirm [!] and [-] for could not run and I would like the other 2 as well please.'"]
parent: "[[FEAT-0104-The-Suite-Is-The-Surface]]"
effort: M
depends: []
blocks: []
related: ["[[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]]", "[[ISS-0141]]"]
tests: []
---

# Six marks, Minimal's

## What

[[ADR-0029]]'s table, implemented: `[ ]` `[x]` `[/]` `[-]` `[!]` `[?]`, with `~` → `/` and `F` → `!` read and never written.

## The two that are not additive

**`[!]` reverses.** It was `excepted` and non-blocking; it becomes `failed` and blocking. Zero rows in the fleet carry one, verified before the decision, so nothing changes meaning underneath anybody.

**`Item.excepted` moves to `[-]`.** The field, the separate count and the payload key all stay — a release exception is still a distinct thing from a partial pass and from a failure. Only the character changes.

## Done when

- [x] all six marks parse, with `~` and `F` as aliases and identical behaviour to their targets
- [x] `[!]` blocks; `[?]` blocks; `[ ]` blocks; `[x]` `[/]` `[-]` clear the gate
- [x] `Item.excepted` is true for `[-]` and false for `[!]`, with its count still reported separately from `reconciled`
- [x] the dialog offers all six with their Minimal names, and refuses every non-pass without a reason
- [x] an unrecognised mark still blocks — the other sixteen Minimal values, and every typo
- [x] the verdict word written for each is the one the corpus already uses where there is one
- [x] `../your-trainer`'s seven legacy rows parse to the same gate outcome before and after
- [x] mutations that must fail: make `[!]` non-blocking again; make `[?]` clear the gate; write an alias instead of its target; drop the reason requirement on `[-]`

## Done 2026-08-17

Six marks, one table, pinned as a table in `test_the_mark_table_is_adr_0029s` — eleven rows including two legacy aliases, one of Minimal's other sixteen and a typo, so a change to any row of the decision is a change to a test rather than a surprise in a release gate.

**Two things the rename exposed, neither of them planned:**

1. **The walker's decision guard covered only `reconciled`.** It refused to overwrite a `~` and happily overwrote a `[-]` — and `[-]` (*could not be run, not holding the release*) is equally somebody's judgement. It was written when `~` was the only decision mark and the rename left the other unprotected. Found by a test that expected the refusal and stopped getting it.
2. **`[-]` was a fixture in `test_a_mark_nobody_recognises_blocks_rather_than_vanishing`** — one of ISS-0141's examples of a typo that must block. It has a meaning now, so `[@]` carries that case and the substitution is commented where a future reader will hit it.

**The treeprocessor stopped carrying its own opinion.** It matched a hard-coded list of five literals; it now matches any single character and lets `acceptance.parse` classify. Sixteen Minimal values and every typo are addressed and blocking, which is what lets a reader see and change them.
