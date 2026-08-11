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

## Follow-up, same day — the fourth issue, and the grammar of the third

Edwin looked at the result and reported three things. All are fixed here; the change note keeps its original title, but the batch is now four issues rather than three.

**[[ISS-0131]] is fixed after all — by his decision.** It was left open above because reversing a recorded design decision is not a bug fix. He asked for the cards, so phase groups are framed again. The original argument was a count (*eighteen boxes read as clutter where four read as structure*) and the count had changed underneath it: the view opens on `OPEN · 8` with the rest rolled up, so the live choice was about eight. ISS-0093's indent protection is kept.

**[[ISS-0132]]'s fix had the wrong grammar.** Only the label navigated, so a click slightly to the right folded the group instead — one row doing two things depending on the pixel. The whole head now opens the note and the chevron alone folds, matching the feature row (select from anywhere, separate control for children).

**And the selected phase never looked selected.** `refreshActiveNavRow` sweeps `li[data-rel]`; a group head is a `<summary>`, so it was invisible to the only function that marks what is current. Heads now carry `data-rel` and take the same highlight as a selected row.

### What this says about the first pass

The ISS-0132 fix was verified — the note opened, the group stayed open, the suite was green — and was still wrong. It had been checked against **its own description** ("a phase cannot be opened") rather than against how every neighbouring row behaves. Reachability was the defect; matching the surface's existing grammar was the actual requirement, and no test asserted it because the note never said it.

Worth carrying into [[ISS-0133]]'s outstanding half and [[ISS-0134]]: a fix that satisfies its issue note can still be wrong for the surface.

### The card fix landed twice, because the stylesheet exists twice

The first attempt at [[ISS-0131]] edited `desktop/src/renderer/renderer.css`, rebuilt, reloaded — and changed **nothing on screen**. Computed style still read `border: 0px none`.

`renderer.css` (mode 3) and `src/project_os_cockpit/static/cockpit.css` (mode 1) each carry their own copy of `.nav-group:has(> .nav-group-header.is-thing)`, **the desktop shell loads both, and cockpit.css wins.** So a UI change to the desktop renderer can be complete, correct, built and deployed while the surface it targets is governed by the other file.

This is the exact cost [[FEAT-0073]] already names — *"a hand-written mode-1 twin whose every UI change costs double — three drifts in two days, all caught by review, none by tests-as-first-written."* This is the fourth, and it was caught by Edwin looking at the screen rather than by review or by tests.

Both files now carry the change, and **both updated guards read both files**, so a one-sided edit fails the suite instead of looking fixed. That is the narrow fix. The general one is FEAT-0073's, and this is another measurement for it.

Phase groups now measure identically to Issues and Intent — `4px 6px · 1px solid · rgb(35,38,41) · 6px` in all three — with the head still left of its features (74px against 86px).

### Still open, and asked rather than assumed

**The Intent rename.** Edwin asked whether the design view was not meant to be renamed. It was: [[FEAT-0087]]'s acceptance criterion is reconciled `[~]`, not ticked — *"**Intent** was agreed and the registry uses it, but the nav mode and the button still read `design`"* — and it was parked on [[FEAT-0084]], which sits in [[PHASE-029]], the phase REL-0001 deferred on 2026-08-11. So the rename is currently scheduled for after this release, which is worth revisiting now that it is being hit repeatedly.

The two halves cost very differently: the **button label** is one string in `index.html`, while the **mode id** is a `localStorage['cockpit:nav-mode']` migration across two front doors. Renaming the label alone would remove the visible mismatch today without the migration. Left undone pending his answer rather than folded in.
