---
type: "[[task]]"
id: TASK-0444
aliases: ["TASK-0444"]
title: "A shipped release shows the snapshot it verified, what it shipped with unfixed, and its artifacts — not today's gate"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0107]]", "Independent review of PHASE-034, 2026-08-16"]
parent: "[[FEAT-0107-Publication-Is-A-List-Of-Releases]]"
effort: M
depends: []
blocks: []
related: ["[[ADR-0028-Work-Has-Three-Phases]]"]
tests: []
---

# A shipped release shows the snapshot it verified, what it shipped with unfixed, and its artifacts — not today's gate

## Why

Three defects in one: the frozen contents are computed and dropped on the floor, the gate is recomputed for a release that shipped months ago, and seven platform artifacts have never been visible.

## Definition of done

- [x] `contents.ids` renders — `REL-0001` currently reads *What shipped — 27 feature(s)* over an empty list
- [x] Acceptance tests come from `tests_verified:`, resolved to their notes
- [x] A release with an empty `tests_verified` says *not recorded*, and five of twelve are empty
- [x] The gate section is ABSENT for a shipped release; its snapshot stands in its place
- [x] The note's `## Known issues (shipping with)` section is surfaced as what it shipped with
- [x] Artifacts are found by the `REL-####-` filename convention, blessed in [[ADR-0028]] rather than inferred
