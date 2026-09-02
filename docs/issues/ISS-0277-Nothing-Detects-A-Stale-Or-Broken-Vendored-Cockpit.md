---
type: "[[issue]]"
id: ISS-0277
aliases: ["ISS-0277"]
title: "Nothing detects a stale, divergent or incomplete tools/cockpit — one repo carried no package at all for five weeks and the stamp said it was fine"
status: open
owner: user:edwin
created: 2026-09-02
updated: "2026-09-02"
severity: medium
component: tooling
phase:
source: ["Found during the fleet release sweep, 2026-09-02"]
related: ["[[CHG-20260902-The-Inbox-Takes-Any-File-Type]]"]
tests: []
---

# Nothing detects a stale or broken vendored cockpit

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
