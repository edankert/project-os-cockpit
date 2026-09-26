---
type: "[[issue]]"
id: ISS-0063
aliases: ["ISS-0063"]
title: "The Risks and Tests stat tiles are dead ends — they look clickable and navigate nowhere"
status: fixed
phase: "[[PHASE-010-Surface-Ownership]]"
owner: user:edwin
created: 2026-07-29
updated: 2026-07-29
source: []
severity: low
component: overview
parent: "[[FEAT-0047-Risks-On-The-Issues-Surface]]"
related: ["[[PHASE-010-Surface-Ownership]]", "[[FEAT-0049-Review-Desk-As-Record]]", "[[TASK-0200-Overview-Stage-Rework]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
reviewed_by: "model:claude-opus-5"
review_date: "2026-07-30"
review_verdict: "approved"
---

# ISS-0063 — Dead stat tiles

## Problem

`buildStatTile` takes an optional `navMode` and renders a `<button>` when it is present, a `<div>` when it is not (`renderer.ts:5186-5196`). Three of the six tiles in the strip are passed nothing: **Reqs**, **Tests** and **Risks**.

Reqs is defensible — requirements nest under features in the Features mode, so the tile has no single destination of its own. Tests and Risks are not: they are dead because the types had no page, which is exactly what [[PHASE-010]] is fixing.

## Repro

Open the project overview. Click the Features, Tasks or Issues tile — the nav mode changes. Click Tests or Risks — nothing happens.

## Expected

A tile showing a count either navigates to the surface listing those items, or does not look like a control.

## Actual

`renderer.ts:5236-5241`:

```ts
buildStatTile('Tests', String(hero.tests.passing),
  `/${hero.tests.total}`, buckets.tests, mix.tests),
buildStatTile('Issues', String(hero.issues.open),
  `open /${hero.issues.total}`, buckets.issues, mix.issues, 'issues'),
buildStatTile('Risks', String(hero.risks.open),
  `open /${hero.risks.total}`, buckets.risks, mix.risks),
```

Issues carries `'issues'`. Tests and Risks carry nothing.

## Evidence

Both tiles still render the mix bar and the count, so they are visually indistinguishable from the three that work — the failure is silent on inspection and only shows on click.

## Next Actions

- [ ] Risks tile → the Issues mode, once risks are listed there — [[TASK-0238]]
- [ ] Tests tile → `~review`, once the desk carries the test register — [[TASK-0241]]

## Notes

Not fixable on its own: a tile can only navigate somewhere that exists, which is why this issue is parented to the feature that builds the destination rather than filed as a standalone renderer fix. The Reqs tile is left dead deliberately and is out of scope — see [[PHASE-010]] Out of Scope.
## Independent review — 2026-07-30, approved

Fresh session, `model:claude-opus-5`, from the notes and the diff for `bed48ea`.

Mechanism confirmed at `renderer.ts:5290` — `buildStatTile` takes `navMode?: NavMode` and renders a `<button>` only when it is passed, so a tile without one is visually identical to a working one. Removing `'issues'` from the Risks call or `'review'` from the Tests call each fails an assertion; so does pointing Risks at the wrong mode. Keeping Reqs inert is defensible and recorded.

**One weakness in the marker test, not blocking.** `test_the_reqs_tile_stays_dead_on_purpose` anchors on `,\s*'[a-z]+'\s*\)$`, so a destination added with a trailing comma (`mix.requirements, 'features',\n    )`) slips past it. It is a decision-recording assertion rather than a defect guard, so the consequence is small — but it would not notice the Reqs tile silently gaining a wrong destination.

**One limit worth recording against this issue specifically.** Both tile assertions parse the call site. Setting `navMode = undefined` inside `buildStatTile` — reintroducing this exact bug at its source — passes all 20 tests in `tests/test_surface_ownership.py`. [[TST-0022]]'s `## Adequacy` says so plainly, and the manual step covers the behaviour, so this is a disclosed limit rather than a finding.
