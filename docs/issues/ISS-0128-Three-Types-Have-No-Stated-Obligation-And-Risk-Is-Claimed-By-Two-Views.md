---
type: "[[issue]]"
id: ISS-0128
aliases: ["ISS-0128"]
title: "Risk is claimed by two views at once, and risk / workflow / phase each carry a candidate obligation nothing has decided about"
status: triage
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["Session 2026-08-10: Edwin asked for a full sweep of the ticket types against the desk's re-homing table, after `change` and `release` were each found missing by the same question"]
severity: medium
component: "docs-taxonomy"
parent: ""
related: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[TASK-0369-The-Obligation-Registry]]", "[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]", "[[REQ-0025-No-Type-Loses-Its-Surface]]"]
tests: []
---

# Three types have no stated obligation, and risk is claimed by two views

## How this was found

[[ADR-0020]] re-homed the review desk's contents. Its table was drawn **from what was on the desk**, so anything never on the desk was invisible from where the table was written. `change` and `release` were each found missing by Edwin asking about them, and each cost an amendment.

A full sweep of all 17 note types found three more, plus a conflict.

## 1. `risk` is claimed by two views

All six risk notes render **today** in the Issues navigator:

```
Risks · high · 3     Risks · medium · 2     Risks · low · 1
```

And [[FEAT-0087]]'s scope lists `risk (6)` in the Intent view's membership.

Two views, six notes, and neither note mentions the other. The Intent membership was written from a type list; the Issues placement came from [[ISS-0063]], where the overview's Risks tile navigated nowhere and was pointed at Issues. Both are defensible in isolation:

- **Issues** — a risk is a problem you might have, which is the same question Issues answers.
- **Intent** — a risk is a standing constraint on the project, alongside ADRs.

This needs deciding, not merging. One type, one owning view — otherwise the badge counts it twice or neither.

## 2. Does an `open` risk carry an obligation?

**All six risks are `open`.** None has ever moved. `mitigating` exists in the vocabulary and is unused here.

If an open risk is an obligation, its verb is something like *mitigate* or *accept*, and there is a `risk-mitigation-planning` skill that describes the work. If it is not, then `open` is the resting state of a risk and six of six sitting there forever is correct. Nothing says which.

## 3. Does a `draft` workflow carry one?

**All three workflows are `draft`** and have never advanced. `draft` on a requirement *is* an obligation — approve it — and that asymmetry is unexplained. Either a workflow's `draft` means the same thing and nobody has ever discharged it, or it means "this is how we work" and `draft` is simply the wrong resting value.

## 4. Where does phase close-out surface?

Closing a phase is a judgment, and the machinery for it exists: `phase_close_blockers()`, the `unclosed: true` computation, the "close out" pill, and `CLAUDE.md`'s rule that *a phase that never closes but whose work is finished will always look like a phase someone forgot*.

**Zero phases are currently due for closing** — which is exactly how `change` and `release` hid. A kind that is empty today is indistinguishable from a kind that does not exist. The Overview is the obvious home, since the phase accordion is already there, but nothing says so.

## Not a gap: task and plan

`task` (381) and `plan` (52) owe nothing, correctly. Tasks are agent-owned end to end; a plan's status follows its parent feature, which is why plans were removed from the desk queue in July.

That is right, and **it is what an omission looks like from the outside**. [[TASK-0369]] now requires both to declare `none` *with the reason*, so the completeness test can tell deliberate silence from something forgotten.

## The structural fix is already applied

[[TASK-0369]] was amended in the same pass: the registry enumerates **by note type** rather than by obligation kind, every type declares a kind or an explicit `none`, and a type present in the corpus with neither fails a test. That is what would have caught all five of these — `change`, `release`, and the three here — without anyone asking.

This issue is the remaining **content** decisions, which a test cannot make.

## Answered 2026-08-10 — two of four

**1. `risk` is surfaced in Intent.** Edwin: *"Risk should be surfaced in intent."* One type, one owning view — so the six risks leave the Issues navigator's `Risks · high/medium/low` cards and join the constraints view. That reading was the stronger one: a risk is a standing constraint on the project, alongside ADRs, rather than a problem you have.

**2. An `open` risk is not an obligation.** Edwin: *"An open risk is not necessarily an obligation, the risk might never materialize."*

This is the more interesting answer, because it says something the measurement could not. All six risks have sat at `open` since they were written, and the tempting reading was that six items had been ignored for months. They have not: **`open` is a risk's resting state.** A risk is a thing you have decided to *carry*, and carrying it is not a debt — the hazard may simply never arrive.

So `risk` declares an owning view and **`none` for its obligation**, with that reason. Which makes it the first entry to exercise [[TASK-0369]]'s requirement that a `none` be explicit and carry its justification: without the reason written down, six untouched notes look exactly like six forgotten ones.

### Still open

**3. Does a `draft` workflow carry an obligation?** All three workflows are `draft` and have never advanced. `draft` on a requirement *is* an obligation — approve it — and the asymmetry is unexplained. Either a workflow's `draft` means the same and nobody has discharged it, or `draft` is simply the wrong resting value for a workflow, the way `open` turns out to be the right one for a risk.

**4. Where does phase close-out surface?** The machinery exists — `phase_close_blockers()`, the `unclosed` computation, the "close out" pill. Zero phases are currently due, which is exactly how `change` and `release` hid. The Overview is the obvious home since the phase accordion is already there.

## Next Actions

- [x] Decide `risk`'s owning view — **Intent** (Edwin, 2026-08-10); Issues drops its Risks cards
- [x] Decide whether `open` risk is an obligation — **no**: `open` is a risk's resting state, and carrying a hazard is not a debt
- [ ] Decide whether `draft` workflow is an obligation, or whether `draft` is the wrong resting status for a workflow
- [ ] Home phase close-out, most likely the Overview, and record it even though nothing is currently due
- [ ] Fold all four answers into [[TASK-0369]]'s registry declarations
