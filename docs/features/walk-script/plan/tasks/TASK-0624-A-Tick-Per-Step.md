---
type: "[[task]]"
id: TASK-0624
aliases: ["TASK-0624"]
title: "A tick goes on a procedure step, a check's verdict is written to the ledger once every step citing it has a tick, and walking a whole sitting this way writes the same events as ticking its checks one by one"
status: backlog
phase: "[[PHASE-044-The-Walk-Page-Reads-As-A-Script]]"
owner: user:edwin
created: 2026-09-14
updated: 2026-09-14
source: ["[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]", "Edwin, 2026-09-14: 'A tick in the cockpit records the verdict for every check that step satisfies.'"]
parent: "[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]"
effort: L
due: ""
depends: []
blocks: ["[[TASK-0626-The-Page-And-The-Sheet-Agree-On-Your-Trainer]]"]
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]", "[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]", "[[ISS-0280-The-Checks-Page-Does-Not-Survive-Leaving-The-Project]]"]
tests: ["[[TST-0089-A-Sitting-Walked-Step-By-Step-Writes-The-Same-Verdicts]]"]
tags: [task, acceptance, ledger, renderer]
---

# A tick per step

## Why

A step in a procedure can satisfy parts of several checks. The walker ticks the step. The ledger records verdicts per check. So something has to hold step ticks until a check's steps are all ticked, and then write one event for that check, the same event FEAT-0149's mark button writes.

## Decide first

1. **Where step ticks live before a verdict.** Options: in the renderer only, lost on reload; in the viewer's per-workspace storage, the mechanism ISS-0280 built for the walker's place; or in the sidecar. The ledger and the repo are ruled out, because a half-walked check in either is a second store (ADR-0040) and a ledger format change (out of scope). Recommended: per-workspace viewer storage, keyed by release, platform, sitting and step, cleared when the check's event is written.
2. **How marks combine.** Recommended: a check's verdict is the worst mark among the steps citing it, in the order `fail` over `partial` over `pass`. A `question` on any citing step makes the check `question`. `na`, `excused` and `blocked` are not step marks; they stay on the check row, and on the release page for the settle marks (ADR-0041).
3. **Reasons.** `ledger.NEEDS_REASON` requires one for every mark but `pass`. A step marked `fail` asks for its reason once, and every check it cites gets that reason with the step number prefixed.

Record the three answers in this note before writing code. If Edwin disagrees with a recommendation, his answer wins.

## Definition of Done

- [ ] A step tick opens `askForMark` with `pass`, `partial`, `fail` and `question`, and records the step mark in the chosen place.
- [ ] When the last step citing a check gets a mark, the page posts one `/api/notes/mark-check` for that check with the combined mark, the walk's platform (not the nav picker's, per FEAT-0149's review finding 1) and `method: manual`.
- [ ] A check with an unticked citing step gets no ledger event.
- [ ] A test builds a fixture sitting with a procedure of four steps citing three checks, ticks every step, and asserts the resulting ledger events equal those from ticking the three checks one by one with the same combined marks. It fails when the combine rule is removed.
- [ ] A test asserts that removing one step tick before the last leaves the ledger unchanged.
- [ ] The ledger file format and `ledger.py`'s event shape are unchanged; a test pins the event keys.

## Notes

- Undoing a step tick after the check's event is written cannot delete a ledger event. It writes nothing; the check is re-marked by re-walking, as today.
