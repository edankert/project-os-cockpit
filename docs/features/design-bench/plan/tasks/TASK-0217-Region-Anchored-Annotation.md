---
type: "[[task]]"
id: TASK-0217
aliases: ["TASK-0217"]
title: "Region-anchored annotation, stored as Markdown"
status: backlog
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-27
updated: 2026-07-27
source: ["user request 2026-07-27"]
parent: "[[FEAT-0042-Design-Bench]]"
effort: "M"
depends: ["[[TASK-0215]]"]
blocks: ["[[TASK-0218]]"]
related: ["[[REQ-0023-Design-Is-A-Project-Record]]"]
tests: []
---

# Region-anchored annotation

## Definition of Done

- [ ] An artifact declares regions with `data-design-region="<id>"`; the surface pins comments to those IDs
- [ ] A comment is written as Markdown into the design note's `## Review` section through the guarded writer, never as a runtime record
- [ ] A comment survives a revision that **moves its region on the page** — the acceptance test, since coordinate anchoring is what this design rejects
- [ ] A comment whose region disappears in a later revision is shown as orphaned rather than silently dropped
- [ ] A validator check reports a design artifact that declares no regions at all
- [ ] The note remains readable without the cockpit: a reviewer can read the comments as plain text and tell what each refers to

## Steps

- [ ] Define the region attribute convention and document it in the design-note guidance
- [ ] Extract declared regions from an artifact; render pins over the frame
- [ ] Write comments via `note_writes.py` with a `DESIGN_FIELDS` allow-list and mtime preconditions, matching the existing guarded-write pattern
- [ ] Test the survives-a-revision case with a real moved region
- [ ] Test the orphaned-region case

## Notes

The whole design turns on rejecting coordinate anchors. Pixel-pinned comments die on the next revision, and the founding artifact went through six in a single session — so coordinate anchoring would have produced a comment set that was worthless by v2.

Region anchoring has a second benefit that is arguably larger: it forces the artifact to name its own structure. A design that cannot say which part is the "focus band" has not been thought through, and the annotation surface makes that visible for free.

Storing comments as Markdown in the note rather than in cockpit state is [[REQ-0023]]'s "readable without the tool" clause. It is also what lets a comment be reviewed, diffed, and blamed like everything else.
