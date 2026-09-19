---
type: "[[issue]]"
id: ISS-0277
aliases: ["ISS-0277"]
title: "No check notices when a repo's copy of the cockpit is missing, out of date or different from what its stamp says"
status: open
owner: user:edwin
reported_by: agent
created: 2026-09-02
updated: "2026-09-19"
severity: medium
component: tooling
phase:
source: ["Found during the fleet release sweep, 2026-09-02"]
related: ["[[CHG-20260902-The-Inbox-Takes-Any-File-Type]]"]
tests: []
---

# No check notices a missing or out-of-date cockpit copy

Nothing warns when a fleet repo's `tools/cockpit/` copy is missing files, lags the cockpit repo, or differs from the release its `CANONICAL_SHA` stamp names.

## Problem

`tools/cockpit/` is a delivery copy in all twelve fleet repos, refreshed by `release-to-project-os.sh` and then by template sync. **No check looks at it.** The 2026-09-02 sweep found three things, none of which anything would have reported:

1. **Every repo was five weeks and 193 commits stale** — `afc4fa7b` (2026-07-28) against a canonical repo that had moved 20,704 lines. Nothing measures the gap, and the stamp files exist precisely to make it measurable.

2. **`articles` had no `src/` at all.** Its `tools/cockpit` held `CANONICAL_DATE`, `CANONICAL_SHA`, `pyproject.toml` and `run.sh` — four files, and not the 45-module package `run.sh` exists to launch. Not gitignored, simply never committed. The stamp said `4100e845`, a different release from the other eleven, and no comparison against a sibling had ever been made. **A repo carrying a stamp for software it does not have reads as up to date.**

3. **`validate_docs_bundled.py` differed between repos carrying the same `CANONICAL_SHA`** — 1969 lines in the four repos PHASE-041 migrated, ~1810 in the rest. A delivery copy that varies at a fixed stamp is not a delivery copy, and the stamp is what everyone reads.

The third is the sharpest, because it is the failure the stamp was supposed to prevent. `fleet-drift.py` exists ([[project-os-cockpit#TASK-0588]]) but measures *validator rule codes*; it says nothing about the vendored cockpit.

## Expected

Some check answers "does every repo have the cockpit its stamp claims, and how far behind is it?" — and answers it from the files, not from the stamp.

## Next Actions

- [ ] A per-repo content hash beside `CANONICAL_SHA`, so a stamp cannot outlive the tree it names
- [ ] Extend `fleet-drift.py` to report cockpit staleness in commits, the way it reports rule-code drift
- [ ] Fail loudly on a `tools/cockpit` with no `src/` — the case that is not drift but absence

## Recurrence, 2026-09-18

Found while settling project-os-dev's open issues (FEAT-0036). The template's `tools/cockpit/` was last released on 2026-09-02 (project-os c24bdff) and 19 files in it now differ from this repository's `src/project_os_cockpit/`. your-trainer's copy has two files of its own, `publication.py` and `server.py`, which the sync reports as local content on every run and leaves alone. Nothing reported either until a person read the sync's output.

## Checked against the code, 2026-09-19: still true, kept

**What a user notices:** A repo can launch an old or incomplete cockpit while its stamp says it is current, and nobody finds out until a person compares the files by hand. Today every copy happens to match, but only because the last sync was done by hand.

Evidence: All 13 repos under ~/Dev/repos carry `tools/cockpit/CANONICAL_SHA` = c665cf8f with a `src/` directory, and a hash of every `src/**/*.py` is identical across them (0ed2d15704), so the 2026-09-02 and 2026-09-18 symptoms are gone. The check is still missing: `grep -in cockpit tools/scripts/fleet-drift.py` only mentions the cockpit as a validator repo (lines 12, 17), and no script in project-os or project-os-cockpit other than `release-to-project-os.sh` (which writes the stamp) reads `CANONICAL_SHA`. `git log c665cf8..HEAD -- src` shows the cockpit has already moved one commit past the stamp.

**Belongs to:** no feature. **Next:** Bigger: extend `fleet-drift.py` (or the template sync) to compare each copy's content hash with the stamp and report missing `src/` and commits behind.

Checked as part of project-os-dev FEAT-0036 (TASK-0141).
