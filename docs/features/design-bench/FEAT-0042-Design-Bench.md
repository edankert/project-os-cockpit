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
review_verdict: changes-requested
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
- ~~A design token changed in the implementation but not the design note fails a test~~ — **NOT MET** (independent review, 2026-07-28). Refuted by mutation: `--status-done` was changed in `base.css`, no design note touched, and all 459 tests stayed green. `design_tokens.check_design_assets()` has **no caller outside its own test module** — not the validator, not an endpoint — and it is silent by construction anyway, since no artifact declares a scoped token. See [[ISS-0049]].
- Rendering an artifact cannot execute anything that reaches the real repo — the render frame is sandboxed and treats artifact HTML as content, not code.

## Design constraints worth stating

**Annotations anchor to declared regions, never to coordinates.** The artifact declares `data-design-region="focus-band"`; a comment references that ID. Coordinate anchors die on the next revision, and the founding artifact went through six. Region anchors survive, and they force the design to name its own structure — which is worth having independently.

**Storage stays plain text.** Comments are Markdown in the design note; revisions are git. No database, nothing the cockpit owns exclusively, everything diffable and readable without the tool. Same reason the rest of project-os works this way.

**The point of building this here is the live render loop and the record** — a design rendered by the same engine as the implementation, at the viewport the app runs at, with its revisions in git beside the features it specifies.

An earlier draft of this note claimed the *token parity check* was the justification. Independent review refuted that, and the evidence is in the founding artifact: [[DES-0001]] names its tokens `--m-done`, `--t-feature`, `--m-accent` while the implementation says `--status-done`, `--severity-critical`, `--accent-link`; its `--m-accent:#3b6ea8` differs from the implementation's `hsl(212 48% 42%)` (≈`#386ba0`) in a block the dossier labels "cockpit tokens, verbatim". The vocabularies do not correspond, so comparing them needs a name mapping — and a hand-maintained mapping is the drift surface reintroduced one level up.

Worse, the direction of authority was contradicted inside this repo on the day it was written: [[TASK-0219]] said "the design becomes the upstream side", while [[DES-0001]]'s own Maintenance section says to *update the HTML when the surfaces change* — i.e. the design trails the code. A parity test with no agreed arrow accumulates waivers.

What survives is narrower and real: a **scoped** check that a design's status/severity palette equals the `statuses.py`-derived palette, with the name mapping declared once in the design's `## Tokens` section. That is worth building. It is not why this phase exists.

## Independent review — 2026-07-28 (`changes-requested`)

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

## Links
- Phase: [[PHASE-009-Design-Surfaces]]
- Requirement: [[REQ-0023-Design-Is-A-Project-Record]]
- First subject: [[DES-0001-Overview-Redesign]]
