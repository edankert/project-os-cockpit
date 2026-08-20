---
type: "[[feature]]"
id: FEAT-0141
aliases: ["FEAT-0141"]
title: "The contract says it upstream — `TESTING.md` and `STATUSES.md` carry the rules, and the fleet is synced"
status: done
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
source: ["Edwin 2026-08-19: 'make sure this is covered eveywhere (project-os) to this extent'"]
goal: "The tier vocabulary, the invalidation rule and the no-verdict rule are stated once in the template-owned instructions and reach every repo by sync."
requirements: []
tasks: ["[[TASK-0573-Testing-Md-Five-Edits-Upstream]]", "[[TASK-0574-Statuses-Md-Line-One-Four-Four]]", "[[TASK-0575-Sync-The-Fleet]]"]
release: ""
acceptance: ""
design: ""
related: ["[[ADR-0038-The-Suite-Is-The-Verdict]]", "[[ADR-0039-Three-Sections-Derived-Not-Filed]]", "[[ISS-0238-There-Is-Nowhere-To-Put-An-Automated-Check]]"]
tags: [feature, documentation]
---

# The contract says it upstream

## Goal

`TESTING.md` is template-owned and canonical at `~/Dev/repos/project-os/tools/instructions/`. Editing the copy in this repo would be reported as divergence by the next sync and would reach nobody. The rules land upstream or they do not land.

## Scope

- Five edits to `TESTING.md`, listed in [[ADR-0039]].
- One correction to `STATUSES.md` line 144.
- A sync across the fleet.

## Out of Scope

- Rewording the 1016 occurrences of *run* in `docs/`. Edwin, 2026-08-19: leave it in the documents, keep it out of the UI.

## Acceptance

- [ ] `TESTING.md` upstream describes three sections and no tiers, and nothing that removes a check
- [ ] `STATUSES.md` no longer attributes to `TESTING.md` a rule it does not state
- [ ] Every fleet repo carrying an acceptance suite is byte-identical to upstream afterwards
