---
type: "[[issue]]"
id: ISS-0131
aliases: ["ISS-0131"]
title: "Phase groups in the features navigator render flat while the Tests view's groups render as cards — one missing `item_layout` field, and the two views disagree about what a group looks like"
status: triage
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-11
updated: 2026-08-11
source: ["Edwin, 2026-08-11: 'The feature view does not show in the same way as the test view did, the test view showed each phase as a card.'"]
severity: low
component: "cockpit-nav"
parent: ""
related: ["[[FEAT-0086-Tests-Becomes-A-View]]", "[[FEAT-0085-The-Navigator-Shows-The-Structure-The-Record-Has]]", "[[ISS-0132]]"]
tests: []
---

# Phase groups render flat while test groups render as cards

## Problem

The Tests view draws each of its groups — `Tier 1`, `Tier 2`, `Tier 3`, `Verified` — as a bordered card. The Features view draws each phase group as a plain collapsible row. Same navigator, same renderer, different result, and nothing decided it should be so.

The cause is a single field. `_tests_groups` sets `"item_layout": "stacked"` on its tier groups; `_features_groups` sets nothing. The renderer turns that into a class:

```ts
const layoutClass = group.item_layout ? ` nav-group-${group.item_layout}` : '';
details.className = `nav-group${layoutClass}`;
```

So `nav-group-stacked` is what produces the card, and phase groups never get it.

**Why it reads as a regression rather than a preference.** A phase is the largest structural unit the record has — it is the thing [[REL-0001]] is now *defined* by — and it is drawn less prominently than a test tier. The `item_layout` field is a presentation hint the server hands the client, so which groups are cards is currently decided one call site at a time rather than by any rule.

## Repro

1. Open the Tests view (`~tests`) — the four groups are bordered cards.
2. Open the Features view — the phase groups are plain rows.

## Expected

Phase groups read as cards, or a stated rule says which groups are cards and why. Either resolves it; drifting per call site does not.

## Actual

`item_layout` is set on the tier groups and absent on the phase groups, so the two views disagree.

## Evidence

- `src/project_os_cockpit/cockpit.py` — `_tests_groups` sets `item_layout: "stacked"`; `_features_groups` does not.
- `desktop/src/renderer/renderer.ts:8738` — `nav-group-${group.item_layout}`.
- Live payload 2026-08-11: `mode=tests` group `tier1` → `layout='stacked'`; `mode=features` group `PHASE-028` → `layout=None`.

## Next Actions

- [ ] Decide the rule: is a card for groups that name a *thing* (a phase, a tier) rather than a category? `groupLabelIsCategory(mode)` already draws that distinction in the renderer for the header's grammar, and the layout could follow the same predicate instead of a per-call-site field.
- [ ] Apply it to `_features_groups`, and to any other group builder the rule catches.
