---
type: "[[change]]"
id: CHG-20260724-Verification-Record-Backfill
title: "Requirement verification records made machine-readable — criteria of record in frontmatter, criteria as checkboxes, `tests:` key present"
status: merged
owner: user:edwin
created: 2026-07-24
updated: 2026-07-24
source: ["downstream:your-sudoku"]
commit: ""
pr: ""
impacts: ["docs/requirements/"]
issues: []
features: []
reviewed_by: ""
review_date: ""
review_verdict: ""
related: []
---

# Verification record backfill

## Why

Raised in `../your-sudoku`, where 97 requirements sat at `implemented` and looked stuck. Two causes: the cockpit rendered `implemented` as if it were done (fixed separately — `../project-os-cockpit` ISS-0023, now synced here), and the requirement notes held their acceptance criteria as prose bullets that no tool could read. The validator's REQ-BOXES check keys off `acceptance:` frontmatter, so criteria living only in the body were invisible to it. This pass applies the same correction here.

## What changed

- **1 requirement notes** touched.
- **1** gained an `acceptance:` frontmatter list — **5 criteria of record** lifted out of prose.
- **5** body bullets became checkboxes, so a criterion can now be ticked individually against evidence.
- **1** notes gained the `tests:` key so a covering `[[test]]` can be linked.

Requirements already at `verified`, `retired`, `superseded`, `cancelled`, or `deferred` were **skipped**: reopening their criteria as unticked boxes would misrepresent work that has already been through close-out.

No criterion was ticked. Ticking requires naming evidence per criterion, which is per-requirement work for whoever knows the coverage — `close-out/SKILL.md`: *"A criterion with no evidence does not get ticked."*

## Impact

Documentation metadata only. No code, no behaviour, no status transitions. `bash tools/scripts/validate-docs.sh` reports no errors.

## Findings

Only one note needed the backfill — 15 of 21 requirements are already `verified` with 19 `TST-*` notes behind them, and 3 more are `retired`. This repo is where the palette half of the same investigation landed: see [[ISS-0023-Implemented-Status-Band-Drift]] and [[CHG-20260724-Delivered-Status-Band]].

## Documentation Coverage (All Types Considered)

- features / requirements: requirements updated (structure only, no status changes)
- tasks / issues / tests / workflows / decisions / risks: not-applicable
- changes: new
- snapshot: not-applicable (no tracked item changed status)

## Follow-ups

- [ ] Tick criteria against evidence, and link `TST-*` notes, per requirement.
- [ ] Independent review of this change is owed per `QUALITY.md`.
