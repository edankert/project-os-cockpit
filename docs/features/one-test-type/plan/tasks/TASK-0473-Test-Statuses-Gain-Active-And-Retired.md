---
type: "[[task]]"
id: TASK-0473
aliases: ["TASK-0473"]
title: "Test statuses gain `active` and `retired` — upstream, and it closes ISS-0178 on the way"
status: done
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0118-The-Test-Type-Absorbs-The-Check]]"]
parent: "[[FEAT-0118-The-Test-Type-Absorbs-The-Check]]"
effort: M
depends: []
blocks: []
related: []
tests: []
---

# Test statuses gain `active` and `retired`

`ALLOWED_STATUS["test"]` goes from `{ready, passing, failing}` to `{draft, active, ready, passing, failing, retired}`, in `~/Dev/repos/project-os` first and synced down. STATUSES.md gains the transitions; the `[[check]]` section is retired with a pointer.

**`active` is what makes the merge safe.** An acceptance test rests there, and `active` is in neither `REVIEW_SETTLED_STATUSES` nor the Run obligation's `states` — so both gates stay off by construction, which is the standard [[ADR-0030]] set and [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] must meet.

**`retired` closes [[ISS-0178-A-Test-Cannot-Be-Retired]]**, `deferred` since 2026 for want of a terminal value. This repo's TST-0029 is the live instance — its subject was deleted by FEAT-0107 and it says so in prose because there was no word for it. Re-home that note as part of this task rather than leaving the issue's own example unfixed.

Done when: both values are legal upstream and here, TST-0029 carries `retired`, and ISS-0178 moves to `fixed`.

## Done

Landed upstream as `eb10a45` and hand-merged here (the file was already locally diverged, so the sync correctly refused it). `ALLOWED_STATUS["test"]` is now `{draft, active, ready, passing, failing, retired}`; STATUSES.md carries the transitions, a `level: acceptance` subsection, and a terminal-table row per half of the type. **The `[[check]]` section is retired with a pointer rather than deleted** — it explains why the type existed and why it stopped, which is the part a reader arriving from an old link needs.
