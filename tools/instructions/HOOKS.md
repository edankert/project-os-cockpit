---
type: instruction
id: INSTR-HOOKS
status: active
owner: group:maintainers
created: 2026-03-08
updated: 2026-05-05
tags: [instructions, hooks, codex]
---

# Codex hook-equivalent contracts

These contracts define the checks that a Codex workflow should perform at key points. The current template implements them with `AGENTS.md` instructions and `tools/agents/*.sh` scripts rather than a tool-specific hook runtime.

## CHC-001: Startup preflight

- Trigger: session start or before selecting work.
- Entrypoint: `bash tools/agents/bootstrap.sh`.
- Check logic:
  - Required context files exist.
  - `SNAPSHOT.yaml` can be read.
  - Current branch, head, focus, and working tree are visible.
- On failure: stop and fix missing required files before implementation.

## CHC-002: Docs-first gate

- Trigger: before functional code changes in downstream projects that enforce docs-first tracking.
- Entrypoints:
  - `bash tools/agents/start-change.sh "<short title>"`
  - `bash tools/agents/check-docs-first.sh`
- Check logic:
  - Code changes have a `docs/changes/CHG-*.md` note when required.
  - `SNAPSHOT.yaml` is updated when code changes are present.
  - Change notes have no pending documentation coverage entries.
- On failure: block close-out until documentation state is explicit.

## CHC-003: Phase alignment

- Trigger: before starting or transitioning a task to `doing`.
- Check logic:
  - Read `focus.phase` from `SNAPSHOT.yaml`.
  - Read the task or parent feature `phase`.
  - If both phases are set and the task belongs to a future phase, flag the mismatch.
- On failure: warn and require explicit user confirmation before proceeding.

## CHC-004: Verification gate

- Trigger: before marking a task `done`, issue `closed`, requirement `verified`, or feature `done`.
- Check logic:
  - Find linked `TST-*` IDs from the snapshot and note frontmatter.
  - Confirm every required test is `status: passing`.
- On failure: block the terminal status transition unless the user explicitly waives verification.

## CHC-005: Close-out check

- Trigger: before final response after implementation work.
- Check logic:
  - Snapshot and note statuses agree.
  - `focus` is cleared or moved to the next active item.
  - Metrics and relationships are updated.
  - Required `CHG-*` and `RISK-*` notes exist when behavior, paths, contracts, or hazards changed.
- On failure: complete the missing close-out work before stopping.
