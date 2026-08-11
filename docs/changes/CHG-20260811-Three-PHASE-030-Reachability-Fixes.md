---
type: "[[change]]"
id: CHG-20260811
title: "Three PHASE-030 defects fixed: the standing documents open, a phase opens from the navigator that groups by it, and the badges say what they count"
status: merged
date: 2026-08-11
owner: user:edwin
related: ["[[ISS-0132]]", "[[ISS-0133]]", "[[ISS-0135]]", "[[ISS-0131]]", "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[FEAT-0091-The-Standing-Documents]]", "[[PHASE-030-Obligations-Go-Home]]"]
tags: [change]
---

# Three PHASE-030 reachability fixes

Reported by Edwin on 2026-08-11 against the running app, after the sidecar restart that made the current code visible for the first time in 33 hours. Four issues were filed; three are fixed here and one is a design decision left open.

## What changed

**[[ISS-0135]] — every standing document was a dead click.** `_standing_group` emitted `/README.md` where every other builder emits `/docs/README.md`. The renderer's `extractRel` discards the bare form deliberately (`/README.md` and `/docs/README.md` both reduce to `README.md`, so routing it would collapse two distinct files onto one fetch — [[ISS-0037]]), leaving the row with no `data-rel` and the delegated handler with nothing to key off. All eight documents on the Intent view's landing were unclickable. Now `/docs/{rel}`.

**[[ISS-0132]] — a phase could not be opened from the navigator that groups by it.** The server has always sent `url` on every phase group and `NavGroupData.url` was declared in the renderer's own type; nothing ever read it. The header's label now navigates and the chevron still folds.

**[[ISS-0133]] — the badges said a number and not what it counted.** `badges_payload` gained `breakdown`, `verbs` and `nouns`, so `81 items here need a person` became `81 change notes to review` and `3 items…` became `2 standing documents to confirm, 1 ADR to decide`. The title moved from the 14px badge to the button, with a matching `aria-label`.

## Paths

- `src/project_os_cockpit/cockpit.py` — `_standing_group` url shape
- `src/project_os_cockpit/obligations.py` — `counts_by_kind`, `KIND_NOUNS`, `STANDING_OBLIGATION_KIND`; `counts` derived from the detail so the total and the breakdown cannot diverge
- `desktop/src/renderer/renderer.ts` — navigable group headers; badge sentence
- `desktop/src/renderer/renderer.css` — `.group-header-inner.is-navigable`
- `tests/test_nav_url_shape.py` *(new)* — the sweep
- `tests/test_obligations.py` — breakdown sums to badge; every owed kind has a noun and a verb

## Contract

`/api/cockpit/obligations` gains `breakdown`, `verbs` and `nouns`. Additive — `views`, `total` and `kinds` are unchanged, and an older renderer ignores the new fields and keeps its old sentence.

## Verification

Full suite green: **933 passed, 2 skipped**. All three fixes were also walked in the running app rather than only asserted: GLOSSARY opens from the Intent view, `PHASE-028` opens from the features tree with the group still expanded, and the four badge tooltips were read off the live DOM.

The sweep test was confirmed to **fail on the pre-fix code** before being kept — `standing document 'README' has url '/README.md'`. A test that passes before and after guards nothing.

## Two things fixed that nobody asked for, and one not fixed

**A drifting test.** `test_a_stub_is_owed_and_staleness_only_marks` asserted `"196 days" in subtitle`, computed from today against a fixture date. It began failing on 2026-08-11 and would have failed every day after. It now asserts the shape (`last confirmed \d+ days ago`) rather than the number. Pre-existing and unrelated to this work — confirmed by stashing these changes and watching it still fail — but a red suite makes every later verification claim worth less.

**A vocabulary leak, caught by an existing test.** The badge's first cut pluralised kinds in TypeScript. `test_the_renderer_reads_the_count_and_declares_no_kinds` is the guard [[TASK-0357]] left for exactly that, and it worked: the nouns now ship from the server.

**[[ISS-0131]] is deliberately not fixed.** Phase groups render flat where the Tests view's groups render as cards, and the first diagnosis in that note — a missing `item_layout` field — was **wrong**; that field styles nothing (`nav-group-stacked` appears in no stylesheet, though it does select the item renderer). The real mechanism is a CSS rule that strips the card from `is-thing` groups, added on purpose, with its reasoning recorded: *"Four boxes around four categories read as structure; eighteen around eighteen phases read as clutter."* Reversing a decision that argued its own case is Edwin's call, not a bug fix. The note now carries the corrected mechanism and the one fact the original reasoning may not have had: the view now opens on `OPEN · 8` with the rest rolled up, so the real choice is about 8 boxes rather than 26.
