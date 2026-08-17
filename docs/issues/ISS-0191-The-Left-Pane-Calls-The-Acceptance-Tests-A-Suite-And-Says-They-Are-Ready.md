---
type: "[[issue]]"
id: ISS-0191
aliases: ["ISS-0191"]
title: "The navigator gives the acceptance tests a hard-coded status of `ready`, which is the one thing a 542-row suite is never, and the release page labels the file `suite`"
status: "fixed"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
source: ["Edwin 2026-08-17: 'Don't call the acceptance tests suite also, at the moment it is unclear what the acceptance tests status is from the left-pane, it says ready at the moment which is very unlikely?'"]
severity: medium
component: cockpit-server
parent: ""
related: ["[[ISS-0190-The-Acceptance-Tests-Sit-Last-On-Both-Release-Surfaces]]", "[[FEAT-0108-The-Gate-Is-A-Delta-Not-A-Census]]", "[[ISS-0179-Six-From-Reading-The-Release-View]]", "[[ISS-0180-The-Release-Page-Printed-What-It-Should-Have-Rendered]]"]
tests: []
---

# `ready` is a claim, and nothing was checking it

## The status was a literal, not a reading

The navigator's acceptance-tests row was written once, with its state baked in:

```python
tests.append({
    "id": "", "title": "ACCEPTANCE_TESTS.md",
    "subtitle": "all acceptance tests", "status": "ready",
    "type": "test", "url": "/docs/tests/ACCEPTANCE_TESTS.md",
})
```

`ready` in this vocabulary means *"a test that is defined and has not been executed"* ([[ADR-0008]]/[[ADR-0010]], and `statuses.py` says so on the line that carries it). Applied to a whole acceptance suite it asserts that **nothing in it has ever been walked** — of `your-trainer`'s 542 checks, several hundred are ticked, so the row was saying something false about every repo that has ever run one. Edwin: *"which is very unlikely?"*

Worse than false: **it was never going to change.** Ticking every check in the file leaves the row reading `ready` forever, which is the shape of a status that is decoration rather than a reading.

Two things follow, and only the first is what was asked for:

1. The row now **reads the gate**: `blocked` while any Tier 1/Tier 2 check is unsettled, `passing` when none is, with the numbers on the subtitle. Same computation the release page's `Release gate · N unchecked` heading uses — `acceptance.gate_payload` — so the two cannot disagree.
2. The **group label carries the number**: `Acceptance tests · 60 unchecked`, not `Acceptance tests · 1`. The old count was of *files*, next to a heading that reads as a count of *tests*.

`blocked` and `passing` are in the canonical vocabulary. `blocked` is its own band, so it cannot settle a group — but `passing` is terminal, and **that turned out to matter**; see below.

## What the existing guard caught, and what it did not

`test_the_next_release_does_not_read_as_settled` — [[ISS-0179]]'s guard — went red on the first run. Its docstring names the property (*"it went to the Completed band"*); its assertion was `all(status == "ready")`, which is **one way** of keeping the group unsettled and had been mistaken for the rule itself. So it fired over a change it had no opinion about.

And it was not covering the state that would genuinely re-open the defect. Two things had to be true at once, and each arrived separately:

1. **The placeholder had become unreachable.** `Nothing unshipped` was emitted only when `_release_content_rows` returned nothing — but the acceptance row was appended unconditionally, so that list was *never* empty and the placeholder could not render in the state it exists for. Dead since [[ISS-0180]] moved the content into subgroups, and silent, because it only shows in a repo with nothing to release.
2. **The acceptance row can now be terminal.** In a repo with nothing unshipped and a settled gate, it is the only row in the whole group — every row terminal, so `groupIsSettled` files `Next release` under COMPLETED. That is [[ISS-0179]] exactly, reached by a different road, and Edwin has now reported that inversion twice.

Both are fixed by the same line: the placeholder is keyed on **whether anything is unshipped**, not on whether the subgroups came back empty. It is reachable again, it says the true thing in the state it describes, and it is the group's structural guarantee of something unfinished to say.

The guard now asserts the property (*no group of entirely terminal rows*) alongside the narrower rule where it still applies (*a row that stands for a note carries `ready`*), and a second test covers the settled-and-empty state directly.

## The word

`suite` was the label on the release page's file row. It is this module's internal noun — `SUITE_REL`, `class Suite`, `suite.blocking()` — and it leaked onto a surface where the thing has a name of its own. The row reads `acceptance tests` now, and the one line of prose that used the word says *the acceptance tests* instead. The internal identifiers are left alone: they name a Python object, not a thing a reader sees.

## Found on the way: a row pointing at a file that need not exist

The row was appended unconditionally with a hard-coded path, so a repo that has never instantiated the contract — every repo in the fleet before 2026-08-10, and some still — got a navigator row leading to a 404. It is emitted only when the suite exists now, and the **release page says the absence out loud** instead of rendering nothing, in the voice `mountReleaseGate` already uses for it:

> No acceptance tests in this repo — the gate cannot be evaluated.

That direction matters more than the dead link. `acceptance.load`'s own docstring says **absent is not passing**: a repo with no suite has no blocking items, so silence there reads as a clear gate, which is exactly the state every repo was in before the gate existed.

## Expected

1. The navigator row's status is derived from the gate, and changes when a check is marked.
2. The group label states how many Tier 1/2 checks are unchecked.
3. Nothing user-facing calls the acceptance tests a `suite`.
4. A repo with no acceptance tests gets no dead row, and the release page says the gate cannot be evaluated.
5. `Next release` never sinks into the Completed band — including in a repo with nothing unshipped and every check settled.

## Fixed 2026-08-17
