---
type: "[[feature]]"
id: FEAT-0072
aliases: ["FEAT-0072"]
title: "The release surface — done-but-unshipped becomes a number, drafting a release becomes an action, and the acceptance-tests gate finally renders"
status: planned
phase: "[[PHASE-026-The-Returning-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[DES-0008-The-Returning-Human]]"]
goal: "An UNRELEASED record card counting features done since the last REL note; Draft-release scaffolds the REL from them as a draft for the actuator row; the REL note view surfaces the acceptance-tests template's own release gate."
requirements: []
tasks: []
release: ""
related: ["[[FEAT-0064-The-Acceptance-Gate]]"]
tests: []
---

# The release surface

## Goal

"Done" and "shipped" are different facts and the cockpit knows only one — while the acceptance-tests template has carried a release gate since it was written ("a release is blocked while any Tier 1/2 test is unchecked") with nowhere to bite. REL notes exist as a type with a counter at zero; this is their minimal, honest surface.

## Out of Scope

- Performing releases. The cockpit records that one was cut; pushing and deploying remain a person's deliberate acts (FEAT-0055's line).
- Versioning policy. The REL template's fields; not this feature's opinion.
