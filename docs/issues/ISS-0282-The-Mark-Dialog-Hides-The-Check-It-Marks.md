---
type: "[[issue]]"
id: ISS-0282
aliases: ["ISS-0282"]
title: "The mark dialog shows the check's id and name and nothing else — its description and earlier comments are not passed to `askForMark`, so recording a verdict means losing sight of what the check asks"
status: fixed
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-09-06
updated: 2026-09-06
source: ["Edwin, 2026-09-06, after walking v2.1.x's suite in ../your-trainer"]
severity: medium
component: ui
parent: ""
depends: ["ISS-0281"]
related: ["[[SUR-0001-The-Tests-View]]", "[[ISS-0281-A-Failing-Verdict-Is-Erased-From-The-Checks-View]]", "[[ISS-0186-The-Mark-Glyphs-Are-Decorative-And-The-Dialog-Is-Too-Narrow-For-Six-Options]]", "[[ISS-0187-The-Repaint-Loses-Your-Place-A-Refusal-Is-Silent-And-The-Dialog-Has-No-Save]]", "[[ISS-0211-The-Mark-Picker-Shows-Words-Where-The-Check-Mark-Was]]", "[[ISS-0280-The-Checks-Page-Does-Not-Survive-Leaving-The-Project]]"]
tests: []
---

# The mark dialog hides the check it marks

## Problem

Opening the mark dialog on a check replaces the row with a box that shows the check's number and name and six mark options. The check's own text, which the row shows clamped to two lines, is not in the dialog, and neither is any earlier comment. The reader chooses a verdict about a sentence they can no longer see.

> [!quote] As reported — 2026-09-06 (user:edwin)
> When setting the state I cannot see the actual test description anymore would be good to show the description and maybe previous comments in the completion / state selection window.

## Repro

1. Open `../your-trainer` in the shell, Tests view, `~checks`.
2. Click the mark control on any check with a long description, for example one whose row text is clamped.

## Expected

The dialog shows the check's id, name, full description, and the comments recorded on it before (mark, date, reason per event), above the mark options and the reason field.

## Actual

The dialog shows the id, the name, the six options and the reason field.

## Cause (diagnosed by the main session, 2026-09-06)

`askForMark` (`desktop/src/renderer/renderer.ts:2343`) is called from `walkOneCheck` with `{number, name, current}` only. `item.text` is on the item the row was built from and is not passed. The verdict history is not on the item at all today: the payload carries only the current verdict's reason, which is the history half of [[ISS-0281]].

## Scope

Two parts, and only one waits on anything. The description can be passed and shown now. The earlier comments can be shown once the payload carries them (`depends: ISS-0281`). The dialog's width was widened once already for six options ([[ISS-0186]]); a description and a comment list will need the box to grow again, and that is part of this fix, not a new issue.

Not included: changing which marks the dialog offers, or the commit-on-Save behaviour from [[ISS-0187]].

## Sibling search

Siblings on the same dialog: [[ISS-0186]] (too narrow for six options), [[ISS-0187]] (no Save, committed on click), [[ISS-0211]] (words where the glyph was). Each was about the controls; none was about showing the check being marked. This is the first issue of that kind on the dialog. Recorded as the sibling search's result; no rule-ADR proposed from this one.

## Risk scan

No trigger applies: no new dependency, env var, path or contract.

## Reopened 2026-09-06 — the first fix showed the words and not the check

Edwin, the same day, on the first cut: *"The dialog only shows the main title/description not the actual tst details."* Measured against `TST-0062-Free-Tier-Locks` in `../your-trainer`, whose body is 2,230 characters:

1. **The card is taller than the window and does not scroll.** 1,245px of card in a 963px viewport, laid out by a centring backdrop: the card's top sits at −141px and its bottom at 1,104px. So the check's id and title are cut off above the screen, **Save is below it**, and there is no scrollbar on either the card or the page. On a long check the dialog cannot be completed at all — worse than the defect this issue was opened for.
2. **The prose is inserted as plain text, so the details are raw Markdown.** `- **New Workout** (the FAB, per workout type) — hard gate…`, `## Walk history`, backticks and asterisks. A check like this one is a structured inventory — two bulleted lists under bold headings, which is exactly the part a walker reads — and it arrives as a wall of syntax. That is what "not the actual test details" names: the detail is present and unreadable as detail.

### Second cut

Render the body through `/api/render`, the same path the reader pane and the review pane already use (`renderer.ts:7538` is the precedent — fetch by `rel`, mount the body into a target element). One renderer, so the dialog cannot grow a second Markdown dialect, and `[[wikilinks]]` resolve as they do everywhere else. Plain text stays as the fallback when the fetch fails, so a dialog still opens with the check's words in it.

Bound the card: the description and the comment list each scroll within their own height, and the card takes a `max-height` as a backstop, so the buttons and Save are always on screen whatever the body's length.

## Next Actions

- [x] Pass `item.text` and the check's history into `askForMark`; render description above the options and comments below it, newest first.
- [x] Guard: a source-level test that `walkOneCheck` hands the dialog the item's text, and a DOM-free assertion that the dialog builder places the description before the option list.
- [x] Update `docs/reference/cockpit-capability-register.md` in the change-note commit (the dialog shows description and history).
- [x] Render the body through `/api/render` instead of inserting it as text, with the plain text as the fallback.
- [x] Bound the card and its two long blocks so Save is always reachable.
- [x] Guard: the dialog fetches the render, and the card carries a max-height.
