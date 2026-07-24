---
type: "[[plan]]"
id: PLAN-FEAT-0039
aliases: ["PLAN-FEAT-0039"]
title: "Plan — model routing subagents + routing-hint hook"
status: done
owner: unassigned
created: 2026-07-24
updated: 2026-07-24
source: []
implements: ["[[FEAT-0039-Model-Routing-Subagents]]"]
related: []
---

# Plan — model routing

## Delivery sequence

1. [[TASK-0195-Phase-Pinned-Subagents]] — create `.claude/agents/planner.md` and `.claude/agents/independent-reviewer.md`, both `model: fable`, prompts pointing at the existing project-os skill playbooks so behaviour stays template-driven.
2. [[TASK-0196-Routing-Hint-Hook]] — create the routing hook (UserPromptSubmit, advisory, reads SNAPSHOT focus + item status), wire it into `.claude/settings.json`, pin the project default model to `opus`, document the routing in `CLAUDE.md`.
3. [[TASK-0197-Upstream-And-Adopt]] — move canonical ownership upstream to `~/Dev/repos/project-os/` (adapter hook HC-008 + generator-emitted subagents) and consume it here, so the whole fleet inherits the routing. The hook's final home is `tools/adapters/claude-code/hooks/model-routing-hint.sh`; the `.claude/hooks/` prototype from step 2 is deleted.

## Dependencies

- **Hard:** none — both tasks are repo-local config; no server code changes.
- **Soft:** keep everything out of `tools/` (template-owned, overwritten by `sync-project-os.sh`); if this pattern proves out, upstream it to `~/Dev/repos/project-os/` as an adapter so downstream repos inherit it.

## Open questions

- Whether `"model": "opus"` in checked-in settings is too opinionated for other sessions — easy to override per session with `/model`, revisit if it annoys.
