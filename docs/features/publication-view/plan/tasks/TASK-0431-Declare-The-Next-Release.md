---
type: "[[task]]"
id: TASK-0431
aliases: ["TASK-0431"]
title: "Declare the next release — create a `REL-*` at `draft` from the cockpit, which is what makes 60 unchecked rows the CURRENT set"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin 2026-08-16: 'the current set of acceptance tests for the next release' — there is no next release, and no way to say there is one"]
parent: "[[FEAT-0103-The-Gate-Is-Walkable]]"
effort: M
depends: []
blocks: ["[[TASK-0432-The-Gate-Lists-Its-Checks]]"]
related: ["[[ADR-0022]]", "[[FEAT-0102-Publication-Becomes-A-View]]"]
tests: ["[[TST-0029-The-Walker-Ticks-What-It-Walked]]"]
---

# Declare the next release

## What

A control on the release rung that creates `REL-<next>` at `status: draft` with a version. `STATUSES.md` already documents `draft` as *"prepared and verified, not yet live"*; nothing has ever written one.

This is the missing half of Edwin's sentence. `your-trainer` has 60 unchecked gating rows and **no release in preparation**, so they are a standing property of a checklist rather than the set gating anything. Declaring `2.1.7` is what makes them *the current set*.

## Definition of done

- [ ] Creates a `REL-*` note from the template at `draft`, with a version the caller supplies
- [ ] Refuses a version at or below the newest `released` one — that is the overtaken-draft state [[FEAT-0102]] already has to work around, and creating another by hand would be manufacturing it
- [ ] Id allocated by the same collide-on-id rule `create_issue` uses, not by filename
- [ ] Loopback-only (`REQ-0027`), and enumerated by `test_every_note_mutating_endpoint_requires_loopback`
- [ ] Refuses when a release is already in preparation — one at a time, or "the next release" means nothing
- [ ] **Creates nothing else and publishes nothing.** Declaring is not shipping ([[ADR-0022]])
- [ ] Once declared, the gate names it: `Release gate · 60 unchecked · preparing 2.1.7`, and the obligation fires
