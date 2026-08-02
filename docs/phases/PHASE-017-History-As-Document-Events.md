---
type: "[[phase]]"
id: PHASE-017
aliases: ["PHASE-017"]
title: "History as document events — what was fixed and when, with git as the boundary rather than the subject"
status: superseded
order: 17
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
goal: "Replace the overview's three history tiles with one History surface whose rows are document state changes and whose commits are dividers — so the question 'what was fixed or implemented, and when' is answered without reading a git log."
features:
  - "[[FEAT-0052-History-Timeline]]"
requirements: []
issues: []
superseded_by: "[[PHASE-016-The-Overview-Answers-Questions]]"
depends: ["[[PHASE-016-The-Overview-Answers-Questions]]"]
related: ["[[FEAT-0040-Overview-Rework]]", "[[FEAT-0048-Changes-On-The-Overview]]", "[[TASK-0199-Commits-As-Documentation-Events]]", "[[ADR-0009]]"]
tags: [overview, history]
---

# History as document events

## Where this came from

Edwin, framing what the whole system is for: *"use the docs solution as a framework on top of git and code, allowing to work without having to understand the underlying code, git and any other implementation specific sources."*

Measured against that, the overview's history band answers the wrong question three times:

| Tile | Shows | Against the framing |
|---|---|---|
| Activity | weekly note-edit count | volume only — never says *what* |
| Changes | CHG notes | only work someone wrote a note for |
| Commits | last 8 commits, notes as chips | **git is the spine, documents hang off it** |

## The inversion

A **document state change** is the row. A **commit is a divider** — a line saying *everything above here is not committed yet; this commit contained these.*

That keeps what commits are actually good for (the boundary between in-flight and durable) and drops what they are bad for (being the unit of meaning in a system whose unit of meaning is a note).

## The filter that makes it work — transitions, not touches

Not every note edit is an event. Measured on `cebee80`, the phase-hygiene commit:

- **notes touched: 20** — what the current tile shows
- **status transitions: 4** — what actually happened

The other sixteen had a `phase:` field corrected. Nothing was fixed or implemented, yet the current tile renders that commit as the largest event of the day. The stated goal is *"understand what was fixed/implemented when"*, and that is a **transition**, not a touch — which is also what this system already treats as the meaningful unit ([[ADR-0009]]: notes are the authored source of state).

## Scope

- **[[FEAT-0052]]** — the payload, the short tile on the overview, and the full view behind it.
- Activity's sparkline survives as a header strip on the tile, not as a peer: it is volume, and volume is context for a list of events rather than a competing answer.

## Out of Scope

- **Removing commits.** Considered and rejected in the same conversation: the boundary *is* the commit, and hiding it loses "is this saved yet", which is half the ask.
- **Per-line git history.** The system's unit is a note; showing hunks would reintroduce exactly what the framing exists to hide.
- **Rewriting `commits_payload`.** It stays — its file→note resolution is what makes this cheap, and it still answers "what did this commit contain".

## Exit Criteria

- [x] The overview shows one History tile, and Activity / Changes / Commits are gone — evidence: the rendered overview returns exactly `["History"]`, plus a guard on the three builders' absence
- [x] Rows are transitions, not touches — evidence: `cebee80` touched 20 notes and renders **4** rows
- [x] Uncommitted work appears above the first divider, marked — evidence: *"not committed yet · 3 files"* over the live tree
- [x] A commit that touched no notes is still visible — evidence: 7 flagged dividers across the 60-commit view
- [x] A full history view exists and the tile links to it — evidence: `~history`, 61 dividers / 165 rows, reached from `Full history ›`

## Notes

**The undocumented flag is the trap.** Today a commit touching no notes is flagged — that is [[FEAT-0022]]'s guardrail catching code that moved with nothing recording why. Under a note-spine model that commit has *no rows*, so a naive implementation makes it vanish: the one commit that most needs to be seen becomes the one that is invisible. It has to survive as a marker on the divider.

**Cost is not the constraint.** One `git log -U0 -- docs/` yields every status transition with its commit in 0.08 s across 40 commits, measured. The reason this was not built earlier is that nobody had framed history as a document question.


## Closed 2026-07-30

[[FEAT-0052]] done, three tasks, every criterion verified live.

**The framing did the work.** Edwin: *"use the docs solution as a framework on top of git and code, allowing to work without having to understand the underlying code, git and any other implementation specific sources."* Held against that sentence, the old history band failed obviously — three tiles, all of them making git or the filesystem the subject, none of them answering "what was fixed and when".

**The measurement did the rest.** A transition-based row was a hypothesis until `cebee80` was counted: 20 notes touched, 4 statuses changed. Without that number, "transitions not touches" is a preference; with it, the old tile is demonstrably rendering bookkeeping as the day's largest event.

### The trap, and that it was named before it was built

A transition-based list gives a commit that documented nothing **no rows at all** — so the commit most worth seeing is the one a naive implementation silently drops. That is [[FEAT-0022]]'s guardrail evaporating as a side effect of an unrelated redesign.

It was written into [[FEAT-0052]]'s plan as "the single most likely way to build this wrong", then guarded at both levels — the payload keeps zero-transition commits, and the renderer keeps the flag on the divider. Both mutation-verified. Worth recording that naming a trap in the plan is what made it cheap; the last three phases each found their equivalent during review instead.

### Worth carrying forward

Six user-reported findings this week — [[ISS-0069]], [[ISS-0072]], [[ISS-0073]], [[ISS-0074]], the unreadable error pill, and now the history band. Every one came from someone **looking at a rendered surface**, none from a check. Four of the six were mine to have noticed and I did not, because I verified each surface *worked* rather than that it *answered the question it exists for*.

## Superseded 2026-07-30 — merged into [[PHASE-016]]

This phase's work shipped and is unchanged; what changed is where it is recorded. [[PHASE-016]] absorbed it along with the other two legs of the same push, because their shared goal states without listing them: **every number on the overview leads somewhere, and everything on it says what it is.**

Four phases for one afternoon was the drift [[ISS-0077]] measured — nine phases opened in a day against nine in the preceding twelve weeks, at a fifth of the historical size. Each was minted reactively, one per request.

The note stays as the record of this leg. Its items now name PHASE-016, which is the phase that delivered them.
