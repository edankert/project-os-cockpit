---
type: "[[issue]]"
id: ISS-0122
aliases: ["ISS-0122"]
title: "Active mode's `Doing · 44` contains one item anybody is working — `active` on a plan, a reference or a glossary is not work in flight"
status: "fixed"
phase: ""
owner: user:edwin
created: 2026-08-09
updated: "2026-08-13"
source: ["Session 2026-08-09: measuring every nav mode's payload while reviewing the views"]
severity: medium
component: "nav-payload"
parent: ""
related: ["[[FEAT-0023-Overview-Scopes]]", "[[DES-0004-Attention-In-The-Squares]]"]
tests: []
---

# Active mode's Doing column counts notes nobody is working

## Problem

`_active_groups` buckets by status alone. `active` is in `_ACTIVE_DOING`, and `active` is what a **plan** carries while its parent feature is open, what a **reference** carries while it is current, and what the **glossary** carries permanently. None of those is work in flight.

Measured on this corpus:

```
Doing (44): feature 1, plan 23, reference 18, phase 1, glossary 1
            statuses: doing 1, active 43
Next (45):  feature 21, adr 9, phase 6, design 5, requirement 3, issue 1
            statuses: planned 27, accepted 14, approved 3
```

**One** of the 44 is being worked (FEAT-0080, `doing`). And 14 of the 45 in `Next` are `accepted` ADRs and designs — settled decisions, not upcoming work.

## Repro

```
python3 - <<'PY'
import sys, collections; sys.path.insert(0, "src")
from pathlib import Path
from project_os_cockpit.index import Index
from project_os_cockpit import cockpit
idx = Index.build(Path("docs"))
for g in cockpit.nav_payload(idx, "active")["groups"]:
    print(g["label"], collections.Counter(i.get("type") for i in g["items"]))
PY
```

## Expected

A column headed `Doing` names work somebody is doing.

## Actual

It names every note whose status happens to be `active`, at a 44:1 ratio of noise to signal.

## Why it still matters when the mode has no button

`active` lost its top-bar button in TASK-0204, but it is not dead:

- `buildNowBoard()` — the overview's board for phase-less projects — is built from `nav?mode=active`. In such a repo this column is what the overview shows as "work in flight".
- The mode is still served, still reachable by a stored preference migration path, and still tested.

So the defect is latent in this repo and live in any phase-less one.

## Next Actions

- [ ] Decide the fix or the retirement — this is `triage` because both are defensible
- [ ] **If fixed:** exclude non-work types (`plan`, `reference`, `glossary`) from the in-flight buckets, and drop `accepted` from `_ACTIVE_NEXT` (an accepted ADR is a decision that has been made). A plan's status follows its parent by design (STATUSES.md), so reading it as independent work is a category error the same shape as queueing plans on the review desk — reported 2026-07-26 and fixed there, not here.
- [ ] **If retired:** delete `_active_groups`, `buildNowBoard` and the mode, and give phase-less projects the same overview everyone else gets. Note that nobody has reported this in the months the mode existed, which is evidence about its value.

## Fixed — 2026-08-13, taking the first of the two options

The issue offered a fix or a retirement and called both defensible. Fixed, because the mode is not dead: `buildNowBoard` — the overview for a **phase-less** project — is built from it, so the defect is latent here and live in any repo without phases.

Both halves of the recommended fix, as written:

- **Non-work types never reach the in-flight buckets.** `plan`, `reference` and `glossary` are excluded — a plan's status follows its parent by design (`STATUSES.md`), a reference is `active` while it is current, a glossary permanently. They remain eligible for `Done today`, where a plan closing with its feature is a real event.
- **`accepted` leaves `_ACTIVE_NEXT`.** An accepted ADR is a decision that has been made. The work it implies is the feature or task implementing it, and those carry their own status.

Measured on this corpus, before and after:

```
before   Doing 27  (feature 1, task 1, phase 1, reference 14, plan 10)
         Next  38  (adr 15, design 7, decision 2, issue 6, phase 4, test 1, feature 3)
after    Doing  3  (feature 1, task 1, phase 1)
         Next  12  (issue 4, phase 4, test 1, feature 3)
```

Twenty-four of twenty-seven rows in `Doing` were noise; the column now names exactly the work somebody is doing. It read 44:1 when this was filed and 27:3 after [[ISS-0125]] took the status off the standing documents — that earlier close-out moved the number without touching the cause, which is the distinction this note was making.

Guarded by `test_the_doing_column_names_only_work_somebody_is_doing` and `test_an_accepted_decision_is_not_upcoming_work`.
