---
type: "[[task]]"
id: TASK-0195
title: "Phase-pinned subagents — planner + independent-reviewer on Fable under .claude/agents/"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: unassigned
created: 2026-07-24
updated: 2026-07-24
source: []
parent: "[[FEAT-0039-Model-Routing-Subagents]]"
effort: "S"
due: ""
depends: []
blocks: []
related: []
tests: []
---

# Phase-pinned subagents (planner / independent-reviewer)

## Definition of Done

- [x] `.claude/agents/planner.md` exists with `model: fable`, a proactive-delegation description covering preflight (issue intake, feature scaffold, task breakdown, impact analysis), and a prompt that defers to the `tools/skills/` playbooks.
- [x] `.claude/agents/independent-reviewer.md` exists with `model: fable`, covering LIFECYCLE close-out step 8 and ad-hoc review requests, deferring to `tools/skills/independent-review/SKILL.md` and `tools/instructions/QUALITY.md`.
- [x] Neither agent can silently drift from the template rules: prompts reference the canonical instruction files instead of duplicating them.

## Steps

- [x] Write `planner.md` frontmatter + prompt (read-and-write tools; no application-code edits).
- [x] Write `independent-reviewer.md` frontmatter + prompt (fresh-eyes stance, verification gates, validator run).

## Notes

Placed under `.claude/agents/` (repo-local) rather than `tools/adapters/` because `tools/adapters/` is template-owned and `sync-project-os.sh` would overwrite it. Model pin uses the `fable` alias so it tracks the latest Fable release.
