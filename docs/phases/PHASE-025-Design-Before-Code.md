---
type: "[[phase]]"
id: PHASE-025
aliases: ["PHASE-025"]
title: "Design before code — the bench renders what a design proposes, measures it against what exists, and holds implementation to what was accepted"
status: planned
order: 25
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
goal: "Turn the design bench from a reader of design prose into the place where design happens: variants rendered live and chosen, surfaces measured side by side, annotations that become requests, and an accepted design that implementation is actually held to."
features:
  - "[[FEAT-0067-Designs-Render-Their-Artefacts]]"
  - "[[FEAT-0068-The-Measure-View]]"
  - "[[FEAT-0069-Annotate-To-Request]]"
  - "[[FEAT-0070-Design-Gating-And-Scaffolding]]"
requirements: []
issues: []
depends: ["[[PHASE-023-Levers-For-The-Human]]"]
related: ["[[DES-0007-The-Bench-Closes-The-Loop]]"]
tags: [design, bench]
---

# Design before code

## Where this came from

Edwin named design-up-front as the first area the tool should be better at (2026-08-03). The review found the *loop* missing, not the parts: DES notes, the bench, revision tracking with `design_revision` anti-laundering, and a review-queue kind for "a design offered for review" all exist — but a design is still prose read once. Nothing renders what it proposes, nothing compares options, nothing holds a feature to the design it claims.

The evidence is again PHASE-022: every one of its twelve rounds began with me measuring two surfaces side by side **by hand over CDP**, because the tool has no way to compare its own views. The session's closing line — *"the answer was already on the screen, in a file I had open, and I built a new one instead of looking"* — is a tooling gap wearing a confession.

## Scope

[[FEAT-0067]] — designs carry renderable HTML variants; the bench shows them side by side; choosing one records the decision. [[FEAT-0068]] — the measure view: two surfaces, computed-style table, the differences named. [[FEAT-0069]] — point at a spot, leave a comment, a review-queue entry exists. [[FEAT-0070]] — an accepted design gates the feature that names it, and can scaffold that feature's requirements through a dispatched skill, not silently.

Design: [[DES-0007]] — fittingly, the bench designed in the bench's own format.

## Out of Scope

- **Arbitrary external apps in the measure view.** v1 measures the cockpit's own surfaces and embedded artefacts; pointing it at a fleet app's UI is a later phase with its own risk scan.
- **Automatic requirement generation.** Scaffolding dispatches a skill with the design as source; an agent drafts, the human approves (through PHASE-023's levers). Text appearing without anyone asking is the failure mode FEAT-0051 already rejected.
- **Upstream contract changes by fiat.** The design-gate rule lands here as this repo's validator rule with an upstream proposal task, the same path the close-out rule took.

## Exit Criteria

- [ ] A design's options can be seen and chosen without leaving the cockpit — evidence: <a variant chooser on a real DES>
- [ ] Two surfaces can be compared with measurements, not eyes — evidence: <the measure table that would have caught ISS-0087/0090/0093>
- [ ] A comment on a design lands in the review queue with its anchor — evidence: <an annotation entry>
- [ ] A feature naming an unaccepted design cannot start — evidence: <the gate firing in the validator>
- [ ] The gate rule is proposed upstream — evidence: <the proposal note's id>
