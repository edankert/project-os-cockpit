---
type: "[[issue]]"
id: ISS-0025
aliases: ["ISS-0025"]
title: "Incoming ADR-0008 taxonomy collapse empties the delivered band and retires ~12 vocabulary members across eight surfaces"
status: fixed
severity: medium
owner: user:edwin
created: 2026-07-25
updated: 2026-07-25
component: ui
source: ["upstream:project-os-dev ADR-0008"]
related: [ISS-0023]
tests: []
---

# Incoming taxonomy collapse

## Problem

`project-os-dev` has opened [[PHASE-0002]] with ADR-0008, "States must earn their keep", which collapses the project-os status taxonomy from 64 declared values to roughly 45 by deleting every value with no observed fleet usage. The cockpit's status vocabulary is downstream of that decision and will need to follow, as it did for ADR-0007.

The measurement behind it: 5,890 `status:` writes across 10 repos and 3,775 notes, reconstructed per-note from git history.

## The part that matters here: the delivered band empties

`statuses.py` documents the band's history precisely — ISS-0023 introduced `delivered` for work shipped but not signed off; `implemented` was its founding member until ADR-0007 made that terminal, leaving:

```python
"delivered": (
    "staged",        # release: verified and ready, not yet live
    "monitoring",    # risk: mitigated, still under watch
),
```

ADR-0008 deletes **both**. Neither `staged` nor `monitoring` has ever been written — zero occurrences in 5,890 status writes across the whole fleet. So the collapse does not shrink the band, it empties it, and with it:

- `DELIVERED_STATUSES` and its deliberate exclusion from Hide-completed
- `STATUS_RANK` slots 51/52
- `BAND_TOKEN["delivered"]` and its CSS custom property in both stylesheets
- the amber band added to the UI on 2026-07-22

## Expected

A decision, recorded here, before the upstream vocabulary lands.

## Options

1. **Retire the band.** The honest reading: it has no members, and never had one anyone wrote. Unwinds ISS-0023.
2. **Retain `staged`/`monitoring` as an explicit ADR-0008 exception**, on the grounds used for `failing` — unreachable rather than unwanted. Weaker here: ADR-0010 makes `failing` reachable by stamping test status from execution, and no planned work makes `staged` or `monitoring` reachable.
3. **Repopulate the band** with a genuinely non-terminal status from the collapsed vocabulary, if one exists.

Option 1 falls out of ADR-0008 by default, which is exactly why it should be chosen deliberately instead: ISS-0023 put real reasoning into that band, and it should be unwound on purpose or not at all.

## Also in scope

- Issue `closed` merges into `fixed` (3% follow-through fleet-wide) — `DONE_BY_TYPE["issue"]` in `cockpit.py` must follow.
- `next`, `blocked`, `reopened`, `retired`, `mitigating`, `deprecated` and possibly `approved` are deleted upstream — all appear in `BANDS`, `TASK_STATUS_ORDER` and `STATUS_RANK`.
- Legacy tolerance for unmigrated repos should stay, but be documented as deliberate rather than incidental.

## Evidence

Eight surfaces enumerate the vocabulary today — the `statuses.py` docstring still says six:

`statuses.py` · `cockpit.py` · `templates.py` · `validate_docs_bundled.py` · `static/cockpit.js` · `static/cockpit.css` · `static/base.css` · `desktop/src/renderer/renderer.ts`

`tests/test_status_vocabulary.py` already parses the JS and both stylesheets, so it will name whichever surfaces fall behind. Updating the docstring's count is part of this work.

## Not yet actionable

Upstream ADR-0008 is `proposed`, and whether `approved` survives is deliberately undecided there (upstream TASK-0053). Scaffolding a feature here before that lands would be implementing against a draft requirement. **Triage until the upstream vocabulary is settled**, then scaffold.

## Verified: nothing is broken today

Every status currently in `project-os-dev` maps to a band (`accepted`, `active`, `backlog`, `cancelled`, `closed`, `done`, `draft`, `fixed`, `implemented`, `merged`, `open`, `planned`, `proposed`, `reference`, `superseded`, `triage`), and its three new phase notes all resolve — including the `PHASE-999` parking-lot sentinel, which `_PHASE_RE` (`PHASE-\d+`) matches and which sorts last on `order: 999`. This issue is about the incoming change, not a live defect.

## Resolution (2026-07-25)

Upstream TASK-0053 settled the vocabulary the same day (64 → 53 declared values), so this moved straight from triage to done without needing a feature scaffold.

- **The `delivered` band is retired** — option 1, recorded as [[ADR-0006-Retire-Delivered-Band|ADR-0006]]. Both members had zero writes across 5,890, so the band could never be entered.
- **`ready` moved from the active band to pending.** Under ADR-0008/ADR-0010 a test at `ready` is *defined but not yet executed*, which is "not started", not "in flight".
- `DONE_BY_TYPE["issue"]` needed no change: it already contained both `fixed` and `closed`, so the merge was a no-op there.
- Surfaces updated: `statuses.py`, `templates.py`, `base.css`, `cockpit.css`, `renderer.ts` (+ rebuilt `dist/`), and two rewritten tests. The parity test named every stale surface in turn — the eight-surface fan-out was a short edit rather than a hunt, which is what `statuses.py` was built for.
- Full suite green: **253 passed, 1 skipped**.

Legacy vocabulary (`todo`, `pending`, `fulfilled`, `met`, `verified`, …) is deliberately retained in `BANDS` so repos with unmigrated history still render; that tolerance is now stated in the module docstring rather than being incidental.
