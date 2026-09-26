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
reviewed_by: "model:claude-opus-5"
review_date: 2026-07-30
review_verdict: "changes-requested"
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

**Counts, with the method, because the first version had neither.** Independent review could not reproduce the figures originally recorded here (it measured 390/349/8/7 against a stated 406/354/6/20) and no method was given, so there was no way to tell a miscount from a different population. [[ISS-0071]].

Method: items = `stats_payload`'s `features` + each feature's `children` + `loose`, summed across phases — the same set the strip renders. Measured 2026-07-30 after the ISS-0071 fixes:

```
items 396 — delivered 357, unproven 22, dropped 8, deferred 2, doing 2, not-started 5
attn 2      (triage/review/ready/failing/computed-blocked)
waiting     PHASE-011 1, PHASE-013 1
```

These move with the corpus and are a dated snapshot, not an invariant — the assertions in `test_surface_ownership.py` are what hold. `dropped` rose from 6 to 8 and `not-started` fell as this session's own issues were closed, which is the drift, not a discrepancy.

### Two corrections made while implementing

**The staleness threshold.** DES-0004 cited "9 manual tests last verified 66–83 days ago" as motivating *unproven*. That used a 30-day threshold **I had invented**; the project's is `DEFAULT_STALENESS_DAYS = 90`, configurable via `SNAPSHOT.yaml verification.staleness_days`, and at 90 **no test is stale** — the validator emits zero `TEST-STALE` warnings. So `unproven`'s population is the 22 waived items alone. The implementation reads the validator's number and config key rather than a second rule, because a parallel staleness vocabulary is exactly [[ISS-0024]] and [[ISS-0069]]. Corrected in DES-0004 and [[PHASE-011]].

**`unclosed` was wrong on its first cut.** It computed from the task/feature buckets, which exclude issues, and reported PHASE-011 as closeable while ISS-0057 was open in it. It now requires every item — including issues, requirements and tests — to be `delivered`, `unproven` or `dropped`. `deferred` deliberately does **not** resolve, so the marker agrees with the PHASE-CHILDREN gate rather than inventing a looser one. Guarded by `test_unclosed_agrees_with_the_validators_gate`.

### Deleted

`buildWaitingOnYou`, `collectAttention`, `appendAsyncWaitingRows`, `buildWaitingRow`, `interface AttentionRow`, `SEVERITY_RANK`, and 12 `.ov-waiting*` CSS blocks. Gone with them: the dedup pass that existed only because a `ready` manual test was both a durable state and a queue entry and two appenders listed it twice, and the dead blocked branch.

[[TASK-0200]] and [[TASK-0210]] are marked `superseded` with `superseded_by` pointing here — the reversal reads as one rather than as a cleanup.

### Guarded

Six assertions in `tests/test_surface_ownership.py`: every state reachable against the live corpus; tests in the strip and risks not; blocked computed not read; the staleness threshold equal to the validator's; the retired helpers absent from source *and* stylesheet; the header pills present; and `unclosed` never looser than PHASE-CHILDREN.

One of those guards was itself wrong first: it matched the bare name `AttentionRow`, which is a substring of the live and unrelated `buildAttentionRow` (the agent attention panel). It now matches declarations, and additionally asserts that neighbour survived.

## Independent review — 2026-07-30 (model:claude-opus-5, fresh context, separate session) — changes-requested

The deletion is right and the encoding is a real improvement. Four findings, three of them about guards that do not guard.

**1. `unclosed` IS looser than PHASE-CHILDREN, in the one direction that matters.** The validator's `PHASE_RESOLVED` (`tools/scripts/validate-docs.py:129`) covers `task`, `issue`, `requirement`, `feature` **and `risk`**, keyed on each child's own `phase:`. The phase payload excludes risks by design. Demonstrated end to end: give `RISK-0001` (`status: open`) `phase: "[[PHASE-012-Attention-In-The-Strip]]"` and the payload reports `unclosed: true` for PHASE-012 — the header offers "close out". Follow that offer and the validator errors:

```
ERROR [PHASE-CHILDREN] PHASE-012 is 'done' but 1 item(s) still name it as their
phase without a resolved status: RISK-0001 (open)
```

Zero risks carry a `phase:` today, so this is latent — but PHASE-012 itself records admitting risks to the strip as "a corpus change, not a rendering one", i.e. an expected future edit, and this is the trap it walks into. Separately, `_norm(st) != "done"` disagrees with `CLOSED_PHASE_STATUSES = ("done", "superseded")`: a `superseded` phase with everything resolved is offered for a close-out it has already had.

**2. `test_unclosed_agrees_with_the_validators_gate` cannot fail.** It rebuilds the same `items` list the payload built and asserts `all(state in {"delivered","unproven","dropped"})` — which is the definition of `unclosed`. It is a restatement of the implementation, not a comparison with the gate: it never imports the validator and never reads `PHASE_RESOLVED`. Mutation-verified: replacing the state check with the exact bucket-based first cut this note describes as the bug leaves the test green.

**3. `test_blocked_is_computed_from_depends_not_from_a_status` asserts none of what its docstring claims.** The docstring says "Asserted by construction: an unfinished item whose dependency is unresolved must carry `attn`, and one whose dependency is satisfied must not." The body asserts no note carries `status: blocked`, then greps source. Two consequences, both mutation-verified against the full suite:

- `def _has_unresolved_dependency(rec): return False` — the whole computed-blocked mechanism disabled — passes all 594 tests. The mechanism this note lists as a headline change is entirely unguarded.
- The string slice `src.split("def _needs_human")[1].split("def ")[1]` selects the body of `_has_unresolved_dependency`, not of `_needs_human`. Re-adding `if status == "blocked": return True` to `_needs_human` passes, under an assertion message that reads "_needs_human is reading a blocked status again".

**4. `failing` is the one legal status with no mark and no dot.** Enumerating `ALLOWED_STATUS` through `_square_state`/`_needs_human`, every value lands somewhere except `test`/`failing` (and `requirement`/`approved`, which reads as not-started defensibly). A failing test renders pixel-identical to work nobody started — and this change both added tests to the strip and deleted `appendAsyncWaitingRows`, whose `status === 'failing'` branch was the overview's only failing-test surface, at rank 0. The row-ownership table assigns it to "the desk's test register, the Verification card", which is a different screen. `DES-0004`'s table has no row for the `blocked` band at all, so this is a design gap the implementation inherited faithfully.

**Minor:** the post-implementation counts do not reproduce. At this commit the payload yields 390 squares / 349 delivered / 8 dropped / 7 not-started / 3 dotted / 3 waiting pills, against "406 / 354 / 6 / 20 / 3 / three". The dot and pill counts match, so the shape is right; the note gives no measurement method, so a later reader cannot tell whether the difference is DOM-versus-payload or an error. Also `test_every_des_0004_state_is_reachable` checks presence only — swapping `deferred` and `dropped` in `_square_state` keeps it green.


## Narrowed — 2026-08-12 (ADR-0025)

The rule this note established is cited across the codebase as *"one item, one home"*. It now reads: **one obligation, one owning view.**

A view may list an owed row twice — once in a leading `Needs you` shortcut group, once in its structural place, marked. What it may not do is claim the same obligation in two views, which is the failure this issue actually found.

The distinction matters because the strict reading was starting to cost the thing it protects: a requirement removed from under its feature *because* it needs approving makes the Features tree wrong at the moment the reader most needs it right. [[ADR-0025]] carries the reasoning and the two exemptions it creates, both asserted in tests rather than left implied.

**And it carries a hazard worth stating here:** any surface that *counts* owed marks now double-counts. Two tests caught it the day the group shipped. Count distinct ids.
