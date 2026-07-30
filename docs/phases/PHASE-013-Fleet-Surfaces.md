---
type: "[[phase]]"
id: PHASE-013
aliases: ["PHASE-013"]
title: "Fleet surfaces — the cockpit reports on every repo it can see, not just the open one"
status: planned
order: 13
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
goal: "Finish the work that treats the fleet as the unit rather than the workspace: roll the design-system convention across the repos that have a UX, and surface per-repo validator health without opening each one. Both already have one leg built."
features:
  - "[[FEAT-0028-Fleet-Health-Surface]]"
  - "[[FEAT-0044-Fleet-Design-Systems]]"
requirements: []
issues:
  - "[[ISS-0055-Deferred-Findings-From-The-Design-Bench-Reviews]]"
depends: ["[[PHASE-009-Design-Surfaces]]"]
related: ["[[DES-0002-Cockpit-Design-System]]", "[[FEAT-0032-Agents-Screen]]", "[[PHASE-011-Unproven-Claims]]"]
tags: [fleet, design]
---

# Fleet surfaces

## Goal

Two features here are half-built, and both were paused rather than abandoned.

[[FEAT-0044]] is `doing` with [[TASK-0230]] `done` and [[TASK-0231]] outstanding: the per-project stylesheet route shipped, the rollout across the fleet did not. [[FEAT-0028]] is `backlog` with no tasks — per-workspace validator badges, which the `~agents` screen already proves is possible because it aggregates per-workspace state across repos.

The reason to do them together is that they need the same thing: a reliable read of *another* repo's docs from this one. `~agents` does it for agent state, `validate-fleet.sh` does it for validation, and neither is wired into a surface.

## Scope

- **[[TASK-0231]]** — roll the design-system convention out across the fleet repos that have a UX, finishing [[FEAT-0044]]. [[DES-0002]] is the template and is `implemented`, so this is application rather than design.
- **[[FEAT-0028]]** — per-workspace validator badges across discovered repos. Needs task breakdown; there are none yet.
- **[[ISS-0055]]** — the deferred design-bench findings (at-rule descent, a dead token, others). Grouped here because they are the residue of the machinery this phase leans on, and fixing them in isolation would mean opening the design bench twice.

## Out of Scope

- **The MCP server** ([[FEAT-0029]]). Also cross-boundary, but a different boundary — exposing this cockpit outward rather than reading other repos inward. Stays in [[PHASE-999-Future]].
- **The downstream pilot** ([[FEAT-0005]] / [[PHASE-003]]). It has its own phase, untouched since PHASE-002. Whether it is still wanted is a decision, not scope to absorb here.
- **Distribution** ([[TASK-0065]] — signing, notarization, auto-update). Deliberately parked until sharing outside this machine matters.
- **Fixing other repos' corpora.** If the rollout finds a fleet repo whose docs do not conform, that is an issue filed against that repo, not work in this phase.

## Exit Criteria

- [ ] Every fleet repo with a UX has a design-system note and a living style guide read from its own CSS — evidence: <per-repo list, with the ones deliberately skipped named>
- [ ] The cockpit shows validator health for every discovered workspace without opening it — evidence: <manual pass across the fleet>
- [ ] [[FEAT-0028]] has tasks before implementation starts — evidence: <it currently has none, and a feature with no breakdown is a wish>
- [ ] [[ISS-0055]]'s findings are each fixed or explicitly declined with a reason — evidence: <the note, item by item>

## Notes

Sequenced last of the three. Nothing here is wrong today — it is unfinished, which is a weaker claim on attention than [[PHASE-011]]'s misleading surfaces or [[PHASE-012]]'s duplicated section.

Worth watching for scope creep: "the fleet" is 11 repos on one machine, and every surface that reads across them is a surface that can be wrong about ten codebases at once. [[FEAT-0028]] in particular should ship read-only and stay that way.
