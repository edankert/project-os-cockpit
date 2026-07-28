---
type: "[[change]]"
id: CHG-20260728-Plan-Statuses-Under-Closed-Features
aliases: ["CHG-20260728-Plan-Statuses-Under-Closed-Features"]
title: "Nine plans advanced to done: PLAN-FOLLOWS had been dead since ADR-0012 and never reported them"
status: merged
date: 2026-07-28
owner: user:edwin
source: ["upstream:project-os-dev/ISS-0011"]
related: ["[[CHG-20260728-Design-Bench-Close-Out]]"]
---

# Plan statuses under closed features

## Summary

Nine `PLAN.md` notes sat at `active` or `draft` under features that closed months ago. `STATUSES.md` is explicit that a plan's status **follows its parent feature** and is advanced at close-out — so every one of these was stale.

They were not reported because the check that should have caught them was broken. `PLAN-FOLLOWS` maps a feature status to the plan status that tracks it, and its map was keyed on `in-progress` / `in-review` — values retired by project-os `ADR-0012`. `follows.get(parent_status)` returned `None` for every feature at `doing` or `review`, and the guarded `if expected:` skipped silently. The check had never fired since the day it shipped; it was written against the vocabulary the same commit was retiring.

Fixed upstream in `project-os-dev` (`ISS-0011`, `CHG-20260726-Phase-Resolved-Declined`), which re-armed the check and surfaced these nine.

## Plans advanced

All to `done`, matching their parent feature:

| Plan | Was | Feature |
|---|---|---|
| `docs/features/agent-state-signal/plan/PLAN.md` | active | FEAT-0013 |
| `docs/features/cockpit/plan/PLAN.md` | active | FEAT-0006 |
| `docs/features/cockpit-api-hardening/plan/PLAN.md` | active | FEAT-0008 |
| `docs/features/desktop-shell/plan/PLAN.md` | draft | FEAT-0007 |
| `docs/features/native-center-pane/plan/PLAN.md` | active | FEAT-0011 |
| `docs/features/native-nav-right-pane/plan/PLAN.md` | active | FEAT-0010 |
| `docs/features/native-ux/plan/PLAN.md` | active | FEAT-0012 |
| `docs/features/overview-rework/plan/PLAN.md` | draft | FEAT-0040 |
| `docs/features/review-desk/plan/PLAN.md` | draft | FEAT-0041 |

## Why `done` and not `superseded`

`STATUSES.md` gives two terminal outcomes for a plan under a closed feature: `done` if the delivery sequence was carried out, `superseded` if it was replaced. Each plan was checked for evidence of replacement before being advanced:

- No plan carries `superseded_by:`, and no parent feature does either.
- Only one plan mentions supersession at all — `native-nav-right-pane` says "real nav supersedes it" about a panel from FEAT-0011's READMEs. That is the plan describing what its own work replaced, not the plan being replaced.
- A feature cannot reach `done` in project-os while its tasks are unresolved (the `VERIFY` gate reads `RESOLVED_STATUSES` over a feature's `tasks:`). This repo validates clean, so every one of these features closed over a resolved task set — the sequences executed.

`done` on all nine.

## Impact

- Documentation only. No code, no behaviour, no paths.
- `PLAN-FOLLOWS` warnings in this repo: 9 → 0.
- Plans carry no `id:` and are not snapshot items, so `SNAPSHOT.yaml` is unaffected.

## Verification

- `bash tools/scripts/validate-docs.sh` → `OK`.
- Re-run under the upstream validator (which carries the fixed `PLAN-FOLLOWS`): 0 `PLAN-FOLLOWS` warnings, down from 9.

## Follow-ups

- [ ] Sync `tools/scripts/validate-docs.py` from upstream to pick up the fixed `PLAN-FOLLOWS` and the new `STATUS-TABLE` check locally; this repo's copy still carries the dead map, so nothing here would catch the next plan left behind.
