---
type: "[[task]]"
id: TASK-0602
aliases: ["TASK-0602"]
title: "The walk is one screen on the release page — the owed list grouped by area, each row carrying its own procedure text beside the three settle buttons"
status: done
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-09-08
updated: "2026-09-08"
source: ["[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]"]
parent: "[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]"
effort: L
due: ""
depends: ["[[TASK-0601]]"]
blocks: []
related: ["[[REQ-0061-A-Release-Is-Written-Through-One-Workflow]]", "[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]"]
tests: []
---

# The walk is one screen on the release page

[[FEAT-0145]]'s own sentence: *"what is genuinely missing is the walk itself being one screen — the owed list, grouped by area, with the check's procedure readable beside the buttons, on the release page rather than a separate Tests view that has forgotten which release it is grading."*

**The procedure text is the price of this surface existing at all.** [[ADR-0035]]'s second objection was that a release page *"shows the check's name and area, not its steps — so the control is offered at exactly the distance from the procedure where a person cannot be walking it"*. [[ADR-0041]] answers it by paying it. A settle row with a name and no steps is that objection, unaddressed, with new buttons on it.

## What the payload does not carry yet

Measured 2026-09-08, and the decomposition this task came from was wrong about it:

- `acceptance.Item` **does** hold `text` — the procedure.
- `release_payload`'s `open_tests` rows carry `id`, `number`, `name`, `area`, `rel`, `mark`, `features` — and **not** `text`.
- `GatePayload.blocking` carries `GateItem`s, and the release page's gate section renders a **summary and a link to the suite**, not per-check rows.

So the text exists in the reader and reaches no release surface. Widening the payload is part of this task, not an assumption it can lean on.

## Definition of Done

- [x] The release page carries a **Settle what is owed** section listing the checks this release owes, scoped to its platform and its contents.
- [x] Rows are **grouped by `area`**, which is the grouping the suite already uses and the one a person walking it recognises.
- [x] **Each row shows the check's own procedure text.** The payload carries it; the row renders it; a row rendering only a name is a defect, not a density choice.
- [x] Three settle buttons per row — `na`, `excused`, `blocked` — each opening the reason field already pre-picked with that mark. **No button submits with an empty reason.**

  *(Built with the shared mark dialog rather than a reason field on the row, and the difference is worth stating. `askForMark` gained a `preset:` so a row's button arrives with its mark chosen and the field focused — one click, as an inline form would be. What the dialog adds is the check's **whole rendered procedure**, which is what [[ADR-0041]] decision 4 requires and what pays [[ADR-0035]]'s second objection; the row shows it clamped to two lines. What it avoids is 67 open textareas on one page, which is the wall ADR-0035 objected to wearing new clothes. One dialog also means one reason field and one set of refusals: a second one built for this surface is how the two would come to disagree about what `excused` means.)*
- [x] **Bulk selection**: checkboxes, a count, and one settle for the selection, sending one request per [[TASK-0601]]'s contract. The reason is written once for the selection and applies to every check in it — which is honest, because a person settling twelve rows at once has one reason.
- [x] `blocked` visibly does not clear the row. It stays in the owed list with its reason showing. A control whose effect is *"still blocked, and now recorded"* must look like that.
- [x] No `pass`, `partial`, `fail` or `question` control appears anywhere on the page, and each row links to the check's own note for those.
- [x] The rewritten ADR-0035 guard ([[TASK-0601]]) passes against this code.

## Steps

- [x] Add the rows as their own `settle` key on `publication.release_payload`, grouped by area — `publication.settle_rows`, built from the gate's own rows, which have carried `text` since [[FEAT-0103]].

  *(Not `open_tests`, which was the plan. `open_tests` is scoped to the release's **contents** — 3 rows on `your-trainer` — and the walk has to cover every check that **holds** the release, which is 67. Widening `open_tests` would have changed what an existing key means; the new key carries `covers_release` per row so the narrower question is still answerable.)*
- [x] Add the `settle` type to `ReleasePayload` in `renderer.ts`.
- [x] Build the section; place it **after** the gate summary and before the contents, so the page still leads with what holds the release.
- [x] Re-render through `renderReleasePage` after a settle, so the count on screen moves.

## Notes

**This is one screen, not a second Tests view.** The distinction is that this one knows which release it is grading, which is what makes `excused` mean anything. `~checks` stays the place a person walks a suite and records a `pass`.

**Long procedures.** Some checks carry several lines of steps. Render them; a truncated procedure is the same defect as no procedure, one paragraph later. If the page becomes unreadable at `your-trainer`'s scale, collapse **settled** rows rather than the steps.
