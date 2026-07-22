---
type: "[[change]]"
id: CHG-20260722-Console-Progress-Rail
title: "Console in-flight progress blocks — current-prompt work items inline in the strip + enriched progress panel"
date: 2026-07-22
author: user:edwin
status: merged
related: ["[[REQ-0021]]", "[[FEAT-0038]]", "[[ISS-0018]]", "[[TASK-0191]]", "[[TASK-0192]]", "[[FEAT-0036]]"]
reviewed_by: "opus-independent-review"
review_date: 2026-07-22
review_verdict: CLOSE
---

# CHG-20260722 — console in-flight progress blocks

## What changed

The console strip now shows the overview block notation for the docs items **being worked for the current prompt**, filling live as they complete. Delivers [[REQ-0021]] via [[FEAT-0038]]; supersedes the first cut (a session-cumulative second rail) after user feedback [[ISS-0018]].

- **Sidecar (TASK-0191)**: the agent tracker records `work_ts` (last edit-touch per work note) and `prompt_started` (stamped on each `UserPromptSubmit`). `/api/cockpit/state` enriches each session's `work_notes` into `work_items` — `{id, rel, title, status, type, done, ts, current_prompt}` resolved from the live index, with `done` computed from the per-type done sets now shared module-level with the overview (`is_done_status`, extracted from `stats_payload`). `current_prompt` is true for notes touched at/after the prompt boundary (or any timestamped touch on a seeded session with no boundary yet).
- **Renderer (TASK-0192)**: the second rail row is gone. The in-flight boxes render **inline in the main strip line, before the ctx meter**, showing only `current_prompt` items (cap 12 + `+N`), filled from the server `done` (with an instant overlay from a just-seen status-change), pulsing the newest-touched open item while live, click→navigate, hover "ID Title (status)". The progress panel rows are enriched — block + id + **title** + **status** (observed `from → to` when seen, else the note's current status) + a `· working` marker + relative time — current-prompt items first, active pinned to top. The expand control is a real **SVG triangle** (borderless) that rotates on open, replacing the low `⌄` glyph.

## Why

First delivery showed every docs note the session ever touched (a scaffolding-heavy session read as "the whole project"), on a second line, with a low chevron glyph and rows lacking titles/status. User feedback ([[ISS-0018]]): scope it to the current prompt, put the boxes inline before ctx, use a real triangle icon, and show title + status + actively-worked in the panel.

## Impact

- **Behaviour**: while a prompt runs, its in-flight items appear as filling blocks inline in the strip — never the project backlog; expanding shows the enriched list. Requirement `implemented` correctly reads open (not done) — consistent with the overview's per-type done semantics.
- **Scope**: sidecar adds two persisted session fields + a state-payload enrichment (no schema break — additive); renderer reworked. `is_done_status` is now the single module-level done definition for boxes, hero counts, and work items. `tsc` clean; 228 pytest passed / 1 skipped.
- **Verification**: pytest for the enrichment/boundary logic; live CDP for placement, prompt scoping, icon, and enriched rows. See task Verification sections.

## Files

- `src/project_os_cockpit/cockpit.py` — module-level `DONE_BY_TYPE`/`is_done_status`; `work_items_for_session`.
- `src/project_os_cockpit/agent_hooks.py` — `work_ts` + `prompt_started` recording, exposed in the slim session.
- `src/project_os_cockpit/server.py` — `/api/cockpit/state` enriches `session`/`last_session` with `work_items`.
- `desktop/src/renderer/{index.html,renderer.css,renderer.ts}` — inline in-flight boxes, enriched panel, SVG caret.
- `tests/test_stats_scope.py`, `tests/test_agent_hooks.py` — enrichment + tracker coverage.
