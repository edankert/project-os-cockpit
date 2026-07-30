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
| [PHASE-007](phases/PHASE-007-Agent-Instrumentation.md) | Agent instrumentation (hooks-aware terminal) | Auto-instrument Claude Code / Codex sessions in the embedded terminal via lifecycle hooks; activity strip, needs-input inbox, task dispatch, session insight. | FEAT-0019..FEAT-0022 | done |
| [PHASE-008](phases/PHASE-008-State-And-Review-Surfaces.md) | State & review surfaces | State-first overview rework (project + phase dashboards per the 2026-07-26 design dossier) and the ~review desk where agent proposals, questions, and manual test runs meet a human. | FEAT-0040, FEAT-0041 | done |
| [PHASE-009](phases/PHASE-009-Design-Surfaces.md) | Design surfaces | Design artifacts become project records: rendered live at the app's own viewport, versioned with per-revision reasoning, annotated and reviewed where the notes live. | FEAT-0042, FEAT-0043 | done |
| [PHASE-010](phases/PHASE-010-Surface-Ownership.md) | Surface ownership | Every note type gets one purpose surface; Library reduces to Pinned + the Docs tree. Plans nest under features, risks join Issues, changes join the overview, tests and reviewed items join the review desk. | FEAT-0046..FEAT-0050 | done |
| [PHASE-011](phases/PHASE-011-Unproven-Claims.md) | Unproven claims become visible | Where the system already knows a claim is unproven — a waiver, a stale manual verification, a drifted status guard, a hand-maintained coverage register — the surfaces must say so. | FEAT-0018 | planned |
| [PHASE-012](phases/PHASE-012-Attention-In-The-Strip.md) | Attention in the strip | Give the phase squares the states they lack (DES-0004) so the Waiting-on-you list has no job, plus PHASE-010's reachability residue. Gated on DES-0004 having a verdict. | ISS-0067, ISS-0068 | planned |
| [PHASE-013](phases/PHASE-013-Fleet-Surfaces.md) | Fleet surfaces | Finish the cross-repo work: roll the design-system convention across the fleet, and surface per-workspace validator health. | FEAT-0028, FEAT-0044 | planned |
| [PHASE-999](phases/PHASE-999-Future.md) | Future / Unphased | Sentinel parking-lot for items without a concrete delivery phase yet. Re-phase out when planning crystallises. **Not a second sentinel:** `PHASE-999-Unscheduled` was a dangling link on 13 notes until 2026-07-30 and never existed. | FEAT-0029, TASK-0045, TASK-0065 | planned |

## Active phase

None active. PHASE-010 closed 2026-07-29; PHASE-011..013 are planned and unstarted, in that order. PHASE-012 is gated on DES-0004 carrying a review verdict. See `SNAPSHOT.yaml` `focus.phase`.

## Operational rules for LLMs

1. **Verify phase alignment**: check `phase` in task/feature frontmatter before starting work.
2. **Consult this registry**: understand the boundaries of the current phase.
3. **Prevent phase bleeding**: don't introduce implementations from future phases prematurely.
4. **Flag scope concerns**: if a task requires future-phase dependencies, document it and discuss before proceeding.
