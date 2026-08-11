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
updated: 2026-08-11
features: ["[[FEAT-0085-The-Navigator-Shows-The-Structure-The-Record-Has]]", "[[FEAT-0059-The-Write-Service-Widens]]", "[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]", "[[FEAT-0061-Quick-Capture-And-Triage]]", "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[FEAT-0091-The-Standing-Documents]]", "[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]", "[[FEAT-0086-Tests-Becomes-A-View]]", "[[FEAT-0088-Features-Carries-Its-Own-Judgments]]", "[[FEAT-0071-Since-You-Looked]]", "[[FEAT-0090-The-Desk-Retires]]", "[[FEAT-0062]]", "[[FEAT-0063]]", "[[FEAT-0064]]", "[[FEAT-0065]]", "[[FEAT-0066]]", "[[FEAT-0067]]", "[[FEAT-0068]]", "[[FEAT-0069]]", "[[FEAT-0070]]", "[[FEAT-0072]]", "[[FEAT-0073]]", "[[FEAT-0074]]", "[[FEAT-0075]]", "[[FEAT-0076]]", "[[FEAT-0077]]", "[[FEAT-0078]]"]
changes: []
tests_verified: []
previous_release: ""
related: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[ISS-0126]]", "[[ISS-0127-The-Charter-Is-Scheduled-By-Its-Consumer-Not-Its-Value]]", "[[PHASE-023-Levers-For-The-Human]]", "[[PHASE-024-Acceptance-Witnessed]]", "[[PHASE-025-Design-Before-Code]]", "[[PHASE-026-The-Returning-Human]]", "[[PHASE-027-The-Standing-Worker]]", "[[PHASE-030-Obligations-Go-Home]]"]
tags: [release]
---

# The human has levers, and every surface says what it owes

**The first release note this project has written.** `counters.REL` has read `0` for six months across 85 features — not because nothing shipped, but because nothing ever drew a line around a shippable state. This draws one.

## What this release is

One sentence: **a person governs a project through the cockpit — they can see every judgment the record owes them, make it in the place that owns it, accept the work that results, and step out of the daily loop without the project stalling.**

Two findings opened it. [[PHASE-023]]'s: *every transition in the ownership table is agent-owned; the cockpit's only actuator is asking an agent in the terminal.* And [[ADR-0020]]'s: the surface built to collect those judgments held two things that were not obligations and omitted the largest one there is.

### The definition widened on 2026-08-11

**This note first defined the release as eleven features, and closed when they were done. That definition was wrong — not incorrectly executed, incorrectly drawn.** Edwin's correction: *"it is complete according to its definition, but the definition was incomplete."*

Eleven features shipped the *levers*. They did not ship the thing the levers are for. A person can now make a judgment on a note — and then has nowhere to accept the work it produced ([[PHASE-024]]), no way to design the surface before it is built ([[PHASE-025]]), no answer to "what shipped" ([[PHASE-026]]), and no way to be absent ([[PHASE-027]]). Each of those was deferred *individually* and defensibly; together they deferred the release's own sentence.

**So the release is now defined by phases resolved, not by a feature list.** [[PHASE-023]], [[PHASE-024]], [[PHASE-025]], [[PHASE-026]] and [[PHASE-027]] must all reach `done` for this release to ship. A feature list is a scope that can be satisfied while the goal is not; a phase carries exit criteria, and cannot close while a child of it is unresolved.

That is a deliberately harder bar, and it is the point — see **The completion bar** below.

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

**All eleven are `done` as of 2026-08-10.** Implemented in the stated order across two sessions; each feature's own note carries what it found. This is leg 1 of the release, and it is finished; nothing below reopens it.

### Leg 2 — in scope, not yet built

The five phases that must reach `done`. Sixteen features, and the `planned` status on every one of them is the honest state as of 2026-08-11.

| Phase | Goal, in a clause | Features | Tasks |
|---|---|---|---|
| [[PHASE-023]] | the levers, finished | FEAT-0062 | 2 |
| [[PHASE-024]] | the human accepts work, with evidence | FEAT-0063, FEAT-0064, FEAT-0065, FEAT-0066 | 13 |
| [[PHASE-025]] | design happens before code, on the bench | FEAT-0067, FEAT-0068, FEAT-0069, FEAT-0070 | 12 |
| [[PHASE-026]] | the returning human is addressed | FEAT-0072, FEAT-0073 | 7 (1 done) |
| [[PHASE-027]] | the project runs without its human daily | FEAT-0074, FEAT-0075, FEAT-0076, FEAT-0077, FEAT-0078 | 16 |

**[[FEAT-0078]] was missing from this note's deferred table** — it listed FEAT-0074..0077 for a phase that has five features. Corrected here; it is the kind of drift the caveat at the foot predicted.

### Leg 2 closed — 2026-08-11

**All five phases are `done`.** [[PHASE-023]], [[PHASE-024]], [[PHASE-025]], [[PHASE-026]] and [[PHASE-027]] each cleared both gates on their own terms: no unresolved child, no unticked exit criterion. The 76 unresolved children measured at the top of the day are 0; the 25 unticked criteria are 0, of which the settled-rather-than-ticked ones each name where they went.

The last thing to move was not code. [[DES-0009]] sat `proposed` for eleven hours with its artifact rendered and every mechanism it describes built and tested, because `design: proposed → accepted` is in `HUMAN_TRANSITIONS` and the server refuses it to an agent ([[REQ-0026]]). Edwin accepted it in session; it is recorded through `/api/design/verdict` at revision `31eac79` with `reviewed_by: user:edwin`. **The release's own sentence, enforced against the release.**

Two things stay open by decision and neither is a phase: [[RISK-0006]]'s supervised week, re-homed to [[PHASE-031]] with the risk still `open`; and [[ADR-0022]], `proposed`, whose unaccepted state *is* the operative rule that the worker never pushes.

**What the release still owes is verification, not work** — see below. `status: draft` now means exactly one thing: the acceptance gate is red.

### The completion bar

"The sixteen features are done" is **not** the bar, and stating it as one would repeat the error this revision fixes. `STATUSES.md` gates a phase twice: **PHASE-CHILDREN** — no phase closes while any note naming it in `phase:` is unresolved; and **PHASE-BOXES** — no phase closes with an unticked exit criterion. Measured 2026-08-11:

| Phase | Unresolved children | Of which are not features/tasks | Exit criteria unticked |
|---|---|---|---|
| PHASE-023 | 5 of 25 | [[ISS-0126]], [[RISK-0005]] | 5 |
| PHASE-024 | 19 of 20 | [[ISS-0096]], [[REQ-0028]] | 5 |
| PHASE-025 | 16 of 17 | — | 5 |
| PHASE-026 | 8 of 14 | — | 5 |
| PHASE-027 | 28 of 28 | [[DES-0009]], [[REQ-0029]], [[REQ-0030]], [[REQ-0031]], [[ISS-0094]], [[ISS-0095]], [[RISK-0006]] | 5 |
| **total** | **76** | **13** | **25** |

Two open risks — [[RISK-0005]] (the write surface on a LAN-visible server) and [[RISK-0006]] (the unattended worker) — are among them. **An open risk is not resolved by the phase that raised it closing**; each needs mitigation or an accepted rationale before its phase can.

### Features NOT Included (deferred)

Only two phases defer, and both were named by Edwin on 2026-08-11.

| ID | Title | Status | Reason |
|---|---|---|---|
| FEAT-0079, FEAT-0080 | Borrowed capability — the harness survey | planned / doing | PHASE-028. Deferred by decision; FEAT-0080 is mid-flight and does not block |
| FEAT-0083, FEAT-0084 | The browser front door | planned | PHASE-029, gated on [[ADR-0010]] which is still `proposed` — the gate, not the effort, is why it defers |

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

### Leg 1 — done, 2026-08-10

1. **[[ISS-0121]]** — smallest, unblocked, and stops a live surface stating something false
2. **[[FEAT-0085]]** — closes PHASE-022, taking three active phases down to two
3. **[[FEAT-0059]] → [[FEAT-0060]] → [[FEAT-0061]]** — the keystone; six phases depend on PHASE-023
4. **[[FEAT-0089]]** — the registry; can run in parallel from the start, it needs nothing
5. **[[FEAT-0091]] + [[FEAT-0087]]** — display only, no write path, and the clearest available win
6. **[[FEAT-0086]]** — the largest new capability, and where the release gate becomes possible
7. **[[FEAT-0088]]** — needs step 3 to be worth doing
8. **[[FEAT-0071]]** — the digest, **before** the desk goes
9. **[[FEAT-0090]]** — last, and only once the registry can prove nothing is homeless

### Leg 2 — the order, and why it is this one

**Step 0, and it is not work: [[ISS-0126]].** Does [[FEAT-0062]] survive [[ADR-0020]]? It builds two verbs onto the surface this release just retired. It is `triage`, it is a decision rather than an effort, and it gates the *smallest* remaining phase. Answering it costs minutes and either removes a feature from the release or unblocks it. **Nothing below should start while it is open**, because the answer may shrink the scope.

1. **[[PHASE-026]] — [[FEAT-0072]] then [[FEAT-0073]].** First, against the instinct to do the biggest thing first, because **this note is the argument for it**. The caveat at the foot says REL-0001 is hand-maintained and will drift until FEAT-0072's release surface exists — and it already did drift ([[FEAT-0078]] missing, above). A release that just grew from 11 features to five phases will be hand-maintained for far longer, so the surface that computes it is worth the most on day one and least on the last day. Two features, 6 open tasks, no external blocker: the cheapest item here is also the most urgent.
2. **[[PHASE-023]] — [[FEAT-0062]] (if ISS-0126 spares it), plus [[RISK-0005]].** Closing the nearest phase. Five unresolved children against twenty-five resolved; the work is small and the value is a phase that stops being 83% forever. RISK-0005 needs mitigation or an accepted rationale — the write surface it names is now shipped, so the risk is live rather than anticipated.
3. **[[PHASE-024]] — [[FEAT-0063]] first.** The acceptance runner. It closes a door-to-nothing this release *created*: [[FEAT-0088]] marks a feature `acceptance: requested` and offers no way to run it, which the leg-1 record already lists as a reconciled-not-ticked criterion. It also makes the release gate real rather than notional — the Tier 1/2/3 suite exists now, and FEAT-0063 is what walks it. Then FEAT-0064 (gate), FEAT-0065 (debt), FEAT-0066 (visual evidence). [[REQ-0028]] advances to `implemented` at close-out; [[ISS-0096]] resolves here.
4. **[[PHASE-025]] — the design bench.** Deliberately fourth and not later: it is the only phase with **no issues, no risks, no requirements and no external gate** — 4 features, 12 tasks, entirely self-contained. It can therefore run in parallel with any of the above whenever something else blocks, which is the role it should play rather than a queue position.
5. **[[PHASE-027]] — last, and it earns it.** 28 unresolved children, every one of them. Its three requirements ([[REQ-0029]], [[REQ-0030]], [[REQ-0031]]) are still `draft` and its design [[DES-0009]] is still `draft` — so it opens with **approval work, not build work**. [[RISK-0006]] (compounding wrong judgment at machine speed) must be mitigated before an unattended loop runs at all. Everything the worker delegates is a judgment the earlier phases made human-ownable, so it is genuinely last rather than conventionally last.

**The one hard ordering:** PHASE-027 after PHASE-024. The worker delegates acceptance; acceptance must exist and be recorded before anything may be delegated to a machine.

## Verification

### Acceptance Tests

**The suite now exists** — created by [[FEAT-0086]] / [[TASK-0373]], which is what the original text below said was still missing. `docs/tests/ACCEPTANCE_TESTS.md` holds 27 Tier 1, 7 Tier 2 and 2 Tier 3 items.

- **Tier 1 (Feature Tests):** 27 items, 11 walked as of 2026-08-11
- **Tier 2 (Regression Tests):** 7 items, 5 walked
- **Tier 3 (Verification Tests):** 2 items, 1 walked

**The widened scope widens this too, and the suite does not yet know it.** Those 36 items were written against leg 1. Sixteen more features, each with acceptance criteria, will add Tier 1 items — so the gate's denominator grows as leg 2 lands, and a green gate today would not be a green gate for the release. **Each leg-2 feature adds its Tier 1 items at close-out**, rather than a sweep at the end; that is the rule this release should establish, since a suite written after the fact is written by someone reading the diff rather than the intent.

The original entry read: *"None exist yet, and that is a scope item rather than an omission… 85 features, 23 test notes, zero tier classification, and a release gate that has never been able to fire."* Kept because the gate firing at all is the thing leg 1 bought.

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

**Step 5/6 — the tier gate.** 27 Tier 1 and 7 Tier 2 items. **16 were walked on 2026-08-10** and carry their evidence in the suite; **7 more on 2026-08-11**, so **23 of 34 are walked and 11 remain unchecked** — the gate is still red.

*The 2026-08-10 figure was written as "seventeen", which counted the one Tier 3 check against a Tier 1/2 denominator. Corrected on the recount; the suite carries the same correction and the reason for it.*

What was walked, and the one worth naming: **every mutation endpoint refuses a non-loopback caller** — driven over the real LAN interface `192.168.68.123:8791`, ten of ten returned **403** while reads returned **200**. That is [[REQ-0027]]'s core claim and [[ISS-0129]]'s regression, and it is the check `test_mutation_endpoints_reject_non_loopback_callers` explicitly disclosed it *could not* make (*"an honest static check, since http.server cannot spoof a peer address"*). Also walked: live reload over `/_events`, workspace discovery across ten repos, the triage-first Issues pane, 71 of 71 plans reachable, 104 verdicts with 0 owed, the badge total of 95 equalling its parts, and close-out committing its own work thirteen times.

What remains needs a person at the keyboard — visual checks of rendered surfaces, an agent session, an interactive terminal. The skill's step 7.2 is explicit that a manual test is *"presented to the user for execution"*.

**The obstacle, and what removed it.** The running shell was on the current renderer — its retirements were confirmed live, `tasks` and `review` gone from the top bar, `tests` present — but its Python sidecar predated this session and 404s on the new endpoints, so payload-dependent views rendered stale. Restarting Edwin's window is his call, not mine.

**Settled 2026-08-11, and it cost a false bug report.** Edwin restarted it. The sidecar had been running since 2026-08-09 19:47 against code from 2026-08-10 20:48, and the gap produced two view complaints that were not view problems: the Tests view appeared to show phases and features (on stale code `mode=tests` is unknown, so `nav_payload` falls back to `DEFAULT_MODE = "features"` and renders the features tree under the Tests label), and tasks appeared to be missing under features (they were added by [[TASK-0366]], which that process had never loaded). Both were correct in the code the whole time. Sidecars are an editable install, so they need no rebuild — but a running process never re-imports, and the SSE soft-reload refreshes documents only, never Python modules. **Nothing restarts a sidecar when the code changes and nothing says one is stale**, which on the one repo whose code *is* the cockpit means the developer sees yesterday's tool while reading today's record.

So the harness got built instead: **`desktop/harness/live-harness.html`** runs the built bundle against a *real* sidecar in a plain browser. Its sibling `overview-harness.html` stubs the sidecar with captured fixtures — right for looking at a layout, useless for verifying a release, because it shows the payloads of the day it was written. This one stubs only the Electron bridge.

The harness also confirmed, by eye, three things this release built and nothing had looked at: the **digest band renders first on the overview**, above the focus band, headed *"Since this cockpit first ran"* with `Caught up` at its foot ([[FEAT-0071]]); the **Intent view opens on the standing set** — `What this project is · 8` — with `Risks · 6 · open` beneath it, where [[ISS-0128]] moved them; and the **record column carries `Reviewed · 104`**, [[TASK-0377]]'s re-homed register in its new home.

Two further visual checks are settled by it: the **Tests view** renders `Tier 1 · 8/27 · Tier 2 · 3/7 · Tier 3 · 0/2 · Verified · 23`, and the **badges** render `overview 81 · design 3 · features 4 · issues 7` — 95, the registry's total, with the Tests button correctly bare at zero.

Three things the harness cost, each recorded in the file because each failed by blaming the renderer: a guessed bridge member (`onChanged` for `onChange`) aborted module evaluation and turned every later `const` into a temporal-dead-zone error; two module scripts did not serialise, so the bundle could load before the bridge existed; and loading only `renderer.js` left the six plain-script globals undefined. The bridge stub is now **synthesised from `preload.ts`** and the script list read from the shell markup, so neither can drift again.

**No exceptions are claimed, and that is a decision.** The contract permits a test to be marked a release exception *"if it cannot be completed"*, documented with justification. The remaining seventeen can be completed; they simply have not been. Granting myself exceptions to clear a gate created the same day would hollow it out on its first use — which is the one thing that would make this feature worse than not having built it.

So the release stays `draft`, which `STATUSES.md` defines as *"prepared and verified, not yet live"* — prepared, and awaiting the half of the verification that is a person's.

**Since 2026-08-11 that is no longer the only thing it waits on.** With the definition widened, `draft` now means what it should have meant from the start: five phases open, 76 unresolved children, and a suite whose denominator has not finished growing. The seventeen unwalked checks are a leg-1 debt inside a release that is roughly a fifth built. Walking them is still worth doing early — they guard what already shipped, and evidence collected months after the fact is evidence about a different codebase.

**What the remaining checks actually need**, so the pass is minutes rather than an hour. **The `eyes on a rendered pane` row was walked on 2026-08-11** and is struck through below; the harness did reach all of it, as predicted:

| needs | checks |
|---|---|
| an agent session in the terminal | 1.9.1, 1.10.1, 1.10.2 |
| a second workspace open | 1.2.2 |
| a write to the record (⌘N, a criterion tick, a manual run) | 1.4.2, 1.7.2, 1.7.3, 1.8.1 |
| ~~eyes on a rendered pane~~ — **7 of 10 walked 2026-08-11** via `desktop/harness/live-harness.html` | ~~1.3.1, 1.3.2, 1.4.1, 1.6.1, 1.6.2, 1.11.1, 1.12.1~~ · still open: 1.5.2, 2.3.1, 2.4.1 |
| a manual test with a `Run ▸` | 1.7.2, 1.7.3 |

The prediction held: the harness reached every one of them and needed no app restart — serve the repo and a sidecar on one origin, open the harness, click. **Seven of the ten were walked on 2026-08-11**; three were left because the session ran out of room, not because the harness could not reach them.

One finding came out of the pass rather than the code: five of nine committed design artifacts hard-code a dark palette and render wrong under a light app ([[ISS-0136]]). [[DES-0009]]'s is among them and is deliberately **not** being fixed — its artifact sha is what this release's last acceptance is pinned to.

### Two acceptance criteria reconciled rather than ticked

- **[[FEAT-0090]]**: the desk's button and mode are gone and migrate; the **route stays served**. `.cockpit/review-requests.json` holds one OPEN entry, and retiring the route would strand it. Where proposals, questions and offered designs land is [[ISS-0126]] — one of the four decisions this note reserves.
- **[[FEAT-0088]]**: a feature at `acceptance: requested` is marked but offers no run, because [[FEAT-0063]]'s runner does not exist. A door to nothing teaches the reader the feature works.

**Both are now in scope rather than reconciled away.** [[FEAT-0063]] is step 3 of leg 2, so the second door leads somewhere before this release ships; and [[ISS-0126]], which the first bullet defers to, is step 0. Reconciling a criterion is the right move when the gap outlives the release — neither of these does any more.

### Still reserved for Edwin

Three of the four are unchanged and none blocked leg 1: [[ADR-0010]] (still `proposed` — it gates PHASE-029, which is now explicitly deferred, so it no longer sits on the critical path), [[ISS-0127]], and the cutoff for the 81 unreviewed `CHG-*` notes ahead of [[ADR-0011]]'s 2026-10-23 deadline.

**[[ISS-0126]] has been promoted out of this list.** It is step 0 of leg 2 and the only reserved decision that now blocks work — it decides whether [[FEAT-0062]] is in the release at all, and PHASE-023 cannot close either way until it is answered.

### The goal it serves

The record already states it, and no separate goal document is needed — [[ISS-0127]], which first argued the opposite and was corrected. Assembled from [[ADR-0009]], [[ADR-0020]], [[DES-0003]] and [[PHASE-028]]:

> The cockpit is how a person governs a project they did not write. It must not be able to say something false about that project without saying so — and everything it shows as owed must be theirs to discharge.

Every feature in this release serves one clause of that sentence. [[FEAT-0089]] and [[FEAT-0091]] make the record stop asserting things that are not true; [[FEAT-0087]], [[FEAT-0086]] and [[FEAT-0088]] put what is owed where its subject lives; [[FEAT-0059]]/[[FEAT-0060]]/[[FEAT-0061]] make those judgments the person's to discharge.

**And the last clause is why leg 2 exists.** *"…governs a project they did not write"* is not satisfied by seeing and judging alone. Governing includes accepting the result ([[PHASE-024]]), settling the shape before it is built ([[PHASE-025]]), being told what happened while away ([[PHASE-026]]), and being able to be away at all ([[PHASE-027]]). Leg 1 built the levers; the goal names what the levers are for. The widened definition is the goal read to its end rather than a new ambition bolted on.

### Caveat — maintained by hand, and for how much longer

[[FEAT-0072]]'s release surface would render this note and compute its unshipped set. Until it exists, this note is hand-maintained and drifts — **which it demonstrably did**: [[FEAT-0078]] was absent from the deferred table above, discovered only by counting PHASE-027's features rather than reading them.

**That is now a scope item rather than a standing cost.** FEAT-0072 is step 1 of leg 2, deliberately first, so the window in which this note is hand-maintained is as short as the plan can make it. The original caveat read: *"a known cost of writing the first release note before the surface that displays it"* — correct, and the right response to a known cost is to stop paying it early rather than to note it repeatedly.
