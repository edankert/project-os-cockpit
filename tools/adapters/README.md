---
type: reference
id: TOOLS-ADAPTERS-README
status: active
owner: group:maintainers
created: 2026-03-08
updated: 2026-03-08
tags: [tools, adapters]
---

# Tool Adapters

Adapters map project-os rules to a target LLM tool's native instruction format. Each adapter lives in a subdirectory named after the tool.

## Why adapters?

project-os rules are defined once in `tools/instructions/` and `tools/skills/`. Different LLM tools consume instructions differently:

- **Claude Code**: `CLAUDE.md` with `@file` imports, `.claude/rules/*.md` for overflow
- **Codex**: `AGENTS.md` in repo root
- **Cursor**: `.cursor/rules/*.mdc` with glob-scoped rules
- **Generic**: `CONTEXT.md` (monolithic fallback for any tool)

Adapters document how to deliver the shared rules via each tool's native format, so rules are maintained in one place but consumed natively by each tool.

## Directory structure

```
tools/adapters/
├── README.md              ← this file
├── claude-code/
│   ├── ADAPTER.md         ← adapter documentation
│   └── hooks/             ← hook implementations (see HOOKS.md)
├── codex/
│   └── ADAPTER.md
├── cursor/
│   └── ADAPTER.md
└── generic/
    └── ADAPTER.md
```

## Adding a new adapter

1. Create a subdirectory under `tools/adapters/` named after the tool
2. Create an `ADAPTER.md` documenting:
   - Tool name and version
   - Native instruction file format and location
   - Import/include mechanism (if any)
   - How to map project-os rules to the native format
   - Hook support (see `tools/instructions/HOOKS.md`)
3. If the tool supports hooks, add a `hooks/` subdirectory with implementations
4. Run the `adapter-sync` skill to generate/update tool-specific files

## Relationship to CONTEXT.md

`CONTEXT.md` remains the generic fallback. It is tool-agnostic and works with any LLM. The `generic/ADAPTER.md` documents this fallback approach. Tool-specific adapters are preferred when available because they use native instruction formats, which tools process more reliably.
