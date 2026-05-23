---
type: "[[requirement]]"
id: REQ-0001
aliases: ["REQ-0001"]
title: "Renders any .md under target docs/ as HTML on request — no build step"
status: verified
phase: "[[PHASE-001-MVP]]"
implements: ["[[FEAT-0001]]"]
owner: user:edwin
created: 2026-05-07
updated: 2026-05-23
implemented_by: ["[[FEAT-0001]]"]
verified_by: []
---

# REQ-0001 — On-the-fly rendering

The render server SHALL serve any `.md` file under the configured docs root as HTML at request time, without a precompilation / build step. Edits to a source file are visible at the next page load (or sooner via [[REQ-0004]]).

## Rationale
A build-step kills the dogfood loop. The whole point is to author notes and see them rendered immediately.

## Verification
- 2026-05-23: marked `verified` — FEAT-0001 Render-Server is done; rendering pipeline shipped (see TASK-0002).
