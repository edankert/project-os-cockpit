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
related: ["[[DES-0001-Overview-Redesign]]", "[[FEAT-0041-Review-Desk]]", "[[ISS-0023-Status-Vocabulary-Drift]]"]
tags: [design]
---

# Design surfaces

## Goal

PHASE-008 gave the agent's *asks* a human surface. This gives the agent's *proposals about how something should look* the same treatment, and closes a gap the last two phases made obvious.

The overview redesign that produced PHASE-008 went through **six revisions in one session**, driven entirely by Edwin's feedback. The final artifact is committed ([[DES-0001-Overview-Redesign]], 139KB of HTML). The five earlier revisions, and the reasoning for every change between them, exist only in a chat transcript. That is the loss this phase addresses: the design survived, the design *process* did not.

## Why the cockpit is the right home for this

Not a general claim about design tools — a specific property of this one. A design artifact written in HTML and CSS is **directly renderable by the engine already rendering the docs**. Design and implementation are the same medium here, which makes two things possible that an external design tool cannot offer:

1. The design renders at the viewport the app actually runs at. [[REQ-0022]] is literally about what fits above the fold in a 900px window; a design reviewed at some other size is reviewed against the wrong question.
2. The design's tokens can become the source of truth the implementation is *checked* against. This repo already has that problem instrumented — `base.css` and `cockpit.css` both restate the status palette, they drifted, and [[TST-0019]] exists because of it ([[ISS-0023]]). Design-token drift is the same failure on a new surface, and it is checkable by the same means.

## Scope

- Design artifacts as project records, with revisions and per-revision reasoning.
- A render surface with viewport presets and live reload.
- Side-by-side comparison of two revisions from git.
- Revision capture: a commit-with-reason action that deposits the history the compare view renders.
- An authoring contract so produced artifacts can satisfy the checks this phase adds.
- Region-anchored annotation, stored as Markdown in the note.
- Review through the existing desk, with per-region verdicts.
- A scoped palette check: a design's status colours against the `statuses.py`-derived palette.

## Out of Scope

- **A drawing tool.** The artifact is authored as HTML/CSS by an agent or by hand. The cockpit renders, versions, annotates and reviews it; it does not become an editor.
- **Defining the `DES-*` type.** That is upstream work and it landed first, deliberately: project-os-dev FEAT-0019 added the type, the status vocabulary, the template and the validator checks before this phase builds anything. Scoping this phase on the `reference` convention and migrating afterwards would have meant doing the work twice.
- **Importing from Figma or any binary design format.** The whole leverage here is that the artifact is text in the same medium as the implementation.

## Exit Criteria

- [ ] A design artifact renders in the cockpit at a selectable viewport, and editing its HTML updates the pane without a reload — evidence: <path + observed>
- [ ] Two revisions render side by side from git with the reason visible, using **history deposited by [[TASK-0220]]** rather than a fixture manufactured for the test — evidence: <the capture, then the comparison>
- [ ] [[DES-0001]]'s dossier renders **identically to the same file opened directly in a browser** — the existing 139KB artifact, not a synthetic fixture. ("Renders correctly" was unfalsifiable; this is the test TASK-0215 already specifies.) — evidence: <side-by-side>
- [ ] A comment survives a region being **renamed** and behaves correctly when an artifact declares **duplicate region IDs** — evidence: <both cases>

  *(Surviving a region that merely moves is true by construction of ID anchoring and tests nothing. Rename is indistinguishable from delete-and-add, so a comment can orphan silently; duplicate IDs are near-certain in a multi-plate dossier. Those are the cases that discriminate.)*
- [ ] A design token declared in a design note and changed in the implementation is caught by a test — evidence: <test + inversion>
- [ ] Edwin has reviewed one real design through the surface and recorded a verdict — evidence: <note frontmatter>
- [ ] **A design produced after this phase lands carries ≥2 committed revisions, each with its reason, without anyone rescuing the history by hand** — evidence: <git log + the note's Revisions section>

  *(The only criterion that would have failed under the old workflow, which is what makes it the one worth having. Without it the phase can exit green while the next session loses five revisions exactly as before.)*

## Notes

The last exit criterion is the phase's acceptance demo and cannot be satisfied by an agent, for the same reason [[TST-0011]] could not: the question "is this design good" is the human's, and a recorded verdict the human did not give is exactly the fabricated verification the criterion exists to prevent.

Sequencing, revised after independent review: convention ([[TASK-0214]]), authoring contract ([[TASK-0221]]), render ([[TASK-0215]]), **capture ([[TASK-0220]]) before compare ([[TASK-0216]])** — rendering history is worthless while nothing deposits it, and every week without capture is potentially another design process lost. Annotation, desk review and the scoped palette check ([[TASK-0217]]..[[TASK-0219]]) follow. Annotation, review integration and token parity ([[TASK-0217]]..[[TASK-0219]]) follow once there is something real to annotate.
