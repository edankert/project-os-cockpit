---
type: "[[issue]]"
id: ISS-0165
aliases: ["ISS-0165"]
title: "The attention card reads a second git walk, so 'one walk, agree by construction' is not true of the three surfaces that shipped"
status: "open"
phase: ""
owner: user:edwin
created: 2026-08-14
updated: "2026-08-14"
source: ["Independent review of [[FEAT-0100]], 2026-08-14, finding 4"]
severity: medium
component: desktop-fleet
parent: ""
related: ["[[FEAT-0100-Unpushed-Work-Needs-A-Person]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[TASK-0415]]", "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]"]
tests: []
---

# The attention card reads a second git walk

## Problem

[[FEAT-0100]]'s claim, and [[FEAT-0089]]'s whole promise, is **one walk, so two surfaces cannot disagree**. Two of the three publication surfaces honour it: the badge (`obligations._publication_rows`) and the History band (`cockpit.history_payload`) both read `git_state.read()`.

The third does not. The rail's attention card takes `ahead` from `fleetHealth`, which gets it from `probeGitState` in `desktop/src/ipc/git.ts` — **an independent implementation, in a different language, on its own 60-second clock.**

So the property is asserted in the notes and false of the code. Two implementations of "how many commits are unpublished" will agree until one of them is changed, which is the [[ISS-0023]] shape the registry exists to end.

## Why it was not caught

`counts_by_kind` is asserted against `owed_items` — one walk, checked. That assertion covers the two Python surfaces and cannot see the TypeScript one, so the guard that exists to prevent exactly this disagreement is structurally blind to the surface that has it.

## Not urgent, and worth saying why

The two implementations currently agree, and the card's clock means it is at worst 60 seconds stale. Nothing is visibly wrong today. **The 2026-08-14 unknown-count fix is the argument for fixing it**: that repair had to be made in `git_state.py` *and* would need making again in `probeGitState`, because an unknown `ahead` reaches the card by a path the Python fix never touches.

## Resolution

Have `fleetHealth` read the sidecar's publication payload rather than shelling out to git a second time — the sidecar already computes it, and the card already talks to the sidecar for everything else on the row.

## Expected

One walk, and a guard that can see all three surfaces rather than the two written in the same language.
