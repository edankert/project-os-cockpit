---
type: "[[task]]"
id: TASK-0242
aliases: ["TASK-0242"]
title: "Reviewed register from note frontmatter — the verdicts that already exist"
status: done
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: []
parent: "[[FEAT-0049-Review-Desk-As-Record]]"
effort: M
depends: []
blocks: []
related: ["[[FEAT-0041-Review-Desk]]", "[[ADR-0009]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
---

# TASK-0242 — Reviewed register

## Definition of Done
- [ ] `review_queue_payload` carries a `registers.reviewed` block sourced from **note frontmatter**
- [ ] Each entry: id, title, type, `review_verdict`, `reviewed_by`, `review_date`
- [ ] Most recent first
- [ ] Rendered under the queue beside the tests register
- [ ] The store's outcome tally is untouched

## Steps
- [ ] Scan the index for notes carrying a **non-empty** `review_verdict` (62 in this corpus)
- [ ] Emit them sorted by `review_date` descending, ties broken by id
- [ ] Renderer: a `Reviewed` section in `renderReviewQueuePane`, below the tests register
- [ ] Test: the register count matches a frontmatter scan, and an item with no `review_date` still lists (sorted last) rather than being dropped

## The empty-verdict case

Some notes declare `review_verdict: ""` — CHG notes and designs that carry the field with no value yet. They must **not** list: an empty verdict is the absence of a verdict, and a register that counted them would overstate how much of the corpus has been reviewed.

**No count is quoted here on purpose.** It was "six … 68 where 62" when this task was written; independent review found 12 at `bed48ea` (because the commit added five, including [[TST-0022]]'s own frontmatter), and 10 a day later once that review stamped verdicts of its own. Every review changes both populations, so any figure written down is stale before it is read. The invariant is what the test asserts: empty is excluded, non-empty is included, and both are counted from the index rather than from a note.

This is the opposite call from the missing-`review_date` case, and the distinction is deliberate. A recorded verdict with no date is a reviewed item with incomplete metadata — worth showing, sorted last. An empty verdict is not a reviewed item at all.

## Notes

Notes, not the store. `resolve()` does retain resolved requests (`review.py:234-236`) so rendering those would be cheaper — but `_MAX_REQUESTS = 200` trims oldest-first on every save (`review.py:91`), so the register would silently lose its tail. Frontmatter has no ceiling and is the authored record per [[ADR-0009]].

The store keeps the outcome counts, which the notes genuinely cannot answer: "accepted-amended" and "changes-requested" are properties of the *review interaction*, not of the note's final verdict. That is the ADR-0007 measurement and it stays where it is.
