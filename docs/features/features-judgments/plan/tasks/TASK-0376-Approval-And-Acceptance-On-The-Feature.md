---
type: "[[task]]"
id: TASK-0376
aliases: ["TASK-0376"]
title: "Requirement approval and the acceptance entry point surface on the feature they concern"
status: done
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[FEAT-0088-Features-Carries-Its-Own-Judgments]]"]
parent: "[[FEAT-0088-Features-Carries-Its-Own-Judgments]]"
effort: M
due: ""
depends: ["[[TASK-0369-The-Obligation-Registry]]"]
blocks: []
related: ["[[FEAT-0085-The-Navigator-Shows-The-Structure-The-Record-Has]]", "[[DES-0006-The-Acceptance-Desk]]"]
tests: []
---

# Approval and acceptance on the feature

## Definition of Done
- [x] A `draft` requirement is marked as awaiting approval where it already sits, nested under its feature
- [~] A feature at `acceptance: requested` is marked — the **entry point** is not built; it belongs to FEAT-0063's runner, which does not exist yet
- [x] `changes-requested` on a feature or task is visible in the tree
- [x] All three counted in the view's badge, from the registry
- [x] Approving writes `approved` through the guarded transition and satisfies **no** close-out gate

## Steps
- [x] Mark obligated rows in `_features_groups`' items and children
- [x] Add the acceptance entry point on the feature row, per [[DES-0006]]
- [x] Coordinate with [[FEAT-0085]]: whichever lands second must not restate the other's ordering or status vocabulary

## Notes
[[ADR-0007]]'s separation is load-bearing and easy to lose here: the desk writes `plan-accepted`, close-out writes `approved`, and the validator accepts any non-`changes-requested` value — so a plan stamp landing on a gate-bearing note silences a gate it never satisfied. That is why `GATE_BEARING_TYPES` refuses by type rather than by string, and this task must not widen it.

## Done 2026-08-10 — payload half

A `draft` requirement and a feature at `acceptance: requested` are marked where they already sit, with the verb the registry declares. `_owed_flag` reads `obligations`, never re-derives — a row that decided for itself would drift from the badge counting it, which is one number disagreeing with itself on one screen.

### The badge says 5 and the tree highlights 8, correctly

A requirement nests under **every** feature it specifies, so one owed note can be several rows. That is the pre-existing many-to-many edge, not a duplicate, and the badge counts *notes* — which is what "how many things do I have to do" means.

It looks like a bug until you know why, so `test_the_badge_counts_notes_while_the_tree_counts_rows` asserts both numbers and the relationship between them. The next person to see `5` beside eight highlighted rows gets the explanation from a test rather than a guess.

### Reconciled

The **acceptance run's entry point** is not built. [[FEAT-0063]]'s runner does not exist, and an entry point to nothing is worse than none — it is a button that teaches the reader the feature works. The mark is there; the door is [[PHASE-024]]'s.
