---
type: "[[plan]]"
title: "The desk shows what it owes — delivery plan"
status: draft
owner: user:edwin
created: 2026-08-09
updated: 2026-08-09
source: ["[[DES-0010-The-Desk-Shows-What-It-Owes]]"]
implements: ["[[FEAT-0082-The-Desk-Shows-What-It-Owes]]"]
related: ["[[ISS-0121-Reviewed-Register-Counts-Settled-Work-As-Owed]]", "[[FEAT-0062-Desk-Resolution-Flows]]", "[[DES-0005-The-Actuator-Grammar]]"]
---

# The desk shows what it owes — delivery plan

## Delivery sequence

0. **[[ISS-0121]]** — filter settled subjects out of the reviewed register. **Not part of this feature, and it goes first.** Ten of the desk's thirteen owed rows are false; building the board on top would render them more prominently than the list does. It is also the cheapest thing here — a predicate in `_reviewed_register`.
1. **[[TASK-0357]]** — obligation groups carry their verb; `Proposals` splits into Approve and Accept. Server-side, so the renderer work that follows is display only.
2. **[[TASK-0358]]** — the board replaces `buildReviewEmpty`. Occupied columns at width, empty kinds on one line, cards carrying what the 240 px row hides.
3. **[[TASK-0359]]** — the left pane becomes mode-dependent and the walk gets `1 of N` / `Next ▸`. **The test-gated step**: [[TST-0022]] step 10 asserts the current pane order source-level and manually.
4. **[[TASK-0360]]** — the right pane carries the selected note's context.

## Dependencies

- **Hard:** 0 before 1 (a wrong column is worse drawn large). 1 before 2 — the board reads groups and verbs from the payload, and building it against today's four merged groups would put the vocabulary in TypeScript exactly where [[TASK-0357]] is removing it. 2 before 3 and 4, which both branch on whether a card is selected.
- **Soft:** [[TASK-0360]] is independent enough to land in either order with 3, and is the smallest of the four.

## Ordering rationale

The board is the visible part and the last thing to build. Every previous round on this surface that started at the renderer had to be redone once the payload changed shape — the vocabulary belongs server-side first ([[ISS-0023]]), and the columns are vocabulary.

## Open questions

- **Column cap.** [[TASK-0358]] caps cards per column with a `+ K more` disclosure. The number is unset: six reads well at `your-trainer`'s 26, and no repo in the fleet has a kind large enough to test the upper end. Pick it against a real corpus rather than guessing, and record what was dropped.
- **Where acceptance lands.** [[DES-0006]]'s `Awaiting your acceptance` is drawn as a seventh column in the design and is unbuilt. If the acceptance runner arrives first it joins as a group with a verb and needs no renderer change — which is the test of whether [[TASK-0357]] did its job.
- **Whether `Re-review` survives [[ISS-0121]].** With the filter in place the column is empty in every fleet repo measured. It should stay in the payload — the state is real and will recur — but if it is never occupied, it never draws a column, and that is the design working rather than a gap.
