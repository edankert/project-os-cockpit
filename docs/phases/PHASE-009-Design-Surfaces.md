---
type: "[[phase]]"
id: PHASE-009
aliases: ["PHASE-009"]
title: "Design surfaces"
status: active
order: 9
owner: user:edwin
created: 2026-07-27
updated: 2026-07-27
goal: "Design moves into the project: the cockpit renders design artifacts live at the viewport the app actually runs at, carries their revisions and the reasoning behind each, and lets a human review them where the notes already live — instead of design happening in a chat transcript and being copied in afterwards."
features:
  - "[[FEAT-0042-Design-Bench]]"
requirements:
  - "[[REQ-0023-Design-Is-A-Project-Record]]"
depends: ["[[PHASE-008-State-And-Review-Surfaces]]"]
related: ["[[REF-0001-Overview-Redesign-Dossier]]", "[[FEAT-0041-Review-Desk]]", "[[ISS-0023-Status-Vocabulary-Drift]]"]
tags: [design]
---

# Design surfaces

## Goal

PHASE-008 gave the agent's *asks* a human surface. This gives the agent's *proposals about how something should look* the same treatment, and closes a gap the last two phases made obvious.

The overview redesign that produced PHASE-008 went through **six revisions in one session**, driven entirely by Edwin's feedback. The final artifact is committed ([[REF-0001-Overview-Redesign-Dossier]], 139KB of HTML). The five earlier revisions, and the reasoning for every change between them, exist only in a chat transcript. That is the loss this phase addresses: the design survived, the design *process* did not.

## Why the cockpit is the right home for this

Not a general claim about design tools — a specific property of this one. A design artifact written in HTML and CSS is **directly renderable by the engine already rendering the docs**. Design and implementation are the same medium here, which makes two things possible that an external design tool cannot offer:

1. The design renders at the viewport the app actually runs at. [[REQ-0022]] is literally about what fits above the fold in a 900px window; a design reviewed at some other size is reviewed against the wrong question.
2. The design's tokens can become the source of truth the implementation is *checked* against. This repo already has that problem instrumented — `base.css` and `cockpit.css` both restate the status palette, they drifted, and [[TST-0019]] exists because of it ([[ISS-0023]]). Design-token drift is the same failure on a new surface, and it is checkable by the same means.

## Scope

- Design artifacts as project records, with revisions and per-revision reasoning.
- A render surface with viewport presets and live reload.
- Side-by-side comparison of two revisions from git.
- Region-anchored annotation, stored as Markdown in the note.
- Review through the existing desk, with per-region verdicts.
- A parity check between declared design tokens and the implementation's CSS.

## Out of Scope

- **A drawing tool.** The artifact is authored as HTML/CSS by an agent or by hand. The cockpit renders, versions, annotates and reviews it; it does not become an editor.
- **A new `DES-*` note type.** Designs have a real lifecycle (`proposed → accepted → implemented | superseded`) that `reference` does not model, but a note type is an upstream taxonomy change. Start on the existing `[[reference]]` + `scope: design-input` convention that [[REF-0001]] already uses; revisit only if the convention proves insufficient.
- **Importing from Figma or any binary design format.** The whole leverage here is that the artifact is text in the same medium as the implementation.

## Exit Criteria

- [ ] A design artifact renders in the cockpit at a selectable viewport, and editing its HTML updates the pane without a reload — evidence: <path + observed>
- [ ] Two revisions of the same artifact render side by side, sourced from git, with the reason for the revision visible — evidence: <path + a real two-revision comparison>
- [ ] [[REF-0001]]'s dossier renders correctly as the first real subject — the existing 139KB artifact, not a synthetic fixture — evidence: <observed>
- [ ] A comment anchored to a declared region survives a revision that moves that region on the page — evidence: <before/after>
- [ ] A design token declared in a design note and changed in the implementation is caught by a test — evidence: <test + inversion>
- [ ] Edwin has reviewed one real design through the surface and recorded a verdict — evidence: <note frontmatter>

## Notes

The last exit criterion is the phase's acceptance demo and cannot be satisfied by an agent, for the same reason [[TST-0011]] could not: the question "is this design good" is the human's, and a recorded verdict the human did not give is exactly the fabricated verification the criterion exists to prevent.

Sequencing is deliberate — render and revisions first ([[TASK-0214]]..[[TASK-0216]]), because they are useful the day they land and need no upstream change. Annotation, review integration and token parity ([[TASK-0217]]..[[TASK-0219]]) follow once there is something real to annotate.
