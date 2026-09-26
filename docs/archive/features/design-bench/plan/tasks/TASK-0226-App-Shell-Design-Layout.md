---
type: "[[task]]"
id: TASK-0226
aliases: ["TASK-0226"]
title: "App-shell layout for the design surface — one scroller, never nested"
status: done
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["[[ISS-0039-Nested-Scrollbars-On-The-Design-Surface]]"]
parent: "[[FEAT-0042-Design-Bench]]"
effort: "M"
depends: []
blocks: []
related: ["[[ISS-0038-Unframed-Design-Stage-Renders-Narrow]]", "[[FEAT-0043-Design-Top-Level-Surface]]"]
tests: []
---

# App-shell layout for the design surface

## Definition of Done

- [x] The design page does not scroll; the artifact frame is the only scroller for the artifact — evidence: harness DOC + FRAMED, `the page does not scroll` PASS (scrollHeight == clientHeight)
- [x] Header and viewport bar stay visible while the artifact scrolls — evidence: `.design-view.is-shell > .design-head { flex: 0 0 auto }` outside the scrolling region
- [x] Revisions and rationale live in a column that scrolls independently, never inside the artifact's scroller — evidence: `test_the_sidebar_holds_the_rail_and_rationale_not_the_stage`; harness asserts `no scroller nests inside another`
- [x] A design that declares **no** `viewport:` fills the available height instead of being forced to 900px — evidence: `test_height_follows_the_same_absence_rule_as_width`; measured 1600×825 in the app-sized case
- [x] A design that **does** declare a viewport keeps its declared frame — the framing is the point and must not be stretched away — evidence: harness FRAMED, `the declared frame keeps its size` 900×900 with the STAGE scrolling, not the page
- [x] `Fill` genuinely fills, vertically as well as horizontally — evidence: `test_fill_actually_fills`; both axes resolve to 100% of the shell-sized stage instead of the 320px min-height
- [x] Compare mode shows two frames side by side, each with its own scroller and no page scroller — evidence: `.is-compare .design-stage { flex: 1 1 0 }` unchanged, now inside a non-scrolling page
- [x] The register (no design selected) still scrolls normally — it is a list, not a stage — evidence: `docView.classList.remove('is-design-shell')` on the register path; `test_the_shell_class_is_cleared_when_leaving_a_design`

## Steps

- [x] Restructure `.design-view` into a fixed-height grid: head / body+sidebar
- [x] Move the revision rail and rationale into the sidebar
- [x] Height follows the same absence rule as width in `buildDesignFrame`
- [x] Fix the `Fill` preset
- [x] Measure the result in the harness rather than asserting source text

## Result

Measured, not asserted. `desktop/harness/design-shell-harness.html` loads the real built stylesheet and checks both cases in a browser:

```
DOC:     page does not scroll · no scroller nests inside another
         frame fills the stage 1600x320 · sidebar is its own scroller
FRAMED:  page does not scroll · no scroller nests inside another
         declared frame keeps its size 900x900 · stage scrolls, not the page
all checks passed
```

The nesting check is the one that matters: it walks every scrollable element under the page and fails if any is contained by another. That is Edwin's complaint stated as a predicate rather than a description.

**A latent bug surfaced while implementing.** `design-page` was never removed from `#doc-view` — harmless while it only added padding, because `overflow: auto` matched the default. Adding `overflow: hidden` to that same element would have frozen scrolling on **every page visited after a design**. Both classes now come off at each of the four switch sites, and a test counts them.

The declared-viewport case deliberately keeps its fixed frame and lets the *stage* scroll. Stretching a 420px phone design to the window height would defeat the framing that the viewport presets exist to provide.

## Notes

Every design-bench test asserts payloads and source text, so both layout defects found today ([[ISS-0038]], [[ISS-0039]]) were invisible to all 81 of them. Edwin found each by looking at the screen. A test for this belongs in `desktop/harness/`, which can load the real bundle in a browser and measure a box — that is the gap worth closing here, not another source grep.
