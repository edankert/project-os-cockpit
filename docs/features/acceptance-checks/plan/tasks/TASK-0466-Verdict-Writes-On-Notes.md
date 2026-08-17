---
type: "[[task]]"
id: TASK-0466
aliases: ["TASK-0466"]
title: "Verdict writes on notes — six marks, a dated pass, and Needs re-run naming the change, each one write"
status: done
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
source: ["[[FEAT-0115-The-Sweep-Is-Continuous]]"]
parent: "[[FEAT-0115-The-Sweep-Is-Continuous]]"
effort: M
depends: ["[[TASK-0461-Pilot-This-Repo]]"]
blocks: []
related: ["[[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]]"]
tests: []
---

# Verdict writes on notes

The `mark-check` write path targets frontmatter instead of row grammar: `mark:`, `verdict_date:`, `verdict_reason:` in one write, with the same refusals — a partial, canceled, failed or question without a reason is refused, and a reason citing a note that does not exist is refused before the write.

**Needs re-run** joins the six marks as the seventh action: it clears the mark and writes `invalidated_by:` (change id, reason, date) in the same write, and it is refused without the change id — the discipline `[-]` already has, applied to the invalidation half of TESTING.md rule 3, which the corpus performs by hand 57 times and left ticked 54 of those.

A pass records its date, which makes staleness arithmetic: a check whose `verdict_date:` predates its `invalidated_by:` date is provably stale, and the 60-versus-113 gap stops depending on hand-written annotations.

## Done when

- [ ] Every verdict from both surfaces (view row, gate row) lands in frontmatter with its date; no write path touches row grammar.
- [ ] Needs re-run without a change id is a refusal with the reason shown; with one, mark cleared and `invalidated_by:` written atomically.
- [ ] Stale is computed from the two dates and the hand-annotation path is retired from the payload.
