---
type: "[[task]]"
id: TASK-0478
aliases: ["TASK-0478"]
title: "Renumber into the `TST-*` space, and record the counter jump where a reader will meet it"
status: done
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0119-The-Merge-Migration]]"]
parent: "[[FEAT-0119-The-Merge-Migration]]"
effort: S
depends: ["[[TASK-0477-The-Merge-Migration-Script]]"]
blocks: []
related: []
tests: []
---

# Renumber into the `TST-*` space

Ids move `CHK-####` → the next free `TST-####` per repo, in `section`/`ordinal` order so the numbering follows the suite's own reading order rather than the old id's. Filenames follow. `aliases:` keeps the `CHK-*` id so a person typing the old id into the palette still lands on the note — the cheap half of provenance, and the half a reader actually uses.

**Measured before it was chosen: zero inbound `[[CHK-*]]` references exist anywhere in the fleet**, so nothing needs rewriting. Verify that again at migration time rather than trusting this sentence — it is a fact about the corpus on 2026-08-18, not an invariant.

`your-trainer`'s TST counter goes 18 → ~597. Record it in that repo's SNAPSHOT `note:` — a counter that jumps 579 in one commit is the kind of thing somebody later reads as corruption.

Done when: every merged note carries a `TST-*` id and a `CHK-*` alias, counters are raised by `sync-snapshot.py`, and the fleet validates.

## Done

Ids run in **suite order** — tier, then section, then ordinal — rather than in old-id order, so the numbering follows the direction somebody walks the suite. That is the one improvement a renumber gets to make over what it replaces.

`aliases:` keeps the `CHK-*` id, so typing it into the palette still lands on the note. Verified again at migration time rather than trusted: **zero inbound `[[CHK-*]]` references exist anywhere in the fleet**, so nothing needed rewriting.

This repo: `CHK-0001..0034` → `TST-0044..0077`, counter raised 43 → 77 by `sync-snapshot.py`.
