---
type: "[[feature]]"
id: FEAT-0042
aliases: ["FEAT-0042"]
title: "Design bench — render, revise, annotate and review designs in the cockpit"
status: doing
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-27
updated: 2026-07-27
source: ["user request 2026-07-27", "[[DES-0001-Overview-Redesign]]"]
goal: "Make a design artifact a first-class project record the cockpit can render live at the real viewport, version with its reasoning, annotate by region, review through the existing desk, and check the implementation against."
requirements: ["[[REQ-0023-Design-Is-A-Project-Record]]"]
tasks:
  - "[[TASK-0214-Design-Note-Convention]]"
  - "[[TASK-0215-Design-Render-Surface]]"
  - "[[TASK-0216-Design-Revisions-And-Compare]]"
  - "[[TASK-0217-Region-Anchored-Annotation]]"
  - "[[TASK-0218-Design-Review-In-The-Desk]]"
  - "[[TASK-0219-Design-Token-Parity]]"
release: ""
design: ["[[DES-0001-Overview-Redesign]]"]
related: ["[[FEAT-0041-Review-Desk]]", "[[FEAT-0008-Cockpit-API-Hardening]]", "[[TST-0019-Status-Vocabulary-Parity]]"]
tests: []
---

# Design bench

## Goal

Design currently happens outside the project and is copied in afterwards. [[DES-0001]] is the evidence: a 139KB dossier committed under `docs/references/design/`, produced through six revisions in a chat session, of which only the last survives and none of the reasoning does.

This makes the project the home. A design artifact gets rendered at the viewport the app runs at, carries its revisions and the reason for each, can be annotated where it is wrong, reviewed where the other notes are reviewed, and checked against the implementation it specifies.

## Scope

**Phase 1 — useful the day it lands.**
- Consume the `[[design]]` type that landed upstream (project-os-dev FEAT-0019): typed membership, not the path regex the Library group uses today ([[TASK-0214]]).
- A render surface with viewport presets and live reload ([[TASK-0215]]).
- Revisions from git, side by side, with per-revision reasoning ([[TASK-0216]]).

**Phase 2 — once there is something real to annotate.**
- Region-anchored comments stored as Markdown ([[TASK-0217]]).
- Review through the desk with per-region verdicts ([[TASK-0218]]).
- Declared design tokens checked against the implementation's CSS ([[TASK-0219]]).

## Out of Scope

- **Authoring/drawing.** The artifact is HTML/CSS written by an agent or by hand. This renders, versions, annotates and reviews it.
- **Defining the `DES-*` type.** Done upstream first (project-os-dev FEAT-0019) so this phase builds on it rather than migrating onto it later.
- **Auto-stamping a design verdict.** Same rule as every other review surface (`note_writes.py`, ADR-0013): the machine gathers, the human decides.

## Acceptance

- The existing [[DES-0001]] dossier renders correctly — the real 139KB artifact, not a fixture.
- Editing a design artifact updates the pane without a manual reload, via the existing watcher/SSE path.
- Two git revisions of one artifact render side by side with the reason for the change visible.
- A comment anchored to a declared region still points at that region after a revision moves it on the page.
- A design token changed in the implementation but not the design note fails a test, and the test fails when the fix is reverted (adequacy, per QUALITY.md).
- Rendering an artifact cannot execute anything that reaches the real repo — the render frame is sandboxed and treats artifact HTML as content, not code.

## Design constraints worth stating

**Annotations anchor to declared regions, never to coordinates.** The artifact declares `data-design-region="focus-band"`; a comment references that ID. Coordinate anchors die on the next revision, and the founding artifact went through six. Region anchors survive, and they force the design to name its own structure — which is worth having independently.

**Storage stays plain text.** Comments are Markdown in the design note; revisions are git. No database, nothing the cockpit owns exclusively, everything diffable and readable without the tool. Same reason the rest of project-os works this way.

**The parity check is the point of building this here.** `base.css` and `cockpit.css` both restate the status palette, they drifted, and [[TST-0019]] exists because of it ([[ISS-0023]]). A design token declared in one place and implemented in another is the identical failure. No external design tool can close that loop; this can.

## Links
- Phase: [[PHASE-009-Design-Surfaces]]
- Requirement: [[REQ-0023-Design-Is-A-Project-Record]]
- First subject: [[DES-0001-Overview-Redesign]]
