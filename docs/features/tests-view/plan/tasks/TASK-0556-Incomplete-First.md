---
type: "[[task]]"
id: TASK-0556
aliases: ["TASK-0556"]
title: "The nav sorts surfaces by percentage incomplete and lists incomplete checks first; the generated page moves incomplete rows to the top of their section"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0128-The-Tests-View-Leads-With-The-Work]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# What is owed, first

Edwin, 2026-08-19: *"sort only the nav (by % in-complete) and the children in-complete first … For the generated page, move the in-complete items to the top of the section."*

## The predicate, and it is one

**Incomplete = not settled, or stale.** A check clears on `pass`, `partial`, `na` or a live `excused`; it is incomplete on `fail`, `blocked`, `question` or **no entry** — and a stale tick is incomplete, because it stands over evidence a change overtook.

**The same predicate the percentage already uses.** One definition, or a surface's bar and its position disagree about the same set.

## Definition of Done

- [x] Nav surfaces sort by **percentage incomplete, descending**. Ties: more open checks first, then title — without both, a 2-of-2 sits below a 2-of-200 and the order shifts between renders.
- [x] Nav children: **incomplete first**, then id order inside each band, so a reader who knows where a check was still finds it.
- [x] The generated page moves incomplete rows to the top of **their own section**. Area order and tier order are untouched — Edwin scoped this to within a section, and the page is where the suite is walked.
- [x] Sorted **server-side**, so both front doors get it from one place ([[ISS-0230]]'s lesson: a sort implemented twice disagrees twice).
- [x] `sort_items` untouched — [[ISS-0224]] settled that the record's canonical order is `(tier, id)`, and this is a display order in a view.

## Done 2026-08-19

Nav surfaces sort by percentage incomplete; nav children put owed first; the generated page moves owed rows to the top of their own section, leaving area and tier order alone. All server-side, so both front doors get it from one place.

**The child sort could not be proved from the corpus, and saying so is the point.** Measured: **zero** surfaces in the fleet mix settled and owed checks — only this repo has a ledger and all 34 of its checks pass, while the other two carry no marks at all. So a corpus assertion about child order agreed with any implementation, and a mutant that removed the sort entirely survived it.

It is proved on constructed input instead — a settled check with a *low* id beside an owed one with a high id, where id order and owed-first order disagree — plus a stale tick, which sorts as owed because it stands over evidence a change overtook.

The surface sort *is* corpus-proved across all three repos, and its mutant fails.