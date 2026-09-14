---
type: "[[task]]"
id: TASK-0623
aliases: ["TASK-0623"]
title: "A sitting with a procedure renders as that procedure: the setup once, the owed steps with the screen each happens on, and expectation lines with their check tags; a sitting without one keeps FEAT-0149's rows"
status: done
phase: "[[PHASE-044-The-Walk-Page-Reads-As-A-Script]]"
owner: user:edwin
created: 2026-09-14
updated: 2026-09-14
source: ["[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]", "project-os-dev ADR-0045 decisions 3 to 5"]
parent: "[[FEAT-0150-The-Walk-Page-Reads-As-A-Script]]"
effort: L
due: ""
depends: []
blocks: ["[[TASK-0626-The-Page-And-The-Sheet-Agree-On-Your-Trainer]]"]
related: ["[[TASK-0619-The-Walk-Page]]"]
tests: ["[[TST-0089-A-Sitting-Walked-Step-By-Step-Writes-The-Same-Verdicts]]"]
tags: [task, acceptance, publication, renderer]
---

# Each sitting as its procedure

## Why

The v2.2.0 data-only sitting has five checks whose setups say the same thing. Printed as rows, the walker reads it five times. Printed as a procedure, once.

## Definition of Done

- [x] The payload carries each sitting's procedure as structured data from the bundled module (project-os-dev TASK-0121): setup text, steps with number and surface, lines with tags, and per-tag owed or passed.
- [x] The page renders the sitting's state and bench (unchanged), then the setup once, then each printed step with its screen name linked to the surface note, then its expectation lines, each showing the check's Expect text it quotes and its ASCII tags (`TST-0648.4`).
- [x] A tag for a check already passed on this platform is visibly marked passed and cannot be ticked again.
- [x] A sitting whose procedure fails the validator shows the validator's message and renders FEAT-0149's per-check rows below it.
- [x] A sitting with no procedure renders exactly as today. Existing walk tests pass unchanged.
- [x] The page does not reorder when anything is ticked, and it restores the walker's place on return (as FEAT-0149).
- [x] Until upstream's payload shape is final, rendering goes through one adapter function over a fixture, so the later change touches one place.
