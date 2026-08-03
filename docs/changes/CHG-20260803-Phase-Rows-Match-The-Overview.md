---
type: "[[change]]"
id: CHG-20260803-Phase-Rows-Match-The-Overview
title: "Phase rows in the features navigator measure the same as the overview's scope rows, and a plan lines up with its sibling requirements"
status: merged
reviewed_by: model:claude-opus-5
review_date: 2026-08-03
review_verdict: approved
date: 2026-08-03
owner: user:edwin
component: [static, desktop-renderer]
related: ["[[PHASE-022-Completed-Work-Gets-Quieter]]", "[[ISS-0090-Phase-Rows-And-The-Missing-Id-Column]]"]
---

# Phase rows match the overview

## What changed

A phase row in the features navigator is now the overview's scope row on every axis — 24px, weight 400, `--text-muted`, 7px gap — with `✓ 3` where the overview says `✓ 8`, and **no status pill**. The pill was the word a third time: the summary beside it already said `done`, and the band it sits in is headed `Completed`.

A plan nested under a feature lines up with the requirements it sits among. It was **78px** adrift.

## Why the plan was adrift

`_plan_child_item` sets `"id": ""` deliberately — an untyped plan still gets a row. The renderer drew the id span only when there was an id, so the plan's *title* took the id column's place.

It now renders its **type** as the handle — `PLAN`, type-coloured like any other id, at slightly lower opacity. That is what an id is for a note with no number of its own.

## Paths

- `desktop/src/renderer/renderer.ts` — the `✓ N` trailing form, the pill condition, the id-column placeholder
- `src/project_os_cockpit/static/cockpit.js` — the same, hand-written
- both stylesheets — `.nav-group-header.is-thing`, `.nav-id.is-typeless`, the nested id column's width

## Restart required

Mode 3 is a built bundle. The change is live after the desktop app restarts.
