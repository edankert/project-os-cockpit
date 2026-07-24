---
type: "[[change]]"
id: CHG-20260724-Model-Routing-Upstreamed
title: "Model routing moves upstream — HC-008 adapter hook + generated planner/reviewer subagents replace this repo's local prototype"
status: merged
owner: unassigned
created: 2026-07-24
updated: 2026-07-24
source: []
commit: ""
pr: ""
impacts: ["tools/adapters/claude-code/hooks/model-routing-hint.sh", ".claude/agents/", ".claude/settings.json", "CLAUDE.md"]
issues: ["[[ISS-0021-Model-Routing-Review-Findings]]"]
features: ["[[FEAT-0039-Model-Routing-Subagents]]"]
reviewed_by: "model:claude-opus-4-8"
review_date: 2026-07-24
review_verdict: approved
review_note: "First pass returned changes-requested; findings filed as ISS-0021 and all nine addressed before close. Same-family review — NOT independent per QUALITY.md; a cross-vendor or human pass is still owed."
related: ["[[CHG-20260724-Model-Routing-Subagents]]"]
---

# Model routing upstreamed

## Summary

The model routing prototyped here in [[CHG-20260724-Model-Routing-Subagents]] now lives in the canonical template at `~/Dev/repos/project-os/`, so every downstream project-os repo inherits it rather than each one hand-rolling its own copy. Upstream gained: the routing hook as template-owned adapter hook **HC-008** (`tools/adapters/claude-code/hooks/model-routing-hint.sh` plus a `UserPromptSubmit` entry in `hooks.json`), a `planner` subagent emitted by `tools/scripts/generate-adapters.py` alongside the existing `independent-reviewer`, both model pins hoisted into named `PLANNER_MODEL`/`REVIEWER_MODEL` constants, the HC-008 contract in `tools/instructions/HOOKS.md`, and a "Model routing" section in the Claude Code `ADAPTER.md`. Upstream's own change note is `CHG-20260724-Model-Routing`.

Both pins are now `claude-fable-5` (previously the reviewer was `claude-opus-4-8`), chosen so the reviewer is not the model most likely to have authored the work. The independent review of this change corrected how that is described: moving the pin is harm reduction, **not** independence. `QUALITY.md` requires a different model *family* or a human, Claude Code subagents can only pin Claude models, and an earlier draft of this work had quietly rewritten the reviewer's briefing from "same family" to "same model" — weakening the rule while claiming to strengthen it. The reviewer briefing and `ADAPTER.md` now state the limitation plainly.

## Impact

- This repo's hook moved from `.claude/hooks/model-routing-hint.sh` (deleted) to the template-owned `tools/adapters/claude-code/hooks/model-routing-hint.sh`; `.claude/settings.json` points at the new path.
- `.claude/agents/planner.md` and `.claude/agents/independent-reviewer.md` are now byte-identical to upstream's generated output (pins changed from the `fable` alias to the full `claude-fable-5` ID), so a future template sync plus generator run is a no-op for them.
- Hook behaviour gained from the upstream port: it stays silent on a template placeholder snapshot (`template.replace_me: true`) and resolves `focus.issue` as well as task and feature. Review then corrected its status handling — the full `STATUSES.md` vocabulary is covered (`open`, `blocked`, `reopened`, `wont-fix` previously fell through to "no focus resolved"), `deferred` is treated as the parked non-terminal state it is rather than as terminal, and the item's own `status:` is anchored at its indentation level so a nested one (e.g. under `tests:`) can no longer be misread.
- `tools/adapters/claude-code/hooks.json` here was missing the `UserPromptSubmit` entry — following ADAPTER.md's documented manual install (copy `hooks.json` into `.claude/settings.json`) would have silently removed the routing hook. It now matches upstream.
- `CLAUDE.md` now names upstream as the owner of these files — edit them there, not here.

## Documentation Coverage (All Types Considered)

- features: updated (FEAT-0039 scope now records the ownership move)
- requirements: not-applicable
- tasks: new (TASK-0197)
- issues: new (ISS-0021 — the review findings, all resolved)
- tests: not-applicable (hook re-exercised manually across every status branch, the template-placeholder case, and both repos)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable (advisory hook, always exits 0; no new dependency)
- changes: new (this note; upstream carries its own `CHG-20260724-Model-Routing`)
- snapshot: updated

## Follow-ups

- [ ] Confirm Claude Code honours a full model ID (`claude-fable-5`) in subagent frontmatter — run `/agents` in a fresh session and check both subagents report the pinned model, not the session model. If full IDs were ignored the routing would be inert with no signal (ISS-0021 follow-up D).
- [ ] Run a full `tools/scripts/sync-project-os.sh ../project-os` once the upstream working tree is committed and clean — deliberately skipped here to avoid pulling unrelated in-flight upstream churn (see TASK-0197 notes).
- [ ] Owed on both change notes: a genuinely independent (cross-vendor or human) review. Every pass so far has been Claude reviewing Claude.
