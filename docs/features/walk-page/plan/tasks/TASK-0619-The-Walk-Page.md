---
type: "[[task]]"
id: TASK-0619
aliases: ["TASK-0619"]
title: "The walk page: ~walk/<platform> in the publication view, sittings in order, the procedure on every row, a tick that writes the ledger"
status: done
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-13
updated: 2026-09-13
source: ["[[FEAT-0149-The-Walk-Page]]"]
parent: "[[FEAT-0149-The-Walk-Page]]"
effort: L
due: ""
depends: ["[[TASK-0618-The-Walk-Payload]]"]
blocks: ["[[TASK-0620-The-Survey]]", "[[TASK-0621-The-Release-Rung-Points-At-The-Walk]]"]
related: ["[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]", "[[TASK-0556-Incomplete-First]]", "[[ISS-0280-The-Checks-Page-Does-Not-Survive-Leaving-The-Project]]", "[[TASK-0465-One-Walk-Layer]]"]
tests: ["[[TST-0088-The-Walk-Page-Hands-Over-The-Owed-Checks]]"]
tags: [task, acceptance, publication, renderer]
---

# The walk page

## Why

The walker needs one page they read top to bottom. `~checks` is the list; the walk page is the list in the consumer's order with the procedure on each row, so nobody flips between the page and the note to find out what to do. [[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]] decision 4 says a surface that records a verdict renders the procedure. This page is that surface for `pass`, `partial` and `fail`; the release page keeps the three settle marks and gains nothing ([[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]).

## Definition of Done

- [x] `~walk/<platform>` renders inside the `publication` nav mode. Arriving at it from anywhere lands on the walk and not on the publication view's default page; reuse the `suppressLandingOnce` mechanism `renderChecksPage` documents rather than rediscovering ISS-0193.
- [x] The page renders, in this order: a header naming the platform, the release and `counts.owed`; the survey section (a placeholder until [[TASK-0620-The-Survey]] fills it); every sitting as a section with its `name`, `state` and `bench` list; the rows inside each; the "Unplaced" section last when non-empty.
- [x] A row shows the check id and title as a link to the note, the `setup`, `steps` and `expect` text under labelled sub-headings, the standing verdict's comment, and one mark button. A `None` setup renders as "Setup: not stated" and is a link to the note. Steps and Expect likewise.
- [x] The mark button calls `askForMark` with no `only:` restriction, `rel` set so the note body renders in the dialog, and `history` from the payload, and the resulting event is written through the same path `markCheckRow` uses for `~checks` rows, with `method: manual`. No new write endpoint.
- [x] After a mark the row repaints in place with its new verdict, and the page's scroll position and row order are unchanged. Tested by a renderer-harness guard that the repaint path never rebuilds the sittings.
- [x] The walker's place is kept per workspace and restored on return, using the mechanism [[ISS-0280-The-Checks-Page-Does-Not-Survive-Leaving-The-Project]] built (`checksPlaceKey`, `saveChecksPlace`, `pendingChecksFilters`), generalised or duplicated for `~walk` with the choice recorded here.
- [x] `order_source: "fallback"` renders a banner at the top reading "Unordered — this repo has no walk order", linking to the WALK.md template's path in the browsed repo.
- [x] No time estimate anywhere on the page. A source guard in the tests greps the walk page's renderer functions for `minute`, `duration` and `estimate`.
- [x] A walk is recorded in a `TST-*` note for this task: one row ticked on `~walk/android` against `your-trainer`, and the same verdict visible on `~checks` and in the release gate afterwards.

## Steps

- [x] Read `renderChecksPage` and `buildChecksPage` (`desktop/src/renderer/renderer.ts`, from the `async function renderChecksPage(` line) and `buildCheckRow`. The row builder is reused; the page builder is not, because the walk has no filters and no facets.
- [x] Read the `~release` routing branch (the `if (normalised === '~release' || normalised.startsWith('~release/'))` line) and add a `~walk` branch beside it that parses the platform.
- [x] Add `renderWalkPage(platform)`, `buildWalkPage(payload)`, `buildSittingSection(sitting)` and `buildWalkRow(row)` beside `renderChecksPage`. `buildWalkRow` wraps `buildCheckRow` and appends the three procedure blocks.
- [x] Fetch `${sidecarBaseUrl}/api/cockpit/walk?platform=…` and hold the payload in a `walkData` module variable the repaint reads.
- [x] Route marks through `markCheckRow` (the `async function markCheckRow(item: GateItem)` line) with a repaint callback that replaces the one row's element by id and nothing else.
- [x] Decide inline comment history versus the dialog's history and record the choice in this note. Default: the dialog only, because it already renders it.
- [x] Renderer-harness tests beside `tests/test_checks_view.py`: the page holds every payload row once, in payload order; a repaint after a mark touches one element; the source guards above. Use `conftest.js_function_body` and name any return type whose braces would confuse it (see [[TASK-0613-A-Generic-HTML-Viewer]]'s last note).

## Notes

**Why not a stepper.** [[TASK-0465-One-Walk-Layer]] measured the retired runner against the checks list and found three axes of difference: transient per-step results recorded in a batch, one step at a time, a single test's scope. The walk page keeps the list's properties, a persistent verdict per row written immediately, and adds only the procedure text and the order. A walker who wants to read ahead can; a stepper would not let them.

**Why the row never moves.** [[TASK-0556-Incomplete-First]] floats owed rows to the top of their area on `~checks`, and Edwin scoped that so the area and section order never move because a reordering list is one you lose your place in. The walk page goes further: nothing moves, including the ticked row, because the page is read once from top to bottom and a row that vanished on tick would make the walker wonder whether the tick landed.

## Done 2026-09-13

`~walk/<platform>` renders inside the publication view: header, the unordered banner where there is one, errors and warnings, the survey, then the sittings, then Unplaced. `buildWalkRow` wraps `buildCheckRow` and appends the three procedure blocks, so a check looks the same wherever it is drawn.

The behavioural tests run the real builders out of the built bundle against a small DOM (`desktop/tests/walk-page.test.mjs`, 20 tests): every owed row once in payload order, the survey first, a repaint that replaces one element and rebuilds no sitting, and the guard rails. The source guards that are claims about a whole function are in `tests/test_walk_links.py`.

### Decisions taken here

- **The dialog's history, not an inline one.** The task left this open on cost. `askForMark` already renders every comment on the check, newest first, above the buttons; a second copy on the row would be the same paragraphs twice on a page that is already long. The walk payload carries `history` for its own rows only — 39 rows against `your-trainer`'s 624 checks — so the dialog opens with it and costs no round trip.
- **Its own place key, not a generalised `ChecksPlace`.** `cockpit:walk-place:<workspaceId>` holds an address and nothing else. `~checks` stores an address plus five filter axes; a walk has no filters, and widening the stored shape would buy shared code and a field that means nothing half the time.
- **`buildCheckRow` gains a fourth parameter** naming which page repaints after the write, defaulting to the checks page's writer. The alternative was a second row builder, which is how one vocabulary of marks becomes two. `tests/test_release_held_back.py` pins the parameter list and caught the addition, which is what that enumeration is for.
- **A row that leaves the owed set keeps its place and shows what was recorded.** The common tick is a `pass`, which removes the check from `ledger.owed` and so from the payload the repaint fetches; the verdict travels with the repaint so the row is redrawn with it rather than keeping the `[ ]` it was built with. Found while walking [[TST-0088-The-Walk-Page-Hands-Over-The-Owed-Checks]].
