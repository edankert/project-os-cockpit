---
type: "[[plan]]"
title: "Plan — git assist"
status: active
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
implements: ["[[FEAT-0055-Git-Assist]]"]
related: ["[[PHASE-021-Git-Is-Not-The-Users-Job]]"]
---

# Plan

1. **[[TASK-0264]]** — the commit. Independent of the other two, and the half that removes a chore rather than exposing one.
2. **[[TASK-0265]]** — the payload and the surface. Depends on nothing; extends [[FEAT-0028]]'s existing path.
3. **[[TASK-0266]]** — the action. Depends on 0265 for somewhere to put it.

## Two rules that are not negotiable

**Never `git add -A`.** Measured 2026-07-30: `your-trainer` 44 dirty files, `your-health` 8, none of them the work in hand. A commit that sweeps those in is worse than no automation.

**Remote classification, not configuration.** `your-applications.com`'s only remote is a server path — pushing deploys a site. This must be decided from the remote URL, not from a setting someone can get wrong.

## What to watch

**Do not build a second health surface.** [[FEAT-0028]]'s badge and roll-up already answer "what is the state of this repo". Unpushed commits are the same question. A separate "git status" panel would be the duplication [[PHASE-016]] was created by undoing.
