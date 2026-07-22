---
type: "[[task]]"
id: TASK-0192
aliases: ["TASK-0192"]
title: "Renderer: in-flight boxes inline before ctx, enriched progress rows (title/status/active), SVG triangle expand icon"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-22
updated: 2026-07-22
source: ["[[ISS-0018]]"]
parent: "FEAT-0038"
effort: ""
due: ""
depends: ["[[TASK-0191]]"]
blocks: []
related: ["[[TASK-0188]]", "[[TASK-0189]]", "[[TASK-0190]]"]
tests: []
verification_waiver: "Renderer-only UI; no automated renderer unit-test surface. Validated live via CDP (inline placement, prompt-scoped block set, enriched rows, icon) plus independent review on the code."
---

# TASK-0192 — inline in-flight boxes + enriched rows + real icon

Fixes the presentation half of [[ISS-0018]], replacing the TASK-0188/0189/0190 surfaces per user feedback: (1) the second rail row is removed; the in-flight boxes render inline in the main strip line between the spacer and the ctx meter — only `work_items` with `current_prompt` (the set being worked for this prompt), cap ~12 with `+N`, filled from the server-computed `done`, pulsing the most recently touched open item while busy, click→navigate, hover "ID Title (status)". (2) The progress panel rows render from enriched `work_items`: block + id + **title** + **actual current status** + actively-worked pulse + relative time, current-prompt items first (then the rest of the session by recency); observed `from → to` transitions still shown when available. (3) The expand button becomes a real SVG triangle (borderless, centred, rotating on expand).

Verification: live CDP — boxes appear inline before ctx scoped to the current prompt's items; rows show title/status; the active item pulses; the icon is an SVG triangle that rotates.

## Verification

Live CDP against a real session: the in-flight boxes render **inside** the main strip line **before** the ctx meter (second rail element gone), scoped to `current_prompt` items only — after editing four notes this prompt, exactly those four showed (three filled done, one open), with hover "ID Title (status)". The expand control is an SVG triangle that rotates on open. The progress panel rows show block + full title + status (`approved → implemented`, current status otherwise) + `· working` on the active item pinned to top. tsc clean.
