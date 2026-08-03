---
type: "[[feature]]"
id: FEAT-0067
aliases: ["FEAT-0067"]
title: "Designs render their artefacts — variants as sandboxed fragments side by side, and choosing one records the decision"
status: planned
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[DES-0007-The-Bench-Closes-The-Loop]]"]
goal: "A `## Variant <name>` section with a fenced html block renders in the bench as a live, sandboxed, token-inheriting fragment; variants sit side by side; Choose stamps `chosen_variant` and scaffolds the ADR as a proposal for the actuator row to accept."
requirements: []
tasks: []
release: ""
related: ["[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]"]
tests: []
---

# Designs render their artefacts

## Goal

Convention over machinery — the variant is a markdown section, so agents and humans author it with what they have. The bench does the rest: sandboxed iframes (`sandbox` sans scripts unless the note opts in), the design-system stylesheet injected so mockups wear real tokens, revisions already tracked by the existing machinery.

## Out of Scope

- A visual editor. Authoring stays in files.
- Auto-accepting the scaffolded ADR — it arrives `proposed`, the human accepts through PHASE-023's row.
