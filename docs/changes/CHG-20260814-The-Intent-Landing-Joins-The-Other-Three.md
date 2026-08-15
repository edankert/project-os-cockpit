---
type: "[[change]]"
id: CHG-20260814-The-Intent-Landing-Joins-The-Other-Three
title: "The Intent landing leads with what its badge counts, and the design register stops speaking a second row vocabulary"
status: merged
owner: user:edwin
created: 2026-08-14
updated: 2026-08-15
reviewed_by: "model:claude-opus-5"
review_date: 2026-08-15
review_verdict: changes-requested
source: ["Edwin 2026-08-14: 'One more thing on the designs landing page, the list of design items looks totally different to for instance the list of to be approved features and it does not seem to have the same philosophy as the other landing pages, although not sure if that is a bad thing. Review this and suggest approach.' → then 'Implement the recommended solution.'"]
commit: ""
pr: ""
impacts: ["the Intent view's page now opens with what Intent owes — it was showing the design register and nothing else", "the design register's rows changed shape: a mono ID chip and a real status chip, where the ID was inline text and the status was grey prose", "settled designs fold behind a disclosure instead of listing at full weight", "a design at `proposed` now opens its NOTE from the register, not the bench", "`.design-row`, `.design-row-title`, `.design-row-meta` and `.design-register h1` are gone from renderer.css"]
issues: ["[[ISS-0167-The-Intent-Landing-Does-Not-Lead-With-What-Its-Badge-Counts]]"]
features: ["[[FEAT-0092-Every-View-Lands-On-What-It-Owes]]", "[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]"]
related: ["[[ADR-0025-An-Owed-Row-May-Appear-Twice]]", "[[ISS-0089-A-Card-Head-Names-A-Category-Not-A-Thing]]", "[[ISS-0068-Waiting-On-You-Is-A-Workaround]]", "[[DES-0008-The-Returning-Human]]", "[[PHASE-030-Obligations-Go-Home]]"]
---

# The Intent landing joins the other three

## Summary

Edwin, from use: the designs list *"looks totally different to … the list of to be approved features and it does not seem to have the same philosophy as the other landing pages, although not sure if that is a bad thing."*

Reviewed before it was changed, and it was two things. One is bad and was measurable: **Intent's badge read `1` and its page never mentioned the thing it counted.** One is not: a register is the right shape for a view of decisions, risks and designs, where a queue is right for Issues — so the register stays, and the identity band stays.

## What changed on screen

The page was: identity band, `Designs`, eleven design rows, flat, in ID order.

It is now: **`Intent — what this project is, and what it should look like`** (the button's own title) → `1 needs you here.` → `DECIDE 1 ADR` with its row → the identity band → `DESIGNS · 11`, live first, `3 settled` folded.

## What was actually wrong

`landing_payload` over this repo, 2026-08-14 — `features` 4, `tests` 1, `issues` 0, **`intent` 1**. The one was [[ADR-0026]] at `proposed`, verb `Decide`. Three views led with their count; the fourth showed a register.

That is [[FEAT-0092]]'s own defect. Its first acceptance criterion reads *"Overview and Intent **keep theirs**"* — a true statement about which views had a page, never checked as a statement about whether the page answered the badge. Intent's page came from [[FEAT-0087]] and predates the registry.

The second half was two row grammars for one object. The register's rows were `<a href="#">` with a `preventDefault`, the ID inline in the title text, and the status as 11px grey prose joined with `·` — **outside `statusChip()` entirely**, so `accepted` and `superseded` had no colour and `superseded` sat between two `accepted` rows at identical weight. [[ISS-0023]] at row scale.

## What was built

- `buildLandingRow` / `buildLandingList` / `buildLandingHead` / `buildLandingLead` / `buildLandingObligations` — extracted from `renderViewLanding`, now used by all four landings. `renderViewLanding` went from ~100 lines to ~20.
- The Intent landing reads `/api/cockpit/landing?view=intent` and renders the same obligation block as the others, **above** the identity band per [[DES-0008]]'s rule that a reader who stops halfway should have seen the obligations rather than the news.
- The register splits live / settled on `completed-work.ts`'s predicate, settled shut by default.
- An **owed** design's row opens its note, where `Accept` lives; every other row opens the bench. The owed set comes from the landing payload, so the predicate is not restated in TypeScript ([[TASK-0357]]'s rule).

## Two parts of the proposal were withdrawn before implementation

Both because a decision already on the record answered them, and both are recorded in [[ISS-0167]] at length.

1. **No `Design system · Live · Settled` grouping.** [[ISS-0089]] removed exactly that split in `TASK-0275`. *(Corrected 2026-08-15: this said ISS-0089 "named live/completed as the axis that matters here". It does not — that sentence is a code comment at `cockpit.py:2872`. The withdrawal stands on ISS-0089's actual line, "the design view drops the `system`/`proposal` split", and on Edwin's own words in its `source:`.)*
2. **No counted roll-up of Intent's other five nav groups.** It would restate the navigator group for group, which is [[ISS-0068]] and is named in [[PHASE-030]]'s *"what this phase must not do"*. Measured: it would also have cost ~70ms per landing fetch against a 59ms payload, doubling a call [[ISS-0166]] had just made fast.

## One correction found by walking it

The fold moves **three** designs, not nine. An earlier draft of the issue called the nine `accepted`-or-`implemented` rows "finished work" — but `accepted` is in the **`active`** band in `statuses.py`, not `done`. That is correct and load-bearing: a design that has been decided and not yet built is live work. It is why the split reads the status band rather than judging how settled a status sounds.

## Verification

Walked in `desktop/harness/live-harness.html` against a real sidecar on this repo's corpus, on the built bundle: the head, the lead, `DECIDE 1 ADR`, the fold opening to `DES-0001`, a register row opening `~design/DES-0004`, and the dead-id fallback rendering the register with no obligation block. Features, Issues and Tests re-checked after the refactor — leads and badges still agree (`4`/`4`, quiet, `1`/`1`).

Five guards in `tests/test_view_landings.py`, each mutation-tested: the page head has one author, one row grammar exists, the register does not read `role:`, Intent reads the obligation payload and puts it above identity, and an owed design opens its note. Two existing guards were widened rather than left passing — the quiet-sentence count went 3 → 4, and the top-bar-label test now asserts the *use* site, which is where it was being violated.

## Independent review — 2026-08-15, `changes-requested`

Clean context, `model:claude-opus-5`, never the authoring session ([[project-os-dev#ADR-0013]]: context is the gate, not family). Verified at `da6a834` with `.venv/bin/pytest` (1287 passed / 1 skipped), `tools/scripts/validate-docs.sh` (OK) and `npm run typecheck` (clean).

The change is real and the impacts list matches the diff. Four mutations against the guards that carry the fix all fail correctly.

Two of this section's own claims do not — filed as [[ISS-0171]], with reproductions:

- *"one row grammar exists"* is not what the guard checks. A second row builder with fresh class names, rendering the `<a href="#">` + `preventDefault` grammar this change removed, is green.
- *"the top-bar-label test now asserts the *use* site"* — it asserts that `buildLandingHead` reads `VIEW_LABELS` and is the only head author. Overwriting the Intent head's text back to `Designs` after calling it is green.

Separately, the first withdrawal's authority — *"[[ISS-0089]] … named live/completed as the axis that matters here"* — rests on a sentence that is not in ISS-0089. Edwin's own words in that note's `source:` say the same thing and are on the record; the citation should point at those.
