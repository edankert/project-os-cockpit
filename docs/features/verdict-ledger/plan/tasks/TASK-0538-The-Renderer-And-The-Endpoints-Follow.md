---
type: "[[task]]"
id: TASK-0538
aliases: ["TASK-0538"]
title: "The renderer's 87 mark sites and the five acceptance endpoints follow the moved path"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0136-The-Cockpit-Reads-And-Writes-The-Ledger]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# The UI side, which is the largest single surface

`desktop/src/renderer/renderer.ts` carries **87** `mark` references — more than any Python module, and unmentioned by the source proposal.

## Definition of Done

- [ ] All five acceptance endpoints state the platform their answer is about: `/api/notes/acceptance`, `/api/notes/acceptance-run`, `/api/notes/mark-check`, `/api/cockpit/acceptance`, `/api/cockpit/acceptance-debt`.
- [ ] The platform the UI is filtered to becomes an input to what a mark **means**, not only to which rows show.
- [ ] [[REQ-0045]] holds unchanged — a rendered mark is a check mark on every surface, whatever the file stores.
- [ ] `docs/references/COCKPIT-API.md` matches the endpoints.
- [ ] The mark picker offers the event vocabulary and refuses a reason-bearing value with no reason.

## Notes

The platform filter changing meaning is the subtle part. Today it hides rows; afterwards it decides which ledger answers. A reader who does not notice the difference will read an Android verdict as a fact about the app.
