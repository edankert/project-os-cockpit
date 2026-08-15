---
type: "[[phase]]"
id: PHASE-030
aliases: ["PHASE-030"]
title: "Obligations go home — every judgment the record owes surfaces where its subject lives, the count is always on screen, and Tests becomes a view"
status: done
order: 30
owner: user:edwin
created: 2026-08-10
updated: "2026-08-14"
goal: "Move every owed human judgment out of a single queue and into the view that owns its subject, with a count on each view button that together covers every kind — so what needs a person is visible without going to look for it, and the surface that once collected them can be removed without anything becoming unreachable."
features:
  - "[[FEAT-0086-Tests-Becomes-A-View]]"
  - "[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]"
  - "[[FEAT-0088-Features-Carries-Its-Own-Judgments]]"
  - "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]"
  - "[[FEAT-0090-The-Desk-Retires]]"
  - "[[FEAT-0091-The-Standing-Documents]]"
  - "[[FEAT-0100-Unpushed-Work-Needs-A-Person]]"
requirements:
  - "[[REQ-0033-Every-Project-Can-Say-What-It-Is]]"
issues:
  - "[[ISS-0121-Reviewed-Register-Counts-Settled-Work-As-Owed]]"
  - "[[ISS-0125-The-Singleton-Documents-Have-No-Lifecycle-And-No-Home]]"
  - "[[ISS-0156-The-Open-Workspace-Is-The-One-Whose-Unpushed-Count-Is-Never-Computed]]"
depends: ["[[PHASE-023-Levers-For-The-Human]]"]   # PARTIAL — see "What this phase depends on, precisely"
related: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[DES-0011-Publication-Is-An-Obligation]]", "[[PHASE-024-Acceptance-Witnessed]]", "[[PHASE-029-One-Tool-Two-Front-Doors]]", "[[FEAT-0061-Quick-Capture-And-Triage]]", "[[DES-0005-The-Actuator-Grammar]]"]
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

Walked 2026-08-13 against the live corpus and the running app, not from the notes that claimed them.

- [x] Every obligation kind is enumerated in one place, with the view that owns it, and no renderer restates the set — `obligations.OBLIGATIONS` by note type plus `NOTE_LESS` for the three whose subject is not a note; the renderer maps view names to buttons and owns no vocabulary ([[TASK-0357]]'s rule)
- [x] Each view's badge shows what that view owes, and the badges together cover **every** kind — `badges_payload`'s total is the sum of its breakdown by construction, and `test_the_page_and_the_badge_are_one_computation` asserts the page and the button are one walk
- [x] Tests is a view: the register, the manual runner, the tier suite and the release gate. **The gate can fire** — 27 Tier 1 and 7 Tier 2 items today, one Tier 1 unchecked; it was 34 unchecked when [[FEAT-0086]] closed, which is the gate working rather than sitting
- [~] `~review` is gone, and every item, register and control that lived on it is reachable elsewhere — **the walk is done and the mode and button are gone; the route stays served.** [[FEAT-0090]] reconciled this at its own close: the agent ledger has one OPEN entry, [[ISS-0126]] owns where those flows land, and deleting the display would strand it. Recorded here rather than ticked, because the criterion says *gone* and it is not
- [x] A stored preference or deep link to `~review` migrates rather than stranding the reader — `RETIRED_NAV_MODES` carries `review → overview`, and `~review/<id>/run` intercepts to `~tests/<id>/run` before the fallback, so the runner has one entry point rather than two
- [x] `issue: triage` is a first-class obligation with `Defer` available, and the fleet's triage pool is visible — declared as `('triage',) → issues`, verb `Triage`; and since [[TASK-0419]] the pool is visible **per project across the fleet** on the attention cards, which is a stronger answer than the per-project badge this criterion was written against
- [x] No write path widened: [[REQ-0027]]'s guards re-checked, no agent-owned transition reachable — `test_every_note_mutating_endpoint_requires_loopback` still enumerates and still passes; [[ADR-0027]] widened what the registry *counts*, never what may write
- [x] The standing documents are declared as data, carry no lifecycle status, and open the Intent view with their freshness visible — ten members resolve, **every one reports `current`**, and none of the eight originals carries a `status:` field. The fleet's 94%-stale figure has an after, and [[ISS-0125]] closed on that evidence rather than on the plan
- [x] An obligation whose subject is **not a note** goes through the same declared path as one whose subject is, yields its count and its rows from one walk, and is covered by the completeness test — [[TASK-0416]], with **three** such sources now (standing documents, unpushed commits, undeployed commits) where the criterion asked for two
- [x] No obligation is admitted whose count can be *unknown* ([[ADR-0027]] test 4) — [[ISS-0156]] was exactly that failure and is fixed: git state is probed for every workspace on one clock, so absence on a badge means nothing is owed and the surface can prove it

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

## Widened 2026-08-13 — publication is an obligation

[[FEAT-0100]] joined after Edwin found the tool silent about this repo's own unpushed work, and then chose where the answer should live: *"add the git status to the needs you section… have the actual push solution in the overview history… an indication of having to push using a number on the overview icon."*

It belongs here for the same reason [[FEAT-0091]] did, and by the same argument. This phase's subject is *what needs a person, visible without going to look for it*, and [[ADR-0022]] made the human the publisher of last resort — so *"three commits are unpushed"* is exactly that, and it was outside the registry only because the registry's stated scope was **judgments about the record**. [[ADR-0027]] widens the scope to **what needs a person**, with four admission tests so the badge does not become a notification centre.

Two things fall out of the widening, and both are this phase's:

- **The note-less obligation path stops being a bolt-on.** [[FEAT-0091]]'s standing document was the first obligation whose subject is not a note, carried by two special cases whose seam already produced *"Intent's group came out 3 against a badge of 5"*. [[TASK-0416]] generalises it and ports standing to it — a repair to what this phase already built, before anything new is added on top.
- **Absent-at-zero makes unknown a defect.** [[ISS-0156]] joins the phase because the badge cannot show what the shell does not know, and a missing count is indistinguishable from nothing owed. It is the first task, not a caveat.

**This does not build a third surface.** The row appears in `Needs you` and in history, which is [[ADR-0025]]'s already-decided shortcut-plus-structural-place, not [[ISS-0068]]'s duplicate list.

## Closed — 2026-08-13

Every member resolved: seven features `done`, [[REQ-0033]] `implemented`, and all three issues `fixed` — [[ISS-0121]], [[ISS-0125]] and [[ISS-0156]], the last two closed during this close-out on evidence rather than on their plans.

**The phase was widened twice and both widenings paid.** [[FEAT-0091]]'s standing documents made *"confirm this is still true"* an obligation, and [[FEAT-0100]]'s publication made *"send this"* one — and it was the second that forced the repair the first had made necessary: the note-less obligation was a bolt-on with a seam that had already produced a badge disagreeing with its own group, and adding a second such obligation without fixing it would have made three.

**One criterion is reconciled rather than met**, and it is the phase's title in miniature. `~review` is not gone; its mode and button are, its registers re-homed, its deep links migrate, and the page stays served for one open ledger entry that [[ISS-0126]] owns. [[FEAT-0090]] recorded that at its own close, in the same words, which is why this close-out found it in a note rather than in the code.

**One member was re-homed rather than closed over.** [[ISS-0130]] — nine automated tests that cannot say how to run themselves — named this phase and was still open. It was never this phase's work: the subject here is what needs a person and where it surfaces, and that is about whether a machine can re-run a test. It landed here because it was found while [[FEAT-0086]] was building the Tests view. It goes to [[PHASE-999]], because nothing schedules it and saying so is better than parking it under a phase that has finished. The validator caught it; the phase's own membership list did not have it.

**What the phase leaves for someone else**, named rather than implied:

- The digest's `needs_you_count` walks the corpus itself with `_owed_flag` instead of reading the registry — a **third** enumeration of what is owed, which is the class this phase exists to end. Found while building [[TASK-0418]]; not filed as an issue yet.
- [[DES-0011]] is `accepted` on an artifact captured from the built surface, and is the first design in this corpus to declare no palette of its own — [[ISS-0136]] measures five of nine hard-coding a dark one.
- [[FEAT-0100]] reached `done` without an independent review pass. `QUALITY.md` asks for one on a feature transition; the validator does not gate it, so it is owed and stated here rather than assumed away.

## Reopened — 2026-08-14

[[FEAT-0100]] came out of `done` on an independent review that returned changes-requested, and a `done` phase may not hold an unresolved child (`PHASE-CHILDREN`). Reopening is the honest move rather than re-homing the feature: this phase is where publication became an obligation, and the findings are about that work.

It closes again when FEAT-0100 does. The [[ISS-0077]] rule applies — reopening is cheap, and a phase whose status means what it says at every moment is the point.

## Closed again — 2026-08-14

Edwin: *"Close off the phase 030."* [[FEAT-0100]] was the only unresolved child of 69, so the debt it carried had to clear rather than be carried past a closing phase. **69 children, all resolved**: 12 features `done`, [[REQ-0033]] `implemented`, 21 issues `fixed`, 33 tasks `done` and 2 `cancelled`, [[ADR-0027]] `accepted`, [[DES-0011]] `accepted`.

**The reopen paid for itself twice.** The first review found the dismissal defect; this close-out re-tested its own finding 3 rather than trusting the earlier repair, and found it still substantially open — mutating `_publication_rows` to `return []` left **1281 tests passing**, with one failure that was about the *unknown* case and said nothing about the counted one. The registry's central kind was still unasserted seventeen days after the registry shipped. It is asserted now.

**27 Definition-of-Done boxes were resolved across [[TASK-0417]], [[TASK-0419]] and [[TASK-0420]]** — three tasks that reached `done` with every box unticked. Twenty-six ticked with evidence, one marked `[~]`: TASK-0417's *"the overview's `Needs you` group carries a row"*, which is not deliverable because `overview` is not a nav mode. [[TASK-0419]] had no test of any kind; the two its own DoD asked for were written here, and the first draft of one was too weak to catch the mutation it existed for.

**The `[~]` exit criterion above stands, and was re-checked rather than assumed.** `~review` is still served: the ledger holds **2 open entries** today (one on [[DES-0009]]), so deleting the display would still strand them. [[ISS-0126]] is `fixed`, which resolves the flows but not the entries.

**One drift found while closing:** `docs/PHASES.md` read `done` for this phase throughout the reopen. `sync-snapshot.py` propagates status into `SNAPSHOT.yaml` but **not** into `PHASES.md`, which is hand-maintained — so reopening a phase updates two of the three places by itself and the registry silently keeps the old answer. The two agree again now, and the gap is the same one [[ISS-0077]]'s merge instructions already warn about for `phase:` entries.

**Of the three things this phase left for someone else, one is closed and two stand:**

- The digest's third enumeration of what is owed — **closed**, by [[ISS-0159]]. `digest_payload` reads `obligations.owed_items` now; the phase's own note predicted this class and the fix landed after it was written.
- [[DES-0011]]'s palette — stands, with [[ISS-0136]].
- **The independent review gate — stands, and is this phase's one unpaid obligation at close.** It is the same debt the pre-reopen close recorded, and the reason that close was wrong. Recorded again in the same words rather than assumed away: `QUALITY.md` asks for a clean-context pass on a feature reaching `done`, the validator does not gate it, and FEAT-0100 returns to `done` here without one. Its `review_verdict` is still the 2026-08-14 `changes-requested`; [[ISS-0121]]'s discriminator makes that stamp settled rather than owed, because the subject's current status decides — but a settled stamp is not a fresh judgment, and this note should not pretend otherwise.
