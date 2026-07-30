---
type: "[[issue]]"
id: ISS-0068
aliases: ["ISS-0068"]
title: "The overview's Waiting-on-you list re-lists items that are already on the page as phase squares — it exists because the squares cannot say anything needs a human, and most of its rows duplicate a mode that owns them"
status: fixed
phase: "[[PHASE-012-Attention-In-The-Strip]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["conversation 2026-07-30, following the PHASE-010 review"]
severity: medium
component: overview
related: ["[[DES-0004-Attention-In-The-Squares]]", "[[TASK-0200-Overview-Stage-Rework]]", "[[TASK-0210-Overview-Announce-Rows]]", "[[REQ-0022-Overview-State-Above-History]]", "[[DES-0001-Overview-Redesign]]", "[[ISS-0064-Two-Reviewed-Sections]]"]
tests: []
---

# Waiting on you is a workaround

## Problem

Two findings, and the second is the one that matters.

**It duplicates surfaces that own its rows.** Measured against Edwin's own hide-completed setting on 2026-07-30:

| Row type | Owning surface | Overlap |
|---|---|---|
| Review-queue rows (`decide`/`review`/`answer`/`run`) | the desk, `~review` | verbatim; the mode button already badges the count |
| Issues at `open` / `triage` | Issues mode | **exact** — 6 issue rows in the mode, the same 6 in the list |
| Tasks `deferred` / `parked` | Tasks mode has a literal `Deferred` group | exact |
| Tests `failing` / `ready` | the desk's test register, the Verification card | exact |

**It exists because the phase squares are under-expressive.** All 9 rows the list showed **already had a square on the page** — 384 squares, 8 of the 9 visible — and every one rendered `data-bucket="backlog"`, pixel-identical to work nobody has started. The squares carry two visual states (filled `done`, hollow everything else) plus type colour, so `blocked`, `triage`, `open`, `review`, `deferred` and `backlog` are indistinguishable. Status lives only in the `title` tooltip, which a tablet cannot reach.

So the list is not a second view of the data. It is prose compensating for an encoding that cannot carry one bit.

## Repro

Open the overview. Read *Waiting on you*, then look for the same ids in the phase strip above it.

## Evidence

```
Waiting on you · 9
  ISS-0024 open · ISS-0066 open · ISS-0037 triage · ISS-0055 triage
  ISS-0057 triage · ISS-0067 open · FEAT-0018 review
  TASK-0045 parked · TASK-0065 parked

squares on page: 384        distinct buckets: backlog | in_progress | done
all 9 present as squares:   9/9      visible: 8/9   (ISS-0024 in a collapsed phase)
every attention square:     bucket="backlog"

Issues mode, hideCompleted on:  6 issue rows   ← the same 6
Tasks mode groups:             Doing, Deferred ← parked work has a home
review queue total:            0               ← the queue half is empty today
```

## Expected

The phase strip says which items need a human; the list is gone.

## Next Actions

- [ ] Review [[DES-0004]] and record a verdict. The encoding is settled (dot / strike / slit / pulse / inverted fill) and the artifact frames at 1:1; what needs judging is whether 9px carries the signal without turning 384 calm squares into noise
- [ ] Mark collapsed phase headers with a count, or the change **loses** information (`ISS-0024`'s square is on the page and not visible)
- [ ] Mark "all items done, phase not closed" on the phase header — the one row nothing else on the page can tell you
- [ ] Decide the `review` row type: nothing owns "in review too long"
- [ ] Then delete `buildWaitingOnYou`, `collectAttention`, `appendAsyncWaitingRows`, `buildWaitingRow`, and the `.ov-waiting*` CSS

## Rejected alternative: counts and pointers

The first proposal was to keep the section but reduce it to an indication — *"3 open issues →"*, *"2 deferred →"*. Rejected, because **the stat tiles two sections above already are that indication**: the Issues tile shows `open /total` and navigates to Issues, and the Tasks tile navigates to Tasks with its mix bar carrying the deferred share. A counts row would have been a third rendering of the same number, one section below the second — the exact pattern [[ISS-0064]] was filed for, and the third instance of it in two days after Library's duplicate groups and the two `Reviewed` headings.

Two gaps in that indication are worth fixing **in the tiles** rather than by adding a panel: `triage` is not distinguishable from `open`, and there is no deferred count, only a mix-bar segment.

## What this supersedes, and it is a design reversal

Not a bug fix, and it should not be committed as one.

- [[TASK-0200]] delivered the Waiting-on-you list.
- [[TASK-0210]] delivered the announce rows that put the desk's queue into it.
- [[DES-0001]]'s plate 5 specified it by name — *"Waiting on you — audited composition. Only states the corpus actually holds: the open issue, the unclosed phase, a 6-week in-review stall, a test defined but never executed, parked work, open risks."*

That composition was right for a page whose squares said nothing. Deleting it is a reversal of a design decision, and both tasks should be marked superseded rather than quietly emptied.

## Notes

Also worth deciding: `deferred`/`parked` should arguably never have been in a list called *Waiting on you*, independent of where else it appears. `STATUSES.md` defines `deferred` as "explicitly out of the current parent's scope, still wanted later" — someone already made the decision, so it is the one row type that is **not** blocked on a human. It sits at rank 5, last, which reads as though the original design half-knew.

One incidental finding while allocating this design's ID: `SNAPSHOT.yaml` has **no `DES` counter**, though `DES-0001`..`DES-0004` exist and the upstream template ships `DES: 0`. Nothing guards design ID allocation here and the validator does not notice. Added with this change; the gap is worth a look upstream.

## Fixed 2026-07-30 — PHASE-012

[[DES-0004]] accepted by Edwin, then implemented. The section is **deleted**, not emptied.

### The payload was half the work

The encoding could not have been done in CSS: three of the six states had no data behind them.

- **`state`** added to every phase item — `delivered` / `dropped` / `deferred` / `doing` / `unproven` / `null`. `bucket` is untouched, because the mix bars and progress fractions read it.
- **`attn`** added, composing with any state — required, since `STATUSES.md` allows blocked-while-doing.
- **Tests joined the strip.** They were absent entirely (features/tasks/requirements/issues only), so a `ready` test had no square to carry its dot. 20 of 22 have a `phase:`. Risks still cannot join and a guard asserts they have not: none carry a phase, so admitting them would dump all four under Unphased.
- **`blocked` is computed from `depends:`**, never a status — the retired code checked `status === 'blocked'`, which no note carries and which the vocabulary forbids.
- **Phase-header aggregates** `waiting` and `unclosed`.

Live counts after implementation: 406 squares — 354 delivered, 22 unproven, 6 dropped, 2 deferred, 2 doing, 20 not-started, 3 carrying the dot, and three `1 waiting` pills.

### Two corrections made while implementing

**The staleness threshold.** DES-0004 cited "9 manual tests last verified 66–83 days ago" as motivating *unproven*. That used a 30-day threshold **I had invented**; the project's is `DEFAULT_STALENESS_DAYS = 90`, configurable via `SNAPSHOT.yaml verification.staleness_days`, and at 90 **no test is stale** — the validator emits zero `TEST-STALE` warnings. So `unproven`'s population is the 22 waived items alone. The implementation reads the validator's number and config key rather than a second rule, because a parallel staleness vocabulary is exactly [[ISS-0024]] and [[ISS-0069]]. Corrected in DES-0004 and [[PHASE-011]].

**`unclosed` was wrong on its first cut.** It computed from the task/feature buckets, which exclude issues, and reported PHASE-011 as closeable while ISS-0057 was open in it. It now requires every item — including issues, requirements and tests — to be `delivered`, `unproven` or `dropped`. `deferred` deliberately does **not** resolve, so the marker agrees with the PHASE-CHILDREN gate rather than inventing a looser one. Guarded by `test_unclosed_agrees_with_the_validators_gate`.

### Deleted

`buildWaitingOnYou`, `collectAttention`, `appendAsyncWaitingRows`, `buildWaitingRow`, `interface AttentionRow`, `SEVERITY_RANK`, and 12 `.ov-waiting*` CSS blocks. Gone with them: the dedup pass that existed only because a `ready` manual test was both a durable state and a queue entry and two appenders listed it twice, and the dead blocked branch.

[[TASK-0200]] and [[TASK-0210]] are marked `superseded` with `superseded_by` pointing here — the reversal reads as one rather than as a cleanup.

### Guarded

Six assertions in `tests/test_surface_ownership.py`: every state reachable against the live corpus; tests in the strip and risks not; blocked computed not read; the staleness threshold equal to the validator's; the retired helpers absent from source *and* stylesheet; the header pills present; and `unclosed` never looser than PHASE-CHILDREN.

One of those guards was itself wrong first: it matched the bare name `AttentionRow`, which is a substring of the live and unrelated `buildAttentionRow` (the agent attention panel). It now matches declarations, and additionally asserts that neighbour survived.
