---
type: "[[plan]]"
title: "Plan — FEAT-0100 Unpushed work needs a person"
status: draft
owner: user:edwin
created: 2026-08-13
updated: 2026-08-13
source: []
implements: ["[[FEAT-0100-Unpushed-Work-Needs-A-Person]]"]
related: ["[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[DES-0011-Publication-Is-An-Obligation]]", "[[ISS-0156-The-Open-Workspace-Is-The-One-Whose-Unpushed-Count-Is-Never-Computed]]"]
---

# Plan — FEAT-0100 Unpushed work needs a person

## Delivery sequence

1. **[[TASK-0415]] — the data.** Fix [[ISS-0156]] so every workspace has a count, including the one with a live sidecar. **Hard first:** absent-at-zero means an unknown count renders as *nothing owed*, so everything after this would ship a surface that is silent exactly where it matters and looks correct while being wrong.
2. **[[TASK-0416]] — the path.** Generalise the note-less obligation so a source yields its count and its rows from one walk. Before the registry entry, not after: adding git the way standing was added is what creates the third and fourth places for the number to disagree with itself.
3. **[[TASK-0417]] — the registry entry.** Publication becomes an obligation owned by the overview, with its noun and verb. The badge and the `Needs you` row both follow from this with no new UI.
4. **[[TASK-0418]] — the surface.** The design artifact, then history marks the unpublished commits and carries the push.

1 and 2 are independent of each other and can run in either order or together; 3 needs both; 4 needs 3.

## Dependencies

- **Hard:** [[ADR-0027]] (accepted 2026-08-13); [[ISS-0156]] fixed; the existing registry, `_needs_you_group()`, and `refreshObligationBadges()` — all of which already do their half.
- **Soft:** [[DES-0011]] leaving `draft`, which requires its artifact ([[TASK-0418]]). The build should not run ahead of the artifact for the history surface; steps 1–3 are not design-gated because they add no new UI.

## Open questions

Carried from [[DES-0011]] rather than restated: whether a deploy remote is counted as an obligation with its own verb (leaning yes), and what marks an unpushed commit in the history list. Both are the artifact's to settle.

## What this deliberately does not touch

`git.ts`'s single home for the deploy-remote refusal. Every surface that offers a push calls it; a second copy is how the two come to disagree on the one action in this app that publishes.
