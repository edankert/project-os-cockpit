---
type: "[[task]]"
id: TASK-0532
aliases: ["TASK-0532"]
title: "Fix the physical-line splitter and repair the six truncated notes, before any repo migrates again"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0134-The-Note-Sheds-The-Verdict]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# The splitter

[[ISS-0216]]. `acceptance.parse` (`src/project_os_cockpit/acceptance.py:579`) matches `_ITEM_RE` per physical line and drops anything that does not match, with no report. A hard-wrapped bullet loses everything after its first line.

## Definition of Done

- [x] A non-matching, indented line following an item appends to that item's text.
- [x] Unclassifiable lines are counted and reported, never dropped silently.
- [x] Proved on a hard-wrapped fixture, both in `parse` and through `migrate-acceptance-checks.py`.
- [x] `your-trainer`'s `TST-0592`..`TST-0597` are repaired from the directory README's verbatim prose, each recording its source.

## Done 2026-08-19

**The row is held open and closed by what follows it.** `parse()` no longer builds an item from its first physical line; it accumulates the row and builds at the close, so the join happens **before** `_NAME_RE` runs. That last detail is not incidental — a cheaper fix that appended continuations to the already-parsed `detail` leaves a wrapped `**bold name**` nameless, and the mutant proving it is in `tests/test_row_wrapping.py`.

**Three rules, each measured against the corpus rather than assumed.** A continuation is *indented*, *non-blank* and *not itself a bullet*. The pre-migration file carries **23 unindented `- *… moved to §3.5*` annotation bullets directly under checkboxes** — accepting Markdown's lazy wrap would have folded every one into the check above it, inventing procedure steps out of cross-references. A blank line, a heading, a fence or the next bullet closes the row.

**The one ambiguous shape is reported, not guessed.** An unindented non-bullet line under a checkbox is what Markdown calls a lazy continuation; `parse(text, report=…)` names it and `migrate-acceptance-checks.py` prints it before applying. Ordinary section prose is deliberately **not** reported — a report nobody can act on is one people learn to skip.

**Eleven tests, mutation-proven against three plausible wrong fixes**: dropping continuations (3 fail), accepting lazy wraps (1 fails), joining after `_NAME_RE` instead of before (1 fails).

## The six notes are repaired, and not committed

All six recovered from `docs/tests/acceptance/README.md`, which is the only surviving copy — the source document was **uncommitted at the migration sha**, so git does not have it. Recovery ran through the *fixed* parser and each recovered body was asserted to start with the truncated text, so the match is proved rather than eyeballed. `TST-0596` went from 4 characters to 254.

**Left uncommitted in `your-trainer` deliberately.** That repo carries 58 modified files belonging to work in flight, and its validator is ~690 lines behind upstream ([[ISS-0209]]). Committing there would entangle this repair with somebody else's afternoon and run it past a gate that cannot check it. Each note records where its body came from.

## Notes

`TST-0596-Chrome-Reachable-From-Every-Pre-Ride.md` is titled *"Chrome reachable from every pre-ride screen"* and its entire body is the word `From`.

The full text survived only because `build_readme` copies the source document's prose verbatim into the checks directory. That is luck, not design, and it is not a recovery path any tool can take — a person has to read both.
