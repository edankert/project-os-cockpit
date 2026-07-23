---
type: "[[change]]"
id: CHG-20260723-Focus-Driven-Inflight
title: "Console in-flight blocks driven by the declared SNAPSHOT focus, not just note-file edits"
date: 2026-07-23
author: user:edwin
status: merged
related: ["[[ISS-0019]]", "[[TASK-0193]]", "[[FEAT-0038]]", "[[REQ-0021]]"]
reviewed_by: "opus-independent-review"
review_date: 2026-07-23
review_verdict: CLOSE
---

# CHG-20260723 — focus-driven in-flight blocks

## What changed

`work_items_for_session` (`cockpit.py`) now unions the workspace's declared `SNAPSHOT.yaml focus` items (`task`/`issue`/`feature`/`phase`/`requirement`, read at `index.docs_root.parent`) with the notes-touched-this-prompt set. Focus items are marked `current_prompt` whenever focus names them (independent of file edits), enriched with title/status/type/`done` from the index, and lead the ordered list; a focus item also touched this prompt appears once and adopts its touch timestamp. The `/api/cockpit/state` enrichment now runs even when no notes were touched, so the focus set still shows.

## Why

On the your-health live run the console strip showed nothing while the agent was clearly working on TASK-0116 / ISS-0022 / PHASE-0007 (ISS-0019). FEAT-0038 attributed "in flight" purely to note **files edited this prompt**, but an agent typically works a task by editing its **code/design**, not by re-touching the note — so `current_prompt` was 0. The authoritative signal, the doc-first `focus` block, was never consulted. Driving the set from focus surfaces the real active work.

## Impact

- **Behaviour**: the strip shows the declared focus items (filled/outline by their real status) as soon as focus is set — live or idle — plus any notes edited this prompt. Renderer unchanged (it already renders `current_prompt` items). Verified live on your-health.
- **Scope**: sidecar-only; additive. Reads the `focus:` block via a small line scanner (no full-YAML load of a large SNAPSHOT); `note` free-text is ignored; wikilink values resolve to the canonical `PREFIX-NNNN` id.
- **Tests**: `test_work_items_include_snapshot_focus`, `test_work_items_focus_union_dedupes_touched`. Full suite 230 passed / 1 skipped.

## Files

- `src/project_os_cockpit/cockpit.py` — `_focus_ids`, focus∪touched in `work_items_for_session`.
- `src/project_os_cockpit/server.py` — enrich `session`/`last_session` unconditionally.
- `tests/test_stats_scope.py` — focus coverage.
