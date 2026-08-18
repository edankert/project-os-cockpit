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

## Independent review

**2026-08-18, `model:claude-opus-5`, fresh context.** The question is a good one and reason 2 is stated correctly. The reading of ADR-0029 is not quite fair, and three things that argue for the characters are missing.

**Reason 1 is a paraphrase of a mechanism, not of the argument.** ADR-0029 does not say "the characters are the storage format". Its stated reason is *"there is a convention and it is not ours"* — Minimal's set is documented and widely used in Obsidian, and *"a mark this project makes up has to be taught in a place nobody reads"*. Rendering was how that convention paid off, and that half has genuinely expired with the document. **The anti-invention half has not.** ADR-0029 opens by counting three vocabularies in two days and rejects a fourth on that record; `verdict: partial` would be the fourth. That is a reason for the characters this note does not weigh. It is a *weakened* reason — no public convention covers a YAML `mark:` scalar, so the interop is gone even if the discipline is not — but it is the ADR's headline, and answering the ADR means answering it.

**The characters cannot be retired, only supplemented.** `acceptance.parse` is annotated *"stays forever"*: `suite_at` reads the document shape at every pre-migration ref, which is all twelve of `your-trainer`'s tags, and the release-gate delta depends on it. The frozen per-release suites are never rewritten by decision — `ACCEPTANCE_TESTS_v2.1.0.md` still holds 268 `[x]`, 25 `[ ]`, 6 `[~]` and 1 `[F]`. So a word vocabulary is **additive**: `_CHECKED_MARKS` … `_QUESTION_MARKS` and `LEGACY_MARKS` survive whatever the live notes carry, and the project ends with two verdict vocabularies rather than one.

**The "against changing it" case is weaker than stated, by this project's own standard of evidence.** Measured across all 669 live acceptance notes: `x` 546, `" "` 122, `/` 1, and **`-`, `!` and `?` written zero times**. The note defends the characters partly on the meanings `-`/`!`/`?` carry that no status word supplies — and none of the three is in use anywhere. That is the same measurement ADR-0029 itself used to justify reversing `[!]`'s meaning ("written in zero suites fleet-wide, verified before deciding"), applied to the survivors.

**"The surfaces already render a label rather than the character" is half true**, and the wrong half for the migration estimate. The filter chips render `MARK_MEANING` words (`passed`, `unwalked`); the row control renders `MARK_GLYPH` — `[x]`, `[/]`, `[-]` — with a comment giving its reason as *"a reader who edits the Markdown by hand has already seen what to type"*. That rationale expires with reason 1 (a hand-editor now types `mark: "x"` in YAML), which **supports** the argument here — but it means the migration is not "669 notes plus the six-value tables": it is `MARK_GLYPH`/`MARK_TITLE`/`MARK_CLASS`, the six-mark dialog, `VERDICTS`/`VERDICTS_NEEDING_REASON`/`MARK_MEANING`/`LEGACY_MARKS`, the five mark frozensets, and the fail-safe that an unrecognised mark blocks — which a word vocabulary has to reproduce or it fails open.

**Verdict: the question stands and reason 2 is correctly analysed; the treatment of ADR-0029 needs the anti-invention argument added and answered, and the cost figures need the parser-stays-forever and zero-usage measurements.**
