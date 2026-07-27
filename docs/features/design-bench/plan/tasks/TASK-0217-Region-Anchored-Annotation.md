---
type: "[[task]]"
id: TASK-0217
aliases: ["TASK-0217"]
title: "Region-anchored annotation, stored as Markdown"
status: done
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
- [x] A comment is written as Markdown into the design note's `## Review` section through the guarded writer, never as a runtime record — evidence: `append_design_comment` / `read_design_comments`; `test_comments_are_plain_markdown_in_the_note`
- [x] A comment survives a revision that **moves its region on the page** — the acceptance test, since coordinate anchoring is what this design rejects — evidence: `test_a_comment_survives_its_region_MOVING_on_the_page` reorders the document and the anchor holds
- [x] A comment whose region disappears in a later revision is shown as orphaned rather than silently dropped — evidence: `test_a_comment_ORPHANS_when_its_region_is_renamed` — flagged, never dropped
- [~] A validator check reports a design artifact that declares no regions at all — **deferred.** DESIGN-ASSET/DESIGN-ORPHAN are upstream; a no-regions check belongs with them and would fire on every pre-contract artifact in the fleet until each is retrofitted. Recorded rather than shipped as noise.
- [x] The note remains readable without the cockpit: a reviewer can read the comments as plain text and tell what each refers to — evidence: comments are `- **region** · date · author — text` lines a reviewer can read as text

## Steps

- [x] Define the region attribute convention and document it in the design-note guidance
- [x] Extract declared regions from an artifact; render pins over the frame
- [x] Write comments via `note_writes.py` with a `DESIGN_FIELDS` allow-list and mtime preconditions, matching the existing guarded-write pattern
- [x] Test the survives-a-revision case with a real moved region
- [x] Test the orphaned-region case

## Result

The discriminating pair, both tested: a comment **survives its region moving** on the page (reordered document, anchor holds) and **orphans when the region is renamed** — flagged, never dropped, because a comment that vanishes takes the objection with it and the reviewer has no way to know.

Fable called the move case near-tautological under id anchoring, and was right; it is kept as the premise check and the rename case is what actually discriminates. Duplicate ids dedupe in declaration order — the real dossier's `data-pin` numbers restart per plate, which is why the contract requires scoping.

**The document lane exists.** A region of `""` carries criticism that has no region — *"too much violet everywhere"*, or a complaint about the relationship between two areas. Inventing a region to host those would make the region list a fiction.

The endpoint refuses an undeclared region **and says what is valid**, because a comment anchored to nothing would never render and the objection would be lost silently.

## Notes

The whole design turns on rejecting coordinate anchors. Pixel-pinned comments die on the next revision, and the founding artifact went through six in a single session — so coordinate anchoring would have produced a comment set that was worthless by v2.

Region anchoring has a second benefit that is arguably larger: it forces the artifact to name its own structure. A design that cannot say which part is the "focus band" has not been thought through, and the annotation surface makes that visible for free.

Storing comments as Markdown in the note rather than in cockpit state is [[REQ-0023]]'s "readable without the tool" clause. It is also what lets a comment be reviewed, diffed, and blamed like everything else.
