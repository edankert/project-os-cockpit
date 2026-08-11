---
type: "[[feature]]"
id: FEAT-0067
aliases: ["FEAT-0067"]
title: "Designs render their artefacts — variants as sandboxed fragments side by side, and choosing one records the decision"
status: done
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[DES-0007-The-Bench-Closes-The-Loop]]"]
goal: "A `## Variant <name>` section with a fenced html block renders in the bench as a live, sandboxed, token-inheriting fragment; variants sit side by side; Choose stamps `chosen_variant` and scaffolds the ADR as a proposal for the actuator row to accept."
requirements: []
tasks:
  - "[[TASK-0300-Variant-Parse-And-Sandbox]]"
  - "[[TASK-0301-Side-By-Side]]"
  - "[[TASK-0302-Choose-Records-The-Decision]]"
release: "[[REL-0001-The-Human-Has-Levers]]"
related: ["[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]"]
tests: []
---

# Designs render their artefacts

## Goal

Convention over machinery — the variant is a markdown section, so agents and humans author it with what they have. The bench does the rest: sandboxed iframes (`sandbox` sans scripts unless the note opts in), the design-system stylesheet injected so mockups wear real tokens, revisions already tracked by the existing machinery.

## Out of Scope

- A visual editor. Authoring stays in files.
- Auto-accepting the scaffolded ADR — it arrives `proposed`, the human accepts through PHASE-023's row.

## Acceptance

- [x] `## Variant <name>` + a fenced html block renders as a live, sandboxed, token-inheriting fragment ([[TASK-0300]])
- [x] Sandboxed **without** `allow-scripts` unless the note sets `scripts: true` — a per-note recorded decision, not a renderer allowance
- [x] A variant whose note declares no stylesheets renders unstyled rather than failing
- [x] Variants sit beside each other, in a row that scrolls rather than a grid that wraps ([[TASK-0301]])
- [x] `Choose` writes `chosen_variant` through the guarded actuator path and **does not accept the design** ([[TASK-0302]])
- [x] The ADR is **offered and dispatched**, arriving `proposed` — nothing is auto-accepted

## Verification

`tests/test_design_variants.py` — 11 tests. Two guard the security shape (script-free by default, opt-in from the note) and two guard the judgment boundary: choosing a shape leaves `status: proposed` untouched, and a variant nobody wrote cannot be chosen.
