---
type: "[[task]]"
id: TASK-0131
aliases: ["TASK-0131"]
title: "Verb registry — per-type actions, YAML override, /api/cockpit/actions"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
parent: "[[FEAT-0024-Agent-Verbs]]"
effort: "S"
depends: []
blocks: ["[[TASK-0132]]"]
related: []
tests: ["[[TST-0013]]"]
---

# Verb registry

## Definition of Done
- [x] Built-in per-type verbs (task/issue/feature/requirement/phase/risk) with prompt templates carrying `{id}`/`{rel}` slots and referencing the relevant `tools/skills/*/SKILL.md`.
- [x] `tools/adapters/cockpit/actions.yaml` (when present in the workspace) overrides/extends per type.
- [x] `GET /api/cockpit/actions` returns `{schema_version, actions}`.
- [x] Tests green (TST-0013).

## Steps
- [x] `agent_actions.py` module + defaults.
- [x] YAML load + per-type merge.
- [x] Endpoint + tests.
