---
type: "[[phase]]"
id: PHASE-014
aliases: ["PHASE-014"]
title: "The project inbox — a place for material that has arrived but not been decided about"
status: done
order: 14
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
goal: "Give a project a staging area for external material — a screenshot, an export, a page of notes — that has arrived but has not been triaged into the record yet, reachable from the app rather than from the Desktop folder."
features:
  - "[[FEAT-0045-Project-Inbox]]"
requirements: []
issues:
  - "[[ISS-0060-Electron-32-Removed-File-Path]]"
  - "[[ISS-0061-Screenshot-Permission-Error-Was-Unreadable]]"
depends: []
related: ["[[PHASE-009-Design-Surfaces]]", "[[PHASE-010-Surface-Ownership]]", "[[ISS-0070-Unanchored-Gitignore-Hid-A-Feature]]", "[[ISS-0074-Sixteen-Delivered-Notes-Stranded-In-The-Parking-Lot]]"]
tags: [inbox, ia]
---

# The project inbox

## Written retrospectively, and saying so

**This phase is a record, not a plan.** The work shipped on 2026-07-28 and this note was written on 2026-07-30, while correcting [[ISS-0074]]. The `order: 14` reflects when the note was allocated, not when the work happened — chronologically it sits between [[PHASE-009]] and [[PHASE-010]].

That is the honest handling of the case [[ISS-0074]] is about. Fifteen of the sixteen stranded notes named a phase that demonstrably delivered them, resolvable from `parent:`, `fixed_by:` or `implements:` without judgement. [[FEAT-0045]] was the sixteenth: built in a day, on request, between two phases whose scope does not cover it. [[PHASE-009]] is design surfaces; [[PHASE-010]] is which page each *note type* belongs on, and an inbox is not a note type. Backdating it into either would have been the fabrication the rule exists to prevent.

So the alternative was a second sentinel meaning "delivered, but unphased" — machinery for a case the corpus contains once. A retrospective phase note is cheaper and says more.

## Goal

`inbox/` at the repo root is **staging**: somewhere to drop a screenshot, an export, or a page of notes that has arrived but has not been decided about. Its success condition is being **empty** — anything sitting there is an unmade decision, not an archive.

Deliberately gitignored and deliberately outside `docs/`: an item is either filed, in which case the *filed* artefact is what gets committed, or discarded. `docs/` is the curated record and untriaged material does not belong in it.

## Scope

- **[[FEAT-0045]]** — the sidecar's `/api/inbox` store and discard routes, drop-and-paste capture, and the tray in the left pane ([[TASK-0232]], [[TASK-0233]], [[TASK-0234]]).
- **[[ISS-0060]]** — Electron 32 removed `File.path`, so every drop silently did nothing.
- **[[ISS-0061]]** — the app reported the absence of screen-recording permission instead of asking for it.
- The `inbox-triage` skill and the `LIFECYCLE.md` section that define what the directory is for.

## Out of Scope

- **Automatic triage.** Reading an item and deciding where it belongs is the human's job; the tray only makes the queue visible.
- **Retention.** Nothing ages items out — an inbox that empties itself defeats the point.

## Exit Criteria

- [x] A file dropped or an image pasted into the app lands in `inbox/` — evidence: [[TASK-0233]]; re-verified after [[ISS-0060]] when Electron 32 broke the path lookup
- [x] The inbox is visible without navigating to it — evidence: [[TASK-0234]], the left-pane tray rather than a top-level section
- [x] `GET /api/inbox` reports the queue, and store/discard are registered — evidence: verified 2026-07-30 in [[CHG-20260730-Two-Features-Closed]]; an empty list is this feature's *success condition*, not an absence of evidence
- [x] `inbox/` is gitignored and a fresh clone sees it empty — evidence: [[ISS-0070]], which found the pattern was **unanchored** and had hidden this feature's own notes from the repository

## Notes

**The gitignore defect belongs to this phase's story.** `inbox/` without a leading slash matches a directory at any depth, so `docs/features/inbox/` — [[FEAT-0045]]'s own record — was absent from `main` for weeks and a fresh clone failed the validator. Found by the [[PHASE-011]] review, fixed as [[ISS-0070]], and swept across nine fleet repos during [[PHASE-013]]. A feature about staging material outside the record accidentally staged its own record outside the repository.

**Closed, not built, in [[PHASE-011]].** [[FEAT-0045]] sat `doing` with all three tasks `done` until PHASE-011's pass — which was about claims nobody had checked — verified it and closed it. That is why its close-out appears in a PHASE-011 change note while the feature belongs here: PHASE-011 resolved it, this phase delivered it, and those are different claims.
