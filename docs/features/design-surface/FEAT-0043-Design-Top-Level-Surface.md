---
type: "[[feature]]"
id: FEAT-0043
aliases: ["FEAT-0043"]
title: "Design as a top-level surface, opening with the project brief"
status: done
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

## Independent review — 2026-07-28, `model:claude-opus-5`, **changes-requested**

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

## Links
- Phase: [[PHASE-009-Design-Surfaces]]
- Requirement: [[REQ-0024-Brief-Is-Maintained]]
- Consumes: [[FEAT-0042-Design-Bench]]
