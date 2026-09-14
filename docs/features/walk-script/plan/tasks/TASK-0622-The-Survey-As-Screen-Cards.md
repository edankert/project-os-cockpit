---
type: "[[task]]"
id: TASK-0622
aliases: ["TASK-0622"]
title: "The walk page's survey renders one card per changed screen: its name, each change's rider-facing sentence, and the before and after captures side by side, with no test id"
status: backlog
phase: "[[PHASE-044-The-Walk-Page-Reads-As-A-Script]]"
owner: user:edwin
created: 2026-09-14
updated: 2026-09-14
source: ["[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]", "project-os-dev ADR-0045 decision 1"]
parent: "[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]"
effort: M
due: ""
depends: []
blocks: ["[[TASK-0626-The-Page-And-The-Sheet-Agree-On-Your-Trainer]]"]
related: ["[[TASK-0620-The-Survey]]", "[[FEAT-0148-One-HTML-Viewer]]", "[[FEAT-0147-Pictures-Beside-The-Note]]"]
tests: ["[[TST-0089-A-Sitting-Walked-Step-By-Step-Writes-The-Same-Verdicts]]"]
tags: [task, acceptance, publication, renderer]
---

# The survey as screen cards

## Why

Edwin's first step on a release is to look at the screens that changed. The survey [[TASK-0620-The-Survey]] built lists surfaces with invalidating task ids and quoted "Acceptance checks reopened" sections. After project-os-dev TASK-0118 the payload carries screens, sentences and capture paths instead. This task draws them.

## Definition of Done

- [x] `acceptance.walk_payload` passes through the bundled module's new survey structure unchanged: surface id, title, parent, sentences with their change ids, before capture path, after capture path, and a "new" flag. *(Landed 2026-09-14 with the template sync — see "What the sync already landed" below.)*
- [ ] Each changed screen renders as a card. Children render inside their parent's card.
- [ ] The before and after images sit side by side at the same width. A card with only an after image says "new". A card with neither shows its sentences only.
- [ ] Images are served through the existing framed viewer route, confined to the workspace's `docs/` or the capture directory the consumer declares. No new route reads outside a workspace.
- [ ] The survey DOM contains no `TST-` string. A test asserts it.
- [ ] The line saying no release tag was found renders when the payload says so.
- [ ] Built and tested against a fixture repo before real captures exist.

## What the sync already landed, 2026-09-14

project-os-dev TASK-0123 synced the new walk module into this repo, and a sync that left this repo's suite red would not be a sync. So three things landed with it, and this task starts from them rather than from FEAT-0149's code:

- **`walk_payload` speaks the new module's API.** `_walk_notes` now also returns the index in the shape upstream's readers take, so `load_surfaces` runs here instead of being written twice. The payload carries `survey[]` with `surface`, `surface_note`, `parent`, `unresolved`, `changes[{id, title, sentence}]` and `captures[{key, state, before, after, new}]`, plus `survey_release`, `survey_tag` and `survey_problem`. Each sitting also carries `procedure` — setup, the owed steps, each line's tags with an `owed` flag — which is [[TASK-0623-Each-Sitting-As-Its-Procedure|TASK-0623]]'s input.
- **`tests/test_walk_survey.py` was rewritten to the new rule**, 11 tests over git fixtures with a real tag. The old file asserted the invalidation join, which upstream retired; a downstream test of a retired rule is stale rather than failing.
- **The renderer draws the new shape plainly, not yet as cards.** `buildSurveySection` prints each screen's sentences, its captures as images, a child one level in, and the "no release to compare against" line. Five node tests cover it. The card layout, the side-by-side widths and the framed-viewer route are still this task's work, and the DoD boxes below are unticked because none of them is done.

## Notes

- The change ids behind each sentence can link to the change note. That is not a test id.
- Where captures live in your-trainer is its TASK-0904's open question. Read the path from the payload; do not assume a directory.
