---
type: "[[change]]"
id: CHG-20260925-Walk-Setup-Reads-As-A-List
title: "The walk's setup reads as a list, the mark dialog stops repeating the screen label, and recorded decisions use the mark's word"
status: merged
owner: user:edwin
created: 2026-09-25
updated: 2026-09-25
source: ["[[TASK-0631-Verify-The-Guided-Walk]]"]
commit: ""
pr: ""
impacts: ["[[SUR-0004-The-Release-Walk]]"]
issues: []
features: ["[[FEAT-0151-The-Release-Walk-Has-One-Next-Action]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[TASK-0631-Verify-The-Guided-Walk]]"]
---

# The walk's setup reads as a list, the mark dialog stops repeating the screen label, and recorded decisions use the mark's word

## Summary

A procedure's required setup on the walk page is now drawn as a bulleted list. Before this change, every setup item after the first printed as a separate paragraph starting with a literal "- ". A browser walk of Your Trainer's current corpus on 2026-09-25 showed this on 12 of its 13 Android sittings. The generator hands the setup over as Markdown, and the page was setting it as plain text. Each item keeps its own line breaks, and bold markers are removed the same way they already are from step instructions. The **Review results** page uses the same list.

The other changes:

- **The mark dialog's title leaves off the screen label (same walk).** The title read "Settings (SUR-0044). In Developer Settings… — Settings". The card already drops that repeated label, and the dialog now does too.
- **A recorded release decision names its mark in words.** The step card said "TST-0003 — na, recorded as a release decision", and the review summary listed "TST-0002 pass". Both now go through `markWord`, so `na` reads "not applicable". The full suite's guard against printing a stored mark raw caught both lines. FEAT-0151 added them on 2026-09-24.
- **A check waits while any of its steps is held (FEAT-0151 review).** A step's hold used to be checked only when that step itself was marked. A mark saved before a procedure edit made the step depend on missing equipment still counted, and marking the check's last step wrote it. The check now waits until every step citing it can be walked. A step whose whole action is its screen label also keeps the label instead of showing nothing.
- **Surface notes no longer get a Library group.** This repository reached six surface notes, one over the threshold for a "by type" Library group, and a Surfaces group appeared. `surface` joins the types kept out of Library because they have a page of their own (the design view, the walk survey). The library guard test caught it.

The one change to what the walk records is that a check with a held step waits. The ledger format, the step signatures that saved observations are keyed on, and the quoted expectation text are all as they were.

## Impact

- [[SUR-0004-The-Release-Walk]]: A check is not recorded while any step citing it is held; the required setup is a bulleted list; the mark dialog's title starts with the action; a recorded release decision reads "not applicable" rather than "na".

## Evidence

Two new renderer tests in `desktop/tests/walk-page.test.mjs`: "a procedure setup written as a list is drawn as one" and "the mark dialog leaves off the screen label its title already names". Each failed when its change was reverted in a copy of the built bundle. The tests now load `markWord` and the real `MARK_TITLE` table from the built bundle through a new `extractConst` helper. The desktop suite passes 238 of 240, with 2 skips that need a payload from the Python side. `tests/test_acceptance_marks.py` and `tests/test_surface_ownership.py` pass. The browser walk that found the first two defects is described in [[TASK-0631-Verify-The-Guided-Walk]] under "Result, 2026-09-25".

## Documentation Coverage (All Types Considered)
Set each item to one of: `updated`, `new`, `not-applicable`, `deferred`.

- features: updated
- requirements: not-applicable
- tasks: updated
- issues: not-applicable
- tests: updated
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new
- snapshot: updated

## Follow-ups
- [ ] Edwin decides whether a quoted expectation may be shown without its `**` bold markers. The card shows 176 of them on Your Trainer's walk, and the 2026-09-14 review decided the quote is shown exactly as validated.
