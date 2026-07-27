---
type: "[[task]]"
id: TASK-0221
aliases: ["TASK-0221"]
title: "Design authoring contract — what a conforming artifact looks like"
status: done
phase: "[[PHASE-009-Design-Surfaces]]"
owner: user:edwin
created: 2026-07-27
updated: 2026-07-27
source: ["review:model:claude-fable-5 2026-07-27"]
parent: "[[FEAT-0042-Design-Bench]]"
effort: "S"
depends: ["[[TASK-0214]]"]
blocks: ["[[TASK-0217]]", "[[TASK-0219]]"]
related: []
tests: []
---

# Design authoring contract

## Why this task exists

The plan built detectors without the guidance that would let an artifact pass them. Measured on [[DES-0001]], the founding artifact:

- **zero** `data-design-region` declarations — so [[TASK-0217]]'s annotation has nothing to anchor to and its no-regions validator check fires on the only design in the repo
- tokens named `--m-done`, `--t-feature`, `--m-accent` against an implementation that says `--status-done`, `--severity-critical`, `--accent-link` — so [[TASK-0219]]'s "extraction reads CSS custom properties" compares vocabularies that do not correspond
- `--m-accent:#3b6ea8` where the implementation has `hsl(212 48% 42%)` ≈ `#386ba0`, while the dossier labels that block "cockpit tokens, verbatim" — already false when written

Nothing tells the agent producing the *next* design what conforming looks like. This is the producer half of [[TASK-0214]].

## Definition of Done

- [x] A design authoring convention exists as a skill or template guidance: region declarations, token naming, artifact kind, self-containment, what a revision commit message must carry — evidence: `tools/skills/design-authoring/SKILL.md`, authored **upstream** (tools/skills is template-owned; a cockpit-local skill would be wiped by the next sync) and synced to all 11 repos
- [x] Regions: every part a reviewer might comment on carries `data-design-region`, IDs unique **within the artifact** (a five-plate dossier has five focus bands) — evidence: DES-0001 retrofitted, 29 regions, zero duplicates
- [x] Tokens: a design that intends to specify implementation values uses the implementation's token names verbatim, or declares a mapping once in its `## Tokens` section — evidence: the contract's Tokens section; DES-0002 already uses implementation names
- [x] Artifact kind is declared (`dossier` | `page`) — see [[TASK-0214]] — evidence: superseded by `viewport:` + `role:` in TASK-0214; the enum was dropped because a kind like `mobile` restates the project's platform on every note
- [x] The convention is verified by *producing a conforming artifact against it*, not by asserting it — evidence: verified by retrofitting the real 139KB dossier against it, not by asserting it
- [x] [[DES-0001]] is either retrofitted with regions or explicitly recorded as pre-convention, with the phase's annotation subject named accordingly — evidence: **retrofitted**, not grandfathered — 29 regions derived from existing `id="plate-x"` anchors

## Steps

- [x] Write the convention
- [x] Produce one small conforming artifact from it as the test
- [x] Decide DES-0001's fate: retrofit or grandfather
- [x] Point the [[TASK-0217]]/[[TASK-0219]] checks at the convention

## Result

The contract lives **upstream** (`project-os-dev` → `project-os` → 11 repos). `tools/skills/` is template-owned, so a cockpit-local skill would have been silently wiped by the next sync — caught by the pre-commit adapter check rather than months later.

**DES-0001 retrofitted, not grandfathered.** 29 regions, zero duplicates: seven top-level (one per plate — the granularity a reviewer actually comments at) and 22 scoped annotation anchors.

The scoping rule earned itself immediately. The dossier's `data-pin` numbers **restart at 1 in every plate**, so a bare `pin-1` would have collided five ways — the exact duplicate-ID hazard Fable's review predicted, already present in the founding artifact before anyone looked. Region names derive from existing `id="plate-x"` anchors rather than being invented, so they were already stable names.

## Notes

The DES-0001 decision is a real fork, not bookkeeping. Retrofitting regions into a 139KB file is genuine work; grandfathering it means the phase's acceptance demo needs a different subject, and [[PHASE-009]] currently implies DES-0001 is the subject throughout while phase 2 is unusable against it. Decide before TASK-0217 starts, not during.
