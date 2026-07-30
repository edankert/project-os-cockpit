---
type: "[[feature]]"
id: FEAT-0005
aliases: ["FEAT-0005"]
title: "Downstream pilot deployment (your-applications.com)"
status: cancelled
phase: "[[PHASE-003-Downstream-Pilot]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-07-30
source:
  - "../your-applications.com/tools/project-os-cockpit/"
goal: "Validate the cross-repo invocation pattern by deploying project-os-cockpit in your-applications.com/tools/project-os-cockpit/ and using it to browse + author the manual content there."
release: ""
related: ["[[FEAT-0001]]", "[[FEAT-0002]]", "[[FEAT-0003]]", "[[FEAT-0004]]"]
requirements: ["[[REQ-0017]]"]
tasks: ["[[TASK-0020]]"]
---

# Downstream pilot deployment

## Goal
Once the upstream tool is functional (PHASE-001 + PHASE-002), deploy a thin shim under `~/Dev/repos/your-applications.com/tools/project-os-cockpit/` that runs the upstream against that repo's `docs/` tree. The shim is small (a wrapper script + a README); the upstream lives in this repo. This validates the pattern that other project-os repos can adopt.

## Scope
- **In scope:**
  - Shim under `your-applications.com/tools/project-os-cockpit/` containing:
    - `dev.sh` — wrapper script: `python -m project_os_cockpit <repo-root>/docs --bind 0.0.0.0 --port 8765 [--terminal --terminal-bind 127.0.0.1 --terminal-port 7681]`.
    - `README.md` — explains the upstream relationship and how to run.
    - Optionally a `Makefile` target.
  - Decide the upstream-source mechanism: editable install via `pipx install -e ../project-os-cockpit` vs running directly from the source checkout vs git submodule. Capture in an ADR before shipping.
  - Document the pattern in upstream `docs/ARCHITECTURE.md` so future downstream repos can adopt cleanly.
- **Out of scope:**
  - Multiple downstream consumers (one is enough to validate the pattern).
  - Auto-discovery of project-os repos — explicit path argument is fine.
  - Packaging for `pip install project-os-cockpit` from a registry (premature; local install path is enough for now).

## Acceptance
- From any directory on the host, running `~/Dev/repos/your-applications.com/tools/project-os-cockpit/dev.sh` starts the render server pointed at that repo's `docs/`.
- Tablet on the same Wi-Fi can browse `http://mac-studio.local:8765/docs/` and see the rendered notes.
- Edits to any `.md` under `your-applications.com/docs/` cause a soft-reload within ~500 ms in the open tablet browser.
- The shim is small (≤30 lines of script + README) so other repos can copy and adapt easily.

## Notes
The "small shim, big upstream" structure is the whole point. Per-repo configuration (port, terminal-on/off) lives in the shim; the rendering / indexing / SSE / project-os adapter logic lives upstream and is shared.

Decision pending — see `docs/decisions/ADR-0003-*` (to be authored before this feature ships) for the install-mechanism choice.


## Cancelled 2026-07-30 — overtaken, not abandoned ([[ISS-0078]])

`cancelled` rather than `done`: nothing here shipped. The thing it existed to prove was proven by a better mechanism instead.

**What replaced it.** [[FEAT-0007]] / [[PHASE-005]] gave the desktop shell workspace discovery — it finds every `SNAPSHOT.yaml`-bearing repo (**12** on this machine) and spawns a sidecar per workspace, and [[FEAT-0028]] validated all twelve in a single pass on 2026-07-30. The cross-repo pattern is not "validated by one pilot"; it is in daily use across the fleet.

**The shim would earn nothing now.** Its entire job is `python -m project_os_cockpit docs` — one command, run by hand against three repos while closing [[TASK-0231]] the same day. A wrapper script and a README to save that is not worth the file.

**Its task and requirement were never really its own.** [[TASK-0020]] is `done` and [[REQ-0017]] is `implemented`, both in [[PHASE-002]], and TASK-0020's actual subject is the upstream *release* mechanism rather than the downstream shim. This feature was left holding links to finished work that did something else — which is why it read as pending for three months while having nothing to do.

**The tablet half is settled, not dropped.** The acceptance criteria included reading over Wi-Fi, which the desktop shell does not serve (its sidecars bind `127.0.0.1`; only mode 1 binds `0.0.0.0`). Edwin, 2026-07-30: **no tablet.** So nothing is lost by closing.

`ADR-0003`, named here as "to be authored before this feature ships", was never written and its number went to "Visual style direction". Recorded so the dangling reference is explained rather than merely stale.
