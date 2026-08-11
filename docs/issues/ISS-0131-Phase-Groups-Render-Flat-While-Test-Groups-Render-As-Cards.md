---
type: "[[issue]]"
id: ISS-0131
aliases: ["ISS-0131"]
title: "Phase groups in the features navigator render flat while the Tests view's groups render as cards — one missing `item_layout` field, and the two views disagree about what a group looks like"
status: fixed
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

The Tests view draws each of its groups — `Tier 1`, `Tier 2`, `Tier 3`, `Verified` — as a bordered card. The Features view draws each phase group as a plain collapsible row.

**Correction, 2026-08-11 — the first diagnosis in this note was wrong.** It claimed the cause was a missing `item_layout: "stacked"` field on the features groups. That field is real, and the tier groups do set it, but it is **inert**: `nav-group-stacked` appears nowhere in any stylesheet, so `item_layout` currently styles nothing at all. Adding it to `_features_groups` would have changed the class list and nothing on screen, and this note would have recorded a fix that fixed nothing.

The actual mechanism is the opposite of a missing field — it is a deliberate removal:

```css
.ws-nav-content .nav-group { border: 1px solid var(--border); … }   /* all groups */
.nav-group:has(> .nav-group-header.is-thing) { border: 0; background: none; }
```

Every group gets a card by default. The second rule **takes it away**, and `is-thing` is added only in features mode (`if (!groupLabelIsCategory(mode))`, where `groupLabelIsCategory = mode !== 'features'`). So phase groups are un-carded on purpose, and the stylesheet records why:

> *"…and a thing is not framed, nor ruled off. Four boxes around four categories read as structure; eighteen around eighteen phases read as clutter, and eighteen hairlines read as a table. The rows are already separated by being rows — the overview's scope pane has never needed anything between them."*

**So this is not a defect. It is a design decision, with a stated reason, and "fixing" it means reversing it.** That is Edwin's call rather than an implementation detail, which is why this note stays open while the other three PHASE-030 issues are fixed.

**One fact the decision's reasoning may not have.** Its argument is about count — eighteen boxes read as clutter. The features view no longer shows all phases at once: it opens on `OPEN · 8` with the completed phases folded into a roll-up. So the choice today is roughly **8 boxes, not 26**, which is much closer to the "four categories read as structure" case the same comment endorses. The count argument might now point the other way; it deserves re-testing rather than assuming either answer.

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

## Resolution — 2026-08-11

**Edwin decided it: the frame comes back.** This note had been left open on purpose, because fixing it reverses a decision that argued its own case. He looked at the result and asked for the cards, so the reversal is his rather than inferred.

The change is to the override, not to `item_layout`:

```css
.nav-group:has(> .nav-group-header.is-thing) {
  padding: 2px 4px;      /* was: border:0; background:none; border-radius:0; padding:0 */
  margin-bottom: 6px;
}
```

**The original reasoning is answered rather than ignored.** Its argument was a count — *eighteen boxes read as clutter where four read as structure* — and the count changed underneath it: the view now opens on `OPEN · 8` with finished phases folded into a roll-up, so the live choice is about eight boxes, which is the case that same comment endorses. Its second worry, that hairlines read as a table, does not return either: these are spaced cards, not rules.

What it was also protecting is kept. ISS-0093's 45px indent came from three paddings compounding, so the head keeps a small one (4px against the body's 5px) and still sits left of its own features.

`item_layout` was **not** touched, because it is not the mechanism — see the correction above. It remains inert for styling while still selecting the item renderer, which is worth a separate look one day.
