---
type: "[[change]]"
id: CHG-20260802-One-Shape-Per-Navigator
title: "All four navigators become a live section plus collapsed cards, and the review desk stops filing changes-requested as finished"
status: merged
reviewed_by: model:claude-opus-5
review_date: 2026-08-02
review_verdict: approved
date: 2026-08-02
owner: user:edwin
component: [static, desktop-renderer]
related: ["[[PHASE-022-Completed-Work-Gets-Quieter]]", "[[FEAT-0058-One-Shape-Per-Navigator]]", "[[FEAT-0057-The-Record-Grammar]]"]
---

# One shape per navigator

## What changed for anyone using the cockpit

Every navigator now reads the same way — live work above, finished work as collapsed cards you open when you want them.

| view | now |
|---|---|
| **Tasks** | no divider. `Done · 265`, `Cancelled · 2`, `Superseded · 2` sit shut in place; live buckets open above them |
| **Issues** | `Completed · 4` divider, then a shut card per severity; open risks above |
| **Features** | `Completed · 16` divider, then every finished phase — open one for its features, open a feature for its requirements and plan |
| **Review** | `Changes requested · 10` with the live work; `Completed · 2` last, holding `approved · 70` and `accepted · 2` |

## The rule behind it

A completed **divider** is needed only where a group's own name does not already say it is finished.

`Done`, `Cancelled` and `Superseded` say it, so the tasks view gets no divider — a heading reading "Completed" above them would be the word four times over. A phase title and a severity say nothing about state, so those views need one. Three view-by-view requests turned out to be one principle.

## The review desk

It was never missing a completed section — `Reviewed · 82` already was one. What the numbers showed is that **10 of those 82 were `changes-requested`**: a reviewer asked for work, and nothing recorded it having happened.

That is a terminal-looking label on an open obligation — the exact error the old Hide-completed switch made, still live on the one surface whose job is tracking obligations. Those ten now sit with the live work.

`rejected` is treated the same way. `accepted` and `approved` are both read as finished; reconciling the two is [[ISS-0069]]'s problem.

## Paths

- `desktop/src/renderer/renderer.ts` — `groupNamesStateThemselves`, `isOwedVerdict`, settled groups open shut, `buildReviewedRegister` rewritten
- `src/project_os_cockpit/static/cockpit.js` — the same rules, hand-written
- both stylesheets — `.review-completed`

## Restart required

Mode 3 is a built bundle. The change is live after the desktop app restarts.
