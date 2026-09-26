---
type: "[[task]]"
id: TASK-0165
aliases: ["TASK-0165"]
title: "Phase-less Now board — the overview centre renders the Active data full-width with animated transitions"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
parent: "FEAT-0036"
effort: ""
due: ""
depends: ["[[TASK-0164]]"]
blocks: []
related: ["[[FEAT-0023-Overview-Scopes]]"]
tests: []
---

# TASK-0165 — phase-less Now board

When `docs/phases/` is empty, the overview centre replaces the empty phase grid with a full-width board rendering TASK-0164's data: Doing / Next / Done-today columns, cards with type icon + status square + agent chip, animated column transitions on status-change events (reduced-motion: instant moves). Phase-bearing projects keep the existing overview untouched. Verification: phase-less fixture → board renders and animates a doing→done flip; phased project → unchanged overview.
