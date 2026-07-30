---
type: "[[issue]]"
id: ISS-0055
aliases: ["ISS-0055"]
title: "Deferred findings from the design-bench reviews: at-rule descent, dead token, leaked observer, content-blind build guard"
status: fixed
severity: low
phase: "[[PHASE-013-Fleet-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-30
source: ["independent review of FEAT-0042, rounds 1–3, 2026-07-28"]
related: ["[[FEAT-0042-Design-Bench]]", "[[TASK-0228-Living-Style-Guide]]", "[[TASK-0226-App-Shell-Design-Layout]]"]
fixed_by: ["[[TASK-0248-Live-Workspace-Validation-Aggregate]]"]
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

## Resolved 2026-07-30 — three fixed, one already fixed, and the closing observation acted on

### 1. `eachRule` never descends into at-rules — **already fixed**

Both copies descend today: `DES-0002-style-guide.html` walks nested `cssRules` to depth 4 and carries a comment naming this issue; `docs/__templates__/design-style-guide.html` has the same walk. It was fixed at some point after filing and the note was never updated — recorded here rather than silently ticked, because "already done" and "just done" are different claims and only one of them means someone checked.

### 2. `--design-fit` is dead — **fixed**

The `setProperty` call is gone. What replaced it is the comment: the negative `marginBottom` on the next line is what actually reclaims a scaled element's unscaled layout box, and the clipping comes from `.design-stage.is-framed { overflow: hidden }`. Both are now stated where the old comment asserted a mechanism that did not exist.

### 3. The fit `ResizeObserver` is never disconnected — **fixed**

One module-level `designFitObserver`, disconnected before each new one is created. The stage holds at most one framed artifact at a time, so at most one observer should exist; previously every repaint (viewport change, revision selection, compare toggle) added one.

**Bounded, not eliminated.** Navigating away from the design surface leaves the last observer connected until the next frame is built. That is one observer on an element that has left the document, which is a leak in principle and nothing in practice — worth naming rather than claiming a completeness the fix does not have.

### 4. `test_desktop_build_is_not_stale` is content-blind on its mtime half — **fixed**

`desktop/scripts/copy-assets.mjs` now writes `dist/renderer/.source-hash` — a sha256 of `renderer.ts` at build time — and the guard compares content instead of timestamps. A build predating the stamp falls back to the mtime comparison, so an older tree gets the weaker check rather than none.

Verified in both directions, which is the point of the change: a **no-op `touch`** of `renderer.ts` no longer fails (the false alarm that fired twice during review), and appending a real line **does** fail.

### The closing observation — acted on, in the new code rather than retroactively

"Convert this file's highest-value guards from *this string appears* to *this behaviour holds*."

`desktop/tests/fleet-health.test.mjs` is that, for [[FEAT-0028]]: real HTTP servers standing in for sidecars, run against the built module by `node --test` (stdlib, no new dependency), wrapped by `tests/test_desktop_node_suite.py` so the repo keeps one test command. It caught two injected mutations that a string-grep guard could not have seen — a removed identity check and a `degrade` that kept its last value.

`test_the_viewport_chooser_is_only_for_surfaces` still has the string shape and is **not** converted here. It guards a different surface, and rewriting it would be work this issue did not scope. Left explicitly rather than quietly.

**One of my own guards had the defect while I was fixing it.** The first cut of `test_the_cold_pass_command_never_carries_fix_metrics` grepped the source for `--fix-metrics` and failed on the *docstring explaining that the flag is not passed*. Same class, arriving as a false positive instead of a false green. It now captures the argv at the `subprocess.run` boundary.

### A fifth finding, made by closing the fourth

Closing this issue emptied the last `triage` bucket, and two PHASE-012 guards went red: `test_every_des_0004_state_is_reachable` and `test_the_phase_header_carries_what_squares_cannot` both asserted that *some* live item needed attention.

**They were measuring the corpus, not the encoding.** A guard that goes red the moment the project is healthy is a guard that trains people to ignore it. Both now build a copied corpus with one `triage` issue and one `ready` test injected, which keeps what they were for — the payload can *reach* every DES-0004 state — without depending on the project being in trouble. Mutation-verified: disabling `_needs_human` still fails them.

**It happened twice.** The first pass injected a `triage` issue and a `ready` test, which fixed the attention half; closing the phase then removed the last `doing` task and the same guard went red again on a different assertion. The fixture now injects **every** square fill as well, because the pattern was the point and patching one instance of it was not.

Worth recording as its own lesson. [[ISS-0071]] found guards that passed while broken; this is the mirror — a guard that fails while everything is right. Both are guards that measure the corpus when they meant to measure the code.
