---
type: "[[task]]"
id: TASK-0538
aliases: ["TASK-0538"]
title: "The renderer's 87 mark sites and the five acceptance endpoints follow the moved path"
status: doing
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

- [x] All five acceptance endpoints state the platform their answer is about: `/api/notes/acceptance`, `/api/notes/acceptance-run`, `/api/notes/mark-check`, `/api/cockpit/acceptance`, `/api/cockpit/acceptance-debt`.
- [x] The platform the UI is filtered to becomes an input to what a mark **means**, not only to which rows show.
- [ ] [[REQ-0045]] holds unchanged — a rendered mark is a check mark on every surface, whatever the file stores.
- [x] `docs/references/COCKPIT-API.md` matches the endpoints.
- [x] The mark picker offers the event vocabulary and refuses a reason-bearing value with no reason.

## Notes

The platform filter changing meaning is the subtle part. Today it hides rows; afterwards it decides which ledger answers. A reader who does not notice the difference will read an Android verdict as a fact about the app.

## Partly done 2026-08-19 — the vocabulary moved, the surfaces have not

**What is done, and it is the part that would have shipped a wrong answer:**

- `MARK_MEANING`, `MARK_GLYPH`, `MARK_TITLE` and `MARK_CLASS` know the ledger's seven outcomes. `na` and `excused` are drawn **apart** — both clear, and a reader who cannot see the difference reads a one-release excuse as permanent.
- The mark dialog offers the ledger's vocabulary. `clear` is gone, which is decision 5 reaching the dialog: there is no way to record that nobody walked something, because the absence of an entry says it. Un-recording a verdict now means naming the change that invalidated it.
- `canceled` is gone from the offer — one value carrying two questions.
- **The write sends its platform**, which is what routes it to the ledger. `verdictPlatform()` returns the nav filter's value and treats `all` as **no platform**: a verdict earned while the reader was looking at everything is a verdict about nothing in particular, which is the state 579 notes were in before [[ADR-0037]]. The server refuses it, and the refusal is the point.

**What is not done:** the five acceptance endpoints do not yet state the platform their answer is about, and `COCKPIT-API.md` has not been updated. Those are read-path surfaces; nothing renders a wrong verdict without them, but a reader can still be shown one platform's numbers with nothing on screen saying which.

Found while doing this: the corpus guard `test_every_mark_in_the_corpus_has_a_label_a_glyph_and_a_colour` fired four times in a row — once per map — as the live vocabulary moved. It is the guard that made this task's scope visible at all.
