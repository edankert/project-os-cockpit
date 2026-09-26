---
type: "[[task]]"
id: TASK-0193
aliases: ["TASK-0193"]
title: "Sidecar: drive the in-flight work set from SNAPSHOT focus ∪ notes-touched-this-prompt"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-23
updated: 2026-07-23
source: ["[[ISS-0019]]"]
parent: "FEAT-0038"
effort: ""
due: ""
depends: ["[[TASK-0191]]"]
blocks: []
related: ["[[TASK-0192]]"]
tests: ["[[TST-0012]]"]
---

# TASK-0193 — focus-driven in-flight set

Fixes [[ISS-0019]]. `work_items_for_session` (cockpit.py) additionally reads the `focus` block of `SNAPSHOT.yaml` (resolved at `index.docs_root.parent`) and includes its declared items — `task`, `issue`, `feature`, `phase`, `requirement` — in the work-item set, deduped with the notes-touched list. Focus items are marked `current_prompt: true` whenever focus names them (independent of whether their file was edited), enriched with title/status/type/`done` from the index; if a focus item was also touched this prompt it carries that `ts`. Focus items lead the ordered list (declared active work first), then touched items by recency. The renderer already renders `current_prompt` items, so no renderer change is required.

Verification: pytest — a session whose `work_notes` touched nothing this prompt still yields `current_prompt` items for the SNAPSHOT focus ids, with real title/status/done; a focus id absent from the index degrades to a bare id (no crash); focus ∪ touched dedupes by id. Live: your-health strip shows TASK-0116/ISS-0022/PHASE-0007.

## Verification

pytest: `test_work_items_include_snapshot_focus` (a session that touched no notes this prompt still yields the SNAPSHOT focus ids as current-prompt, enriched with title/status/done; the free-text `note` id is ignored; a `[[wikilink]]` resolves to the canonical id) + `test_work_items_focus_union_dedupes_touched` (a focus item also touched appears once, adopting its touch ts). Full suite 230 passed / 1 skipped. Live (your-health, mid-run): the strip that previously showed nothing now shows TASK-0116 / ISS-0022 / PHASE-0007 (the SNAPSHOT focus), with real titles/status, PHASE-0007 pinned as the active "· working" item — while the agent edits Kotlin source, not the notes.
