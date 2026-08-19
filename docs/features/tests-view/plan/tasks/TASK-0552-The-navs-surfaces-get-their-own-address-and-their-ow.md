---
type: "[[task]]"
id: TASK-0552
aliases: ["TASK-0552"]
title: "The nav's surfaces get their own address and their own children"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0128-The-Tests-View-Leads-With-The-Work]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# [[ISS-0227]]

See the issue for the reasoning and the suggested fix; its `Done when` is this task's definition of done.

## Done 2026-08-19

`_surface_rows` gives each surface `~checks/tier/{n}/area/{slug}` and its own `items`. The slug is derived from free text and a rename breaks a bookmark — stated in `_area_slug` rather than discovered, with [[FEAT-0130]] named as the eventual fix. Children are collapsed by default and the toggle says how many.
