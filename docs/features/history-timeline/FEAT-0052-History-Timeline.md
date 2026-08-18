---
type: "[[feature]]"
id: FEAT-0052
aliases: ["FEAT-0052"]
title: "History — document state changes as the rows, commits as dividers"
status: done
phase: "[[PHASE-016-The-Overview-Answers-Questions]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["Edwin 2026-07-30: 'the goal is to understand what was fixed/implemented when (commits are important but only from a document level point of view)'"]
goal: "One History surface whose rows are note status transitions and whose commits are dividers marking what is saved, replacing the overview's three separate history tiles."
requirements: []
tasks:
  - "[[TASK-0255-History-Payload]]"
  - "[[TASK-0256-History-Tile-On-The-Overview]]"
  - "[[TASK-0257-Full-History-View]]"
release: ""
related: ["[[FEAT-0048-Changes-On-The-Overview]]", "[[TASK-0199-Commits-As-Documentation-Events]]"]

---

# History

## Goal

Answer *"what was fixed or implemented, and when"* without reading a git log.

Rows are **status transitions** — `TASK-0253 → done`, `ISS-0072 → fixed`. Commits are **dividers**: a thin line saying what that commit contained, with everything above the first one being work not yet saved.

## Brief plan

1. **[[TASK-0255]]** — `history_payload`: one `git log -U0 -- docs/` yields every `+status:` line with the commit that carried it; plus `git status --porcelain` for the uncommitted band. Both cheap, both already-used techniques in this codebase.
2. **[[TASK-0256]]** — one **History** tile on the overview replacing Activity, Changes and Commits. Short — the last few days — with the sparkline folded into its header and a link to the full view.
3. **[[TASK-0257]]** — the full view at `~history`.

## Acceptance

- The overview has one History tile; Activity, Changes and Commits are gone as separate tiles.
- A commit whose notes changed status shows those transitions and no others: the phase-hygiene commit renders **4** rows, not the 20 notes it touched.
- Uncommitted work appears above the first divider, marked as not yet saved.
- A commit touching no notes still appears, flagged — it does not vanish for having no rows.
- The tile links to `~history`, which shows the same thing further back.

## Scope

- In: the payload, the overview tile, the full view.
- Out: removing commits entirely (the boundary is the point); per-line diffs (the unit is a note); changing `commits_payload`, which stays and still answers "what did this commit contain".


## Done 2026-07-30

All five acceptance criteria verified against the running app.

- **One History tile; the other three gone** — `document.querySelectorAll('.ov-tile h3')` returns exactly `["History"]`, and a guard asserts the three builders are absent.
- **Transitions, not touches** — `cebee80` touched 20 notes and renders **4** rows.
- **Uncommitted work above the first divider**, marked *"not committed yet · 3 files"*.
- **A commit touching no notes still appears** — 7 flagged across the 60-commit view.
- **`~history` exists and the tile links to it** — clicking `Full history ›` lands there.

## What this changed about the overview

The history band was three tiles answering one question three ways, and each made git or the filesystem the subject. It is now one tile whose rows are documents and whose commits are punctuation.

The sparkline survived as a header strip rather than dying with Activity: *how busy* is useful context above a list of events and useless as a competing answer beside one.

## Owed

- **Day grouping on `~history`** — in [[TASK-0257]]'s DoD, deliberately not built. At this density the dividers already carry dates and a third level of structure earns nothing. Marked `[~]` rather than ticked.
- **Mode 1 (the browser client) still has the old tiles.** Unchanged and not in scope; the endpoint is renderer-agnostic, so porting is additive — the same shape of debt [[FEAT-0018]] carried for its badge, and worth not forgetting twice.
