---
type: "[[issue]]"
id: ISS-0018
aliases: ["ISS-0018"]
title: "Progress blocks show the whole session's touched notes (reads as all-project), on a second line, without titles/status — should be prompt-scoped, inline before ctx, enriched"
status: fixed
severity: medium
owner: user:edwin
created: 2026-07-22
updated: 2026-07-22
source: ["user-feedback"]
related: ["[[FEAT-0038]]", "[[REQ-0021]]", "[[TASK-0191]]", "[[TASK-0192]]"]
---

# ISS-0018 — progress blocks: wrong scope, wrong line, no enrichment

## Symptom (user feedback 2026-07-22 on the first FEAT-0038 delivery)

1. The rail shows every docs note the session ever edited — on a scaffolding-heavy session (Your Health: 26 notes over 2 prompts) it reads as "all the open requirements/features of the project", not "what's being worked on for this prompt".
2. The blocks live on a second line under the strip; the user wants them inline in the main strip line, before the ctx meter ("in-flight boxes").
3. The expand chevron (`⌄` text glyph in a bordered button) sits too low in its box; should be a real triangle/arrow icon.
4. The progress rows show no title for most items (titles only arrived via live status-change events) and no actual status or actively-worked indicator.

## Root cause

The first implementation scoped the blocks to the session-cumulative `work_notes` list and enriched rows only from transitions the renderer happened to witness. Nothing in the pipeline carried prompt attribution, titles, or current status.

## Fix

[[TASK-0191]] (sidecar: timestamp work-note touches, mark prompt start, serve index-enriched prompt-scoped `work_items`) + [[TASK-0192]] (renderer: inline in-flight boxes before ctx, enriched rows with title/status/active, SVG triangle icon, second rail removed).
