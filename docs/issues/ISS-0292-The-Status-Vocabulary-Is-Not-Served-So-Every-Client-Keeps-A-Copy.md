---
type: "[[issue]]"
id: ISS-0292
aliases: ["ISS-0292"]
title: "The status bands, the severity order and the known types are not served as data, so every client outside this repository keeps a copy and the copies drift"
status: triage
phase: ""
owner: user:edwin
created: 2026-09-09
updated: 2026-09-09
source: ["Filed from project-os-deck on 2026-09-09, by TASK-0044 of FEAT-0012, which is the task that had to copy the vocabulary"]
severity: medium
component: api
parent: ""
related: []
tests: []
---

# The vocabulary a client cannot ask for is a vocabulary it has to copy

## Problem

**`statuses.py` is the single source of truth for which statuses exist and which band each belongs to, and nothing serves it.** Inside this repository that is fine: `test_status_vocabulary.py` parses `static/cockpit.js`, the two stylesheets and the Electron renderer so no surface here can fall behind. Outside it there is no such rope. A second application over the same corpus has to write the table down again, and nothing tells it when the table changes.

**It has already drifted once, in under two days.** project-os-deck copied the bands on 2026-09-07 and put `draft`, `proposed` and `ready` in its "doing" band, where `BANDS` puts all three in `pending`. Nothing caught it; it was found on 2026-09-09 while writing the task that reads the description's `band` section. Deck now pins its copy with a fixture recorded from `statuses.py` by a script, which turns the drift into a failing test — but a fixture is a workaround for the absence of an endpoint, not an answer to it.

**The same is true of two more vocabularies.** The severity order that bands the Issues view, and the set of known note types. A client that wants to draw either has the same choice: copy it, or do without.

## What would fix it

One read endpoint carrying the vocabulary as data — the bands with their members, the completed set, the legacy mapping, the severity order, the known types — so a client can ask instead of copying. It is a read, so it fits behind the existing guards and needs no new write surface.

## Why this is filed rather than worked around

`docs/reference/cockpit-capability-register.md` describes what the cockpit can do, and Deck's `docs/reference/cockpit-adoption.md` tracks what it has adopted. A capability that exists only as a Python module cannot be adopted, only duplicated. This is the issue the Deck task was required to file on the day it started copying, following the same pattern as the whole-edge-list endpoint.

## Where the copy lives now

- `project-os-deck/desktop/src/shared/statuses.ts` — the copy.
- `project-os-deck/desktop/fixtures/cockpit-statuses.json` — recorded from `statuses.py` on 2026-09-09 at commit `11ded07`.
- `project-os-deck/tools/scripts/record-sidecar-fixture.py` — what records it.
- `project-os-deck/desktop/tests/band-and-face.test.mjs` — what fails when the two diverge.

## Next Actions
- [ ] Decide whether the vocabulary is worth serving, or whether a pinned copy per client is the accepted answer
- [ ] If it is served, name the endpoint and the shape, and tell Deck so its copy can go
