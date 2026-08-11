---
type: "[[issue]]"
id: ISS-0133
aliases: ["ISS-0133"]
title: "The view badges say a number and not what it counts — the registry knows the kinds, the tooltip discards them, and it is hover-only"
status: fixed
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-11
updated: 2026-08-11
source: ["Edwin, 2026-08-11: 'There is no clear indication what the numbers next to the view icons at the top relate to. For features, design and overview.'"]
severity: medium
component: "cockpit-nav"
parent: ""
related: ["[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[ADR-0020-Obligations-Live-With-Their-Subject]]"]
tests: []
---

# The view badges say a number and not what it counts

## Problem

The top-bar view buttons carry counts — overview 81, design 3, features 4, issues 7 — and nothing on screen says what they are counting. The only affordance is a `title` tooltip, which requires hovering one button at a time and waiting for the browser delay, and when it appears it says:

> `4 items here need a person`

That is the same sentence for every view. It names no kind, so the reader learns that four *somethings* are owed under Features and must open the view to find out what. The counts are the mechanism by which anyone notices there is work at all, and they are currently the least self-describing element on the surface.

**The information exists and is thrown away.** [[FEAT-0089]] built the obligation registry precisely so the kinds would be data rather than a hand-written list — [[ADR-0020]] decision 3 requires the badges to cover every kind, which is only enforceable because each obligation carries its kind and verb. The badge render reads the *total* for a view and drops the breakdown:

```ts
badge.title = `${n} item${n === 1 ? '' : 's'} here need a person`;
```

A badge that said `4 · 2 unreviewed, 1 stale, 1 unaccepted` would be answering the question the number raises, from data already in the payload.

**A second, smaller inconsistency.** The review badge sets `btn.title` (replacing the button's own description) while the mode badges set `badge.title` (a separate hover target inside the button). Two hover behaviours for one control.

## Repro

1. Look at the top bar. Note the numbers next to the view icons.
2. Nothing labels them. Hover one and wait — a generic sentence appears.

## Expected

The number says what it counts, without a hover. At minimum the tooltip names the kinds; better, the view's own header states its owed breakdown so the count is explained where it is acted on rather than only where it is displayed.

## Actual

Hover-only, and generic — the same wording for every view regardless of what is owed.

## Evidence

- `desktop/src/renderer/renderer.ts:3288` — the generic title string.
- `desktop/src/renderer/renderer.ts:3878` — `btn.title` on the review badge, a different hover target.
- Live 2026-08-11: `overview 81 · design 3 · features 4 · issues 7`, total 95 = the registry total.

## Next Actions

- [ ] Decide where the explanation belongs: the tooltip, a legend, or the view's own header. Prefer the last — it survives a touch device, where hover does not exist and the tablet read-path is a stated use of this tool.
- [ ] Render the kind breakdown from the registry rather than a count alone.
- [ ] Make the two badge hover behaviours one.

## Resolution — 2026-08-11

`badges_payload` gained three fields: `breakdown` (per view, `{kind: n}`), `verbs` (the action each kind is owed) and `nouns` (how each kind names itself, singular and plural). The badge composes its own sentence from them.

Live, replacing `N items here need a person` on every view:

| view | before | after |
|---|---|---|
| Overview | `81 items here need a person` | `81 change notes to review` |
| Design | `3 items here need a person` | `2 standing documents to confirm, 1 ADR to decide` |
| Features | `4 items here need a person` | `4 requirements to approve` |
| Issues | `12 items here need a person` | `12 issues to triage` |

**The nouns ship from the server, and that was a correction mid-fix.** The first cut pluralised in the renderer with `kind === 'adr' ? 'ADRs' : kind + 's'`, which is a second vocabulary in TypeScript — the exact thing [[TASK-0357]] forbids and `test_the_renderer_reads_the_count_and_declares_no_kinds` exists to catch. The renderer now picks a string it is handed and owns no plural rule.

**Both halves of the hover inconsistency are closed.** The title moved from the ~14px badge to the button, so hovering anywhere on the control answers the question, and an `aria-label` carries the same sentence. The count resets to the plain description before the early return, so a view whose count drops to zero loses the stale sentence instead of keeping it.

**What is deliberately not done:** the count is still explained on hover rather than in the view's own header. Hover does not exist on the tablet the `0.0.0.0` bind is for, so the header remains the better home — left as a follow-up rather than smuggled into a bug fix.

Guarded by `test_the_breakdown_explains_the_badge_and_sums_to_it` (a breakdown that disagrees with its count is one number contradicting itself on one screen) and `test_every_owed_kind_can_name_itself_and_its_verb` (asserted over the registry, so a kind added later fails in the suite rather than on screen).
