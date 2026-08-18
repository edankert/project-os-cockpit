---
type: "[[task]]"
id: TASK
aliases: ["TASK"]
title: "A feature reaching a terminal status with nothing covering it is a validator error"
status: backlog
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
parent: "[[FEAT-0132-Acceptance-Tests-Are-Scaffolded-By-Rule]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# A feature reaching a terminal status with nothing covering it is a validator error

One error, on the feature, at close-out — **not** a per-check obligation and **not** a badge that counts checks (ADR-0027, ADR-0030).

Needs the once-only exception field first, or the rule has no honest escape and becomes the thing people disable. Dated promotion per ADR-0011: warn, then error.
