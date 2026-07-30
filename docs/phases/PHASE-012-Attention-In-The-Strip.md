---
type: "[[phase]]"
id: PHASE-012
aliases: ["PHASE-012"]
title: "Attention in the strip — the overview stops re-listing what it already draws"
status: planned
order: 12
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
goal: "Give the phase squares the states they are missing so the Waiting-on-you list has no job, and finish the reachability residue PHASE-010 left behind. The overview gets quieter, not busier: one section is deleted and nothing replaces it."
features: []
requirements: []
issues:
  - "[[ISS-0037-Library-Root-File-Rows-Are-Dead-Clicks]]"
  - "[[ISS-0067-Untyped-Task-Notes-Are-Unreachable]]"
  - "[[ISS-0068-Waiting-On-You-Is-A-Workaround]]"
depends: ["[[PHASE-010-Surface-Ownership]]"]
related: ["[[DES-0004-Attention-In-The-Squares]]", "[[TASK-0200-Overview-Stage-Rework]]", "[[TASK-0210-Overview-Announce-Rows]]", "[[REQ-0022-Overview-State-Above-History]]", "[[PHASE-011-Unproven-Claims]]"]
tags: [overview, ia]
---

# Attention in the strip

## Goal

The overview's **Waiting on you** list is a workaround for an under-expressive encoding. Measured 2026-07-30: all 9 rows it showed already had a square on the page — 384 squares, 8 of the 9 visible — and every one rendered as a plain hollow square, indistinguishable from work nobody has started.

[[DES-0004]] is the answer, and it is `draft`. **This phase does not start until that design has a review verdict.** That is the gate, not a formality: the encoding change is a stylesheet change to the densest element on the page, and 384 calm squares can be turned into noise by one bad mark.

Alongside it, two small reachability items of exactly [[PHASE-010]]'s family — found *after* it closed, which is why they are here rather than reopening it.

## Scope

- **[[ISS-0068]]** — the encoding from [[DES-0004]]: the dot for outstanding human action, the strike for parked, the slit for resolved-not-delivered, the pulse for in-progress. Then the phase-header markers (a collapsed-phase waiting count and the close-out pill), then deleting `buildWaitingOnYou`, `collectAttention`, `appendAsyncWaitingRows`, `buildWaitingRow` and the `.ov-waiting*` CSS.
- **Tests into the phase payload.** `ready` tests get a dot, and tests are not in the strip at all today — measured 50 feature / 244 task / 25 requirement / 54 issue = 373. 20 of 22 tests carry a `phase:` so they slot in without corpus work.
- **`blocked` computed from `depends:`, not read off a status.** `STATUSES.md:59` says blocked-ness is a relationship; 0 notes carry `status: blocked`; `collectAttention`'s check for it is dead code.
- **[[ISS-0067]]** — three task notes carry no frontmatter and reach no surface. Same mechanism as ISS-0062, same fix available (read the path).
- **[[ISS-0037]]** — Library rows for top-level project files are dead clicks.

## Out of Scope

- **The `unproven` mark** from the same design — [[PHASE-011]]. One design spans two phases deliberately: this one is renderer-only and shippable quickly, that one touches the validator and the test format.
- **Risks in the phase strip.** All 4 carry no `phase:`, so this is a corpus change, not a rendering one.
- **The `review` row type's replacement.** Nothing owns "in review too long"; [[DES-0004]] leaves it an open question and so does this phase. [[PHASE-011]] closing FEAT-0018 may make it moot.
- **Retyping the 19 untyped `PLAN.md` files or the 3 untyped tasks.** The fix is to read the path; adding frontmatter would mask whether it works ([[ISS-0062]]'s reasoning).

## Exit Criteria

- [ ] [[DES-0004]] carries a recorded review verdict before any code lands — evidence: <frontmatter>
- [ ] Every state in the accepted encoding is distinguishable on a real phase strip at true density, including under `prefers-reduced-motion` — evidence: <manual pass; motion is the only thing separating two of the marks>
- [ ] A collapsed phase holding attention says so on its header — evidence: <`ISS-0024`'s square is on the page and `offsetParent: null`; without this the change loses information>
- [ ] `buildWaitingOnYou` and its three helpers are deleted, and [[TASK-0200]] / [[TASK-0210]] are marked superseded rather than emptied — evidence: <diff + note statuses>
- [ ] Every `TASK-*.md` on disk is reachable, whether or not it carries frontmatter — evidence: <a count assertion against a glob, as [[TST-0022]] does for plans>
- [ ] No Library row is a dead click — evidence: <ISS-0037 test>

## Notes

**This is a design reversal, not a bug fix**, and the close-out should say so. [[TASK-0200]] delivered the Waiting-on-you list, [[TASK-0210]] delivered the announce rows that put the desk's queue into it, and [[DES-0001]]'s plate 5 specified it by name with an audited composition. That composition was right for a page whose squares said nothing. Both tasks want `superseded`, with the successor named.

The counts-and-pointers alternative was considered and rejected: the stat tiles two sections above already carry those counts and navigate, so a counts row would have been a third rendering of the same number. Recorded in [[ISS-0068]] so it is not re-proposed.

Two gaps in the tiles' indication are worth fixing *in the tiles* if they annoy anyone: `triage` is not distinguishable from `open`, and there is no deferred count.
