---
type: "[[issue]]"
id: ISS-0019
aliases: ["ISS-0019"]
title: "Console in-flight blocks miss the work when the agent edits code, not notes — the declared SNAPSHOT focus is ignored"
status: fixed
severity: medium
owner: user:edwin
created: 2026-07-23
updated: 2026-07-23
source: ["user-report"]
related: ["[[FEAT-0038]]", "[[REQ-0021]]", "[[TASK-0193]]"]
---

# ISS-0019 — in-flight detection ignores the declared focus

## Symptom (your-health, live run 2026-07-23)

The console strip showed no in-flight items while the agent was actively working on TASK-0116 / ISS-0022 / PHASE-0007. The sidecar was serving 28 enriched `work_items` but `current_prompt = 0`, so the inline boxes were hidden.

## Root cause

FEAT-0038 attributes "in flight" purely to note **files edited at/after the prompt boundary** (TASK-0191). But an agent typically works a task by editing its **code / design**, not by re-editing the note: this run the agent touched `design/README.md` and Kotlin source, and the only two notes with edit timestamps (ISS-0022 @15:56, PHASE-0007 @17:06) belonged to earlier prompts. So nothing counted as current-prompt. Meanwhile the authoritative signal — `SNAPSHOT.yaml focus` (`task: TASK-0116`, `issue: ISS-0022`, `phase: PHASE-0007`), which the doc-first workflow maintains as "what's being worked on now" — was never consulted.

## Fix

See [[TASK-0193]]: drive the in-flight set from `SNAPSHOT.yaml focus` (task/issue/feature/phase/requirement) **unioned with** notes-touched-this-prompt. Focus items are marked current-prompt whenever focus is set (live or idle), enriched with title/status/done from the index like any other work item.
