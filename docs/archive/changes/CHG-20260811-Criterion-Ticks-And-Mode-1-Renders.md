---
type: "[[change]]"
id: CHG-20260811-Criterion-Ticks-And-Mode-1-Renders
title: "A criterion carrying markup ticks, the browser front door renders, and the Verification card names the notes it counts"
status: merged
date: 2026-08-11
owner: user:edwin
issues: ["[[ISS-0137-A-Criterion-With-Inline-Markup-Cannot-Be-Ticked]]", "[[ISS-0138-Mode-1-Nav-And-Context-Panes-Throw]]"]
features: ["[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]", "[[FEAT-0018-Verification-Health]]", "[[FEAT-0083-The-Browser-Cockpit-Answers-Questions]]"]
tasks: []
tests: []
related: ["[[REL-0001-The-Human-Has-Levers]]", "[[ADR-0021]]"]
tags: [change]
---

# Criterion ticks, mode 1 renders, and the validator card names names

Three behaviour changes, all found by **walking [[REL-0001]]'s acceptance suite by hand** rather than by reading code or running the tests. The suite was green through every one of them.

## What changed

**1. A criterion containing inline markup can be ticked ([[ISS-0137]]).** `renderer._annotate_checkbox_source` now stamps each rendered checkbox with `data-raw` — the criterion's prose *as the file has it* — and `criterionTextOf` reads that instead of reconstructing prose from the DOM. Markdown had already eaten the backticks, brackets and asterisks by then, so the client was sending a string the source did not contain and the write was refused. **26 of this corpus's 53 open criteria were untickable**, and each refused only *after* the reader had typed their evidence.

**2. The browser front door renders again ([[ISS-0138]]).** `groupIsSettled` was called four times in `cockpit.js` and defined nowhere; mode 1 loads exactly one script, so both side panes threw `groupIsSettled is not defined` on every page. Now defined there, beside the `completionRank` it calls.

**3. The Verification card names the notes it counts.** It rendered `validator: 4 errors` and stopped — agreeing with a terminal run on the number and giving the reader nothing to act on. It now lists the erroring notes, reading the per-error `id`/`rel` that [[FEAT-0018]]'s payload has carried since it was written.

## Guards, because none of these were visible to 1137 tests

- `tests/test_criterion_raw_text.py` — drives render → read the box → write. Sabotaged to send rendered text, **all three marked-up cases fail and the plain control passes**: the bug's exact signature. The tempting test (call `stamp_tick` with the raw string) would have passed throughout; the defect was in the caller.
- `tests/test_mode1_identifiers_resolve.py` — statically resolves every name `cockpit.js` calls against what it defines plus real browser globals. This is the check that catches a four-times-called, never-defined function without a browser.
- `tests/test_verification_card_names_errors.py` — the card still reads per-error fields and still bounds its list visibly.

Suite 1137 → 1152.

## What this does not fix

**Fix 2 adds a fifth hand-copied twin**, which is the debt [[ADR-0021]] exists to end, and the file's own header said *"the three functions below are its twin"* while the desktop side had four. The comment was right there and the drift still shipped. The shared module remains the correct answer and remains the principal's decision.
