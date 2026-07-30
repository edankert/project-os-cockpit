---
type: "[[phase]]"
id: PHASE-003
aliases: ["PHASE-003"]
title: "Downstream pilot"
status: superseded
order: 3
owner: user:edwin
created: 2026-05-07
updated: 2026-07-30
features:
  - "[[FEAT-0005-Downstream-Pilot]]"
superseded_by: "[[PHASE-005-Desktop-Shell]]"
depends: ["[[PHASE-001-MVP]]", "[[PHASE-002-Project-OS-Adapter]]"]
related: ["[[ISS-0078-Downstream-Pilot-Was-Overtaken-And-CLAUDE-Md-Still-Claims-It]]"]
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


## Superseded 2026-07-30 by [[PHASE-005]] ([[ISS-0078]])

`superseded`, not `done`: nothing here was built. **Workspace discovery replaced the need before the work started.**

This phase's goal was to prove the cross-repo pattern with one pilot shim so other repos could adopt it. [[PHASE-005]]'s desktop shell instead discovers **every** `SNAPSHOT.yaml`-bearing repo — twelve on this machine — and spawns a sidecar per workspace; [[FEAT-0028]] validated all twelve in one pass on 2026-07-30. The pattern is in daily fleet-wide use, which is more than one pilot could have shown.

### The exit criteria, each answered

- **"The shim is small (≤30 lines)"** — no shim. Its whole job is `python -m project_os_cockpit docs`, one command, and a wrapper to save typing it is not worth a file.
- **"Tablet on the same Wi-Fi can browse …"** — **settled: no tablet** (Edwin, 2026-07-30). Worth naming that the desktop shell would not have delivered it anyway: its sidecars bind `127.0.0.1`, and only standalone mode 1 binds `0.0.0.0`.
- **"The pattern is documented well enough that a new project-os repo could adopt it"** — met by a different route. A repo is adopted by *existing*: the shell discovers it, and [[TASK-0231]] applied the design-system convention across the fleet on the same basis.

### What this phase leaves behind

`ADR-0003` — "to be authored before this phase ships" — was never written and its number was taken by "Visual style direction". A gate that could not be satisfied under its own ID, which is a decent sign the phase had stopped being real some time ago.
