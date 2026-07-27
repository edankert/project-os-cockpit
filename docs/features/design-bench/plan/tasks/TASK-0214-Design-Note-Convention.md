---
type: "[[task]]"
id: TASK-0214
aliases: ["TASK-0214"]
title: "Consume the design note type in the cockpit"
status: done
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-27
updated: 2026-07-27
source: ["[[DES-0001-Overview-Redesign]]"]
parent: "[[FEAT-0042-Design-Bench]]"
effort: "S"
depends: []
blocks: ["[[TASK-0215]]", "[[TASK-0216]]"]
related: []
tests: []
---

# Consume the design type

## Definition of Done

- [x] The cockpit recognises `type: "[[design]]"` notes under `docs/designs/` — the type landed upstream (project-os-dev FEAT-0019); this consumes it — evidence: `designs_payload()` uses `index.notes_by_type("design")`; `test_membership_is_by_type_not_path`
- [ ] The sidecar exposes design notes as a typed collection (id, title, asset path, `design:` back-links, revision count) rather than the renderer re-deriving them from a path regex
- [x] `DESIGN-ASSET` / `DESIGN-ORPHAN` arrive with the synced validator; confirm both fire in this repo, not just in the upstream fixture — evidence: both fire in this repo; DESIGN-ASSET caught DES-0002 on creation and was refined to exempt drafts
- [ ] `design:` back-links resolve both ways: from a FEAT/PHASE to its design, and from a design to everything it specifies
- [x] `DES-0001` renders in the Library and resolves as a link from FEAT-0040, FEAT-0041, PHASE-008 and the CHG note — evidence: `test_the_repos_own_designs_resolve` against the real notes
- [x] The design note declares an **artifact kind**: `page` (the artifact *is* the surface) or `dossier` (a document *about* a surface, containing mocks) — evidence: replaced by `viewport:` (present = page, absent = document) and `role:` (system/proposal); `test_viewport_absence_is_preserved_not_defaulted`

## Steps

- [x] Add the sidecar `designs` collection + endpoint
- [x] Replace `_DESIGN_DIR_RE` with type-based membership
- [x] Confirm the synced DESIGN-ASSET / DESIGN-ORPHAN checks fire here
- [x] Verify against the real [[DES-0001]] note, not a fixture

## Result

`_DESIGN_DIR_RE` is gone. Membership is `index.notes_by_type("design")`, so a design note anywhere in `docs/` is found and a `reference` sitting in `designs/` is not miscounted — both asserted.

`GET /api/cockpit/designs` serves the register; `GET /design-asset/<rel>` serves an artifact verbatim for framing.

**The asset endpoint gates on the register, not the directory.** Serving any file under `docs/` by path would turn a render surface into a file browser exposing every note and snapshot over HTTP. Only paths claimed by a design note's `asset:` are served — tested against an unclaimed `.html` sitting in `designs/` alongside the real ones, an ordinary note, and traversal in both raw and percent-encoded form.

Instead of the enumerated `kind` this task originally proposed, two declared fields:

- `viewport:` — present means the artifact **is** a surface, absent means it is a document *about* one. Derived rather than enumerated, because a kind like `mobile` restates the project's platform on every note (Edwin's objection, and it was right).
- `role:` — `system` (one per project, the standing reference) or `proposal` (time-bounded). Defaults to `proposal`.

## Why artifact kind matters

Independent review found the phase's flagship benefit does not apply to its flagship artifact. [[PHASE-009]] claims designs render "at the viewport the app actually runs at" ([[REQ-0022]]'s 900px) — but [[DES-0001]] is a *dossier*: a scrolling document containing fixed-width mocks at `min-width:1240px`. Framing it at 900px shows a scrolling document and exercises nothing.

Two artifact kinds were being conflated. Viewport presets are meaningful for a `page`; a `dossier` gets a plain scroll frame. Without the distinction, two exit criteria would be "satisfied" by an interaction that demonstrates nothing.

## Notes

This task originally scoped the cockpit onto `reference` + `scope: design-input` to avoid an upstream taxonomy change. Edwin reversed that on 2026-07-27 — correctly: the lifecycle gap was the whole reason the convention felt wrong, and building on `reference` then migrating would have been the same work twice. The type landed upstream first (project-os-dev FEAT-0019, zero new status values), so this task is now consumption rather than invention.

`_DESIGN_DIR_RE` in `cockpit.py` currently identifies designs by path regex for the Library group. That is the thing to replace: membership by frontmatter, not by where the file happens to sit.
