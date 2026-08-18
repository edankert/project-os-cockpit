---
type: "[[issue]]"
id: ISS-0200
aliases: ["ISS-0200"]
title: "Why are acceptance verdicts six terse characters rather than more status values? The reasoning is recorded but it was never tested against the alternative it dismisses"
status: triage
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: medium
component: docs
phase: "[[PHASE-999-Future]]"
related: ["[[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]]", "[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[TESTING-MODEL]]"]
---

# Marks versus statuses

Edwin, 2026-08-18: *"The status vs marks, why would we use those terse characters to identify these marks and why not simply add more states to status?"*

## What the record says today

`mark:` is one of `" "`, `x`, `/`, `-`, `!`, `?` — [Minimal's alternate checkbox vocabulary](https://minimal.guide/checklists), adopted by [[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]]. Two reasons are on the record:

1. **The characters were the storage format.** When the suite was one Markdown document, a check *was* a `- [x]` line, and the mark was the character inside the brackets. Obsidian renders them; a person editing the file saw exactly what the parser saw.
2. **`mark` is not `status`.** [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] leans on this hard: a walk writes `mark:` and never `status:`, which is what keeps a suite of several hundred rows out of the review gate, the runner-only rule and the `Run` obligation *by construction*. If the verdict were a status, all three would have to be taught to ignore it.

## Why the question is a good one

**Reason 1 expired.** The document is gone — [[ADR-0030]] deleted it and [[ADR-0031]] moved the notes onto the test type. Nothing renders `- [x]` any more; the mark is a YAML scalar in frontmatter that a person reads as `mark: "/"` and has to look up. The vocabulary outlived the format that made it legible.

**Reason 2 is real but it is an argument for a separate FIELD, not for terse characters.** `verdict: partial` would keep every property the construction needs — it is still not `status:`, so all three gates still miss it — while being readable without a table. The two reasons have been carried together as though they were one, and only the second still holds.

**Against changing it**, honestly: 669 notes carry these characters; `ADR-0008` collapsed the status vocabulary from 64 values to 53 by measurement and adding six more would be a real reversal; and `-`/`!`/`?` genuinely do carry meanings no status word obviously supplies (*shipped undone*, *walked and failed*, *the check itself is unclear*).

## What would settle it

- [ ] Decide whether the verdict stays a character or becomes a word in the same field. **Not** whether it becomes a `status:` — that part of ADR-0031 is load-bearing and is not in question.
- [ ] If it becomes a word, it is a mechanical migration of 669 notes plus the six-value tables, and the surfaces already render a label (`passed`, `unwalked`) rather than the character.
