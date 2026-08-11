---
type: "[[phase]]"
id: PHASE-025
aliases: ["PHASE-025"]
title: "Design before code — the bench renders what a design proposes, measures it against what exists, and holds implementation to what was accepted"
status: done
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

- [x] A design's options can be seen and chosen without leaving the cockpit — evidence: `## Variant <name>` sections render as live sandboxed fragments side by side, and `Choose` writes `chosen_variant` through the guarded path ([[TASK-0300]]–[[TASK-0302]]). Choosing does **not** accept the design — two judgments, kept apart (user:edwin, 2026-08-11)
- [x] Two surfaces can be compared with measurements, not eyes — evidence: the measure panel harvests box/type/colour/space via `getComputedStyle` and diffs them into a table, copyable as the markdown shape PHASE-022's issues used ([[FEAT-0068]]). Not pixel diffing — [[DES-0007]]'s rejection holds (user:edwin, 2026-08-11)
- [x] A comment on a design lands in the review queue with its anchor — evidence: `annotation` joins the store's kinds with an allow-listed anchor (`variant` / `path` / `quote`), round-tripped and re-resolved as `found`/`moved`/`lost` ([[FEAT-0069]]). A coordinate cannot be persisted under any name (user:edwin, 2026-08-11)
- [~] A feature naming an unaccepted design cannot start — **reconciled: it warns rather than blocks.** `DESIGN-GATE` fires on a feature past the pending band whose design was never accepted, proven both ways and quiet on this corpus ([[TASK-0309]]). "Cannot start" was the criterion as written; a blocking gate on a judgment that cannot be automated gets cleared to unblock the build rather than because somebody looked, which is the same argument ACCEPT-STALE and independent review both settled on. Escalation is deferred until lived with ([[ADR-0011]]'s path)
- [x] The gate rule is proposed upstream — evidence: `TAXONOMY.md` carries `design:` and `DESIGN-GATE` marked as deliberate local divergence with the reasoning, including the narrowed satisfied set that the obvious rule gets wrong ([[TASK-0311]]) (user:edwin, 2026-08-11)
