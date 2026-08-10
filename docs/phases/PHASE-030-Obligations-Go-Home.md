---
type: "[[phase]]"
id: PHASE-030
aliases: ["PHASE-030"]
title: "Obligations go home — every judgment the record owes surfaces where its subject lives, the count is always on screen, and Tests becomes a view"
status: active
order: 30
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
goal: "Move every owed human judgment out of a single queue and into the view that owns its subject, with a count on each view button that together covers every kind — so what needs a person is visible without going to look for it, and the surface that once collected them can be removed without anything becoming unreachable."
features:
  - "[[FEAT-0086-Tests-Becomes-A-View]]"
  - "[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]"
  - "[[FEAT-0088-Features-Carries-Its-Own-Judgments]]"
  - "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]"
  - "[[FEAT-0090-The-Desk-Retires]]"
  - "[[FEAT-0091-The-Standing-Documents]]"
requirements:
  - "[[REQ-0033-Every-Project-Can-Say-What-It-Is]]"
issues:
  - "[[ISS-0121-Reviewed-Register-Counts-Settled-Work-As-Owed]]"
  - "[[ISS-0125-The-Singleton-Documents-Have-No-Lifecycle-And-No-Home]]"
depends: ["[[PHASE-023-Levers-For-The-Human]]"]   # PARTIAL — see "What this phase depends on, precisely"
related: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[PHASE-024-Acceptance-Witnessed]]", "[[PHASE-029-One-Tool-Two-Front-Doors]]", "[[FEAT-0061-Quick-Capture-And-Triage]]", "[[DES-0005-The-Actuator-Grammar]]"]
tags: [surfaces, obligations]
---

# Obligations go home

## Where this came from

[[ADR-0020]], accepted 2026-08-10. Edwin, reviewing the view set: *"I don't think we need the separate review item then anymore ???"*

The desk was built on the premise that obligations belong in one place. Measurement retired two of the three claims holding that up — **zero questions have ever been created** (8 ledger requests in the repo's history, all reviews), and *"am I done?"* needs a **count**, not a page. Meanwhile the desk held two things that were not obligations at all (the tests register, the reviewed register) and omitted the largest one there is: **39 issues at `triage` across the fleet, median age 56 days**, deliberately excluded from `QUEUE_INTAKE_STATES`.

## The order, and why

1. **[[FEAT-0089]] first.** The obligation registry is the single source of *what is owed, of what kind, and which view owns it*. Every other feature consumes it. Building views first would put the vocabulary in four renderers, which is [[ISS-0023]] with a different noun.
2. **[[FEAT-0086]], [[FEAT-0087]], [[FEAT-0088]] and [[FEAT-0061]]'s triage tray** then land in any order, each consuming the registry.
3. **[[FEAT-0090]] last.** The desk is removed only once nothing on it is homeless — which the registry can prove rather than assert.

[[ISS-0121]] is carried here as a member because the reviewed register moves in [[FEAT-0090]], and moving a register that counts settled work as owed would relocate the defect rather than fix it.

## What this phase depends on, precisely

The `depends:` above says [[PHASE-023]] and means **half of this phase**. Written down because the blanket claim already contradicts reality — this phase is `active` while its stated dependency is `planned`.

- **Needs nothing.** [[FEAT-0089]] (the registry — server-side, read-only), [[FEAT-0091]] (standing documents), [[FEAT-0087]] (the Intent view), [[FEAT-0086]] (the Tests view, minus its runs). These *display* obligations; displaying is not writing.
- **Needs [[PHASE-023]].** [[FEAT-0088]] — surfacing requirement approval is only worth doing once [[FEAT-0060]]'s actuator row can perform it. Likewise the triage tray's verbs, which are [[FEAT-0061]]'s.
- **Needs [[FEAT-0071]] from [[PHASE-026]].** [[FEAT-0090]], the retirement itself — see below.

## Exit criteria

- [ ] Every obligation kind is enumerated in one place, with the view that owns it, and no renderer restates the set
- [ ] Each view's badge shows what that view owes, and the badges together cover **every** kind — asserted, so a new kind cannot be added without a home
- [ ] Tests is a view: the register, the manual runner, the tier suite and the release gate. **The gate can fire** — meaning at least one Tier 1 test exists and an unchecked one blocks a release note, which has never been possible in this repo
- [ ] `~review` is gone, and every item, register and control that lived on it is reachable elsewhere — demonstrated by walking the re-homing table in [[ADR-0020]], not by inspection
- [ ] A stored preference or deep link to `~review` migrates rather than stranding the reader
- [ ] `issue: triage` is a first-class obligation with `Defer` available, and the fleet's 39-item pool is visible from the Issues badge
- [ ] No write path widened: [[REQ-0027]]'s guards re-checked, no agent-owned transition reachable
- [ ] The standing documents are declared as data, carry no lifecycle status, and open the Intent view with their freshness visible — and the fleet's 94%-stale figure has an after

## What this phase must not do

**Build a third surface.** [[ISS-0068]] removed the overview's *Waiting on you* because it re-listed items that already had a home. A view grouping its own obligations is regrouping; a second list of the same items anywhere is the failure this phase inherits the lesson about.

**Widen the write surface.** Obligations become more visible, not more actionable-from-anywhere. Actuators stay on the note ([[DES-0005]]), loopback-only ([[REQ-0027]]).

## Superseded on opening

[[DES-0010]] and [[FEAT-0082]] designed a board for `~review`, two days before it was decided the surface should go. Nothing was built. They take `superseded` with a pointer to [[ADR-0020]] — and one of their ideas is carried forward explicitly rather than lost: [[TASK-0357]]'s *"the obligation vocabulary ships in the payload, not in TypeScript"* is what [[FEAT-0089]]'s registry is.

## Widened 2026-08-10 — the standing documents

[[FEAT-0091]] joined after Edwin's observation that some notes *"are one-off notes… we never need more than one and there is not really a state associated with them."*

It belongs here rather than in a phase of its own because **"confirm this is still true" is a judgment the record owes**, which is this phase's subject. A six-month-old style guide is that judgment going unasked, so staleness becomes an obligation kind in [[FEAT-0089]]'s registry, owned by the Intent view [[FEAT-0087]] builds, and badged like every other. It also removes [[ISS-0122]]'s cause rather than re-bucketing its symptom.

## The one cost, and where its mitigation lives

[[ADR-0020]] accepts one cost honestly: discharging judgments becomes up to four visits instead of one. It names the mitigation — [[DES-0008]]'s landing digest, *"since Thu · 14 transitions · 2 need you"*.

**That digest is [[FEAT-0071]], in [[PHASE-026]], and nothing scheduled it.** Retiring the desk before it lands ships the cost without the mitigation, which is how an accepted trade-off becomes an unaccepted regression. [[TASK-0378]] carries the dependency so ordering cannot skip it by accident.
