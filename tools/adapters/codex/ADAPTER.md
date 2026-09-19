---
type: adapter
tool: codex
status: active
owner: group:maintainers
created: 2026-03-08
updated: 2026-09-16
---

# Codex adapter

## Overview

Codex reads project instructions from `AGENTS.md` in the repository root. It can also read referenced files on demand, but `AGENTS.md` should remain self-contained enough to define the startup contract, docs-first gate, canonical state file, and close-out expectations.

Note: `AGENTS.md` is a cross-tool convention, not Codex-specific — several agent tools read it. The root `AGENTS.md`/`LLM_BRIEF.md` pair is therefore the **generic instruction layer** (see `../generic/ADAPTER.md`); this adapter documents how Codex specifically consumes it plus the `tools/agents/*.sh` enforcement scripts.

## Native instruction files

- `AGENTS.md`: mandatory startup contract and docs-first gate.
- `LLM_BRIEF.md`: compact project identity, important paths, and common commands.
- `CONTEXT.md`: tool-agnostic project-os contract.
- `SNAPSHOT.yaml`: canonical machine-readable work state.

## Current repository integration

`AGENTS.md` states the startup and docs-first contract. The repository scripts below are the enforcement points that the current Codex adapter documents. This repository does not yet check in `.codex/hooks.json`, generate Codex-native skills or custom subagents, or load native hooks for the cockpit's Codex session feed. [[ISS-0312]] records that gap.

| Contract | Entrypoint | Purpose |
|---|---|---|
| Startup preflight | `bash tools/agents/bootstrap.sh` | Verify required files, snapshot focus, branch, and basic tooling. |
| Docs-first intake | `bash tools/agents/start-change.sh "<short title>"` | Scaffold a change note when downstream projects require docs-first change records. |
| Docs-first validation | `bash tools/agents/check-docs-first.sh` | Check that code changes have documentation coverage and snapshot updates. |

See `tools/instructions/HOOKS.md` for the shared hook contracts. The Claude adapter installs native hooks for several of them; Codex currently relies on instructions, these scripts, and the pre-commit and CI checks.

## Native Codex integration to add

The upstream `project-os` repository now contains a native adapter at local commit `336d5f9` with generated `.agents/skills/`, `.codex/agents/`, `.codex/hooks.json`, and a Codex payload hook runner. It is tracked in `project-os-dev` PHASE-0006 and has not been synced into this cockpit. The list below records the integration design and the cockpit-specific telemetry that remains in [[ISS-0312]].

OpenAI's [Hooks documentation](https://learn.chatgpt.com/docs/hooks) describes lifecycle hooks in a trusted project `.codex/hooks.json` or `.codex/config.toml`. It includes `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PermissionRequest`, `Stop`, and `SessionEnd`. Project hooks need the user's trust review before they run. The installed `codex-cli 0.154.0` reports the hooks feature as stable and enabled; this is an availability check, not a claim that hooks are installed in this repo.

Generate Codex's native adapter from the same canonical `tools/skills/` and `tools/instructions/` sources used by the Claude adapter:

- `.codex/hooks.json` should register project-os lifecycle checks after each HC contract is adapted to Codex's payload, tool names, path lookup, and decision format. A Claude hook command cannot be copied unchanged because it assumes `CLAUDE_PROJECT_DIR` and Claude's edit payload.
- [Repository skills](https://learn.chatgpt.com/docs/build-skills) under `.agents/skills/` can point to the canonical playbooks, as `.claude/skills/` does today.
- [Custom subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) under `.codex/agents/` can provide clean-context planning and independent review where the task warrants them. The model choice and delegation rule must be explicit rather than inherited from Claude's pins.

Register generated Codex paths in `tools/sync/MANIFEST.yaml` so downstream repos receive them, and update the HC-001 path exclusions in `tools/instructions/HOOKS.md` for generated `.codex/` and `.agents/` files.

The cockpit's per-session telemetry is a separate installation problem. `desktop/src/ipc/agent-instrument.ts` currently passes only `notify` to Codex, while Claude gets lifecycle hooks and a statusline feed. The hook forwarder proposed in [[ISS-0312]] must preserve Codex login state, send `agent: codex` into the existing sidecar endpoint, and avoid changing the user's `~/.codex` without explicit opt-in. Native tool events need a Codex-specific file-path mapping before the activity strip can claim touched-file parity.

## Synchronizing the adapter

Run `tools/skills/adapter-sync/SKILL.md` when shared lifecycle, status, quality, snapshot, or skill rules change. The sync should update Codex-facing guidance without introducing tool-specific files for unsupported agents.
