---
type: "[[task]]"
id: TASK-0225
aliases: ["TASK-0225"]
title: "Design rationale — the ADRs a design links, not all of them"
status: done
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["[[FEAT-0043-Design-Top-Level-Surface]]"]
parent: "[[FEAT-0043-Design-Top-Level-Surface]]"
effort: "S"
depends: ["[[TASK-0223]]"]
blocks: []
related: []
tests: []
---

# Design rationale

## Definition of Done

- [x] The surface lists ADRs reachable from a design note's `related:` / `implements:` links — evidence: `_design_rationale()`; `test_only_the_adrs_a_design_links_appear`
- [x] Governance ADRs that no design links do **not** appear — evidence: same test — ADR-0011 sits in the fixture corpus, accepted and real, and stays out
- [x] Each entry states the decision in one line, and opens the ADR — evidence: `test_the_line_is_the_adrs_own_decision_field`; the line is the ADR's own `decision:` frontmatter, never a paraphrase
- [x] A design linking no ADRs shows nothing rather than an empty section — evidence: `test_a_design_linking_no_adrs_gets_nothing` asserts both the empty payload and the renderer's `return null`

## Steps

- [x] Resolve design → ADR through the existing link graph
- [x] Render the list
- [x] Test that an unlinked governance ADR stays out

## Result

Verified against the real corpus, not only fixtures: DES-0001 links ADR-0006 and DES-0002 links none — exactly what this note predicted before the code existed. `test_the_real_corpus_matches_what_the_task_predicted` asserts it, so the feature is checked against the project it ships in.

**A broken link is reported, not dropped.** `[[ADR-9999]]` renders as "ADR-9999 is linked but no such note exists" rather than vanishing. Omitting it would hide a typo in the note's own frontmatter, and the entire reason resolution goes through the link graph is that links are *checkable* — silently discarding the unresolvable ones would throw that away.

**Never a paraphrase.** The line is the ADR's `decision:` field, falling back to the title and then the bare id. An ADR with neither is listed by id rather than summarised, because a generated summary of a decision is the kind of confident restatement that misleads precisely where accuracy matters.

`implements:` is read before `related:` so the stronger relationship leads, and the list is deduped across both.

A test greps `_design_rationale` for title-matching (`in record.title`, `title.lower()`) and fails if any appears. The heuristic was tried once in the review desk and removed in independent review; a comment saying "resolve by link" would not have stopped it coming back.

## Notes

The filter is the whole task. [[ADR-0006]] (retire the delivered band) is design rationale; ADR-0011 (dated promotion) is process governance. Surfacing every ADR would drag governance into a product surface and bury the two or three that actually explain why something looks the way it does.

Resolution is through the **link graph**, not a title heuristic. An ADR title-substring match was tried once in the review desk and removed in independent review for exactly this reason: it guesses, and a guess that is usually right is worse than an explicit link, because nobody can tell when it is wrong.
