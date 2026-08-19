---
type: "[[task]]"
id: TASK-0544
aliases: ["TASK-0544"]
title: "`evidence` moves to the ledger as a sibling collection, not onto the entry and not onto the note"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0133-The-Ledger-Is-The-Only-Place-A-Verdict-Lives]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# The seventh field has no home, and nothing has said so

[[REQ-0053]] removes seven fields from the note. Six have a destination or a stated reason to disappear. **`evidence:` has neither** — the ledger entry schema in [[TASK-0527]] is `check`, `mark`, `date`, `by`, `method`, `reason`, and evidence is not in it.

This is not a small omission. [[ADR-0030]]'s honest tally of what one-note-per-check bought led with *"per-check evidence attachments"* — it is the first item on the list of things that were **genuinely unlocked** rather than merely improved. Deleting the field without replacing it would give that back.

## Decided 2026-08-19 (Edwin)

*"The entry does not carry evidence, this should be in the ledger."*

**The ledger carries a sibling `evidence` collection**, alongside `entries`, joining by `check` + `date`. Not on the note — a screenshot proves one walk on one platform on one date, and on a permanent check that is the standing claim decision 3 rejects for `automation:`. Not inline on the entry either — an entry is one short line in an append-only file, and evidence is bulky, arrives late, and is often produced once for a session covering several checks.

**Measured first, as this task required: `evidence:` is non-empty on 0 of 671 acceptance notes** across all three repos. It is populated only on *executable* tests, where it holds run output (`"30 passed in 0.75s"`), and those are untouched. The field has never held anything on an acceptance note precisely because a walk's evidence has no home on a permanent check — the same argument [[ADR-0037]] makes about the verdict.

## Definition of Done

- [x] Decided in [[ADR-0037]] decision 1 rather than in a commit.
- [x] Measured per repo before deciding: 0 of 671.
- [x] The ledger schema carries `evidence` as a sibling of `entries`, with `check` and `date` required on each item.
- [x] `ledger.orphan_evidence` reports an item whose `check` + `date` matches no entry — the same guard `cover_check` applies to `covered_by:` ([[ISS-0198]]), and for the same reason: a claim pointing at nothing reads as backed and is not.
- [x] `Item.evidence` (`acceptance.py:358`, read at `:801`) reads the ledger, and the field leaves the note schema with [[TASK-0530]].
- [x] Evidence freezes at the seal with everything else — it is in the same file.

## Completed 2026-08-19

`Item.evidence` is joined out of the ledger's sibling collection, matched on `check` + `date`, so evidence follows the verdict it backs and a different platform gets neither.
