---
type: "[[issue]]"
id: ISS-0257
aliases: ["ISS-0257"]
title: "`sync-project-os.py` walks upstream's filesystem, so it copies gitignored build output into every downstream repo — invisible to review because git ignores it on both sides"
status: open
owner: user:edwin
created: 2026-08-29
updated: 2026-08-29
severity: low
component: tooling
phase: "[[PHASE-999-Future]]"
related: ["[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]", "[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]", "[[FEAT-0143-The-Fleet-Runs-One-Validator]]"]
---

# The sync carries upstream's build output

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
