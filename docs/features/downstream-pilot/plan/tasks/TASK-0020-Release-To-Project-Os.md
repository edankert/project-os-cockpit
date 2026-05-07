---
type: "[[task]]"
id: TASK-0020
aliases: ["TASK-0020"]
title: "Release docs-server to project-os (sync script + run.sh wrapper + LIFECYCLE rule)"
status: doing
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-08
updated: 2026-05-08
source: []
implements: ["[[FEAT-0005]]", "[[REQ-0017]]"]
fixes: []
effort: S
due: ""
depends: []
blocks: []
related: ["[[REQ-0017]]"]
tests: []
---

# TASK-0020 — Release docs-server to project-os

## Definition of Done
- [x] `tools/scripts/release-to-project-os.sh` syncs the deployable source set (`src/docs_server/`, `pyproject.toml`, `README.md`) into `~/Dev/repos/project-os/tools/docs-server/`, with the standard exclude set (`.venv`, `__pycache__`, `.pytest_cache`, `dist`, `build`, `*.egg-info`). `tests/` is intentionally NOT synced — delivery artefact, not a dev environment.
- [x] Script refuses to run on a dirty canonical-repo working tree (`git diff --quiet && git diff --cached --quiet` gates the sync).
- [x] Script refuses to run when the project-os destination has uncommitted local edits (forces deliberate review of any drift).
- [x] Script stamps `CANONICAL_SHA` (canonical commit hash) and `CANONICAL_DATE` (ISO date) into the project-os copy for one-line provenance.
- [x] `~/Dev/repos/project-os/tools/docs-server/run.sh` is a ~30-line bash wrapper that ensures a venv exists, `pip install -e .`'s the synced source, then `exec python -m docs_server "$@"`.
- [x] LIFECYCLE.md (this repo's `tools/instructions/LIFECYCLE.md`) carries a close-out rule: when a CHG touches `src/docs_server/` or `pyproject.toml`, the agent runs the sync and commits the result.
- [x] `tests/test_release.py` verifies the sync against a temp dir: dirty-tree refusal (PASS) + happy-path file set / stamps + asserts `tests/` is absent from the destination (auto-skips when canonical is dirty; runs the assertions when clean — see below).
- [ ] Initial sync run executed; project-os/tools/docs-server/ committed with the bootstrap copy. **(Pending: requires committing the canonical-side work first so the script's dirty-tree guard passes; see Notes.)**

## Steps
- [x] Write `tools/scripts/release-to-project-os.sh` (bash, ~80 lines including comments + guards).
- [x] Write `~/Dev/repos/project-os/tools/docs-server/run.sh` (committed to project-os, not synced).
- [x] Add the close-out rule to LIFECYCLE.md.
- [x] Add `tests/test_release.py` exercising the script via `subprocess.run` against a temp dir target.
- [ ] Run the initial sync; commit the result in project-os. **(See Notes.)**

## Notes
- Sync is intentionally one-way. The script overwrites; it never reads from project-os back into the canonical repo.
- Provenance stamps are committed plain text — easy to grep across project-os when debugging downstream version mismatches.
- The run.sh wrapper lives ONLY in project-os, not in this repo's source tree, because it's a project-os concern (how project-os hosts the synced tool). Syncing the wrapper out of docs-server would couple docs-server to a specific deployment shape; better to let project-os own its own bootstrap.

### To complete the initial sync
The dirty-tree guard refuses to run while this conversation's canonical-side
work is uncommitted (which is correct — provenance stamps must trace to
real commits). Two-step close-out:

```bash
# 1. From the docs-server repo, commit the canonical-side work
git add -A && git commit -m "Add release-to-project-os mechanism (TASK-0020)"

# 2. Run the sync (now that the tree is clean)
tools/scripts/release-to-project-os.sh

# 3. Commit the result in project-os
cd ~/Dev/repos/project-os
git add tools/docs-server/
git commit -m "Bootstrap synced docs-server copy from canonical repo"
```

After step 1 the happy-path test (`test_release_happy_path_writes_expected_files`)
will run and assert; before then it auto-skips.
