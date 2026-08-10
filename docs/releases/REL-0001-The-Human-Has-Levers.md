---
type: "[[release]]"
id: REL-0001
aliases: ["REL-0001"]
title: "The human has levers, and every surface says what it owes"
status: draft
version: ""
tag: ""
date: ""
platform:
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
features: ["[[FEAT-0085-The-Navigator-Shows-The-Structure-The-Record-Has]]", "[[FEAT-0059-The-Write-Service-Widens]]", "[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]", "[[FEAT-0061-Quick-Capture-And-Triage]]", "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[FEAT-0091-The-Standing-Documents]]", "[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]", "[[FEAT-0086-Tests-Becomes-A-View]]", "[[FEAT-0088-Features-Carries-Its-Own-Judgments]]", "[[FEAT-0071-Since-You-Looked]]", "[[FEAT-0090-The-Desk-Retires]]"]
changes: []
tests_verified: []
previous_release: ""
related: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[ISS-0127-The-Charter-Is-Scheduled-By-Its-Consumer-Not-Its-Value]]", "[[PHASE-023-Levers-For-The-Human]]", "[[PHASE-030-Obligations-Go-Home]]"]
tags: [release]
---

# The human has levers, and every surface says what it owes

**The first release note this project has written.** `counters.REL` has read `0` for six months across 85 features — not because nothing shipped, but because nothing ever drew a line around a shippable state. This draws one.

## What this release is

One sentence: **a person can see every judgment the record owes them, in the place that owns it, and can make it without asking an agent.**

Two findings produced it. [[PHASE-023]]'s: *every transition in the ownership table is agent-owned; the cockpit's only actuator is asking an agent in the terminal.* And [[ADR-0020]]'s: the surface built to collect those judgments held two things that were not obligations and omitted the largest one there is.

## Scope

### Features Included

| ID | Title | Status | From |
|---|---|---|---|
| FEAT-0085 | The navigator shows the structure the record has | done | PHASE-022 |
| FEAT-0059 | note_writes widens — the transition table as data | done | PHASE-023 |
| FEAT-0060 | The actuator row on the note | done | PHASE-023 |
| FEAT-0061 | Quick capture and the triage tray | done | PHASE-023 |
| FEAT-0089 | The obligation registry and the badges | done | PHASE-030 |
| FEAT-0091 | The standing documents | done | PHASE-030 |
| FEAT-0087 | Design widens into the project's constraints (Intent) | done | PHASE-030 |
| FEAT-0086 | Tests becomes a view | done | PHASE-030 |
| FEAT-0088 | Features carries its own judgments | done | PHASE-030 |
| FEAT-0071 | Since you looked — the watermark and digest | done | PHASE-026 |
| FEAT-0090 | The desk retires | done | PHASE-030 |

Order is the implementation order, not the table's convenience — see below.

**All eleven are `done` as of 2026-08-10.** Implemented in the stated order across two sessions; each feature's own note carries what it found.

### Features NOT Included (deferred)

| ID | Title | Status | Reason |
|---|---|---|---|
| FEAT-0062 | Desk resolution flows | planned | Targets a surface this release retires; [[ISS-0126]] decides whether it survives at all |
| FEAT-0063..0066 | Acceptance runner, gate, debt, visual evidence | planned | PHASE-024. [[FEAT-0086]] gives the runner its home here; building it is the next release |
| FEAT-0067..0070 | The design bench | planned | PHASE-025. Self-contained; defers at no cost |
| FEAT-0072, FEAT-0073 | Release surface, one voice | planned | PHASE-026 remainder. **See the caveat below** — the release surface being deferred is why this note is maintained by hand |
| FEAT-0074..0077 | The standing worker | planned | PHASE-027. Biggest bet, most dependencies, deliberately last |
| FEAT-0083, FEAT-0084 | The browser front door | planned | PHASE-029, gated on [[ADR-0010]] which is still `proposed` |

### Issues Fixed

| ID | Title | Severity |
|---|---|---|
| ISS-0121 | The reviewed register counts settled work as owed | medium |
| ISS-0125 | The singleton documents have no lifecycle and no home | medium |
| ISS-0124 | Four note types have no status table | low |

### Known Issues (shipping with)

| ID | Title | Severity | Notes |
|---|---|---|---|
| ISS-0122 | Active mode's `Doing` counts notes nobody is working | medium | [[FEAT-0091]] removes the cause; the mode itself may simply retire |
| ISS-0123 | The upstream ADR namespace is cited but absent | medium | 26 files cite `ADR-0011`, which exists nowhere; unrelated to this scope |
| ISS-0120 | The gate's own severity is untested | medium | Repo-wide sweep, not this release |

## Implementation order

1. **[[ISS-0121]]** — smallest, unblocked, and stops a live surface stating something false
2. **[[FEAT-0085]]** — closes PHASE-022, taking three active phases down to two
3. **[[FEAT-0059]] → [[FEAT-0060]] → [[FEAT-0061]]** — the keystone; six phases depend on PHASE-023
4. **[[FEAT-0089]]** — the registry; can run in parallel from the start, it needs nothing
5. **[[FEAT-0091]] + [[FEAT-0087]]** — display only, no write path, and the clearest available win
6. **[[FEAT-0086]]** — the largest new capability, and where the release gate becomes possible
7. **[[FEAT-0088]]** — needs step 3 to be worth doing
8. **[[FEAT-0071]]** — the digest, **before** the desk goes
9. **[[FEAT-0090]]** — last, and only once the registry can prove nothing is homeless

## Verification

### Acceptance Tests

**None exist yet, and that is a scope item rather than an omission.** The Tier 1/2/3 contract in `tools/instructions/TESTING.md` has never been instantiated in this repo — 85 features, 23 test notes, zero tier classification, and a release gate that has never been able to fire. [[FEAT-0086]] / [[TASK-0373]] creates the suite.

So this release is **drafted at step 1 and gated at step 6**. Until then its verification section is honestly empty, not passing.

- **Tier 1 (Feature Tests):** to be created by [[TASK-0373]]
- **Tier 2 (Regression Tests):** to be created — [[ISS-0121]], [[ISS-0125]] and [[ISS-0124]] each want one
- **Tier 3 (Verification Tests):** n/a

### Unit Tests

Existing suite, currently green. Each feature adds its own; [[FEAT-0089]]'s badge-total assertion and [[FEAT-0090]]'s "badge total equals registry total with no desk present" are the two that guard the release's central claim.

### Build

Not applicable — this is not a versioned artifact. The "release" here is a stated, gated, shippable state of the record and the tool, which is what makes the gate meaningful.

## Notes

### What this release does not claim

It does not claim the record is *correct*. [[FEAT-0091]] makes the 94%-stale standing documents visible; it does not make them true. Twelve are still template stubs fleet-wide. Visibility is the deliverable.

### Landed 2026-08-10 — and the gate is red

Eleven features, in the release's own order. What the sessions found, rather than what they built, is the part worth keeping:

- **Surfaces asserting things that were not true**, found by measurement rather than by report: 10 false *Changes requested* rows (all terminal), 8 of 8 badge kinds where a hand-written list had 6, an issue draft two records described and nothing produced, a `Risks` tile pointing at a pane its type had left, and two staleness rules disagreeing by 30 days and a field.
- **[[ISS-0056]] had been quietly re-opened** by [[FEAT-0059]]'s generic transition table — a design could have been accepted with no `design_revision`. Unreachable only because no design here has ever been `proposed`.
- **The tier contract had never been instantiated anywhere.** 92 `TST-*` notes across twelve repos, zero tier classification, a release gate that had never been able to fire.

**It fires now, and it blocks this release.** `docs/tests/ACCEPTANCE_TESTS.md` holds 27 Tier 1 and 7 Tier 2 items, every one unchecked, because nothing in it has been walked. Per `tools/instructions/TESTING.md`: *"a release is blocked while any Tier 1/Tier 2 test is unchecked (exceptions must be documented in the release note)."*

This note therefore stays `draft`. **No exceptions are claimed** — the honest state is that the code is done, the record is closed, and the manual acceptance pass has not been run. A green gate here would have meant nothing, since the suite that produces it was created the same day.

### Release verification, run 2026-08-10

`tools/skills/release-verification/SKILL.md`, against the eleven features in scope.

**Step 7 — automated re-runs.** Thirteen of the 23 `TST-*` notes resolve to an entrypoint and were re-run against the code as it stands today; all thirteen pass and carry `last_run: 2026-08-10` with the command and its output in their `## Runs` log. That closes the two genuinely `STALE` rows in the matrix — TST-0001 and TST-0002 were last verified 2026-05-08, 94 days, and the Tests view's `Stale` group is now empty rather than argued away.

**Step 7 — what could not be re-run.** Ten notes declare no entrypoint. One (TST-0011) is correctly manual. The other **nine are automated pytest modules that run green in `pytest -q` and cannot say so** — filed as [[ISS-0130]]. That is a real finding of the verification step rather than an obstacle to it: the gate exists to catch stale evidence, and evidence that cannot be refreshed by machine is the case it cannot see.

**Step 5/6 — the tier gate.** 27 Tier 1 and 7 Tier 2 items, **all unchecked**. Per `TESTING.md` and the skill's step 6: *release blocked, 34 tests need attention.* Each needs a **first run**, and every one is a manual procedure — the skill's step 7.2 is explicit that a manual test is *"presented to the user for execution"*.

**No exceptions are claimed, and that is a decision.** The contract permits a test to be marked a release exception *"if it cannot be completed"*, documented with justification. Thirty-four of them can be completed; they simply have not been. Granting myself exceptions to clear a gate created the same day would hollow it out on its first use — which is the one thing that would make this feature worse than not having built it.

So the release stays `draft`, which `STATUSES.md` defines as *"prepared and verified, not yet live"* — prepared, and awaiting the half of the verification that is a person's.

### Two acceptance criteria reconciled rather than ticked

- **[[FEAT-0090]]**: the desk's button and mode are gone and migrate; the **route stays served**. `.cockpit/review-requests.json` holds one OPEN entry, and retiring the route would strand it. Where proposals, questions and offered designs land is [[ISS-0126]] — one of the four decisions this note reserves.
- **[[FEAT-0088]]**: a feature at `acceptance: requested` is marked but offers no run, because [[FEAT-0063]]'s runner does not exist. A door to nothing teaches the reader the feature works.

### Still reserved for Edwin

Unchanged, and none of them blocked the work: [[ISS-0126]], [[ADR-0010]] (still `proposed`, and the constraints view's single obligation), [[ISS-0127]], and the cutoff for the 81 unreviewed `CHG-*` notes ahead of [[ADR-0011]]'s 2026-10-23 deadline.

### The goal it serves

The record already states it, and no separate goal document is needed — [[ISS-0127]], which first argued the opposite and was corrected. Assembled from [[ADR-0009]], [[ADR-0020]], [[DES-0003]] and [[PHASE-028]]:

> The cockpit is how a person governs a project they did not write. It must not be able to say something false about that project without saying so — and everything it shows as owed must be theirs to discharge.

Every feature in this release serves one clause of that sentence. [[FEAT-0089]] and [[FEAT-0091]] make the record stop asserting things that are not true; [[FEAT-0087]], [[FEAT-0086]] and [[FEAT-0088]] put what is owed where its subject lives; [[FEAT-0059]]/[[FEAT-0060]]/[[FEAT-0061]] make those judgments the person's to discharge.

### Caveat — maintained by hand

[[FEAT-0072]]'s release surface is deferred to PHASE-026's remainder, so nothing renders this note and nothing computes its unshipped set. Until then it is hand-maintained, and it will drift unless someone updates it as features land. That is a known cost of writing the first release note before the surface that displays it.
