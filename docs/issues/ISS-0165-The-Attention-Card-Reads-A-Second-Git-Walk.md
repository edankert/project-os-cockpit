---
type: "[[issue]]"
id: ISS-0165
aliases: ["ISS-0165"]
title: "The attention card reads a second git walk, so 'one walk, agree by construction' is not true of the three surfaces that shipped"
status: "fixed"
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-14
updated: "2026-08-14"
source: ["Independent review of [[FEAT-0100]], 2026-08-14, finding 4"]
severity: medium
component: desktop-fleet
parent: ""
related: ["[[FEAT-0100-Unpushed-Work-Needs-A-Person]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[TASK-0415]]", "[[TASK-0421-An-Unknown-Count-Is-Unknown-On-Every-Surface]]", "[[TASK-0422-One-Walk-For-Publication]]", "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[CHG-20260814-One-Walk-For-Publication]]"]
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

---

## Fixed — 2026-08-14 ([[TASK-0421]], [[TASK-0422]], [[CHG-20260814-One-Walk-For-Publication]])

**Two things in this note were wrong, and both mattered to the fix.**

**There were three implementations, not two.** `fleet_validate.git_standing` is a third — its own remote table, its own `rev-list`, its own handling of the missing upstream — which nobody reads, because the shell computes it and deliberately discards it (the comment doing so cites [[ISS-0156]]). A rule that exists three times and is consumed twice has already stopped being a rule.

***"Nothing is visibly wrong today"* was false when this was filed.** The 2026-08-14 unknown-count repair landed in `git_state.py` and `_publication_rows` only. Both renderer surfaces coerced the null to `0` and dropped it: the attention card at `typeof row.ahead === 'number' ? row.ahead : 0` followed by `if (ahead <= 0 && dirty <= 0) continue`, and the roll-up between a `behind` filter needing a number and a `noRemote` filter needing no remote. So a repo with a real remote and no upstream counted one obligation on the badge and appeared on neither other surface — the divergence this note predicted, already shipped, in the case ADR-0027's fourth admission test exists for. **The repo is `edankert.com`**, measured across all 18 under `~/Dev/repos/` on 2026-08-14: a deploy remote, no upstream, `ahead: null`. Not a hypothetical. That is [[TASK-0421]], and it was worth doing on its own before any refactor.

**The resolution proposed here was not taken, deliberately.** *"Have `fleetHealth` read the sidecar's publication payload"* — a sidecar exists only for a workspace someone has **opened**, so it would answer for the open repo and leave eleven blank. That is [[ISS-0156]] with the sign flipped, on the one surface whose value is being cross-workspace. What survives instead is the property that issue bought — *one clock for the whole fleet* — with the missing one added: `project_os_cockpit.fleet_git` prints one line per repo from `git_state`, and the shell spawns it for every workspace on the clock it already had. `probeGitState` is gone; `git.ts` keeps only the classification that gates the push, which it re-derives on purpose.

**`dirty` was the same defect one number to the left** and is fixed with it: `git_state.dirty_paths()` is the single walk, History decorates its rows from it, and the shell reads the count. Removing one of two git walks from a module while leaving the other, on the same row of the same card, would not have been a fix.

**The guard this note asked for exists**: `git.ts` is asserted to contain no `rev-list` and no `--porcelain`, and the shell's numbers are compared against `python -m project_os_cockpit.fleet_git`'s output for the same repo rather than against a number that happens to match. Both structural guards were first written so that their own explanatory comments satisfied the string search — the TypeScript one *failed against the fix it was written for* — and both now strip comments before asserting, then were mutation-tested by reintroducing the defect in code.
