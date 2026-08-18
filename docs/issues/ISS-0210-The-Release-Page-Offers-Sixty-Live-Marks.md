---
type: "[[issue]]"
id: ISS-0210
aliases: ["ISS-0210"]
title: "The release page offers a live mark control on every blocking check — sixty of them on REL-0013, on the page whose purpose is to report that the release is not ready"
status: open
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: high
component: cockpit-desktop
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[FEAT-0125-The-Release-Page-Reports-What-Holds-It]]", "[[ISS-0192]]", "[[ISS-0190]]"]
---

# The fastest way to unblock a release is to tick the things that say it is blocked

Edwin, reading `REL-0013 · 2.1.7` in `your-trainer`: *"on the release view, I still see all these checks, I would suggest we show something different there and definitely do not allow these acceptance tests to be checked."*

## Measured

`GET /api/cockpit/release?id=REL-0013` on the live sidecar returns `gate.blocking` with **60 rows**, and `buildReleasePage` renders each through `gateMark(item, releaseId, actionable)` with `actionable` **true**. Each is a button that opens the six-mark dialog and writes the check's note.

The release is `status: draft`, `preparing: 2026-08-16`, `features: []`, `contents.kind: derived` (32 features since REL-0012).

## Two defects, one page

1. **The control should not be there at all.** Reasoning is in [[ADR-0035]]: a release is not the subject of an acceptance check, and the page shows the check's *name*, never its steps — so the mark is offered at exactly the distance from the procedure at which a person cannot be walking it.
2. **Sixty rows is not an answer.** The reader's question is *"can I ship"*. Edwin: *"these should either show a list of open tsts or suggest something else."*

## Why it survived ISS-0192

[[ISS-0192]] deleted `mountAcceptanceMarks` — the marks drawn over a *rendered document*. The release page builds its rows in a different function and kept its own control, added earlier by [[ISS-0190]] for a reason that was good then: the release page was where a person stood while clearing a gate.

Nothing detected the survivor, because both surfaces were correct in isolation. It took reading the page.

## Done when

- [ ] `gateMark` has no `actionable` parameter and no release-page row carries a mark control.
- [ ] The release page shows the verdict, the breakdown by area/feature, and the open `TST-*` rows for its contents.
- [ ] A guard fails if a release page emits a control that can write a check.
