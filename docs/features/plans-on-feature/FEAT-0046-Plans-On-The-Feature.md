---
type: "[[feature]]"
id: FEAT-0046
aliases: ["FEAT-0046"]
title: "Plans belong to their feature — nested in the Features mode, found by path"
status: done
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: []
goal: "A delivery plan is one feature's sequence, not a document type you browse. It nests under its feature the way requirements already do, and it is found by path so the 19 untyped PLAN.md files stop being invisible."
requirements: []
tasks: ["[[TASK-0235-Plan-Lookup-By-Path]]", "[[TASK-0236-Plan-Nested-Under-Feature]]"]
release: ""
related: ["[[PHASE-010-Surface-Ownership]]", "[[FEAT-0050-Library-Reduction]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
---

# FEAT-0046 — Plans on the feature

## Goal

Library's Plans group renders 14 rows titled `Plan: …` / `Plan — …`, with no ID and no status chip, in a flat list ordered by a `note_id` every one of them lacks. It is a second, worse copy of the feature list — and an incomplete one, since 19 of the 33 plans are missing entirely ([[ISS-0062]]).

The relationship is already encoded in the filesystem: `features/<slug>/plan/PLAN.md` sits beside `features/<slug>/FEAT-*.md`. Reading it gives every plan a home and needs no corpus migration.

## Scope

- Resolve a feature's plan by path, from the feature record's own directory.
- Render it as a child row under the feature in the Features mode, alongside the requirement children that already nest there.
- Row shows the plan's status when it has one, and nothing when it does not — an untyped plan is still reachable, just less informative.

## Out of Scope

- Adding frontmatter to the 19 untyped plans. See [[ISS-0062]] Notes: it would mask whether the mechanism works.
- A `plan` nav mode. The whole point is that a plan is not browsed on its own.
- Changing how `PLAN-STATE` validates plans. That check reads notes, not the UI, and is unaffected.

## Acceptance

- Every `PLAN.md` on disk resolves to its feature — asserted against a filesystem glob, so a regression to type-based lookup fails rather than silently dropping the untyped ones.
- A feature with no plan renders exactly as it does today (no empty child, no placeholder row).
- The Library Plans group is gone — removed in [[FEAT-0050]], not here, so the destination lands first.

## Links

- Issue: [[ISS-0062-Most-Plans-Are-Invisible]]
- Tasks: [[TASK-0235-Plan-Lookup-By-Path]], [[TASK-0236-Plan-Nested-Under-Feature]]
- Reduction: [[FEAT-0050-Library-Reduction]]
