---
type: "[[issue]]"
id: ISS-0077
aliases: ["ISS-0077"]
title: "Nine phases opened in one day against nine in the preceding twelve weeks — a phase became the unit of a request rather than of a delivery push, at a fifth of the historical size"
status: fixed
severity: medium
phase: "[[PHASE-016-The-Overview-Answers-Questions]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["Edwin 2026-07-30: 'Let's review the phase granularity, suggest how to consolidate'"]
component: docs-system
related: ["[[PHASE-015-Phase-Hygiene]]", "[[ISS-0074-Sixteen-Delivered-Notes-Stranded-In-The-Parking-Lot]]"]
fixed_by: ["[[PHASE-016-The-Overview-Answers-Questions]]"]
tests: []
---

# A phase became the unit of a request

## Measured

| Era | Phases | Items per phase |
|---|---|---|
| PHASE-001…009, ~12 weeks | 9 | 15, 61, 1, 7, 10, 65, 123, 21, 43 — median **21** |
| PHASE-011…019, **one day** | 9 | 12, 4, 12, 6, 2, 4, 4, 5, 1 — median **4** |

Same count as the preceding twelve weeks, at a fifth of the size.

## The line inside today

- **PHASE-011 / 012 / 013 were planned together**, in one commit (`0f7b2bc`), before any of the work — Edwin asked for a review of the open set and a phase proposal. 12, 4 and 12 items. Normal.
- **PHASE-014 through 019 were each created reactively**, one per request, as the conversation went.

## Cause

The document-first rule needs a focus item before code changes. An open phase is the cheapest way to get one, so every new request minted a phase rather than finding a home for the work.

That is **a phase used as the unit of a thing asked for, rather than of a delivery push.**

At four items a phase, both of a phase's jobs fail. Its gate is trivial — `PHASE-CHILDREN` over four notes is not a gate. And the overview's phase strip now has twenty rows, each saying almost nothing, which is the opposite of what that strip is for.

## Expected

A phase is a body of work with a goal statable without listing its parts. Single requests, single issues and same-session fixes belong to a **standing** phase for the surface they touch — which is what [[PHASE-019]] accidentally became.

## Next Actions

- [x] Merge PHASE-016..019 — one push, four phases
- [x] Leave PHASE-013 (planned, own subject), PHASE-014 (retrospective, dated earlier), PHASE-015 (records, not overview)
- [x] Touch nothing before PHASE-013
- [x] Write the rule for when a phase is opened, and when it is too small
- [x] Propose the rule upstream — `LIFECYCLE.md` says when a phase note is *needed* and never when one is *too small*

## Notes

Not a defect in the system — a drift in how I used it, visible only once someone counted. Worth recording that the previous phase ([[PHASE-015]]) was itself about phases carrying the wrong answer, and this is the same field carrying the wrong *granularity*.


## Fixed 2026-07-30

### The merge

**19 phases → 16.** PHASE-016 widened from *"Errors become work"* to **"The overview answers questions"** and absorbed [[PHASE-017]], [[PHASE-018]] and [[PHASE-019]]:

| leg | delivered |
|---|---|
| errors | a validator count became rows in the session's work list, and issues at close-out |
| history | the history band became document state changes, with commits as dividers |
| navigation | a contribution grid whose days are destinations, and History in the rail |
| legibility | the phase rows say which phase they are |

**14 items**, against today's median of 4 and the historical median of 21.

Nothing was deleted. The three absorbed phases are `superseded` with `superseded_by`, each note kept as the record of its leg; ten notes were re-homed **before** the supersede, because a superseded phase with children still naming it fires `PHASE-CHILDREN`.

**Left alone, with reasons:** [[PHASE-013]] (planned in advance, own subject), [[PHASE-014]] (retrospective — folding it into today would misdate 2026-07-28 work), [[PHASE-015]] (a records correction, not an overview change). Nothing before PHASE-013 was touched.

### The rule

In `CLAUDE.md`, because `tools/instructions/LIFECYCLE.md` is template-owned and a sync would report the edit as divergence:

> Open a phase when its goal is statable **without listing its parts**, and its exit criteria are something other than **"the tasks are done"**. Otherwise use an `ISS-*` or a task in a **standing phase** for the surface. A phase closing with ≤3 items is a signal, not a small success.

**The standing phase is the actual fix.** The rest is advice; that is a mechanism. Without somewhere to put a small thing, minting a phase is the only move that satisfies the document-first hook — which is why this was structural rather than careless.

Three guards: no note may name a superseded phase, a superseded phase must say what absorbed it, and the rule must stay written down. All mutation-verified.

Proposed upstream as `project-os-dev` ISS-0029, including a `PHASE-THIN` **warning** at close-out — a warning rather than an error, because small phases are sometimes right and the point is to make the author look.

### What this does not fix

The incentive is still there. The rule tells me where to put small work; it does not stop the hook from wanting a focus item. If the standing phases fill up with unrelated fixes, that is the same drift wearing a different shape, and the next count will show it.
