---
type: "[[workflow]]"
id: WF-0003
title: "Recovery and resume"
status: draft
owner: group:maintainers
created: 2026-01-29
updated: 2026-01-29
entrypoints:
  - tools/skills/snapshot-sync/SKILL.md
prereqs:
  - access to SNAPSHOT.yaml and docs
inputs:
  - SNAPSHOT.yaml
  - docs/**
outputs:
  - reconciled snapshot and notes
  - resumed focus or reassigned claims
related:
  - ../INDEX.md
  - ../../tools/instructions/HANDOFF.md
---

# Recovery and resume

## When to use
- Work stopped unexpectedly or multiple agents need to coordinate safely.

## Entrypoint(s)
- `tools/skills/snapshot-sync/SKILL.md`

## Prerequisites
- Access to `SNAPSHOT.yaml` and docs notes.

## Inputs
- Snapshot and relevant notes for in-flight work.

## Outputs
- Updated snapshot (focus, statuses) and aligned notes.

## Notes / Troubleshooting
- Check `git status` for uncommitted or partial work from interrupted sessions.
- Agent coordination is handled by your tool's native orchestration (Agent Teams, Codex parallel, etc.).
