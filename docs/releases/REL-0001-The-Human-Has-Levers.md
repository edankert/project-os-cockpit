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
| FEAT-0085 | The navigator shows the structure the record has | planned | PHASE-022 |
| FEAT-0059 | note_writes widens — the transition table as data | planned | PHASE-023 |
| FEAT-0060 | The actuator row on the note | planned | PHASE-023 |
| FEAT-0061 | Quick capture and the triage tray | planned | PHASE-023 |
| FEAT-0089 | The obligation registry and the badges | planned | PHASE-030 |
| FEAT-0091 | The standing documents | planned | PHASE-030 |
| FEAT-0087 | Design widens into the project's constraints (Intent) | planned | PHASE-030 |
| FEAT-0086 | Tests becomes a view | planned | PHASE-030 |
| FEAT-0088 | Features carries its own judgments | planned | PHASE-030 |
| FEAT-0071 | Since you looked — the watermark and digest | planned | PHASE-026 |
| FEAT-0090 | The desk retires | planned | PHASE-030 |

Order is the implementation order, not the table's convenience — see below.

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

### The goal it serves

[[ISS-0127]]: the intent charter is currently scheduled in PHASE-027 because delegated acceptance reads it, and is needed far earlier because this release has nothing to be checked against. The charter is the goal; this is the first delivery against it.

### Caveat — maintained by hand

[[FEAT-0072]]'s release surface is deferred to PHASE-026's remainder, so nothing renders this note and nothing computes its unshipped set. Until then it is hand-maintained, and it will drift unless someone updates it as features land. That is a known cost of writing the first release note before the surface that displays it.
