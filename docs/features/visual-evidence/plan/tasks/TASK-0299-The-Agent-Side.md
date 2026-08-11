---
type: "[[task]]"
id: TASK-0299
aliases: ["TASK-0299"]
title: "Agents cite pictures too"
status: done
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0066-Visual-Evidence]]"]
parent: "[[FEAT-0066-Visual-Evidence]]"
effort: S
depends: ["[[TASK-0297]]"]
blocks: []
related: []
tests: []
---

# Agents cite pictures too

## Definition of Done

- The capture endpoint is agent-callable (loopback, like dispatch); a CHG note carries the first before/after pair as proof of the loop.
- The attachments path convention is documented where agents read (CLAUDE.md project notes).

## Done — 2026-08-11

Agents cite pictures through the same endpoint and the same path: `POST /api/notes/attach` takes `png_base64` directly, returns the Markdown, and the picture renders wherever that Markdown is pasted — a criterion's evidence, a run log, an issue body.

**No agent-specific path exists, deliberately.** One write path with one guard is the rule the whole write surface follows ([[REQ-0027]], [[RISK-0005]]): the endpoint is loopback-only and enumerated by `test_every_note_mutating_endpoint_requires_loopback`, so an agent citing a picture is subject to exactly the checks a human is. A separate agent route would be a second door to audit.

The `data:` URI prefix is accepted because that is what a capture bridge hands back, and making each caller strip it is the kind of detail that gets got wrong once per call site.
