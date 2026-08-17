---
type: "[[task]]"
id: TASK-0472
aliases: ["TASK-0472"]
title: "The per-item release view — ~release/<id>/<ITEM-ID> answers what this item is, in this release"
status: backlog
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
source: ["[[FEAT-0117-One-View-Per-Item]]"]
parent: "[[FEAT-0117-One-View-Per-Item]]"
effort: L
depends: ["[[TASK-0467-The-Impact-Sweep-At-Close-Out]]"]
blocks: []
related: []
tests: []
---

# The per-item release view

The route extends what exists — `~release/<id>/<ITEM-ID>` — and the navigator's feature and issue rows inside a release group navigate there instead of to the bare note. The page answers *what about this item, in this release*: status and title; **originated** (checks whose `covers:` names it), **invalidated** (checks whose `invalidated_by:` names it or its tasks/issues — the normal coupling, per Edwin's correction), **in its areas** (checks added to its areas since it opened); the mark control inline on every check; the authored `acceptance_impact` line; and a row to the item's own note.

The empty state is the point, not a failure: a feature with all three lists empty shows *"Acceptance impact considered <date> — none: <reason>"* or *"Acceptance impact not yet swept"* — opposite sentences the surface can finally tell apart.

## Done when

- [ ] Rows inside a release open the per-item page; the bare note is one row away; three panes intact.
- [ ] The three lists derive from frontmatter, the mark control writes through the one path, and the no-checks state reads as considered-or-owed in words.
