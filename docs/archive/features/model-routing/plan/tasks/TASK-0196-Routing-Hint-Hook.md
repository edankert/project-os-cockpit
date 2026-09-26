---
type: "[[task]]"
id: TASK-0196
title: "Snapshot-driven routing hint — UserPromptSubmit hook + settings wiring (main loop pinned to Opus)"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: unassigned
created: 2026-07-24
updated: 2026-07-24
source: []
parent: "[[FEAT-0039-Model-Routing-Subagents]]"
effort: "S"
due: ""
depends: ["[[TASK-0195-Phase-Pinned-Subagents]]"]
blocks: []
related: []
tests: []
---

# Snapshot-driven routing hint hook

## Definition of Done

- [x] `.claude/hooks/model-routing-hint.sh` reads `focus.task` / `focus.feature` from SNAPSHOT.yaml, resolves the item's status, and prints a one-line routing hint (planning statuses → `planner`, doing → main loop, in-review → `independent-reviewer`).
- [x] Hook is advisory: always exits 0, prints nothing harmful when SNAPSHOT.yaml is absent or focus is empty.
- [x] `.claude/settings.json` wires the hook under `UserPromptSubmit` and sets `"model": "opus"` as the project default.
- [x] Project `CLAUDE.md` documents the routing contract in a short "Model routing" section.

## Steps

- [x] Write the hook script (bash, grep/awk only — same zero-dependency style as `tools/adapters/claude-code/hooks/`).
- [x] Add the `UserPromptSubmit` block and `model` key to `.claude/settings.json`.
- [x] Add the CLAUDE.md section.

## Notes

Hooks cannot change the session model — the hint only steers delegation to the model-pinned subagents from [[TASK-0195-Phase-Pinned-Subagents]]. Status parsing relies on the SNAPSHOT indentation contract (4-space item IDs, 6-space `status:`), which `tools/instructions/SNAPSHOT.md` fixes.

Independent review (Opus, 2026-07-24, approved) drove two hardening fixes before close: full-slug wikilink focus values (e.g. `"[[FEAT-0039-Slug]]"`) now reduce to the bare ID so `status_of` matches, and terminal statuses (done/fixed/closed/…) get an explicit "no active work in focus" hint instead of falling through to the unresolved-focus message.
