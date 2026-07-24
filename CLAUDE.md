# Project: project-os-cockpit

Read SNAPSHOT.yaml at session start to understand current project state and focus.
Read CONTEXT.md for the full project-os contract, edit policy, and invariants.

## What this repo is

`project-os-cockpit` is a small Python server that renders project-os Markdown notes as a three-pane cockpit UI — on the fly, no build step. It's the upstream tool; downstream project-os repos consume it via a thin shim under their own `tools/project-os-cockpit/`.

The first downstream pilot is `~/Dev/repos/your-applications.com/` — that repo's `tools/project-os-cockpit/` is the integration point used to validate this tool against real project-os content.

## project-os documentation system (core rules -- always active)

@tools/instructions/LIFECYCLE.md

## Reference instructions (read when relevant)

These files contain detailed rules. Read them when performing the related operation:
- Status values and transitions: tools/instructions/STATUSES.md
- Quality gates and close-out checks: tools/instructions/QUALITY.md
- Snapshot structure and update rules: tools/instructions/SNAPSHOT.md
- Allowed taxonomy values: tools/instructions/TAXONOMY.md
- Required link graphs: tools/instructions/TRACEABILITY.md
- ADR conventions: tools/instructions/DECISIONS.md
- Ownership rules: tools/instructions/OWNERSHIP.md
- Obsidian conventions: tools/instructions/OBSIDIAN.md
- Handoff/recovery: tools/instructions/HANDOFF.md
- Importing from existing projects: tools/instructions/IMPORTING.md
- Syncing template updates: tools/instructions/SYNCING.md
- Hook contracts: tools/instructions/HOOKS.md
- Cockpit driving (LLM in any terminal): tools/instructions/COCKPIT.md

## Skill playbooks (read before performing these operations)

- Issue intake: tools/skills/issue-intake/SKILL.md
- Feature scaffold: tools/skills/feature-scaffold/SKILL.md
- Task breakdown: tools/skills/task-breakdown/SKILL.md
- Close-out: tools/skills/close-out/SKILL.md
- Change note: tools/skills/change-note/SKILL.md
- Status transition: tools/skills/status-transition/SKILL.md
- Snapshot sync: tools/skills/snapshot-sync/SKILL.md
- ADR authoring: tools/skills/adr-authoring/SKILL.md
- Risk scan: tools/skills/risk-scan/SKILL.md
- Independent review: tools/skills/independent-review/SKILL.md
- Docs audit: tools/skills/docs-audit/SKILL.md
- Ad-hoc intake: tools/skills/ad-hoc-intake/SKILL.md
- Backlog grooming: tools/skills/backlog-grooming/SKILL.md
- Risk mitigation: tools/skills/risk-mitigation-planning/SKILL.md
- Impact analysis: tools/skills/impact-analysis/SKILL.md
- Adapter sync: tools/skills/adapter-sync/SKILL.md
- Cockpit driving: tools/skills/cockpit-driving/SKILL.md

## Model routing (lifecycle phase → model)

Models are pinned to lifecycle phases via subagents (FEAT-0039, upstreamed as project-os HC-008). The main session runs on Opus (`model` in `.claude/settings.json`) and does the implementation. Preflight/planning (LIFECYCLE steps 1–5) is delegated to the `planner` subagent (`.claude/agents/planner.md`, pinned to `claude-fable-5`). Close-out review (LIFECYCLE step 8) and ad-hoc review requests are delegated to the `independent-reviewer` subagent (`.claude/agents/independent-reviewer.md`, same pin). The `UserPromptSubmit` hook `tools/adapters/claude-code/hooks/model-routing-hint.sh` injects a routing hint derived from the SNAPSHOT focus item's status; follow it unless the prompt clearly says otherwise.

Keeping the session model off the reviewer's pin is harm reduction, not independence: QUALITY.md requires a different model *family* or a human, and Claude Code subagents can only pin Claude models. A same-family review does not close that gate — record a cross-vendor or human pass manually when it matters.

Canonical ownership of these files is upstream in `~/Dev/repos/project-os/`: the hook is a hand-written adapter hook under `tools/adapters/claude-code/hooks/`, and both agent files are emitted by upstream's `tools/scripts/generate-adapters.py`. Edit them upstream, not here. The copies here are byte-identical to upstream's, but note that `sync-project-os.sh` copies `tools/` and never touches `.claude/`, and this repo carries no generator — so the agent files can only be refreshed by re-copying them, and nothing here detects drift.

## Project-specific notes

Stack: Python 3.11+. Dependencies live in `pyproject.toml`. Source under `src/project_os_cockpit/`. Run with `python -m project_os_cockpit <path-to-docs-dir>` or the installed console script `project-os-cockpit <path-to-docs-dir>`. The render server binds to `0.0.0.0` (so a tablet on the same Wi-Fi can read), the optional terminal endpoint binds to `127.0.0.1` only (Mac-local).

Upstream relationship: this repo is downstream of `~/Dev/repos/project-os/` (the canonical project-os template). Run `tools/scripts/sync-project-os.sh ../project-os` to pull template-owned files (`tools/instructions/`, `tools/skills/`, `docs/__templates__/`, `docs/__bases__/`) when the upstream changes.
