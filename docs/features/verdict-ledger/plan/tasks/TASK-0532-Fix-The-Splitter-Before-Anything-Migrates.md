---
type: "[[task]]"
id: TASK-0532
aliases: ["TASK-0532"]
title: "Fix the physical-line splitter and repair the six truncated notes, before any repo migrates again"
status: backlog
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

- [ ] A non-matching, indented line following an item appends to that item's text.
- [ ] Unclassifiable lines are counted and reported, never dropped silently.
- [ ] Proved on a hard-wrapped fixture, both in `parse` and through `migrate-acceptance-checks.py`.
- [ ] `your-trainer`'s `TST-0592`..`TST-0597` are repaired from the directory README's verbatim prose, one at a time, each recording its source address.

## Notes

`TST-0596-Chrome-Reachable-From-Every-Pre-Ride.md` is titled *"Chrome reachable from every pre-ride screen"* and its entire body is the word `From`.

The full text survived only because `build_readme` copies the source document's prose verbatim into the checks directory. That is luck, not design, and it is not a recovery path any tool can take — a person has to read both.
