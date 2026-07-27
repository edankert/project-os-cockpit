---
type: "[[task]]"
id: TASK-0221
aliases: ["TASK-0221"]
title: "Design authoring contract — what a conforming artifact looks like"
status: backlog
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

- [ ] A design authoring convention exists as a skill or template guidance: region declarations, token naming, artifact kind, self-containment, what a revision commit message must carry
- [ ] Regions: every part a reviewer might comment on carries `data-design-region`, IDs unique **within the artifact** (a five-plate dossier has five focus bands)
- [ ] Tokens: a design that intends to specify implementation values uses the implementation's token names verbatim, or declares a mapping once in its `## Tokens` section
- [ ] Artifact kind is declared (`dossier` | `page`) — see [[TASK-0214]]
- [ ] The convention is verified by *producing a conforming artifact against it*, not by asserting it
- [ ] [[DES-0001]] is either retrofitted with regions or explicitly recorded as pre-convention, with the phase's annotation subject named accordingly

## Steps

- [ ] Write the convention
- [ ] Produce one small conforming artifact from it as the test
- [ ] Decide DES-0001's fate: retrofit or grandfather
- [ ] Point the [[TASK-0217]]/[[TASK-0219]] checks at the convention

## Notes

The DES-0001 decision is a real fork, not bookkeeping. Retrofitting regions into a 139KB file is genuine work; grandfathering it means the phase's acceptance demo needs a different subject, and [[PHASE-009]] currently implies DES-0001 is the subject throughout while phase 2 is unusable against it. Decide before TASK-0217 starts, not during.
