---
type: "[[issue]]"
id: ISS-0126
aliases: ["ISS-0126"]
title: "FEAT-0062 builds two verbs onto the surface ADR-0020 retires, for one state that is empty after ISS-0121 and one that has never occurred"
status: fixed
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-11
source: ["Session 2026-08-10: reviewing all open phases for implementation order"]
severity: medium
component: "review-desk"
parent: ""
related: ["[[FEAT-0062-Desk-Resolution-Flows]]", "[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[ISS-0121-Reviewed-Register-Counts-Settled-Work-As-Owed]]", "[[FEAT-0090-The-Desk-Retires]]"]
tests: []
---

# Desk resolution flows target a retired surface and two empty states

## Problem

[[FEAT-0062]] is `planned` in [[PHASE-023]] with two tasks. Its goal, verbatim:

> Every obligation **the desk shows** has its resolution on the same surface: request re-review dispatches the reviewer with the note and its prior findings; answering a question writes the answer where the asking agent will read it.

Three things have happened since it was written on 2026-08-03:

1. **[[ADR-0020]] retires the desk** (accepted 2026-08-10). "The same surface" will not exist; [[FEAT-0090]] removes it.
2. **The re-review state is empty.** [[ISS-0121]] measured all ten `Changes requested` rows as terminal — genuinely owed: 0 — and the state was absent from every other fleet repo measured.
3. **The question state has never occurred.** Zero questions across 8 ledger requests in the repo's history, and [[ADR-0020]] decision 6 drops questions deliberately rather than building a surface for them.

So both verbs point at a surface being removed, for one state that is empty once its defect is fixed and one that has never been written.

## Why this needs deciding before PHASE-023 runs

[[PHASE-023]] is the keystone — six phases depend on it — and [[FEAT-0062]] is one of its four features. Reaching it mid-phase and discovering it builds onto something retired costs the phase its momentum and invites a rushed answer. Deciding now costs one triage.

## The options

- **Cancel it.** Both verbs address states that do not occur. The dispatch machinery it would use already exists and is not lost.
- **Keep re-review, re-pointed.** A `changes-requested` note whose subject is *not* terminal is a genuine obligation — [[ISS-0121]]'s fix must preserve exactly that inverse case. If it occurs, it now surfaces in the view owning the note's type, not on a desk. The verb would move to [[FEAT-0088]] or wherever that type lives.
- **Keep answer, deferred.** [[ADR-0020]] says if a question ever occurs, [[FEAT-0062]] decides where it goes — *as a decision, not a discovery*. That sentence already anticipates this issue.

## Expected

A feature in the keystone phase either builds something that will exist, or says why it is being kept.

## Actual

It is `planned`, unchanged since before the decision that removes its subject.

## Next Actions

- [ ] Decide: cancel, re-point re-review at the owning view, or keep and defer
- [ ] If cancelled, record what survives — the dispatch machinery and [[ISS-0121]]'s inverse case are both real and independent of this feature
- [ ] Update [[PHASE-023]]'s feature list so the phase's scope matches what it will build

## Re-measured 2026-08-11 — the evidence is unchanged, and this is the last thing holding PHASE-023

Working [[REL-0001]]'s leg 2, [[PHASE-023]] reduced to **exactly this decision**: its only unresolved children are [[FEAT-0062]], its two tasks, and this issue. [[RISK-0005]] closed today, so nothing else stands between the keystone phase and `done`.

Both states re-counted against the live corpus:

| state | count |
|---|---|
| `changes-requested` notes | 10 |
| …whose subject is **not** terminal — the genuine obligation | **0** |
| review-ledger entries | 8 |
| …of kind `question` | **0** |

So the position is exactly as filed on 2026-08-10, with a day's more evidence and the desk now actually gone ([[FEAT-0090]] shipped).

**Not decided here, deliberately.** The snapshot records this as *"BLOCKED PENDING A HUMAN DECISION, do not guess"*, and cancelling a feature in the keystone phase is a scope call with an owner. Cancelling is reversible — the note stays, `cancelled` is a status — but it is still Edwin's.

**What the record points at**, stated so the decision is one reading rather than a re-investigation: *cancel it, and keep the inverse case*. Both verbs address states that do not occur, on a surface that no longer exists. The one thing worth preserving is the case [[ISS-0121]]'s fix already preserves — a `changes-requested` note whose subject is **not** terminal is a genuine obligation, and if one ever appears it surfaces in the view owning that note's type, which is where [[ADR-0020]] puts it. The dispatch machinery FEAT-0062 would have used already exists and is not lost.

Once answered, PHASE-023 closes with its exit criteria in the same pass.

## Resolved — 2026-08-11

**Edwin's decision: cancel [[FEAT-0062]].** Done — the feature and both its tasks ([[TASK-0285]], [[TASK-0286]]) are `cancelled`, with the reasoning on the feature note.

### Why `fixed` rather than `declined`

Set to `declined` first, then corrected. The distinction is not bookkeeping:

- **`declined`** is *deliberate no-action, keep the note* — right if FEAT-0062 had been left standing and this issue closed with a shrug.
- **`fixed`** is what happened. This issue reported a defect in the record — a `planned` feature in the keystone phase aimed at a surface [[ADR-0020]] had removed — and asked for one of three outcomes. It got one, and **the record changed as a result**: three notes moved to `cancelled`.

An issue whose report caused a correction is fixed, whatever shape the correction took. Cancelling was the fix.

The note stays, as every terminal note does, because the argument for *not* building it is the durable part.
