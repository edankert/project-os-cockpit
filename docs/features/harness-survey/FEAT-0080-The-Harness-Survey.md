---
type: "[[feature]]"
id: FEAT-0080
aliases: ["FEAT-0080"]
title: "The harness survey — a repeatable pass over adjacent agent tools whose output is filed issues and recorded declines, not prose"
status: doing
phase: "[[PHASE-028-Borrowed-Capability]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-13
source: ["Edwin 2026-08-05: 'create a separate feature to consider porting more t3.codes functionality/features'"]
goal: "Turn the one-off t3.codes comparison into a repeatable survey: a named method, a living not-taken list, and a round whose output is filed work — so adjacent tools are mined deliberately instead of whenever someone remembers."
requirements: []
tasks:
  - "[[TASK-0340-The-Survey-Method]]"
  - "[[TASK-0341-The-Not-Taken-List]]"
  - "[[TASK-0342-The-T3-Backlog]]"
  - "[[TASK-0386-The-Omnigent-Round]]"
  - "[[TASK-0414-The-Remote-Transport-Round]]"
release: ""
related: ["[[FEAT-0078-Turn-Checkpoints]]", "[[FEAT-0079-Supervision-From-A-Phone]]", "[[ISS-0094-Permission-Prompts-Are-Detected-But-Not-Answerable]]", "[[ISS-0095-The-Agent-Roster-Is-Hard-Coded]]", "[[ISS-0096-No-Surface-Says-What-Changed]]"]
tests: []
---

# The harness survey

## Goal

The first round already paid for itself: four findings filed ([[ISS-0094]], [[ISS-0095]], [[ISS-0096]], [[FEAT-0078]]), one of them a **hole in a phase not yet built** — [[FEAT-0076]]'s "nothing waits silently" invariant does not cover permission prompts, and that was invisible from inside. An outside tool that had solved the same problem made it obvious in an afternoon.

This feature makes that repeatable, and — more importantly — makes **declining** as recorded as adopting. The value is not a longer backlog; it is a defensible answer to *"should we build this?"* for anything an adjacent tool already ships.

## The method, in one line

Read the code, not the marketing; ask what problem each capability solves; keep only what serves the governance thesis; **write down every no with its reason.**

## Round 3 tested the trigger rule, 2026-08-13

[[TASK-0414-The-Remote-Transport-Round]] was fired by the second of the three triggers — *a phase about to build something adjacent* — rather than by a new tool arriving. [[PHASE-033]] opens on a transport decision that VS Code and t3.code have both already made, and the round changed the decision: two alternatives the ADR had eliminated came back with the mechanism that makes them safe, and one of our own task definitions (*degrade explicitly* on version mismatch) was replaced by the stricter thing VS Code chose (*refuse*).

It also produced the method's first honest failure: the round read **documentation, not source**, which is the opposite of the method's first line. Recorded in the round note with a source-verification list, rather than downgraded quietly — a method that cannot report being half-followed is not a method.

## Out of Scope

- **Feature parity with anything.** The cockpit is not competing with harnesses and should not be measured against them.
- **Surveying on a schedule.** A round is triggered by an event — a new tool, a phase about to build something adjacent, a stall like the one this round caught — never by a calendar.
