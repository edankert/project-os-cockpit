---
type: "[[issue]]"
id: ISS-0055
aliases: ["ISS-0055"]
title: "Deferred findings from the design-bench reviews: at-rule descent, dead token, leaked observer, content-blind build guard"
status: triage
severity: low
phase: "[[PHASE-013-Fleet-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["independent review of FEAT-0042, rounds 1–3, 2026-07-28"]
related: ["[[FEAT-0042-Design-Bench]]", "[[TASK-0228-Living-Style-Guide]]", "[[TASK-0226-App-Shell-Design-Layout]]"]
fixed_by: []
---

# Four non-gating findings, filed so they do not leave with the feature

The reviewer's words: *"file at triage before close so they don't vanish with the feature."* None of these blocked approval; all four are real.

## 1. `eachRule` never descends into at-rules

`DES-0002-style-guide.html` iterates `sheet.cssRules` one level deep, so a token declared inside `@media`, `@supports` or `@layer` is invisible to it. The page's own stated rule is that anything it cannot read is **reported rather than skipped** — this is skipped silently. Nothing declares tokens in an at-rule today, so it is latent, not live.

## 2. `--design-fit` is dead

`renderer.ts` sets `wrap.style.setProperty('--design-fit', String(scale))` with a comment claiming it prevents overflow. The token appears in **no stylesheet**, `src` or `dist`. The clipping actually comes from `.design-stage.is-framed { overflow: hidden }`. A comment asserting a mechanism that does not exist is worse than no comment: it will be believed.

## 3. The fit `ResizeObserver` is never disconnected

`buildDesignFrame` creates a `ResizeObserver` per frame and never calls `disconnect()`. Each repaint — every viewport change, every revision selection, every compare toggle — leaks one. Small, and bounded by how often a design is repainted in one session, but unbounded in principle.

## 4. `test_desktop_build_is_not_stale` is content-blind on its mtime half

Fired twice during review on a **no-op touch**: `renderer.ts` restored byte-identical after a mutation run, mtime bumped past the build, test red with nothing stale. Its content assertions are worth keeping; the mtime comparison would stop crying wolf if it hashed the source instead.

## Worth reading together

Both reviewers independently walked through a **string-shaped guard** — a rename in one case ([[ISS-0054]] N1), a hoist in the other. `test_the_viewport_chooser_is_only_for_surfaces` still has that shape (`assert "b.disabled = true" not in head`), so renaming the loop variable readmits the regression. The reviewer's suggestion is worth a pass on its own: convert this file's highest-value guards from *"this string appears"* to *"this behaviour holds"*, as the F4 fix and the two ISS-0054 tests now do.
