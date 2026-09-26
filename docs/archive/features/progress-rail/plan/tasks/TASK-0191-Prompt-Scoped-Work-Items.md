---
type: "[[task]]"
id: TASK-0191
aliases: ["TASK-0191"]
title: "Sidecar: prompt-scoped, index-enriched work items (id/title/status/type/done/ts) in the state payload"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-22
updated: 2026-07-22
source: ["[[ISS-0018]]"]
parent: "FEAT-0038"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[TASK-0181]]"]
tests: ["[[TST-0012]]"]
---

# TASK-0191 — prompt-scoped enriched work items

Fixes the data half of [[ISS-0018]]. The tracker (`agent_hooks.py`) additionally records `work_ts` (rel → ISO of the last edit-touch per work note) and `prompt_started` (stamped on every `UserPromptSubmit`), both included in the slim session. The `/api/cockpit/state` handler enriches each session's `work_notes` into `work_items`: `{id, rel, title, status, type, done, ts, current_prompt}` resolved from the live index — real title, real current status, `done` computed with the same per-type done sets the overview uses (extracted to module level from `stats_payload`, TASK-0181), `current_prompt` true when the note was touched at/after `prompt_started` (or, for seeded sessions with no prompt yet, whenever a touch timestamp exists).

Verification: pytest — work_ts recorded on an edit-tool touch and refreshed on re-touch; prompt_started stamped per prompt; the state endpoint's `work_items` carry title/status/type from disk notes, `done` flips with a per-type terminal status (requirement `accepted` counts done; task `accepted` does not), and `current_prompt` excludes items only touched before the latest prompt.

## Verification

pytest: `test_work_items_enrichment` (per-type done — accepted requirement done, accepted task not; `current_prompt` gated on the prompt boundary) + `test_work_items_seeded_session_without_prompt` (no boundary → any timestamped touch counts) + `test_work_ts_and_prompt_boundary` (tracker records `prompt_started` on UserPromptSubmit and `work_ts` on an edit-tool touch). Full suite 228 passed. Live: `/api/cockpit/state` `work_items` carry real title/status/type/done; after an edit-tool touch of one note, exactly that note flipped to `current_prompt` (1 of 7) — the rest of the session's backlog stayed out.
