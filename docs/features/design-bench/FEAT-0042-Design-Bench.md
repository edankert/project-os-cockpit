---
type: "[[feature]]"
id: FEAT-0042
aliases: ["FEAT-0042"]
title: "Design bench — render, revise, annotate and review designs in the cockpit"
status: review
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-27
updated: 2026-07-27
source: ["user request 2026-07-27", "[[DES-0001-Overview-Redesign]]"]
goal: "Make a design artifact a first-class project record the cockpit can render live at the real viewport, version with its reasoning, annotate by region, review through the existing desk, and check the implementation against."
requirements: ["[[REQ-0023-Design-Is-A-Project-Record]]"]
tasks:
  - "[[TASK-0214-Design-Note-Convention]]"
  - "[[TASK-0220-Revision-Capture]]"
  - "[[TASK-0221-Design-Authoring-Contract]]"
  - "[[TASK-0215-Design-Render-Surface]]"
  - "[[TASK-0216-Design-Revisions-And-Compare]]"
  - "[[TASK-0217-Region-Anchored-Annotation]]"
  - "[[TASK-0218-Design-Review-In-The-Desk]]"
  - "[[TASK-0219-Design-Token-Parity]]"
  - "[[TASK-0227-Expose-Shell-Stylesheet]]"
  - "[[TASK-0228-Living-Style-Guide]]"
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
- Revision **capture** — commit-with-reason, plus a revision log in the note ([[TASK-0220]]).
- Revisions from git, side by side, with per-revision reasoning ([[TASK-0216]]).

**Phase 2 — once there is something real to annotate.**
- An authoring contract for conforming artifacts ([[TASK-0221]]).
- Region-anchored comments stored as Markdown ([[TASK-0217]]).
- Review through the desk with per-region verdicts ([[TASK-0218]]).
- A scoped palette check against `statuses.py` ([[TASK-0219]]).

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

**The point of building this here is the live render loop and the record** — a design rendered by the same engine as the implementation, at the viewport the app runs at, with its revisions in git beside the features it specifies.

An earlier draft of this note claimed the *token parity check* was the justification. Independent review refuted that, and the evidence is in the founding artifact: [[DES-0001]] names its tokens `--m-done`, `--t-feature`, `--m-accent` while the implementation says `--status-done`, `--severity-critical`, `--accent-link`; its `--m-accent:#3b6ea8` differs from the implementation's `hsl(212 48% 42%)` (≈`#386ba0`) in a block the dossier labels "cockpit tokens, verbatim". The vocabularies do not correspond, so comparing them needs a name mapping — and a hand-maintained mapping is the drift surface reintroduced one level up.

Worse, the direction of authority was contradicted inside this repo on the day it was written: [[TASK-0219]] said "the design becomes the upstream side", while [[DES-0001]]'s own Maintenance section says to *update the HTML when the surfaces change* — i.e. the design trails the code. A parity test with no agreed arrow accumulates waivers.

What survives is narrower and real: a **scoped** check that a design's status/severity palette equals the `statuses.py`-derived palette, with the name mapping declared once in the design's `## Tokens` section. That is worth building. It is not why this phase exists.

## Links
- Phase: [[PHASE-009-Design-Surfaces]]
- Requirement: [[REQ-0023-Design-Is-A-Project-Record]]
- First subject: [[DES-0001-Overview-Redesign]]
