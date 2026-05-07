---
type: adapter
tool: codex
status: draft
owner: group:maintainers
created: 2026-03-08
updated: 2026-03-08
---

# Codex Adapter (Stub)

## Overview

OpenAI Codex reads project instructions from `AGENTS.md` in the repo root. It does not support file imports — all instructions must be inlined.

## Native instruction format

- **File**: `AGENTS.md` (repo root)
- **Syntax**: Markdown (no import mechanism)
- **Limit**: Single file, all instructions must be self-contained

## Import strategy

Since Codex does not support `@file` imports, the adapter must **inline** the relevant project-os rules into `AGENTS.md`. This means:

1. Core rules (LIFECYCLE, STATUSES, QUALITY) should be included directly
2. Condensed versions of reference instructions can be appended as sections
3. Skill playbook references can be listed as file paths (Codex can read files on demand)

### Generating AGENTS.md

Use the `adapter-sync` skill (`tools/skills/adapter-sync/SKILL.md`) to regenerate `AGENTS.md` from the project-os instruction files:

```
"Run tools/skills/adapter-sync/SKILL.md for the codex adapter"
```

The generated file should contain:
- The project-os operating rule (document-first, then implement, then close-out)
- SNAPSHOT.yaml as the canonical state file
- Status lifecycle definitions
- Quality/verification rules
- Paths to skill playbooks for on-demand reading

## Hook support

Codex does not currently support shell hooks. Enforcement relies on instruction-based rules only. When Codex adds hook support, implement the hook contracts from `tools/instructions/HOOKS.md`.

## Limitations

- No file import mechanism — instructions must be regenerated when rules change
- No hook support — enforcement is prescriptive only
- Parallel agent coordination is handled by Codex's native orchestration
