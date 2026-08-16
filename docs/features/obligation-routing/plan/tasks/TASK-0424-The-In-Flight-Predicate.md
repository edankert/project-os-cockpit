---
type: "[[task]]"
id: TASK-0424
aliases: ["TASK-0424"]
title: "The in-flight predicate — a requirement or test asks only while a subject it names is being worked, `deferred` overrides, and a subject-less obligation keeps asking"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[ADR-0028]] decisions 3 and 4", "Edwin 2026-08-16: 'can we do this to other items as well (probably not issues)?'"]
parent: "[[FEAT-0101-Obligations-Route-By-The-State-Of-Their-Subject]]"
effort: M
depends: ["[[TASK-0423-An-Obligations-View-Is-Decided-Per-Item]]"]
blocks: ["[[TASK-0425-The-Quiet-Is-On-Screen]]"]
related: ["[[ADR-0028-Work-Has-Three-Phases]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]"]
tests: ["[[TST-0025-Obligation-Routing-Is-Per-Item-And-Complete]]", "[[TST-0026-The-In-Flight-Rule-Against-The-Live-Fleet]]"]
---

# The in-flight predicate

## What

An obligation asks while a subject it names is in flight, and rests otherwise. Applies to exactly two kinds — **requirement** and **test** — per [[ADR-0028]]'s table. Every other kind is unchanged, and `issue: triage` explicitly so.

- **requirement** → the features its `implements:` names
- **test** → the features its `verifies:`/`features:` name, and (once [[FEAT-0102]] lands) the release it gates

The predicate takes a *subject*, not a feature, so the release rung slots in without rewriting it.

## The three things that decide whether this is right

**1. The discriminator is feature status, never phase.** Checked against `your-trainer`: `PHASE-019` is `active` and holds two features already `done` — phase-keying would wake their requirements back up. `PHASE-017`/`PHASE-018` read `planned` while holding `done` features. 19 features carry no phase; 3 of 12 repos have no `PHASE-*` notes at all.

**2. `deferred` beats the derived rule, in both directions.** The rule is a default (quiet because nothing is happening). `deferred` is a decision (quiet because a person decided). The case that separates them: a `deferred` requirement whose feature moves to `doing` **stays quiet**.

**3. A subject-less obligation keeps asking.** `TST-0001` and `TST-0002` in `your-trainer` name no feature — `scope: system`, `features: []`. A naive reading makes them never-owed, which loses two tests rather than quieting them. Nothing can prove a subject-less obligation is resting, so it asks. This is the direction that fails safely, and it is the criterion most likely to be got wrong.

## Definition of done

- [ ] The predicate takes a subject and is defined for requirement and test only; no other kind's behaviour changes
- [ ] In flight = the subject is at `planned`, `doing` or `review`; resting = `backlog`, `done`, `cancelled`, `superseded`, `deferred`. Any status not in either list is treated as in flight and named in a comment — an unrecognised status must not silence anything
- [ ] An obligation naming **several** subjects asks if **any** is in flight
- [ ] An obligation naming **no** subject asks. Tested explicitly against `TST-0001`/`TST-0002`'s shape
- [ ] `deferred` on the obligation itself wins regardless of subject state — asserted with the feature at `doing`
- [ ] `issue: triage` is untouched: `your-trainer`'s 22 is 22 before and after
- [ ] Measured on the live fleet, recorded in [[TST-0026]]: `your-trainer` 64 → 31; requirements 26 → 3; tests 15 → 5
- [ ] A repo with no `PHASE-*` notes routes correctly, and no code path requires a phase to exist
- [ ] Mutation-tested. Each guard is checked against a mutation **chosen by trying to defeat it**, not against the one that was in mind while writing it — [[ISS-0171]] is what the other habit costs
