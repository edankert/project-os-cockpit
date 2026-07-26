---
type: "[[issue]]"
id: ISS-0027
aliases: ["ISS-0027"]
title: "Stat-tile mix bars don't span the tile on Features/Tasks/Issues — those tiles are buttons, and the UA stylesheet centres their flex children"
status: fixed
severity: low
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
component: ui
source: ["user-report:2026-07-26"]
related: []
tests: []
---

# Stat-tile mix bars are narrow on the clickable tiles

## Problem

In the overview stat strip, the coloured status mix bar runs the full width of the **Reqs**, **Tests** and **Risks** tiles, but is narrower than the tile on **Features**, **Tasks** and **Issues**.

## Cause

`buildStatTile()` takes an optional `navMode`. When present the tile is created as a `<button>` (so clicking switches nav mode); otherwise it is a `<div>`:

```ts
const tile = document.createElement(navMode ? 'button' : 'div');
```

Exactly the three tiles that look wrong are the three that pass a `navMode` — `features`, `tasks`, `issues`.

`.ov-stat` is `display: flex; flex-direction: column`. Chromium's UA stylesheet sets `align-items: center` on `<button>`. In a **column** flex container the cross axis is horizontal, so that centring makes children shrink to their content width instead of stretching. `.ov-mixbar` is itself a flex row of segments, so it collapses to the width of its segments rather than filling the tile.

The `<div>` tiles inherit the CSS default `align-items: normal` (stretch), which is why they look right.

## Repro

Open the overview. Compare the bar under **Features** with the bar under **Tests**.

## Expected

All six tiles render an identical full-width mix bar; whether a tile happens to be clickable is not a visual distinction.

## Fix

One declaration — `align-items: stretch` on `.ov-stat`, so the rule does not depend on which element the tile was built from. The other button resets (`font`, `color`, `text-align`) are already present, which is why this was the only symptom left.

## Resolution (2026-07-26)

`align-items: stretch` added to `.ov-stat`, with the UA-stylesheet reason in a comment so the next person does not "tidy" it away. All six tiles now render an identical full-width mix bar regardless of whether they were built as a `<button>` or a `<div>`.

Desktop bundle rebuilt; suite green (306 passed, 1 skipped).
