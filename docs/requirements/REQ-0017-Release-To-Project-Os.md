---
type: "[[requirement]]"
id: REQ-0017
aliases: ["REQ-0017"]
title: "Release the cockpit into project-os via one-way sync"
status: approved
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-08
updated: 2026-05-08
source: []
priority: medium
scope: "FEAT-0005"
specifies: ["[[FEAT-0005]]"]
verifies: []
related: []
tests: []
---

# REQ-0017 — Release the cockpit into project-os via one-way sync

## Statement
The canonical project-os-cockpit source SHALL continue to live in its own repo (locally at `~/Dev/repos/docs-server`, GitHub: `edankert/project-os-cockpit`). A vendored copy SHALL be maintained at `~/Dev/repos/project-os/tools/cockpit/`, populated by a one-way sync from the canonical repo. Downstream project-os consumers receive the cockpit via their existing `sync-project-os.sh` flow — no separate install step required.

The sync direction SHALL be enforced as **canonical → project-os only**. The project-os copy is a delivery artefact, not a parallel development branch.

### Why dual-repo (vs folding into project-os)
project-os is the meta repo — it ships templates and conventions but has no project-os *instance* notes (no FEAT-/TASK-/REQ-) to render. docs-server's development environment requires a consumer repo with real instance notes; this repo is exactly that. Folding docs-server into project-os would remove the only place where the cockpit can be dogfooded against real content.

### Sync mechanism
A script `tools/scripts/release-to-project-os.sh` in this repo SHALL:

1. Refuse to run if `git status` in the canonical repo is dirty (forces deliberate sync moments).
2. Refuse to run if the project-os destination has uncommitted local edits (prevents silent overwrites of any drift the LLM didn't authorise).
3. Copy the deployable source set into `~/Dev/repos/project-os/tools/cockpit/`:
   - `src/project_os_cockpit/` (Python package — the only thing run at runtime)
   - `pyproject.toml`
   - `README.md`
   - Excluded: `tests/` (dev-only — lives in the canonical repo, not the delivery copy), `.venv/`, `__pycache__`, `.pytest_cache`, `dist/`, `build/`, `*.egg-info`, editor temp files.
4. Stamp a `CANONICAL_SHA` text file in the project-os copy carrying the canonical-repo commit SHA at sync time, for one-line provenance.
5. Stamp a `CANONICAL_DATE` text file with the ISO date of the sync, so a `cat` reveals when the copy was last refreshed.

### Downstream consumer entry point
`project-os/tools/cockpit/run.sh` SHALL be a tiny wrapper that:

- Ensures a project-local Python venv exists at `tools/cockpit/.venv/` (or reuses one).
- Installs the synced docs-server source into that venv if not already installed (`pip install -e .`).
- Execs `python -m project_os_cockpit "$@"` so all CLI flags pass through.

The wrapper SHALL be ~10 lines, no exotic shell. Downstream projects invoke it as `tools/cockpit/run.sh docs --bind 0.0.0.0 --port 8765`.

### LLM-managed sync trigger
A rule SHALL be added to `tools/instructions/LIFECYCLE.md` (or an adjacent rules file) stating: when a CHG note merges that touches `src/project_os_cockpit/` or `pyproject.toml`, the agent's close-out routine MUST run the sync script and commit the result to project-os.

This is the discipline that makes dual-repo viable. Forgetting to sync is the failure mode the rule prevents; LLMs are reliable at "always do step N" once the rule is encoded.

## Acceptance Criteria
- Running `tools/scripts/release-to-project-os.sh` from the docs-server repo populates `~/Dev/repos/project-os/tools/cockpit/` with the source set above, plus `CANONICAL_SHA` and `CANONICAL_DATE` markers.
- Running with a dirty docs-server working tree fails fast with a clear error.
- Running when the project-os copy has uncommitted local edits fails fast with a clear error pointing at `git status`.
- `project-os/tools/cockpit/run.sh <docs-path>` from inside any downstream project starts the docs-server cockpit against the given docs path, after a one-time venv bootstrap.
- LIFECYCLE.md (or equivalent) carries a rule that obligates the agent to run the sync as part of close-out for any CHG that touches docs-server source.
- A unit test in `tests/test_release.py` verifies the sync against a temp dir: dirty-tree refusal, expected file set after a clean sync, presence of stamps, AND the absence of `tests/` in the destination (delivery artefacts must not ship the test suite).

## Rationale
Two sources of truth become unmaintainable when sync is a human-attention task. With LLM-managed close-out, "always run the sync after a touching-docs-server CHG" is reliable — humans skip steps; agents under a rule do not. This pattern lets us:

- Keep docs-server's own dogfood corpus (this repo) as the dev environment.
- Ship a frozen copy via project-os's existing sync mechanism, so downstream consumers don't need a second install path.
- Avoid the PyPI publishing / Homebrew tap / Docker image overhead while we're still pre-1.0.

The provenance stamps mean any version drift is visible in two `cat` commands; the dirty-tree guards mean accidental partial syncs can't slip through.

## Traceability
- Implements: [[FEAT-0005]] (downstream-pilot deployment)
- Implemented by: [[TASK-0020]]
