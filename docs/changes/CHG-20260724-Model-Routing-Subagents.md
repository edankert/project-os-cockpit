---
type: "[[change]]"
id: CHG-20260724-Model-Routing-Subagents
title: "Model routing — Fable-pinned planner/reviewer subagents, Opus main loop, snapshot-driven routing hint hook"
status: merged
owner: unassigned
created: 2026-07-24
updated: 2026-07-24
source: []
commit: ""
pr: ""
impacts: [".claude/settings.json", ".claude/agents/", ".claude/hooks/", "CLAUDE.md"]
issues: []
features: ["[[FEAT-0039-Model-Routing-Subagents]]"]
reviewed_by: "model:claude-opus-4-8"
review_date: 2026-07-24
review_verdict: approved
review_note: "Same-family review (Opus reviewing Fable) — NOT independent per QUALITY.md, which requires a different model family or a human; a cross-vendor or human pass is still owed. The Impact section's original independence claim was corrected on 2026-07-24 (ISS-0021 §1)."
related: []
---

# Model routing — phase-pinned subagents + routing hint hook

## Summary

Claude Code sessions in this repo now route lifecycle phases to models automatically. The project default model is pinned to Opus (`"model": "opus"` in `.claude/settings.json`) for implementation work. Two new repo-local subagents pin Fable to the phases where the strongest model pays off: `.claude/agents/planner.md` (preflight — issue intake, feature scaffold, task breakdown, impact analysis) and `.claude/agents/independent-reviewer.md` (close-out step 8 and ad-hoc reviews). A new `UserPromptSubmit` hook, `.claude/hooks/model-routing-hint.sh`, reads the SNAPSHOT focus item's status and injects an advisory routing hint (planning statuses → planner, `doing` → main loop, `in-review` → reviewer). The routing contract is documented in a new "Model routing" section of `CLAUDE.md`. All new files are deliberately outside `tools/` because that tree is template-owned and overwritten by `sync-project-os.sh`.

## Impact

- Every prompt in a Claude Code session now carries one extra context line from the routing hook; sessions default to Opus unless overridden with `/model`.
- Preflight and review work is expected to be delegated to Fable-pinned subagents. **Correction (2026-07-24, per [[ISS-0021-Model-Routing-Review-Findings]] §1):** this note originally claimed the Opus-implements / Fable-reviews pairing "satisfies the independent-review skill's different-model-family rule by construction". That is wrong — `claude-opus-4-8` and `claude-fable-5` are both Claude family. Moving the reviewer off the likely authoring model is harm reduction (it avoids literal self-review); `QUALITY.md` still requires a different model *family* or a human, and no subagent pin can deliver that. A cross-vendor or human pass remains owed.
- No server/runtime code touched; behavior change is limited to the Claude Code harness configuration.

## Documentation Coverage (All Types Considered)

- features: new (FEAT-0039)
- requirements: not-applicable
- tasks: new (TASK-0195, TASK-0196)
- issues: not-applicable
- tests: not-applicable (hook exercised manually across all four branches; no runtime code)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable (advisory-only hook, always exit 0; no new external dependency)
- changes: new (this note)
- snapshot: updated

## Follow-ups

- [ ] If the pattern proves out, upstream it to `~/Dev/repos/project-os/` as a Claude Code adapter so downstream repos inherit it via `sync-project-os.sh`.
