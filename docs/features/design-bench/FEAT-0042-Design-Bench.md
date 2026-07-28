---
type: "[[feature]]"
id: FEAT-0042
aliases: ["FEAT-0042"]
title: "Design bench — render, revise, annotate and review designs in the cockpit"
status: review
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-27
updated: 2026-07-28
reviewed_by: "model:claude-opus-5"
review_date: 2026-07-28
review_verdict: approved  # round 3, 2026-07-28 — PREDATES TASK-0229
source: ["user request 2026-07-27", "[[DES-0001-Overview-Redesign]]"]
goal: "Make a design artifact a first-class project record the cockpit can render live at the real viewport, version with its reasoning, annotate by region, review through the existing desk, and check the implementation against."
requirements: ["[[REQ-0023-Design-Is-A-Project-Record]]"]
tasks:
  - "[[TASK-0214-Design-Note-Convention]]"
  - "[[TASK-0220-Revision-Capture]]"
  - "[[TASK-0221-Design-Authoring-Contract]]"
  - "[[TASK-0215-Design-Render-Surface]]"
  - "[[TASK-0216-Design-Revisions-And-Compare]]"
  - "[[TASK-0217-Region-Anchored-Annotation]]"
  - "[[TASK-0218-Design-Review-In-The-Desk]]"
  - "[[TASK-0219-Design-Token-Parity]]"
  - "[[TASK-0227-Expose-Shell-Stylesheet]]"
  - "[[TASK-0228-Living-Style-Guide]]"
  - "[[TASK-0229-Offer-A-Design-For-Review]]"
release: ""
design: ["[[DES-0001-Overview-Redesign]]"]
related: ["[[FEAT-0041-Review-Desk]]", "[[FEAT-0008-Cockpit-API-Hardening]]", "[[TST-0019-Status-Vocabulary-Parity]]"]
tests: []
---

# Design bench

## Goal

Design currently happens outside the project and is copied in afterwards. [[DES-0001]] is the evidence: a 139KB dossier committed under `docs/references/design/`, produced through six revisions in a chat session, of which only the last survives and none of the reasoning does.

This makes the project the home. A design artifact gets rendered at the viewport the app runs at, carries its revisions and the reason for each, can be annotated where it is wrong, reviewed where the other notes are reviewed, and checked against the implementation it specifies.

## Scope

**Phase 1 — useful the day it lands.**
- Consume the `[[design]]` type that landed upstream (project-os-dev FEAT-0019): typed membership, not the path regex the Library group uses today ([[TASK-0214]]).
- A render surface with viewport presets and live reload ([[TASK-0215]]).
- Revision **capture** — commit-with-reason, plus a revision log in the note ([[TASK-0220]]).
- Revisions from git, side by side, with per-revision reasoning ([[TASK-0216]]).

**Phase 2 — once there is something real to annotate.**
- An authoring contract for conforming artifacts ([[TASK-0221]]).
- Region-anchored comments stored as Markdown ([[TASK-0217]]).
- Review through the desk with per-region verdicts ([[TASK-0218]]).
- A scoped palette check against `statuses.py` ([[TASK-0219]]).

## Out of Scope

- **Authoring/drawing.** The artifact is HTML/CSS written by an agent or by hand. This renders, versions, annotates and reviews it.
- **Defining the `DES-*` type.** Done upstream first (project-os-dev FEAT-0019) so this phase builds on it rather than migrating onto it later.
- **Auto-stamping a design verdict.** Same rule as every other review surface (`note_writes.py`, ADR-0013): the machine gathers, the human decides.

## Acceptance

- The existing [[DES-0001]] dossier renders correctly — the real 139KB artifact, not a fixture.
- Editing a design artifact updates the pane without a manual reload, via the existing watcher/SSE path.
- Two git revisions of one artifact render side by side with the reason for the change visible.
- A comment anchored to a declared region still points at that region after a revision moves it on the page.
- **The design bench does not check token parity, by decision** (Edwin, 2026-07-28, [[ISS-0049]] option 1). The original bullet claimed a test would catch a token changed in the implementation but not in a design note; independent review refuted it by mutation. Rather than build the check, the claim is withdrawn: `statuses.py` and [[TST-0019]] guard the implementation's own vocabulary, which is where drift actually happened ([[ISS-0023]]), and a second checker over artifacts that declare no tokens would have been a guard with nothing to guard.
- Rendering an artifact cannot execute anything that reaches the real repo — the render frame is sandboxed and treats artifact HTML as content, not code.

## Design constraints worth stating

**Annotations anchor to declared regions, never to coordinates.** The artifact declares `data-design-region="focus-band"`; a comment references that ID. Coordinate anchors die on the next revision, and the founding artifact went through six. Region anchors survive, and they force the design to name its own structure — which is worth having independently.

**Storage stays plain text.** Comments are Markdown in the design note; revisions are git. No database, nothing the cockpit owns exclusively, everything diffable and readable without the tool. Same reason the rest of project-os works this way.

**The point of building this here is the live render loop and the record** — a design rendered by the same engine as the implementation, at the viewport the app runs at, with its revisions in git beside the features it specifies.

An earlier draft of this note claimed the *token parity check* was the justification. Independent review refuted that, and the evidence is in the founding artifact: [[DES-0001]] names its tokens `--m-done`, `--t-feature`, `--m-accent` while the implementation says `--status-done`, `--severity-critical`, `--accent-link`; its `--m-accent:#3b6ea8` differs from the implementation's `hsl(212 48% 42%)` (≈`#386ba0`) in a block the dossier labels "cockpit tokens, verbatim". The vocabularies do not correspond, so comparing them needs a name mapping — and a hand-maintained mapping is the drift surface reintroduced one level up.

Worse, the direction of authority was contradicted inside this repo on the day it was written: [[TASK-0219]] said "the design becomes the upstream side", while [[DES-0001]]'s own Maintenance section says to *update the HTML when the surfaces change* — i.e. the design trails the code. A parity test with no agreed arrow accumulates waivers.

What survives is narrower and real: a **scoped** check that a design's status/severity palette equals the `statuses.py`-derived palette, with the name mapping declared once in the design's `## Tokens` section. That is worth building. It is not why this phase exists. **Superseded 2026-07-28 ([[ISS-0049]] option 1): that scoped check was descoped, not deferred.** `design_tokens.py` remains in the tree as a working module with no caller; it is not a plan. Read this paragraph as history.

## Independent review — 2026-07-28 (final verdict: `approved`, round 3)

Three rounds. Rounds 1 and 2 returned `changes-requested`; round 3 approves. The rounds are kept in full below rather than collapsed, because what was claimed and then withdrawn is the part a later reader needs.

Reviewed from the notes and the diff by a fresh session with no memory of authoring this work. Same model family as the author (`model:claude-opus-5`), so this **does not** satisfy QUALITY.md's cross-vendor requirement; it satisfies the clean-context requirement of ADR-0013 only. Ran `.venv/bin/pytest -q` (460 passed) and `bash tools/scripts/validate-docs.sh` (OK) unchanged, then tried to break the claims. Where a finding says "measured", it was measured in a `sandbox="allow-scripts"` frame against a live sidecar over CDP — the runtime ISS-0043/0046/0047 established as the only one that counts.

**F1 — Acceptance bullet "a design token changed in the implementation but not the design note fails a test" is false.** Refuted by mutation: `--status-done` changed in `base.css` from `hsl(160 28% 38%)` to `hsl(160 28% 41%)`, no design note touched, full suite still green. `design_tokens.check_design_assets()` has no caller anywhere outside its own test module — not `validate-docs`, not an endpoint, not a test that gates. It scans `docs/designs/**/*.html`, and `test_the_real_corpus_declares_no_scoped_tokens_yet` asserts that no artifact in the corpus declares a scoped token, so the check is silent by construction. The only divergence tests compare two hand-written strings inside `tests/test_design_tokens.py`, which no implementation change can perturb. [[PHASE-009]]'s exit criterion "A design token changed in the implementation is caught by a test — [x]" carries the same defect, and [[DES-0002]]'s Conformance section goes further: "The **table above** … *can* drift from `base.css`. It is the thing [[TASK-0219]] still guards." Nothing reads that table; it survived the mutation unchanged and unflagged. Either wire the check to something real, or narrow the three claims to what the code does (inversion-proven against fixtures, silent on the corpus, as [[TASK-0219]]'s own Result section already says honestly).

**F2 — the live artifact route serves no charset, so [[DES-0001]] renders as mojibake in the bench.** `_serve_design_asset` takes its type from `mimetypes.guess_type()` → `Content-Type: text/html`, no charset; `_serve_design_asset_at` hard-codes `text/html; charset=utf-8`. `overview-redesign-dossier.html` declares no `<meta charset>` and is full of UTF-8. Measured, same bytes, two routes: `/design-asset/…` → `project-os-cockpit Â· design review`; `/design-asset-at/DES-0001/4ebe62d` → `project-os-cockpit · design review`, `document.characterSet === "UTF-8"`. So acceptance bullet 1 ("the existing DES-0001 dossier renders correctly — the real 139KB artifact") is not met, and acceptance bullet 3 renders the two compared revisions in *different encodings*. `test_design_asset_response_is_not_cacheable_and_does_not_sniff` cannot see it: it `inspect.getsource`s the handler and greps for `no-store`/`nosniff` rather than issuing a request. Fix is one header; the authoring contract should also require `<meta charset>`.

**F3 — the style guide's Spacing & density section is dead in the real runtime.** Re-injected sheets are `<style>` elements, so `sheet.href` is `null`, and the spacing counter filters on `(sheet.href || '').includes('cockpit.css')`. Measured in the sandboxed frame: zero bars, the section renders its fallback "cockpit.css not readable" under prose promising "the counts below are computed, not quoted … this one is the live measurement". `shellPresent` was taught to look at `data-reinjected-from`; the spacing counter and the override attribution were not. This is the ISS-0043 pattern — verified in a context the app never uses — recurring in the same file, one function away from its own fix. `test_zero_is_not_counted_as_spacing` passes by asserting `"if (px !== '0px')"` appears in the source: a string match guarding unreachable code.

**F4 — the "shell redefines 10 tokens" block measures something other than what it claims.** It accepts only selectors matching `/^:root\b/`. `base.css` writes its dark block as a bare `[data-theme="dark"]` and so contributes light values only; `renderer.css` writes `:root[data-theme="dark"]` and contributes both. Every `renderer.css` token therefore shows ≥2 distinct values and is reported as a shell-over-base override — including the eight `base.css` never declares. Measured output: `--fg → : #1c1d1f then : #d6d6d6`, a light/dark pair inside one file presented as a cross-file override, with empty file labels (same `href === null` cause as F3). The headline count agrees with [[ISS-0042]] by coincidence — that issue counts 2 overridden + 4 parallel + 4 shell-only, the page counts `renderer.css`'s 10 dark overrides. [[ISS-0042]] is a real finding, but it was filed on a measurement that does not measure it.

**F5 — ISS-0048 was fixed in `swatchRow` only; the same defect is live in the typography section.** `'<span style="font-family:' + v + ';font-size:15px">'` where `v` is `--font-sans`, whose value contains `"Segoe UI"`. Measured: the specimen span carries six stray attributes (`segoe=""`, `ui",=""`, `roboto,=""`, …) and its `style` is truncated at the first quote, so the declaration is invalid and the "specimen" silently renders the inherited body font — it demonstrates nothing. `test_token_values_never_reach_an_html_parser` passes because it inspects only `swatchRow`. `#membership`, `#geometry` and the override block concatenate CSS-derived text into `innerHTML` the same way.

**F6 — latent: `eachRule` never descends into at-rules.** `@media`/`@supports`/`@layer` bodies have no `.style`, so a token declared inside one is absent from every count with no report — against the page's stated rule that anything unreadable is reported rather than skipped. Not live today, but `base.css` already uses `@media`, and DES-0001's own artifact declares its dark palette inside `@media (prefers-color-scheme: dark)`.

**F7 — `--design-fit` is dead.** `renderer.ts` sets it with a comment claiming it stops the scaled frame's unscaled layout box from reintroducing overflow; the custom property appears in no stylesheet, `src` or `dist`. The clipping actually comes from `.design-stage.is-framed { overflow: hidden }`. Also `new ResizeObserver(fit)` is never disconnected on repaint or navigation.

**On test adequacy (the question that matters more than coverage).** Nearly all 119 tests in `tests/test_design_bench.py` assert on source text — `_renderer()` reads `renderer.ts`, `_style_guide()` reads the HTML, one uses `inspect.getsource` on the server. Both failure modes are present. *Correct refactors break them*: `test_reinjected_sheets_go_before_the_artifacts_own_styles` demands the literal `document.head.insertBefore(el, document.getElementById('own-styles'));`, so hoisting that per-iteration DOM query out of the loop fails the test with no behaviour change; `test_a_framed_design_is_scaled_rather_than_scrolled` demands the literal `Math.min(1, box.height / framedHeight, box.width / width)`, so reordering the arguments fails; `test_the_viewport_chooser_is_only_for_surfaces` asserts `"b.disabled = true"` is absent, so renaming the loop variable to `btn` readmits the exact regression. *And bugs survive*: F3 and F5 are both live in the shipped page with the suite green. Credit where due — `test_no_top_level_declaration_shadows_a_window_property` is a genuine mechanism check that would have caught the `const top` SyntaxError, `test_desktop_build_is_not_stale` closes the source-versus-bundle gap, and the `/_shell/` and CORS tests make real requests.

**Not a finding — TASK-0227 and the ISS-0043 CORS allowance are as narrow as they claim.** `SHELL_ASSET_FILES` is an exact-name allow-list of one, checked before any filesystem access, on top of a `..` rejection and a `resolve()`/`relative_to()` containment check that also defeats a symlink out of the tree; `renderer.js` and its map 404. `_send_stylesheet_cors` sets `Access-Control-Allow-Origin: *` only for `.css`, only on two routes that serve package- and build-shipped files, with no `Access-Control-Allow-Credentials`, so no ambient authority is lent and nothing behind it is user data. On a `0.0.0.0` bind that CSS is already readable by anyone who can reach the port; letting a script read it too is not an escalation. One forward hazard worth a comment: the helper keys off the filename alone, so a future route serving *user-supplied* CSS would inherit the header silently.

**Not a finding — the two `- [~]` reconciliations on [[REQ-0023]] are honest.** Each names the mechanism, the tests behind it, the corpus state that does not exist, and the human who must close it; `[~]` is a first-class validator outcome and QUALITY.md explicitly permits "ticked with evidence **or** reconciled"; and the loop is closed rather than dangling, because [[PHASE-009]] still carries both as unticked `[ ]` exit criteria. Reconciling was more informative than ticking would have been. The dishonesty in this note set is in the opposite place: the claims that *are* asserted flat — this feature's Acceptance bullets (no checkboxes, two of them false), PHASE-009's `[x]` token criterion, and DES-0002's Conformance sentence.

**What would close this review:** F1 and F2 must be fixed or the claims narrowed, since they falsify stated acceptance. F3, F4 and F5 are defects in the delivered artifact of the same class the feature spent the day fixing, and belong in `ISS-*` notes (not filed here — the reviewer was asked not to move statuses or allocate IDs).

### Round 2 — 2026-07-28, verdict unchanged (`changes-requested`)

Re-reviewed `b5ec48f`, `4b30c85`, `877bf7f`, `8b52d5b`. Four of the five substantive findings are genuinely fixed and I verified each where it fails, not in the source.

- **F1 — withdrawn honestly, not quietly deleted.** The acceptance bullet was replaced rather than removed, and it names the decision, the decider, the date and [[ISS-0049]]; PHASE-009's box went `[x]` → `[~]` with the same reasoning rather than disappearing; [[DES-0002]]'s Conformance now says "**Not checked** … the palette table below is **unchecked prose**"; [[TASK-0219]] gained an Outcome section explaining why the module is kept. That is a withdrawal a later reader can audit. The one thing left to re-read is the paragraph further up *this* note ("What survives is narrower and real: a **scoped** check … That is worth building"), which still reads as a live plan for the thing just descoped.
- **F2 — fixed and verified end to end.** `Content-Type: text/html; charset=utf-8` on the live route; DES-0001 in a sandboxed frame now reports `characterSet UTF-8`, `Cockpit Overview — Redesign Proposal`, `project-os-cockpit · design review`, 29 regions. `test_the_asset_route_declares_utf8` asks the server instead of grepping the handler, which is the right shape.
- **F3 — fixed and verified.** `sheetOrigin()` in the sandboxed frame: 9 spacing bars, and Icons / Widgets / Motion / Accessibility all render (687, 225, 399 characters of content where the `append()`-return bug had removed them). No `.append(…)`/`.appendChild(…)` result is assigned to anywhere else in the file — I scanned for it; the one occurrence was the one already caught.
- **F5 — fixed and verified.** The type specimen span now carries a single `style` attribute (was six stray ones) and resolves the real `--font-sans` stack.
- **F4 — NOT resolved, and now strictly worse.** The hypothesis that ISS-0042 made the code dead is wrong: measured in the frame after `8b52d5b`, the block renders "**The shell redefines 4 token(s) over `base.css`**" listing `--bg-elevated → renderer.css: #ffffff then renderer.css: #232629`, `--accent-soft`, `--row-hover`, `--row-active`. Those are precisely the four **shell-only** tokens `base.css` does not declare — the four the fix deliberately kept, with a comment above them saying so. Same file, same `:root`, light value then dark value, reported as a cross-file override. Before the fix the block was 8/10 wrong; now it is **4/4 wrong**, and `test_the_shell_declares_no_alias_for_a_base_css_role` guarantees the genuinely-overridden set is empty forever, so the block can only ever emit false positives. Two lines fix it: require `new Set(seen.map((x) => x.from)).size > 1`, and attribute light and dark separately instead of letting `/^:root\b/` collapse them. A page whose thesis is "read from the source so drift is impossible" must not print a finding about the codebase that is false.
- **F6 / F7 — should not block.** At-rule descent is latent (no token is declared inside an at-rule today) and `--design-fit` / the undisconnected `ResizeObserver` are cosmetic. Worth an `ISS-*` at triage, not a gate.

**On the [[ISS-0042]] rewrite** — the mechanical part holds. `base.css` declares all four rewritten roles in *both* schemes (`--text`, `--text-muted`, `--text-faint`, `--accent-link` appear in `:root` and in `[data-theme="dark"]`), so nothing was rewritten to a token missing from the scheme it is used in. No reference to `--fg`, `--fg-muted`, `--fg-faint` or `--accent` survives anywhere in `desktop/src`, `desktop/harness` or `src/` — I checked `.ts`, `.js`, `.css` and `.html`, not just the stylesheet. Every consumer of the removed `--bg`/`--border` overrides is a colour property (`color`, `background`, `border*`, `outline`, `box-shadow`, `accent-color`) — no length, `calc()`, `content` or font consumer — so **nothing beyond colour changes**. Two caveats worth recording. First, the colour change is larger than "slightly lighter ground and hairlines": the shell's neutrals were blue-tinted hex (`#1c1d1f`, `#6b6e73`, `#95989d`, `#33373b`) and `base.css`'s are true greys, so the whole app de-tints — a move *toward* what DES-0002 documents, but a visible one; the light `--border` gets **darker** (`#e3e3e6` → `hsl(0 0% 86%)`), not lighter; and the dark accent goes `#7da6ff` → `hsl(212 50% 65%)`, noticeably less vivid. "Every role resolves" is not "every role reads right", and this one needs Edwin's eyes. Second, `/_shell/renderer.css` is no longer self-sufficient — it now depends on `base.css` for every core token. [[TASK-0221]]'s amendment already tells artifacts to link all three, so this is a coupling to record rather than a defect.

**One claim in [[ISS-0042]] is written wider than its evidence** — the same failure mode this whole review has been about, in the note written to close it. "Four tokens are referenced but never declared anywhere … `var()` with no fallback is invalid at computed-value time, so those properties silently render inherited" is true of exactly one of the four. `--token` occurs only inside a `base.css` *comment* ("rules use `var(--token)` only") and is a regex false positive; `--tree-indent` is used three times in `cockpit.css` as `var(--tree-indent, 0px)` and `--bg-hover` once as `var(--bg-hover, rgba(125, 166, 255, 0.08))` — both have fallbacks, so neither is ever invalid and neither renders inherited. Only `--surface-1` (`cockpit.css:487`, no fallback) matches the description. `test_every_token_the_shell_uses_is_declared_somewhere` repeats the reasoning in its docstring and pins all four, which normalises three non-problems; it would be sharper if it ignored comments and flagged only `var()` **without** a fallback.

**The tree is red as received.** `.venv/bin/pytest -q` → `1 failed, 464 passed`: `test_desktop_build_is_not_stale` fails because `desktop/src/renderer/renderer.ts` carries an mtime (14:37:57) later than `desktop/dist/renderer/renderer.js` (14:33:12). The content is not stale — the working tree is clean, `renderer.ts` was untouched by these four commits, and the build's content assertions pass — so a rebuild (or a touch) clears it. Worth noting that the guard's mtime half is content-blind and will cry wolf on any no-op save; a content hash would not. `validate-docs.sh` is OK.

**Verdict stays `changes-requested`, on a much shorter list:** fix F4 so the artifact stops printing a false finding about the codebase, correct the dangling-token sentence in [[ISS-0042]], and get the suite green. None of that is large. F6, F7 and the stale paragraph above should not hold it up.

### Round 3 — 2026-07-28, `approved`

Re-reviewed `6eb6888`. All three conditions met, and the one I said I would attack hardest survives the attack.

**F4 — fixed, and the fix discriminates.** The objection was that "the block reports nothing" is worthless unless absence means *nothing is wrong* rather than *the check cannot see*, so I built a positive control instead of reading the diff: a copy of `desktop/dist/renderer` with two genuine cross-file overrides appended (`:root { --border: #123456 }` and `:root[data-theme="dark"] { --text: #abcdef }`), served through `--shell-assets`, loaded in a sandboxed frame. It fires, precisely and with correct attribution:

```
The shell redefines 2 token(s) over base.css.
--border (light) → base.css: hsl(0 0% 86%)  then  renderer.css: #123456
--text (dark)    → base.css: hsl(0 0% 87%)  then  renderer.css: #abcdef
```

Two rows, correctly scheme-labelled, correctly file-attributed — and the four shell-only same-file light/dark pairs that produced the 4/4 false positives are **not** reported. Note the dark row was read out of `base.css`'s **bare** `[data-theme="dark"]` block, so the `isRootish`/scheme split handles the selector asymmetry that caused the original misreading. Same page against the pristine shell: block `ABSENT`, 98 swatches, 9 spacing bars, no `.missing` boxes. Absence now means nothing is wrong. One scope note, not a defect: the block iterates `SEMANTIC`, which excludes `--status-*`, `--severity-*`, `--font*` and `--radius*`, so a shell override of a status token would not appear here — `test_the_shell_declares_no_alias_for_a_base_css_role` covers that case and covers it more strongly, being set-disjointness over every token.

**The dangling-token correction is right on all four, and the overstatement is kept as the finding** rather than edited away — `--surface-1` genuine, `--tree-indent` and `--bg-hover` fallback-protected, `--token` a comment. The guard now strips comments and matches only `var(--x)` with no fallback, pinning `--surface-1` alone. That is the right generalisation: the bug was in the measurement, and the measurement is what changed.

**ISS-0054 — I re-ran both mutations rather than take them on report.** Reverting `MODES_WITH_VIRTUAL_LANDING` to `{'overview'}` now fails `test_the_boot_path_does_not_race_a_virtual_landing_mode`; substituting `const notOnDesign = !!currentRel && !currentRel.startsWith('~design'); if (!notOnDesign)` now fails `test_the_guard_polarity_is_the_one_that_navigates`. Both were green before. Neither changes my read of FEAT-0042 — they close reachability holes in FEAT-0043's surface — but they confirm the pattern I flagged in round 1: the guards in `tests/test_design_bench.py` are string-shaped, and two reviewers have now each found a hole where a rename or a hoist walked straight through one. `test_the_viewport_chooser_is_only_for_surfaces` still has that shape (`assert "b.disabled = true" not in head` — rename the loop variable and the regression returns). Cosmetic chrome rather than reachability, so not a gate, but the file would benefit from a pass that converts the highest-value guards from "this string appears" to "this behaviour holds", as F4's fix and the two ISS-0054 tests now do.

**Suite:** `466 passed`. The single failure I see, `test_desktop_build_is_not_stale`, is **my own artifact** — restoring `renderer.ts` after the two mutation runs bumped its mtime past `dist/renderer/renderer.js`; the content is byte-identical to HEAD (`git diff HEAD` empty) and the run is green with that one test deselected. That is now the second time in this review that guard fired on a no-op touch with no content change. Its content assertions are valuable and its mtime half is content-blind; hashing the source, or comparing against the build's own recorded input, would end the false alarms. Worth an `ISS-*` at triage, no more. `validate-docs.sh` OK.

**F6 / F7:** file them at triage before close so they do not disappear with the feature — at-rule descent in `eachRule`, the dead `--design-fit`, the undisconnected `ResizeObserver`, plus the stale-build guard above. None of them gate the verdict, and none needs to precede it.

**Verdict: `approved`.** Every claim this note makes about what is checked now matches what the code checks, and the three findings that falsified stated acceptance (F1, F2) or shipped a false statement inside the delivered artifact (F3, F4, F5) are fixed and verified in the runtime where they failed. What earns the approval is not that the defects were fixed but that the *claims were brought back to the evidence* — an acceptance bullet withdrawn rather than quietly deleted, a phase criterion reconciled rather than unticked, and an overstated measurement recorded as the finding rather than edited out.

**Correction accepted:** there is no cross-vendor gate. QUALITY.md line 49 and [[ADR-0013]] make clean context the mechanism and say model family is not the gate; the paragraph in `CLAUDE.md` that both of us were reading was stale and is now fixed ([[ISS-0053]]). My round-1 sentence claiming this review "does not satisfy QUALITY.md's cross-vendor requirement" was wrong — there is no such requirement to fail. The review gate is satisfied: fresh context, separate session, notes and diff only. `reviewed_by` records the model as provenance, not as a compliance token.

## Links
- Phase: [[PHASE-009-Design-Surfaces]]
- Requirement: [[REQ-0023-Design-Is-A-Project-Record]]
- First subject: [[DES-0001-Overview-Redesign]]
