---
type: "[[task]]"
id: TASK-0567
aliases: ["TASK-0567"]
title: "The left pane: six sections, `Needs you` first"
status: done
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
source: []
parent: "[[FEAT-0140-Sections-Are-Derived-Not-Filed]]"
effort: "M"
due: ""
depends: []
blocks: []
related: []
tests: []
---

# The left pane: six sections, `Needs you` first

## Definition of Done
- [ ] Sections are `Needs you`, Feature tests, Regression tests, Automated tests, `Broken command`, Retired
- [ ] Empty sections are absent
- [ ] `Needs you` matches the shared group's name and styling

## Steps
- [ ] Replace the eight verdict-state groups in `_tests_groups`
- [ ] Rename `Needs a run`; remove `tests` from `_VIEWS_THAT_ALREADY_GATHER` or keep the local group — decide and record which
- [ ] Assert no row appears in two sections other than the deliberate `Needs you` shortcut

## Notes

**The duplication is the real decision here.** `tests` is in `_VIEWS_THAT_ALREADY_GATHER` precisely to avoid a row appearing twice. [[ADR-0025]] permits the shortcut — *'a shortcut list, not a second home'* — but adopting the shared name means adopting the shared behaviour. Record the choice in the code, not just in the diff.

What disappears: `Failing`, `Stale`, `Never verified`, `Verified`, `Resting`, `Unrecognised status`. All were verdict states; 37 of this repo's 38 automated tests currently sit in the collapsed `Verified` group.
