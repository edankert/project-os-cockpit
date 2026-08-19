---
type: "[[issue]]"
id: ISS-0218
aliases: ["ISS-0218"]
title: "`TAXONOMY.md` documents the single-character mark vocabulary in every repo including upstream, three weeks after ADR-0034 moved all 671 notes to words — and the reader silently accepts both"
status: fixed
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: medium
component: docs
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
related: ["[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]]", "[[ISS-0200-Marks-Versus-Statuses]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[FEAT-0137-One-Outcome-Vocabulary-Written-Down-Once]]"]
---

# The vocabulary document says characters; the corpus says words

## Problem

[[ADR-0034-Three-Axes-Not-One-Word]] decision 5 replaced the single-character mark vocabulary with words on 2026-08-18 and migrated the corpus. **`TAXONOMY.md` was never updated, in any repo.**

Measured 2026-08-19 — `tools/instructions/TAXONOMY.md` in `project-os-cockpit`, `your-trainer`, `your-sudoku` and upstream `project-os` all still carry:

> The verdict on an acceptance test — **one character**, Minimal's alternate checkbox vocabulary …
>
> | `" "` | `x` | `/` | `-` | `!` | `?` |

Against a corpus of 671 acceptance notes whose live values are `done` (546), `todo` (124) and `incomplete` (1). **Not one note in the fleet carries a character.**

## Why it does not fail anything

`acceptance.py` accepts both — `_CHECKED_MARKS = {"done", "x", "X"}`, and `LEGACY_MARKS` maps the characters forward. That tolerance is correct and deliberate (a suite mid-migration must keep working), and it is exactly why nothing has fired: **the drift is invisible to every gate**, so only a person reading the document finds it, and what they find is wrong.

## The count that matters

There are now **four** vocabularies in play, not the three the [[ADR-0037]] source proposal names:

1. Minimal's characters — `TAXONOMY.md`, all four repos, documented as current.
2. The words — [[ADR-0034]], live in all 671 notes.
3. The words the reader also accepts but nothing writes — `canceled`, `important`, `question`, `rerun`: **0 occurrences each, fleet-wide**.
4. The event marks [[ADR-0037]] proposes — `pass` / `partial` / `na` / `excused` / `blocked` / `fail` / `question`.

The mapping is not clean and the source proposal is right about that. Two values it lists cannot absorb what the old vocabulary held, and [[ADR-0037]] decision 6 widens it twice rather than dropping either by omission:

- **`?` (question) has no home in the five values the proposal lists.** Kept as a seventh: `fail` says the behaviour is wrong, `question` says the *check* is wrong.
- **`-` (canceled) is carrying two meanings**, which is what Edwin's question on 2026-08-19 exposed — *unable to test* and *not tested this cycle* are different claims about a release, and today only the first is expressible. It splits into `na` (persists) and `excused` (expires when its ledger seals).

## Expected

One vocabulary, defined in one document, and the document matches the data. Legacy values stay **readable** — that is what let the last two migrations land — but they are not what the document presents as current.

## Next actions

- [x] Rewrite `TAXONOMY.md`'s `mark` section upstream first ([[ADR-0030]] decision 6), then sync down.
- [x] Add a check that reads the documented vocabulary and the corpus and fails when a live value is undocumented — the drift is invisible to every gate today, and that is the actual defect.
- [x] Settle values 3 and 4 in one pass under [[FEAT-0137-One-Outcome-Vocabulary-Written-Down-Once]] rather than leaving a fifth behind.

## Fixed 2026-08-19

`TAXONOMY.md`'s vocabulary section is the ledger's, in **all four repos** — upstream `project-os@ce789d7` first, then this repo and both fleet repos. Seven values with a gate column *and* a survives-the-seal column, absence documented as a state rather than a value, and both legacy vocabularies under a heading that says they are read and never written.

**The drift check is the half that matters**, and it is what this issue was really about: the old table failed nothing for three weeks because `acceptance.py` accepts both forms — correctly, since a suite mid-migration must keep working. Tolerance in the reader plus silence in the gate is what produced it.

`test_taxonomy_documents_exactly_the_vocabulary_the_code_writes` reads the table's values **and both behaviour columns** against `ledger.MARKS`. Mutation-proven three ways: deleting a row fails it, flipping a gate column fails it, and flipping the persistence column — the exact inversion [[ADR-0037]] calls its sharpest argument, which the first version of the check let through — fails it.

The fourth vocabulary this issue counted is now the only one that is current; the other three are legacy, and the reader still accepts them.
