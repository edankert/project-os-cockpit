---
type: "[[task]]"
id: TASK-0464
aliases: ["TASK-0464"]
title: "The generated list view — the same suite a reader knows, from notes, and the document plumbing retired"
status: doing
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
source: ["[[FEAT-0114-The-Suite-Is-A-View]]"]
parent: "[[FEAT-0114-The-Suite-Is-A-View]]"
effort: L
depends: ["[[TASK-0461-Pilot-This-Repo]]"]
blocks: []
related: ["[[ISS-0185-The-Mark-Control-Sits-Inside-Tasklists-Leftover-Box-And-The-Cycle-Makes-You-Walk-Past-States]]"]
tests: []
---

# The generated list view

Tier → area → rows in `ordinal` order, the rules preamble as a page header, and filters over mark, tier, area, covering feature and automation — every filter derived from frontmatter, none from prose. The mark dialog is `askForMark`, unchanged: the review confirmed it consumes plain data and is storage-independent.

What gets retired is the document plumbing: `mountAcceptanceMarks` and the `li[data-check]`/`data-mark` path exist only because the stored file was the display, and they lose their subject with it. Deleted, not stranded — the unreachable-function guard is the check that nothing keeps reading as coverage.

## Done when

- [ ] A reader who knew the document finds nothing missing — preamble, tier counts, area order, every row.
- [ ] Marking from the view writes the note and repaints without moving the reader — the ISS-0187..0189 lesson, held on the new surface from day one.
- [ ] `mountAcceptanceMarks` is gone and the guard suite is green.

## Outcome, 2026-08-17

The view is built at `~checks` — tier, area, rows in `ordinal` order, the rules preamble as a row rather than republished prose, filters over mark, tier, area, covering feature and automation, and `askForMark` unchanged. Marking from it holds the reader's position twice, once synchronously and once inside the animation frame, which is the [[ISS-0188]] answer inherited rather than re-earned.

**The deletion clause is not met, and cannot be yet.** `mountAcceptanceMarks` and the `li[data-check]` path are still here because `../your-trainer` still stores its suite as a document, and deleting the document's mark control would leave a live fleet surface with no way to mark anything. They lose their subject when the last file-shaped suite migrates ([[TASK-0463-The-Fleet-Migrates-Trainer-Last]]) and should be deleted in that same commit — with the unreachable-function guard as the check that nothing is left reading as coverage.
