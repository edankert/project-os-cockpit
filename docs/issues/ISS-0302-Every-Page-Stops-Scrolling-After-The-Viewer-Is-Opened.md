---
type: "[[issue]]"
id: ISS-0302
aliases: ["ISS-0302"]
title: "Every page stops scrolling once the viewer has been opened, because the viewer's page class is added and never removed"
status: fixed
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["Edwin, 2026-09-12: 'Btw. the generated acceptance checks page and any other page shown in the details section do not scroll anymore ..'"]
severity: high
component: desktop-renderer
parent: ""
related: ["[[FEAT-0148-One-HTML-Viewer]]", "[[TASK-0613-A-Generic-HTML-Viewer]]"]
tests: []
---

# Every page stops scrolling after the viewer is opened

## Problem

Open a framed page once, and from then on nothing in the centre pane scrolls: the acceptance checks page, a long note, any page in the details section. The content is there and the pane is the right size; it simply will not move.

## Repro

1. Open any page in the viewer (`~view/<rel>`), or a design note's "Open the page" button.
2. Go anywhere else — `~checks`, a long note.
3. The page does not scroll.

Restarting the window clears it until the viewer is opened again.

## Actual

`renderViewerPage` adds `viewer-page` to `#doc-view` (`renderer.ts:6133`) and **nothing removes it.** The class carries `overflow: hidden` (`renderer.css:4402`), which is right for the viewer — the framed file is meant to be the only scroller, which is ISS-0039's fix — and wrong for every other page, which must scroll itself.

Every other page class in this renderer is cleared by the next page that renders: each `renderX` opens with `docView.classList.remove('overview-pane', 'agents-page', 'review-page', …)`. There are ten such lists. `viewer-page` was added to none of them, so it is the one page class that outlives its page.

## Why the tests did not catch it

Every guard over the viewer reads source text or a single render. Nothing walks *away* from a page and asserts what the next one looks like, and both walks ([[TST-0086-A-Note-Shows-The-Pictures-Beside-It]], [[TST-0087-An-HTML-Page-Opens-In-The-Viewer]]) end on the surface they opened.

## Next Actions

- [x] The page classes are a named set, `DOC_PAGE_CLASSES`, cleared by one helper. Thirteen hand-written `classList.remove(...)` lists became thirteen calls to it.
- [x] Checked in the renderer harness on the built renderer: `~checks` scrollable, then the viewer (`overflow: hidden`, not scrollable — which is right), then `~checks` scrollable again, then a note scrollable. Before the fix the last two were `hidden`.

## Fixed (2026-09-12)

`DOC_PAGE_CLASSES` names the set once and `clearDocPageClasses()` is the only thing that clears it. `tests/test_framing.py::test_every_page_class_is_cleared_by_the_next_page` fails if a page adds a class the set does not know, and if anything clears by hand again — the shape of the bug rather than this instance of it.

**It found a second one immediately.** `history-page` was also added and never cleared. It carries only padding, so nobody noticed, but it is the same defect and is now in the set.

**Also removed:** `is-design-shell`, which nothing has added since the design bench went, and the dead CSS rule that styled it.
