---
type: "[[design]]"
id: DES-0004
aliases: ["DES-0004"]
title: "Attention in the squares — retire Waiting-on-you by giving the phase strip the states it is missing"
role: proposal
status: "accepted"
phase: "[[PHASE-012-Attention-In-The-Strip]]"
owner: user:edwin
created: 2026-07-30
updated: "2026-07-30"
source: ["conversation 2026-07-30: 'does this mean we can get rid of the Waiting on You section?'"]
asset: "DES-0004-attention-in-the-squares.html"
implements: []
supersedes: ""
superseded_by: ""
reviewed_by: "user:edwin"
review_date: "2026-07-30"
review_verdict: "accepted"
related: ["[[ISS-0068-Waiting-On-You-Is-A-Workaround]]", "[[DES-0001-Overview-Redesign]]", "[[DES-0002-Cockpit-Design-System]]", "[[TASK-0200-Overview-Stage-Rework]]", "[[TASK-0210-Overview-Announce-Rows]]", "[[REQ-0022-Overview-State-Above-History]]", "[[ADR-0010]]", "[[project-os-dev#ADR-0011]]"]
tags: [design, overview]
design_revision: "55a743d"
---

# Attention in the squares

## Problem

The overview's **Waiting on you** list is a workaround for an encoding gap, not a view of its own.

Measured 2026-07-30: the list showed 9 rows, and **all 9 already had a square in the phase section** — 384 squares on the page, 8 of the 9 visible. All nine rendered as plain hollow squares, indistinguishable from work nobody has started.

The square has two states: filled for the `done` bucket, hollow for everything else, plus type colour. The payload computes a third bucket, `in_progress`, and **the stylesheet has no rule for it**. Everything else lives in the `title` tooltip, which a tablet cannot reach — and the render server binds `0.0.0.0` precisely so a tablet can read it.

Most of the list's rows also duplicate a mode that owns them: Issues mode with hide-completed on shows exactly the 6 open/triage issues; Tasks mode has a literal `Deferred` group. Those are covered in [[ISS-0068]]. This design addresses the half that is a genuine gap.

## Approach

Six marks on the square, and colour stays on *type* throughout — it is spent, and the type legend is used across six surfaces.

| Mark | Means | Members |
|---|---|---|
| Solid fill | **Delivered** | `done` band — done, fixed, implemented, merged, passing, resolved, closed, complete, released, published, verified, fulfilled, met |
| Solid fill + transparent slit | **Resolved, nothing delivered** | `archived` band — cancelled, superseded, retired, obsolete, deprecated, declined, reverted |
| Hollow + strike | **Parked, still wanted** | deferred |
| Inverted fill, pulsing | **In progress** | doing, active, in-progress |
| Inverted fill, static | **Complete but unproven** | terminal under a recorded `verification_waiver`, or a manual test `passing` on a stale `last_verified` |
| Corner dot, `--status-blocked` | **Outstanding human action** | triage, review, `ready` tests, and computed-blocked |
| *(plain hollow)* | **Not started** | backlog, open, draft |

**Precedence is load-bearing, contrary to an earlier claim here.** This note said "no precedence rule is needed" because every status is in exactly one band. That is false: `cancelled` / `superseded` / `retired` / `declined` are in **both** `BANDS["archived"]` and the per-type done sets, so `_square_state` testing archived *before* `_is_done` is what makes them read as *dropped* rather than *delivered*. Reversing that order silently relabels six squares (found in review, [[ISS-0071]]).

**`failing` and the `blocked` band.** This table had no row for them. `failing` is a legal test status and — until [[ISS-0071]] — fell through to plain hollow, rendering a failing test identically to unstarted work on a strip this design had just added tests to. It now carries the **dot**: a failing test is an outstanding human action in exactly the sense the dot means, and it needs no new mark.

**The dot composes with every fill state; the fills are mutually exclusive.** That is required, not convenient: `STATUSES.md` says "an item can be blocked while still `doing`, which a status cannot express", so a pulsing square must be able to carry a dot. The fills are already mutually exclusive by construction — every status belongs to exactly one band (`statuses.py`), so no precedence rule is needed. *unproven* is the one overlay: it applies to an item that is otherwise *delivered*, and wins, because the point is that the delivered claim is unproven.

### Why each mark is that mark

**Two struck states, and the fill separates them.** Both mean *deliberately not being done*; what differs is whether it is **settled**, and fill is exactly the signal that carries that.

- **Archived is solid with a transparent slit.** Solid because an archived item *is* settled — it resolves its parent's scope and a phase can close over it. The slit is what withdraws the *delivered* claim: accounted for, but nothing came out of it. This fixes a false reading rather than a missing one — measured, of 357 squares in the `done` bucket, **6 are `retired`/`cancelled`/`superseded`** and render identically to the 351 genuinely built.
- **Deferred is hollow with a strike.** Hollow because it is neither built nor terminal: `STATUSES.md:144` — *"explicitly out of the current parent's scope, still wanted later… never satisfies completeness"* — and a parent holding one **cannot close**. The strike says "not now"; the hollow keeps it out of the built count.

The arrangement was reversed during review, and the discarded version is worth recording: filling *deferred* would have put the strip's strongest signal behind work that is not built **and** still blocks its parent from closing. Owner's call, and correct.

**Inverted fill for the two "qualified" states**, distinguished by motion. The form reads as *the fill is present but the claim is not clean*: pulsing means in motion, static means settled-but-unverified. `doing` was already invisible despite being computed; `unproven` was never encoded at all.

**Static inverted fill has a real population, and it is the one this project cares most about.** Measured: **22 items are terminal under a recorded `verification_waiver`** and render as clean solid squares today. That is the whole population — see the correction immediately below for the stale-test figure this sentence used to add, and why it was withdrawn. A waiver is the stronger case anyway: it is a standing statement that the gate was skipped, where staleness is a clock that has not run out. Either way the strip was laundering exactly what [[ADR-0010]] and [[project-os-dev#ADR-0011]] exist to prevent.

### Correction, 2026-07-30 — the stale-test figure was wrong

This note claimed *"9 were last verified 66–83 days ago"* as part of `unproven`'s motivating population. That used a **30-day threshold I chose**, not the project's.

The project's threshold is `DEFAULT_STALENESS_DAYS = 90` in `tools/scripts/validate-docs.py`, configurable via `SNAPSHOT.yaml` `verification.staleness_days` (unset here, so 90 applies). At 90 days **no test in this corpus is stale**, and the validator emits zero `TEST-STALE` warnings — which is the check that would have told me, and which I did not consult before writing the figure.

So `unproven`'s population today is **the 22 waived items alone**. The mark is still worth having, and for the stronger of the two reasons: a waiver is a standing claim that verification was skipped, whereas staleness is a clock that has not yet run out. But the design must not cite 9 stale tests as evidence, and the implementation must use the project's threshold and config source rather than a second one — inventing a parallel staleness rule is precisely what [[ISS-0024]] and [[ISS-0069]] are about.

**The dot is one hue regardless of type**, because attention is one signal. It sits outside the top-right corner with a 1px `--bg` ring so it never occludes the fill beneath it.

## `blocked` is a relationship, not a status

This design cannot read `blocked` off a status, and the current code does.

`STATUSES.md:59`: *"Blocked-ness is **not** a status: record `depends: [ID]` on the blocked item, which names what is blocking it."* It is absent from the allowed sets for `task` and `issue`, and **0 notes in the corpus carry it**. So `collectAttention`'s `status === 'blocked'` branch is dead code that can never fire in a conforming corpus.

Computed instead: *the item is unfinished and has a `depends:` whose target is unresolved*. Measured — 141 notes carry `depends:`, 135 are themselves finished (the dependency is history), and the remaining 6 have **satisfied** dependencies. **Genuinely blocked today: 0.**

So blocked will be rare by nature, because a blocker usually lands. The dot's steady-state population is triage + review + `ready` tests, which today is 4 of 373. Rare is what makes a hard marker the right choice for it.

## Tests join the squares

`ready` tests get a dot, which requires a change the CSS cannot make: **tests are not in the phase payload.** The strip carries features, tasks, requirements and issues only — measured 50 / 244 / 25 / 54 = 373.

Worth doing on its own merits: 20 of 22 tests carry a `phase:`, so they slot in without corpus work, and it is where *unproven* earns its keep. A `ready` test — defined, never executed — is an outstanding human action in exactly the sense the dot means.

**Risks cannot join.** All 4 carry no `phase:` at all, which is why they are absent from the strip. Adding them is a corpus change, not a rendering one, and is out of scope.

## Regions

- `premise` — the measurement the design rests on, and the claim that the list is a workaround
- `proposal` — the five-mark table, the composition rule, and the precedence rule
- `strip-realistic` — PHASE-010 at true density with every state present, and the legend
- `terminal-and-parked` — the two struck states side by side at 1:1 and 3×, and why fill separates them
- `composition` — each fill with and without the dot, at 1:1 and 3×, so the geometry is checkable
- `tests-in-the-strip` — the payload change, and the 22 waived items that motivate *unproven* (an earlier revision cited 9 stale tests on an invented threshold; see Revisions)
- `header-markers` — what the squares cannot carry
- `accordion-headers` — the close-out pill and the collapsed-phase waiting count
- `quiet-state` — the common case, where the change makes the page quieter
- `alternatives` — the five treatments and framings that lost, with why

## Tokens

Status, severity and type tokens are copied **verbatim** from `src/project_os_cockpit/static/base.css` and `static/cockpit.css` on 2026-07-30, light and dark blocks both. Checked against those files rather than recalled — the founding artifact's `verbatim` claim was false when written ([[TASK-0221]]), and this is the first artifact the parity checker has ever been able to check.

The design specifies one palette decision the implementation must match:

- **`--status-blocked`** is the attention hue for the dot, regardless of the type colour underneath.

Descriptive, not specified: strip geometry (`9px`, `12px` feature, `1.5px`/`2px` border) is transcribed from `renderer.css:2234` so the treatments render at true density. The design does not propose changing it. The strike is a `linear-gradient` rather than a pseudo-element so it composes with the dot's `::after`.

## Accessibility

**Motion is the only thing separating `doing` from `unproven`**, so it needs a static fallback or the two collapse for anyone who turns motion off. Under `prefers-reduced-motion: reduce` the pulse is dropped and `doing` takes an offset outline instead. That is in the artifact and must survive implementation.

Every mark is also distinguishable without colour — solid, struck, ringed, dotted, hollow are shape differences, not hue differences. That matters because hue already carries type, so a reader who cannot separate the type colours still reads the state.

## Out of scope

- **Encoding *which* attention state.** One bit. Six statuses in 9px is unreadable; the row you land on says why.
- **Risks in the strip.** No `phase:` on any of the 4.
- **Changing strip geometry, the type palette, or the accordion's collapse rules.**
- **The stat tiles.** They already carry counts and navigate; this adds no second counts surface ([[ISS-0068]] records why that was rejected).
- **A dot for `open` or `deferred`.** Owner's call, and correct: `open` is accepted work waiting on capacity, and `deferred` is a decision already taken — neither is waiting on anyone. `deferred` does get its own *fill* mark; what it does not get is the attention dot.

## Revisions

- 2026-07-30 — initial. Four candidate treatments for one attention bit, plus the header markers.
- 2026-07-30 — revised to the settled encoding after owner review: dot for outstanding action (`open`/`deferred` excluded), diagonal strike for the archived band, pulsing inverted fill for `doing`, static inverted fill for unproven completion, and tests added to the strip. Four alternatives demoted to the `alternatives` region. Recorded that `blocked` is a relationship and that the existing status check is dead code.
- 2026-07-30 — **after the accepting verdict**, and recorded here because [[ISS-0057]] exists for exactly this: the staleness correction below was appended to this note *after* Edwin accepted it at `design_revision: 55a743d`, with no entry here and the revision unchanged. Found by independent review ([[ISS-0071]]). The change is a correction of an overstated figure, not a change of design — but a reviewer cannot know that from a digest, which is why it is written down. `at_note_digest` now covers this note's substance; nothing rendered `note_moved` at the time.
- 2026-07-30 — `deferred` promoted to its own mark, and the two struck states assigned by settledness rather than by which came first: **archived** takes solid-plus-slit, **deferred** takes hollow-plus-strike. New `terminal-and-parked` region. The region formerly proposed as `deferred-decision` (a two-candidate comparison) was renamed rather than deprecated — safe only because the artifact has never been reviewed and carries no annotations; once it has, the contract is add-and-deprecate.

## Review

**2026-07-30 — accepted by Edwin.** Recorded from "I have reviewed DES-0004, please continue with PHASE-011, 012 and 013"; the verdict value and attribution are his, the wording of this line is not. No region-anchored comments were raised, and the encoding was settled through the four exchanges recorded under `## Revisions` rather than in a single pass at the end — which is why there is no findings list here.

Correct this line if the verdict was more qualified than `accepted`; [[PHASE-012]]'s first exit criterion depends on it.

## Notes

**`viewport:` is omitted, and the first draft got this wrong.** It declared `viewport: 900`, reasoning that a design about 9px legibility must be framed at true width. Backwards: declaring a viewport makes the bench treat the artifact as a fixed-height surface and fit it to the pane — `scale = min(1, box.height / framedHeight, box.width / width)` — and because this is a tall document the height term dominated, rendering at **`scale(0.6596)`** and presenting the squares at ~6px. Width was never binding; the pane was already 902px. Omitted, the frame reports `transform: none` at 1151px and the squares are at their true size.

The skill's guidance was right for a reason it does not state: `viewport:` buys width fidelity at the cost of height fitting, and a tall document pays that in the one dimension it cannot afford. Worth adding to the skill.

The artifact renders every state over one shared DOM, generated deterministically, so two revisions diff meaningfully rather than as a wall of regenerated markup.

## Independent review — 2026-07-30 (model:claude-opus-5, fresh context, separate session) — changes-requested

**Recorded here and not in frontmatter, deliberately.** `reviewed_by` / `review_date` / `review_verdict` / `design_revision` on a design note are the *design-acceptance* record, written by `note_writes.stamp_design_verdict` and pinned to the revision the owner judged. Overwriting Edwin's `accepted` at `55a743d` with a close-out verdict would destroy that record and conflate two different reviews. This section is the independent-review pass required by QUALITY.md for a design reaching `accepted`; the acceptance above stands untouched.

**1. The note's substance changed after its accepting verdict, and nothing recorded it.** The verdict landed in `4daa6c1`. `0e8008a` then appended `### Correction, 2026-07-30` retracting "9 were last verified 66–83 days ago" — the measurement the *unproven* mark's justification rests on. `design_revision` still reads `55a743d`, `review_date` is unchanged, and `## Revisions` has no entry. This note's own contract says "once it has [been reviewed], the contract is add-and-deprecate". This is the exact failure [[ISS-0057]] was filed for, occurring on the design that specifies the fix for it, inside the same commit range.

**2. The artifact still asserts the retracted figure, and the artifact is the specification.** `DES-0004-attention-in-the-squares.html` was not touched: the `tests-in-the-strip` region reads "**9 were last verified 66–83 days ago**. Today they would all be solid squares", and its caption reads "13 proven, 9 stale, and a `ready` test that has never run carries the dot". `## Regions` line 101 still describes that region as "the 9 stale tests that motivate *unproven*", and line 64 still states the figure as a measurement with the retraction below it. `renderer.css` says "if these diverge, the artifact is the specification" — so the specification of record still cites evidence this note has withdrawn.

**3. "The fills are already mutually exclusive by construction … so no precedence rule is needed" is false, and the implementation depends on the opposite.** `cancelled`, `superseded`, `retired` and `declined` are in `BANDS["archived"]` **and** in the per-type done sets (`DONE_FEAT`, `DONE_TASK`, `DONE_REQ`, `DONE_ISS`), and `deferred` is in `BANDS["reference"]`. `_square_state` is correct only because it tests `deferred`, then `archived`, then `_is_done` — reorder those three lines and the six `retired`/`cancelled`/`superseded` items this design counts as the *dropped* population render as *delivered*, which is the false reading the slit exists to fix. The precedence rule is real, load-bearing, and documented as unnecessary.

**4. Exhaustiveness, not exclusivity, is where the encoding has a hole.** The table has no row for the `blocked` band. Enumerating `ALLOWED_STATUS` through the implementation, `test`/`failing` maps to no fill and no dot, so a failing test is pixel-identical to work nobody started — on a strip this design has just added tests to, replacing a section whose `status === 'failing'` branch surfaced them at top rank. `requirement`/`approved` is the same shape and more defensible. The design should say what the `blocked` band gets.

Everything else I tried to refute held. The CSS is a faithful transcription including the `prefers-reduced-motion` fallback (`animation: none` plus an offset outline), the dot composes over every fill as specified, the `blocked`-is-a-relationship reading of `STATUSES.md:59` is correct and the retired status check really was dead code, and the `viewport:` note is a genuinely useful finding about the bench's fit arithmetic. The measurement discipline in this note is high — which is why the two withdrawn-but-still-present figures matter: a reader has no way to tell which numbers survived.
