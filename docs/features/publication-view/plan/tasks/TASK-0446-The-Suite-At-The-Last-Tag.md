---
type: "[[task]]"
id: TASK-0446
aliases: ["TASK-0446"]
title: "Parse the suite as it stood at the last released tag and diff it — new, chronic, regressed"
status: backlog
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0108-The-Gate-Is-A-Delta-Not-A-Census]]"]
parent: "[[FEAT-0108-The-Gate-Is-A-Delta-Not-A-Census]]"
effort: M
depends: []
blocks: ["[[TASK-0449-Order-The-Walk-By-Its-Setup-Cost]]"]
related: ["[[ADR-0028-Work-Has-Three-Phases]]"]
tests: []
---

# The suite at the last tag

## Why

The gate's number is only meaningful against a baseline, and the baseline exists: `git show <tag>:docs/tests/ACCEPTANCE_TESTS.md` reconstructs the suite exactly as it stood at every release. `acceptance.parse` reads it unchanged. This was demonstrated across all twelve of `../your-trainer`'s tags in about two seconds.

## What

Given the newest `released` release and its tag, parse the suite at that tag and diff it against the working tree, partitioning today's blocking rows into **new**, **chronic** and **regressed**.

Also derive **age** for chronic rows by walking backwards through the tags to the last one where the row was ticked, or its first appearance if never ticked.

## How

- Match on `Item.name` within tier, **not on `Item.number`**. Numbers shift when a section is inserted above; the same asymmetry `locate()` already relies on.
- Read through the existing git plumbing rather than adding a second way to run git.
- Cache per (repo, tag) — twelve tags is twelve `git show` calls and the page must not pay them per render.

## Degradation, which is most of this task

Eleven of the twelve discovered repos have **no release tags at all**. This must be a first-class path, not an exception:

- no tags → the census the page renders today, with the reason stated
- tags but no `released` release note → newest tag by version order, and say which was used
- the tag exists but the suite file does not exist at it → census, reason stated
- the file exists at the tag but does not parse → census, reason stated

## Done when

- [ ] `new` / `chronic` / `regressed` counts computed against the newest `released` tag
- [ ] chronic rows carry the tag they were last ticked at and the number of releases shipped since
- [ ] matched on name within tier, and a test inserts a section above a check to prove the number is not used
- [ ] all four degradation paths render the census with a stated reason
- [ ] no measurable regression in page render time; the tag reads are cached
- [ ] verified against `../your-trainer`'s real twelve tags, and the numbers recorded in the note
