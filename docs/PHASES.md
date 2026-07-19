# Phase Registry

This document is the **semantic source of truth** for development phases. It maps phase IDs to specific milestones and is consumed by Bases / dashboards.

## How Phases Work

- **Property**: `phase` (string wikilink in frontmatter, e.g. `"[[PHASE-001-MVP]]"`)
- **Purpose**: Groups related work into delivery milestones.

## Phase Definitions

| Phase | Name | Description | Key Deliverables | Status |
|---|---|---|---|---|
| [PHASE-001](phases/PHASE-001-MVP.md) | MVP | Renderer + live reload — the smallest useful tool. | FEAT-0001, FEAT-0002 | done |
| [PHASE-002](phases/PHASE-002-Project-OS-Adapter.md) | Project-os adapter | ID resolution polish, auto-index pages, backlinks panel, bases-driven cockpit layout. | FEAT-0004, FEAT-0006 | active |
| [PHASE-003](phases/PHASE-003-Downstream-Pilot.md) | Downstream pilot | Deploy under `your-applications.com/tools/project-os-cockpit/`. Validate cross-repo invocation. | FEAT-0005 | planned |
| [PHASE-004](phases/PHASE-004-Embedded-Terminal.md) | Embedded terminal | Opt-in `ttyd`-iframe terminal panel, loopback-only. Pulled out of PHASE-001. | FEAT-0003 | planned |
| [PHASE-005](phases/PHASE-005-Desktop-Shell.md) | Desktop shell (Electron + Python sidecar) | System-wide Electron app that wraps the existing cockpit as a sidecar. Multi-project. Additive to modes 1 + 2. | FEAT-0007 | active |
| [PHASE-006](phases/PHASE-006-Native-Cockpit-UI.md) | Native cockpit UI (TypeScript rewrite) | Replace the iframe-mounted cockpit with native TypeScript panes. Python becomes a pure data + Markdown-render API. Mode 1 (browser) preserved. | FEAT-0008..FEAT-0013 | done |
| [PHASE-007](phases/PHASE-007-Agent-Instrumentation.md) | Agent instrumentation (hooks-aware terminal) | Auto-instrument Claude Code / Codex sessions in the embedded terminal via lifecycle hooks; activity strip, needs-input inbox, task dispatch, session insight. | FEAT-0019..FEAT-0022 | active |
| [PHASE-999](phases/PHASE-999-Future.md) | Future / Unphased | Sentinel parking-lot for items without a concrete delivery phase yet. Re-phase out when planning crystallises. | FEAT-0018 | planned |

## Active phase

PHASE-007. See `SNAPSHOT.yaml` `focus.phase`.

## Operational rules for LLMs

1. **Verify phase alignment**: check `phase` in task/feature frontmatter before starting work.
2. **Consult this registry**: understand the boundaries of the current phase.
3. **Prevent phase bleeding**: don't introduce implementations from future phases prematurely.
4. **Flag scope concerns**: if a task requires future-phase dependencies, document it and discuss before proceeding.
