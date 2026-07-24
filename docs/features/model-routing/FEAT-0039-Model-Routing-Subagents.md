---
type: "[[feature]]"
id: FEAT-0039
title: "Model routing — phase-pinned Claude Code subagents (planner/reviewer on Fable) + snapshot-driven routing-hint hook"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: unassigned
created: 2026-07-24
updated: 2026-07-24
source: []
goal: "Route lifecycle phases to the right Claude model automatically: planning and independent review on Fable, implementation on Opus in the main loop."
requirements: []
tasks: ["[[TASK-0195-Phase-Pinned-Subagents]]", "[[TASK-0196-Routing-Hint-Hook]]", "[[TASK-0197-Upstream-And-Adopt]]"]
release: ""
related: []
tests: []
---

# Model routing — phase-pinned subagents + routing-hint hook

## Goal

Claude Code has no built-in "Fable for planning, Opus for execution" model split (the only native combo is `opusplan`, which is Opus→Sonnet). This feature gets automatic per-phase model routing anyway, by mapping the project-os lifecycle onto model-pinned subagents: preflight/planning delegates to a `planner` subagent pinned to Fable, implementation runs in the main loop pinned to Opus, and close-out review delegates to an `independent-reviewer` subagent pinned to Fable. A `UserPromptSubmit` hook reads `SNAPSHOT.yaml` focus and injects a routing hint so the delegation is driven by the docs system's own state rather than by model judgment alone.

## Scope

**In:** the `planner` and `independent-reviewer` subagents (both pinned to `claude-fable-5`); the `UserPromptSubmit` routing hook wired in `.claude/settings.json`; `"model": "opus"` as the project default; a "Model routing" section in the project `CLAUDE.md`. Canonical ownership of the hook and both subagents was moved upstream to `~/Dev/repos/project-os/` under [[TASK-0197-Upstream-And-Adopt]] — the hook is now the template-owned adapter hook HC-008 and the subagents are emitted by upstream's `generate-adapters.py`, so the whole fleet inherits them.

**Out:** an Agent SDK orchestrator that dispatches work unattended (possible later evolution of the cockpit dispatch runtime, see [[FEAT-0025-Dispatch-Runtime]]); hook-based hard gating (the hint is advisory — hooks cannot switch the session model); a full template sync of this repo from upstream (deliberately deferred, see [[TASK-0197-Upstream-And-Adopt]]).

## Acceptance

- A prompt implying new work gets a hint to delegate preflight to `planner`, and Claude Code resolves that agent on Fable.
- With focus on a `doing` item, the hint says to implement directly in the main loop (Opus).
- With focus on an `in-review` item, the hint routes to `independent-reviewer` (Fable).
- The hook never blocks a prompt (always exit 0) and degrades silently when SNAPSHOT.yaml is missing.
- `bash tools/scripts/validate-docs.sh` passes.

## Links

- Tasks: [[TASK-0195-Phase-Pinned-Subagents]], [[TASK-0196-Routing-Hint-Hook]], [[TASK-0197-Upstream-And-Adopt]]
- Issues: [[ISS-0021-Model-Routing-Review-Findings]]
- Repo paths: `.claude/agents/`, `tools/adapters/claude-code/hooks/model-routing-hint.sh`, `tools/adapters/claude-code/hooks.json`, `.claude/settings.json`, `CLAUDE.md`
- Lifecycle contract this maps onto: `tools/instructions/LIFECYCLE.md` (preflight / execution / close-out)
