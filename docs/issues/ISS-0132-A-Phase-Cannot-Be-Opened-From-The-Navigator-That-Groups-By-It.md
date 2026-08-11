---
type: "[[issue]]"
id: ISS-0132
aliases: ["ISS-0132"]
title: "A phase cannot be opened from the navigator that groups by it — the server sends every phase group's `url` and the renderer never reads it"
status: triage
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-11
updated: 2026-08-11
source: ["Edwin, 2026-08-11: 'I cannot select a phase in the features section (and see the phase note contents in the details pane).'"]
severity: medium
component: "cockpit-nav"
parent: ""
related: ["[[FEAT-0085-The-Navigator-Shows-The-Structure-The-Record-Has]]", "[[ISS-0131]]", "[[REL-0001-The-Human-Has-Levers]]"]
tests: []
---

# A phase cannot be opened from the navigator that groups by it

## Problem

The Features view groups every feature under its phase and prints the phase's ID and title as the group header. Clicking that header only folds the group. There is no way to reach the phase note — the note that carries the goal, the scope and the exit criteria — from the surface that is organised entirely around it.

**The data is already there.** The server populates `url` on every phase group:

```
group url: '/docs/phases/PHASE-028-Borrowed-Capability.md'
```

`NavGroupData.url` is declared in the renderer's own type (`renderer.ts:2954`). It is never read: `group.url` appears nowhere in `renderer.ts`. The payload has carried a working target all along and the client discards it.

**Why this matters more now.** [[REL-0001]] was re-scoped on 2026-08-11 to be defined by five phases reaching `done`, with exit criteria as the completion bar. The phase note is where those criteria live, so the release's own definition is currently unreachable from the view that lists its work.

## Repro

1. Open the Features view.
2. Click any phase group header, e.g. `PHASE-023 · Levers for the human`.
3. The group folds. The centre pane does not change.

## Expected

Selecting a phase group header opens the phase note in the centre pane, as selecting any feature row does. Folding stays available — the chevron already exists for it.

## Actual

The header is a `<summary>` whose only behaviour is toggling `<details>`. `group.url` is ignored.

## Evidence

- `desktop/src/renderer/renderer.ts:2954` — `url?: string` on `NavGroupData`.
- `desktop/src/renderer/renderer.ts:8752` — `summary.className = 'nav-group-header'`; no click handler, no `data-rel`.
- `grep -n "group\.url" desktop/src/renderer/renderer.ts` → no matches.
- Live payload 2026-08-11: every `mode=features` group carries a `/docs/phases/…` url.

## Next Actions

- [ ] Give the header a nav target from `group.url` via `extractRel`, without breaking the fold — the chevron toggles, the label navigates.
- [ ] Check the other modes whose groups carry a `url` (the tier groups point at `/tests/ACCEPTANCE_TESTS.md`) so this is fixed as a rule rather than for phases alone.
