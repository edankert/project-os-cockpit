---
type: "[[change]]"
id: CHG-20260803-Names-Not-Labels
title: "Phase names read as names rather than labels, task cards drop a pill that repeated their title, and the overview's completed card contains the phases it counts"
status: merged
reviewed_by: model:claude-opus-5
review_date: 2026-08-03
review_verdict: approved
date: 2026-08-03
owner: user:edwin
component: [server, static, desktop-renderer]
related: ["[[PHASE-022-Completed-Work-Gets-Quieter]]", "[[ISS-0089-A-Card-Head-Names-A-Category-Not-A-Thing]]"]
---

# Names, not labels

## What changed

- **Phase heads read as names** — 12.5px, sentence case, full text colour, with the ID type-coloured. They were 11px uppercase grey, the treatment the context pane uses for category labels.
- **Phases are no longer individually framed.** Eighteen boxes became a list with a hairline between rows. Categories stay framed; things do not.
- **Task cards lost their pill.** A card called `Done` does not need a `done` pill.
- **The issues view has two named sets** — `Open · 4` above, `Completed · 3` below.
- **The overview's completed card contains its phases.** The frame was on the heading button, with the 22 rows outside it.
- **The design view is one list.** The `Design system` section held a single note and split three designs across two headings for a `role:` field the reader never asked about.

## The reasoning, once

The right pane's card head names a **category** — `TASKS`, `FEATURES`. The features navigator's head names a **thing** — `PHASE-007 · Agent instrumentation`.

A category is scaffolding you read past, so faint and small is right and a frame around each of four reads as structure. A thing's name is the content: the same treatment hides what you opened the pane to find, and eighteen frames around eighteen things read as clutter.

Four rounds were spent making the two match.

## And a rule that now serves three uses

The pill was got wrong twice in opposite directions — first suppressed by a condition whose output looked random, then made unconditional. Neither extreme was right. The question is **whether the name already says it**, which is the same question that decides whether a view gets a completed divider and whether a head repeats its status in its summary.

## Restart required

Mode 3 is a built bundle, and the design view's grouping is served by the per-workspace Python sidecar — both pick the change up when the app restarts.
