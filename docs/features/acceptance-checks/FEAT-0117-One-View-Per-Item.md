---
type: "[[feature]]"
id: FEAT-0117
aliases: ["FEAT-0117"]
title: "One view per item — a release's row opens the item as it stands in this release, not the bare note"
status: review
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
source: ["Edwin 2026-08-17: 'It also feels like having features defined as they are now, makes them selectable in this view but instead you would like to have one view per item.'"]
goal: "Selecting a feature inside a release answers 'what about this item, in this release' — its status, the checks it originated, the checks it invalidated, the checks added to its areas, its authored acceptance_impact line, the issues it closed since the baseline, and a row to its own note — instead of dropping the reader onto a plain note with no release context."
requirements: []
tasks: ["[[TASK-0472-The-Per-Item-Release-View]]"]
design: ""
release: ""
depends: ["[[FEAT-0115-The-Sweep-Is-Continuous]]"]
related: ["[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]", "[[FEAT-0107-Publication-Is-A-List-Of-Releases]]", "[[PHASE-035-Acceptance-Checks-Are-Notes]]"]

---

# One view per item

## The mismatch, and the reading

Edwin: *"having features defined as they are now, makes them selectable in this view but instead you would like to have one view per item."* The review's reading, which he did not correct: you select a feature *inside a release* and receive something with no release context — `navigateTo('/docs/features/…')` renders the plain note. The thing selected and the thing received are mismatched.

The route extends what exists: **`~release/<id>/<ITEM-ID>`**, navigator rows inside a release group navigate there, three panes intact — the navigator navigates, the centre pane acts.

## Why it is deliberately last

Two reasons, both from the review and both Edwin-shaped. First, the item list was wrong until this phase fixes it — features only, never frozen — and a per-item view over a wrong list multiplies the error. Second, his own correction: *"not all features might need acceptance tests"* — the coupling runs through invalidation, so the page's three lists (originated / invalidated / in its areas) only exist once `covers:` and `invalidated_by:` are fields, which is [[FEAT-0113-The-Check-Type-And-The-Migration]] and [[FEAT-0115-The-Sweep-Is-Continuous]]. A feature whose three lists are all empty shows its `acceptance_impact` line — *"considered, none"* or *"not yet swept"* — which are opposite sentences the surface can finally tell apart, rather than looking broken.

## Acceptance criteria

- [ ] A feature row inside a release opens `~release/<id>/<ITEM-ID>` and never the bare note; the bare note is one row away.
- [ ] The page shows the three derived lists with the mark control inline on each check, and the authored `acceptance_impact` line.
- [ ] A feature with no checks anywhere reads as considered-or-owed, in words — never as an empty page.
