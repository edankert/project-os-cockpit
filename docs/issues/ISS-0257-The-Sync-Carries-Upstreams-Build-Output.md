---
type: "[[issue]]"
id: ISS-0257
aliases: ["ISS-0257"]
title: "A template sync copies the template's local build files, such as `__pycache__` folders, into every repo"
status: fixed
owner: user:edwin
created: 2026-08-29
updated: "2026-09-19"
severity: low
component: tooling
phase: ""
related: ["[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]", "[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]", "[[FEAT-0143-The-Fleet-Runs-One-Validator]]"]
reported_by: agent
---

# A template sync copies the template's local build files into every repo

When the template repo has a `__pycache__` folder (or `.pytest_cache`, or an `.egg-info`) inside a folder the sync owns, `sync-project-os.py` copies it into the repo being synced, and the dry run lists it as a synced file.

`tools/sync/MANIFEST.yaml` marks `tools/scripts/` as `template`, and `sync-project-os.py` copies it by walking upstream's **filesystem**. Upstream's `.gitignore` has `__pycache__/`, so `~/Dev/repos/project-os/tools/scripts/__pycache__/` exists on disk and is invisible to git — and the sync copies it.

Observed 2026-08-29 migrating `obsidian-supernote-sync` ([[TASK-0581-Migrate-Obsidian-Supernote-Sync]]):

```
[dry-run]   synced  tools/scripts/__pycache__/validate-docs.cpython-313.pyc
```

**The reason it has gone unnoticed is the reason it matters.** The artefact is gitignored *upstream*, so no reviewer of the template sees it; and it is gitignored *downstream* by the same stock rule, so it never appears in a `git status` after a sync either. It is copied, it lands, and nothing in either repo mentions it. A `.pyc` compiled by whatever interpreter the template author happened to run is now sitting in twelve other repositories.

Harmless today — CPython validates a cached `.pyc` against its source and a script run as `__main__` does not consult one at all. Not harmless in principle: the same walk would carry `.pytest_cache/`, an `.egg-info/`, or anything else a template-owned directory accumulates. `MANIFEST.yaml` already has an `excludes:` mechanism and uses it — but only for `tools/cockpit/`.

## Options

1. **Apply `excludes:` globally**, not per-path — `__pycache__`, `.pytest_cache`, `*.egg-info` are never template content anywhere.
2. **Copy from upstream's git index** rather than its worktree, so what syncs is what someone could review. Stricter, and it would also stop a locally-edited-but-uncommitted upstream file from propagating.
3. Leave it and prune downstream — what `migrate-fleet-validator.py` does today (`ARTEFACT_FRAGMENTS`), which fixes the symptom in one tool and not the sync everybody else runs.

Option 1 is the small correct fix; option 2 is the one that closes the class.

## Done when

- [ ] `sync-project-os.py` does not copy `__pycache__` or comparable build output for any manifest path.
- [ ] Proposed upstream — `tools/scripts/` and `tools/sync/` are template-owned, so the fix belongs there.

## Checked against the code, 2026-09-19: still true, kept

**What a user notices:** a sync dry run lists `.pyc` files as "synced", and the files land in the downstream repo without appearing in `git status`. Harmless today, but the same copy would carry any other untracked output the template author has on disk.

Evidence: `tools/sync/MANIFEST.yaml:70-71` still has only one `excludes:` entry, for `tools/cockpit/`. `tools/scripts/sync-project-os.py:294-296` walks the template's folders with `rglob("*")` and skips only `.git` and those per-path excludes. The script and manifest are template-owned and identical upstream (`~/Dev/repos/project-os/tools/sync/MANIFEST.yaml:70-71`). Upstream has no `tools/scripts/__pycache__` on disk right now, so the copy does not happen today, but nothing stops it.

**Small fix:** yes. Apply `__pycache__`, `.pytest_cache` and `*.egg-info` as excludes for every manifest path, in the template's `sync-project-os.py`, with a test that a planted `__pycache__` is not copied.

**Belongs to:** no feature; the fix goes in the template (project-os). **Next:** file or fix it in project-os, then sync.

Checked as part of project-os-dev FEAT-0036 (TASK-0141).

## Fixed in the template, 2026-09-19

The sync no longer copies `__pycache__`, `*.pyc`, `.pytest_cache` or `.DS_Store` from the template's working copy, anywhere (project-os `01031af`, `ALWAYS_EXCLUDED` in `sync-project-os.py`). `test-sync-stale.sh` asserts it and fails without the fix. Synced here as `36c9bf9`. Recorded upstream as project-os-dev TASK-0142.
