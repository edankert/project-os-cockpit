---
type: "[[feature]]"
id: FEAT-0043
aliases: ["FEAT-0043"]
title: "Design as a top-level surface, opening with the project brief"
status: review
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-28
updated: 2026-07-28
source: ["user decision 2026-07-28", "measurement:2026-07-28 fleet brief audit"]
goal: "Give design its own top-level mode, positioned before the structure modes, opening with the durable answer to 'what are we building and what should it look like' — so an agent reads it every session and it stays true."
requirements: ["[[REQ-0024-Brief-Is-Maintained]]"]
tasks:
  - "[[TASK-0222-Fill-And-Guard-The-Brief]]"
  - "[[TASK-0223-Brief-Payload-And-Identity-Band]]"
  - "[[TASK-0224-Design-Mode-In-The-Strip]]"
  - "[[TASK-0225-Design-Rationale]]"
release: ""
reviewed_by: model:claude-opus-5
review_date: 2026-07-28
review_verdict: changes-requested
design: ["[[DES-0002-Cockpit-Design-System]]"]
related: ["[[FEAT-0042-Design-Bench]]", "[[REQ-0022-Overview-State-Above-History]]"]
tests: []
---

# Design as a top-level surface

## Why, with the measurement

`LLM_BRIEF.md` ships in every project-os repo and describes itself as "the machine-oriented project brief". Measured 2026-07-28: **10 of 11 fleet repos still carry `Name: REPLACE ME` and `Purpose: REPLACE ME`.** The only exception was created yesterday, and only because an agent happened to be reading the template at the time.

That file is not failing because nobody needs it. It is failing because **nothing ever shows it**. A file nobody can see is a file nobody maintains.

The same lesson arrived twice more in two days, from the other direction: the design bench was built, tested by 44 tests, and unreachable — first because nothing linked to it, then because the link used a URL shape the nav discards. A surface people cannot find does not get used, and a surface that does not get used does not stay true.

## Scope

- The brief filled in for this repo, and a validator check so a placeholder brief is reported rather than shipped ([[TASK-0222]]).
- A brief payload and identity band: what this is, who for, its shape ([[TASK-0223]]).
- A `design` mode in the strip, **positioned second** — after Overview, before the structure modes ([[TASK-0224]]).
- Design rationale: ADRs a design note *links*, not the whole set ([[TASK-0225]]).

Reading order on the surface: **identity → design system → artifacts → rationale.** What it is, what it should look like, what has been proposed, why it is that way.

## Out of Scope

- **Risks and workflows.** A risk is an operational hazard with no bearing on what the app should be; a workflow is how to run the build. Both are Library material — consulted when relevant, not context you carry.
- **Every ADR.** ADR-0006 (retire the delivered band) is design rationale; ADR-0011 (dated promotion) is process governance. Surfacing all of them would drag governance into a product surface. Only linked ones appear.
- **Widening Overview.** It already carries focus, counts, phases, waiting-on-you, activity and commits, and [[REQ-0022]] pins it to fitting above the fold at 900px. Identity there costs the thing that requirement protects.

## Acceptance

- The strip carries seven modes with `design` second; an existing stored mode preference still resolves.
- The surface opens with this repo's real identity — not a placeholder.
- A brief still carrying `REPLACE ME` is reported by the validator, and the surface says so rather than rendering it.
- Only ADRs linked from a design note appear; the rest stay in Library.
- The design system and artifacts remain reachable in one click, as they are now.

## The ordering argument

The strip encodes *kinds of thing*, not frequency: state · structure ×3 · queue · record. Design sits **upstream of structure** — what it should be, before what is being built — so `overview · design · features · tasks · issues · review · library` reads as a progression rather than a list.

Worth stating plainly: Active and Recent were retired two days ago on the reasoning that six modes was the ceiling. Going to seven is a deliberate reversal of that ceiling, not a drift, and it is justified by the brief being read every session rather than browsed occasionally.

## Independent review — round 1 (2026-07-28, `model:claude-opus-5`) — changes-requested

**Disposition:** findings 1–4 filed as [[ISS-0033]] / [[ISS-0034]] / [[ISS-0035]] and addressed in `c2ef660`. All four verified fixed at round 2 below. Kept verbatim as history.

Fresh context, separate session: the reviewer started from these notes and the diffs of `14c3856`, `693dfcc`, `86a79e6`, `0185ad3` and never saw the author's reasoning trace. Same model family as the author, which per ADR-0013 is expected and not the gate — but it does mean **this pass does not satisfy a cross-vendor or human review**, and QUALITY.md's family requirement is still open. Suite `411 passed / 0 skipped`; `validate-docs.sh` OK.

### Blocking

1. **The identity band's only link is a dead click.** `buildIdentityBand` renders 'Read the full brief' / 'Open LLM_BRIEF.md' onto `navigateTo(brief.rel)` with `rel: "LLM_BRIEF.md"`. That path is not a virtual page, so `navigateToInner` fetches `/api/render?path=LLM_BRIEF.md`, which resolves against `docs_root` — `<workspace>/docs`, per `desktop/src/ipc/sidecar.ts`. The brief lives at the repo root and is **not** in `cockpit.PROJECT_SUPPORT_ROOT_FILES` (`README.md`, `ROADMAP.md`, `SECURITY.md`). Verified live against this repo: the endpoint returns `{"ok": false, "error": "not a markdown file: LLM_BRIEF.md"}`, and the renderer's 404 path calls `mountPlaceholder`, **replacing the design surface** with "No note here". This refutes [[TASK-0223]]'s DoD bullet "The band links to the file so editing is one click", and it is the same defect class as `e5f4e90` ("a Library row pointing at a virtual page was a dead click") — the failure this feature's own "Why" section cites as its reason for existing. No test covers it.

2. **Nothing tests that the design mode reaches the design surface.** Two mutations, each of which makes the mode permanently unreachable by click, both survive all 70 tests in `tests/test_design_bench.py`: (a) inverting the guard to `if (currentRel && currentRel.startsWith('~design'))`, and (b) deleting the `navigateTo('~design', …)` call while keeping the branch and its comments. The three tests that look like they cover this are all source-greps satisfied by both mutants — `test_reselecting_design_keeps_the_open_artifact` greps for a substring and for the absence of an equality check, `test_design_mode_still_fetches_the_nav` greps for the absence of `return;`, and `test_the_mode_has_a_button_an_icon_and_a_server_that_serves_it` checks the button, the icon and `cockpit.NAV_MODES` — three endpoints of the path and never the wire between them, despite its docstring claiming "this asserts the whole path". The route *is* correct as written; it is simply unguarded, which is exactly the state that let the bench ship unreachable twice.

3. **`brief_payload` does return the placeholder text.** `sections[].body` is unscrubbed: an unfilled brief yields `{"heading": "Project Identity", "body": "- Name: REPLACE ME\n- Purpose: REPLACE ME"}`. The docstring's "The placeholder text is deliberately **not** returned" and the test name `test_placeholder_text_is_never_returned` (which only asserts `name == "" and purpose == ""`) both claim a property the code does not have. Rendering `brief.sections` inside the unfilled branch of the band leaks `Purpose: REPLACE ME` onto the surface with all 70 tests still green, so `test_the_band_never_renders_the_placeholder` does not protect its namesake property either.

4. **A placeholder anywhere makes the band deny an identity the payload just parsed.** `state` is `unfilled` whenever `placeholders > 0` anywhere in the file. With `Name` and `Purpose` filled and a `REPLACE ME` left in, say, `## Invariants`, the payload returns the real name and purpose but `state: "unfilled"`, and the band's unfilled branch returns before touching either — rendering the headline "This project has not said what it is" about a project that has. [[TASK-0223]]'s two DoD bullets ("a half-filled brief keeps what is real" and "the unfilled branch returns BEFORE touching name or purpose") are in direct tension, and the second nullifies the first at the only consumer.

### Process gates, independent of the findings above

- REQ-0024's four acceptance criteria are all unticked, with placeholder evidence tokens (`<grep>`, `<check + inversion>`, `<test>`, `<the file>`). `implemented` requires every criterion ticked-with-evidence or reconciled (STATUSES.md, REQ-BOXES), and a feature may not reach `done` while a requirement naming it has an unresolved criterion (ADR-0007, FEATURE-REQ).
- The proposed `draft → implemented` skips `approved`; the validator already warns REQ-PREMATURE on REQ-0024.
- No `CHG-*` note exists for work that adds a seventh nav mode, a new endpoint (`GET /api/cockpit/brief`) and a new validator check (LIFECYCLE close-out step 3).
- `validate_brief` has no regression test in this repo — REQ-0024's "reported by the validator" criterion rests on a one-off manual run. (The reviewer re-ran the inversion independently: silent when absent, silent when filled, warns with a count on `REPLACE ME` / `replace me` / `Replace_Me` / `REPLACE-ME`. The check behaves exactly as [[TASK-0222]] documents.)

### Claims the reviewer tried and failed to refute

- `_design_rationale` cannot surface an unlinked governance ADR — ids come only from the design's own `implements:`/`related:`, filtered to `ADR-`; ADR-0011 stays out in both fixture and real corpus, and narrowing the field tuple to `("implements",)` fails four tests. It cannot silently drop a linked one either: `_ANY_ID_RE` matches bare ids and wikilinks alike, and an unresolvable id is emitted with `missing: true`. Two limits consistent with the stated contract: an ADR named only in the note's prose body is not surfaced, and the regex is case-sensitive and requires `\d{2,}`.
- The happy-path route reads correctly end to end, and `GET /api/cockpit/nav?mode=design` returns both groups against this repo. Seven buttons, `design` second, in both `NAV_MODES` and the markup.
- No regressions found: the design register, the Library Design group, `buildDesignNoteBanner` and `loadStoredNavMode` are untouched, `design` is absent from `RETIRED_NAV_MODES`, and the browser cockpit keeps its own five-mode literal.

## Independent review — round 2 (2026-07-28, `model:claude-opus-5`) — **changes-requested**

Re-review of `c2ef660` against round 1's four findings, plus the two questions the author asked. Same fresh-context session as round 1; still a Claude model, so **this still does not satisfy a cross-vendor or human pass**. Suite `417 passed / 0 skipped` (the author's "416 / 1 skipped" is the same run on a machine where `dist/` was absent and `test_desktop_build_is_not_stale` skipped; here the bundle exists, is fresh, and carries the round-2 renderer changes). `validate-docs.sh` OK.

### Round 1 findings: all four fixed, verified independently

1. **Dead link — fixed, and the deeper diagnosis is right.** `GET /api/render?path=LLM_BRIEF.md` now returns the rendered brief. The observation that `_serve_render` never consulted `PROJECT_SUPPORT_ROOT_FILES` at all — so `/README.md`, `/ROADMAP.md` and `/SECURITY.md` had been dead clicks since FEAT-0010 — is correct and is a better finding than the one that prompted it. The widening itself is tight: exact filename membership on a separator-free name, `..` rejected before the branch, and `CLAUDE.md`, `CONTEXT.md`, `SECRETS.md`, `../README.md` all still refused over HTTP.
2. **Reachability — genuinely guarded now.** Both round-1 mutations were re-run: inverting the guard fails `test_the_guard_polarity_is_the_one_that_navigates`; deleting the navigate call fails `test_the_branch_actually_navigates`. The claim is accurate.
3. **Placeholder scrubbing — fixed for `name`, `purpose` and `sections[].body`,** with the real line surviving beside a scrubbed one. Verified across four brief shapes. One field remains — see R2 below.
4. **State semantics — the reported bug is fixed;** a stray `REPLACE ME` under a later heading no longer denies a parsed identity, and the "carries 0 template placeholder(s)" nonsense the author found on their own is real and correctly fixed.

### R1 — blocking: the render-endpoint widening shadows docs-root files

The change resolves the root allowlist **before** `docs_root`, and it tests the allowlist **after** stripping the `docs/` prefix. Both halves are wrong, and together they make `docs/README.md` — a real note in this repo, `id: DOCS-README`, "# Docs structure" — unreachable from the cockpit. Verified live against this repo: `path=README.md` and the explicit, unambiguous `path=docs/README.md` **both** now return `<h1>project-os-cockpit</h1>` from the root README, with `frontmatter: {}` where the docs note's metadata strip used to be. Reproduced in a minimal fixture (root + docs README, distinct bodies): the explicit docs path serves the root file.

It compounds in the client. `extractRel('/docs/README.md')` and `extractRel('/README.md')` now both return `'README.md'`, and the live Library nav emits **both** url shapes as separate rows — so two distinct rows fetch the same thing. Before `c2ef660` there was no collision, because `/README.md` returned `null`. The CHG note's "**This is a fix, not a widening**" is true about exposure and untrue about resolution: an existing path now resolves to a different file.

The guard added for ISS-0033 cannot see this — `test_the_brief_link_resolves_over_http` creates `docs/README.md` but no root `README.md`, so the shadowing branch is never taken. Reordering to docs-root-first makes my repro pass with the full suite still green, so nothing pins the current order; but reordering alone only mirrors the bug (the root README then becomes unreachable whenever `docs/README.md` exists). The real fix is to stop discarding `docs/` as a disambiguator — in `extractRel` **and** in `_serve_render` — so `/docs/X.md` means docs-root and `/X.md` means project-root.

### R2 — `sections[].heading` is still unscrubbed

`## REPLACE ME` survives verbatim in the payload. The docstring now says the placeholder text is not returned "**anywhere**" and the commit says "across every field a surface could render"; the rewritten `test_the_band_never_renders_the_placeholder` enumerates `name`, `purpose` and each `s["body"]` and omits `s["heading"]` — one field short, which is the shape of the defect it was written to close. Nothing renders headings today, so impact is low; the corrected claim is still wider than the code.

### R3 — the new `state` rule introduces the mirror of the bug it fixed

`state` is now `filled` iff `name and purpose`, and those come only from `- Name:` / `- Purpose:` bullet lines. A complete, hand-authored brief that uses prose headings instead of the template's bullet convention reports `state: "unfilled"`, `placeholders: 0`, and the band headlines "This project has not said what it is" over a fully written file, adding "LLM_BRIEF.md does not say what this project is or what it is for." Verified. This contradicts `brief_payload`'s own "parsing is tolerant by design — a missing section, a reordered one, an added heading are all normal, and none may break the surface": a brief that simply did not use the bullet convention is exactly the hand-written variation tolerance exists for.

### R4 — the surface now stays silent about residual placeholders

With `state` keyed on name+purpose, the filled branch never mentions `placeholders`. A brief with a real name and purpose and `REPLACE ME` still under a later heading (`state: filled`, `placeholders: 1`) now looks complete on the surface. The validator still warns, but the *surface* feedback loop is this feature's entire thesis — "a file nobody can see is a file nobody maintains" — and it goes quiet for precisely the partially-filled case. One line in the filled branch closes it.

### The two questions asked

- **Is `test_the_guard_polarity_is_the_one_that_navigates` robust?** No realistic false negative — I tried four broken variants (inverted guard, deleted call, `if (false)` wrapper, redirected target) and each fails via it or via `test_the_branch_actually_navigates`. It is brittle in the *other* direction: hoisting the condition into `const alreadyOnDesign = !!currentRel && currentRel.startsWith('~design')` — a semantically identical, entirely plausible refactor — fails it, because `rsplit("if (", 1)` then yields `!alreadyOnDesign`. Extracting the navigate into a helper fails `test_the_branch_actually_navigates` the same way. A test that fails on correct refactors trains people to weaken it. Worth moving to a real DOM assertion; `desktop/harness/` already exists for exactly this.
- **Do the new state semantics break another consumer?** No — there is no other consumer. `brief_payload` is reached only through `GET /api/cockpit/brief` → `fetchBrief` → `buildIdentityBand`, plus the tests. That question answers cleanly.

### Process

- The four REQ-0024 criteria now carry real evidence; I re-verified each and they hold.
- **The skipped `approved` does need reconciling.** STATUSES.md gives `draft → approved → implemented` and sets `approved → implemented` at feature close-out. The REQ-PREMATURE warning has gone quiet now that the status is terminal, so nothing mechanical will catch it — record in the note that approval was folded into close-out, or pass through `approved` explicitly.
- **`status: done` on this feature was premature** and is currently self-contradictory: the note carries `review_verdict: changes-requested` beside it, and the review skill's step 5 says to keep the item out of terminal status while that verdict stands. R1 is a live regression, so `done` is not yet true. Not changed here — status is the implementer's and the human's call.

## Links
- Phase: [[PHASE-009-Design-Surfaces]]
- Requirement: [[REQ-0024-Brief-Is-Maintained]]
- Consumes: [[FEAT-0042-Design-Bench]]
