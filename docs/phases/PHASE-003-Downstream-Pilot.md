---
type: "[[phase]]"
id: PHASE-003
aliases: ["PHASE-003"]
title: "Downstream pilot"
status: planned
order: 3
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
features:
  - "[[FEAT-0005-Downstream-Pilot]]"
depends: ["[[PHASE-001-MVP]]", "[[PHASE-002-Project-OS-Adapter]]"]
---

# Phase 3: Downstream pilot

## Goal
Validate the cross-repo invocation pattern by deploying project-os-cockpit in `~/Dev/repos/your-applications.com/tools/project-os-cockpit/`. Use it day-to-day on real project-os content and harden the pattern so other repos can adopt it.

## Scope

### In scope
- Thin shim under `your-applications.com/tools/project-os-cockpit/` (wrapper script + README).
- Decided install mechanism (ADR-0003 — to be authored before this phase ships).
- Documentation updates in the upstream `docs/ARCHITECTURE.md` reflecting what we learned.

### Out of scope
- Multiple downstream consumers (one is enough to validate the pattern).
- pip-registry packaging.

## Exit criteria
- The shim is small (≤30 lines of script + README).
- Tablet on the same Wi-Fi can browse `your-applications.com` docs via `mac-studio.local:<port>/docs/` and watch live-reload as edits land.
- The pattern is documented well enough that a new project-os repo could adopt it with copy-paste + minor edits.

## Dependencies
PHASE-001 + PHASE-002 must both be complete (or close enough) — there's nothing to deploy without them.
