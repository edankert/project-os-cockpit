---
type: "[[feature]]"
id: FEAT-0056
aliases: ["FEAT-0056"]
title: "Open work sorts first, long lists fold, and the context pane never filters — so a corpus that is 99% complete reads without a switch that empties it"
status: done
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
source: ["Edwin 2026-08-02: 'we should instead hide/collapse these completed items, allowing us to see them conditionally instead of not making them visible at all using the hard visible or not switch'", "Edwin 2026-08-02, correcting my first review: 'tasks are ordered in the left on status and the completed statuses are at the end'"]
goal: "Make completed work quiet rather than absent: one comparator that sorts open before done, groups that sort by whether they still contain open work, a fold keyed on length, and a context pane that orders by state but never removes by it."
requirements: []
tasks:
  - "[[TASK-0267-One-Comparator-Open-Before-Done]]"
  - "[[TASK-0268-Groups-With-Open-Work-Sort-First]]"
  - "[[TASK-0269-The-Context-Pane-Stops-Filtering]]"
  - "[[TASK-0270-Folding-Keyed-On-Length]]"
release: ""
related: ["[[DES-0004-Attention-In-The-Squares]]", "[[FEAT-0043-Overview-Rework]]", "[[ISS-0023-Status-Vocabulary-Drift]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
reviewed_by: model:claude-opus-5
review_date: 2026-08-02
review_verdict: changes-requested
review_round: 2
---

# Completed work ordering

## Goal

At **99% lifecycle completion** (tasks 99%, features 98%, issues/changes/requirements 100%; 90% across all note types), `Hide completed` is not a filter but a demolition — 1 of 18 feature groups survives, 0 of the 4 issue severity buckets, and the context pane of a finished note empties entirely. Replace it with ordering, and fold only what is genuinely long.

## The rule the whole feature encodes

**Fold on volume, never on meaning.**

A done task under its feature is what the feature is made of. A done task in a list of 261 is something you scroll past. Same status, different job — so the response differs by *pane*, not by status:

| pane | what state does | what length does |
|---|---|---|
| **Left** — a selection list | orders groups *and* items; the done tail folds | — |
| **Right** — a description | orders items only | folds long groups, regardless of state |

## Why each view needs something different

Each groups on a different axis, and **state is orthogonal to all three** — which is precisely why a global switch got invented instead of ordering:

| view | groups by | ordering today | what it needs |
|---|---|---|---|
| Tasks | status | **already correct** — completed statuses last | nothing; it has a *volume* problem (270 rows, 261 in one bucket) |
| Issues | severity | wrong — a fixed `high` outranks an open `low` | open-first within each bucket |
| Features | phase order | wrong — phase 1 (done) above phase 22 (active) | groups with open work first |
| Context pane | note **type** | n/a | order by state, never filter |

Edwin's correction is load-bearing: I had called the tasks view the worst case. It is the one view whose ordering is already right. I saw 270 rows and diagnosed ordering when the problem was length.

## Scope

Four tasks, each shippable alone: [[TASK-0267]] the comparator, [[TASK-0268]] group ordering, [[TASK-0269]] the context pane, [[TASK-0270]] the fold.

## Out of Scope

- **The status vocabulary.** `statuses.COMPLETED_STATUSES` already defines terminal ([[ISS-0023]]); this feature consumes it and does not extend it.
- **Removing the switch.** It becomes a collapse control rather than a hide control; users who want the terse view keep it.

## Independent review — round 2, 2026-08-02 (model:claude-opus-5, fresh context, separate session)

**Verdict: changes-requested.**

### Round 1, for the record

The first pass (same day, same model pin, different session) returned `changes-requested` with ten findings and its full text is in git history for this file. What it cost: the right pane's length fold had to be built on both surfaces, `_phase_group_rank` replaced a two-band sort, the guard suite roughly doubled (12 → 26 Python cases plus a node-driven harness for mode 1), and two exit criteria were rewritten because their evidence expired at close-out. That was a productive round and most of it holds.

### Method

Fresh context: I started from `git status`, the diff, and the notes, and have no memory of authoring any of it. I did not read the round-1 findings until after reading the code. Refutation was by mutation — 20 source mutations across `cockpit.py`, `static/cockpit.js` and `completed-work.ts`, each applied, built where needed, run against the full suites and reverted — plus an independent re-derivation of every number from the live corpus rather than from the notes.

Suites, run from a clean tree: `pytest tests/ -q` → **684 passed, 1 skipped**; `node --test desktop/tests/*.test.mjs` → **61 passed**; `validate-docs.sh` → **OK** (19 pre-existing `[REVIEW]` warnings, none of them this work's).

### Round-1 findings: what actually got fixed

| # | claim | verdict |
|---|---|---|
| F1 | right pane folds on length, both surfaces | **fixed in code**, not in every note — see N4 |
| F2 | mode 1 has guards that fail | **fixed** — 6 of 7 mutations to `cockpit.js` fail the suite (the 7th, N3) |
| F3 | comparator call sites guarded | **fixed** — `_open_first`, `_features_groups`, `_settled_last`, `_phase_group_rank`, `_phase_target`, `open_first_key`, `_group_is_settled` all fail when mutated, including the two the adversarial fixture was built for |
| F4 | ISS-0082 guard detects ISS-0082 | **fixed** — re-introducing `phase: "[[PHASE-016-Errors-Become-Work]]"` fails `test_the_dangling_link_guard_can_actually_fail`. Caveat N6 |
| F5 | mode 3 orders children open-first | **fixed** — `renderItemChildren` calls `openFirst`. The dead `renderRightPane(ctxCache)` on mode 1's toggle (`cockpit.js:1176`) is still there |
| F6 | PHASE-999 pen; expiring evidence | **mostly fixed** — three bands, and both criteria now cite non-expiring assertions. But N1 |
| F7 | numbers checkable | **partly** — the whole before/after table now reproduces exactly; seven figures still do not. See N4 |
| F8 | fold invariant at 0 / negative / non-finite / null | **fixed in code on both surfaces, guarded on only one** — N2 |
| F9 | TASK-0270 DoD wording | **fixed** ("first **completed** item") |
| F10 | traceability | **fixed** — TST-0023 links from FEAT-0056, all four tasks and ISS-0082; the CHG carries the review fields |

Numbers I re-derived that **do** check out: tasks 5 groups / 270 items, sizes 261/3/2/2/2; issues 7 groups (4 issue + 3 risk) / 86 items, sizes 52/18/11/2/1/1/1; features 18 groups / 56 items; the before/after table in [[PHASE-022]] and the CHG in **every cell** (tasks 2/5 → 5/8, features 1/1 → 18/18, issues 3/4 → 7/8, FEAT-0051 0 → 9, ISS-0080 0 → 5); "four groups over 12, twenty-six whole"; the 79-item group is `PHASE-007`'s **backlinks** task group, and 79 is the corpus maximum; 98.7% reproduces as 98.75% over `{task, change, issue, feature, requirement, test, risk}`.

### N1 — `_phase_group_rank` ranks a `deferred` phase as *in flight* (medium)

`deferred` is one of the five statuses `STATUSES.md` allows a phase (`planned`, `active`, `done`, `deferred`, `superseded`). It sits in the `reference` band, which the function does not enumerate, so it falls through to the `phase_record is not None` arm and returns **0 — in flight**:

```
planned  → 1   active → 0   done → 2   superseded → 2   deferred → 0
```

A deferred phase therefore ties with the active one and, having the lower `order`, sorts **above** it — the exact failure mode the three-band rework was built to prevent, reintroduced for a different status. The comment on that arm ("its status is outside the vocabulary") also misdescribes it: `deferred` is in the vocabulary. `test_the_backlog_pen_does_not_outrank_the_phase_in_flight` enumerates four of the five legal phase statuses and omits this one.

### N2 — the context pane's "never filters by state" rule has no guard on either surface (high)

This is the feature's headline change ([[TASK-0269]], "the smallest change and the largest fix"), and [[TST-0023]] lists *"the context pane never filtering by state"* under **What it covers**. It is not covered.

Mutation, applied to **both** surfaces at once — `renderContextGroup` → `foldGroup(items, CONTEXT_GROUP_FOLD_LIMIT, hideCompleted)` and `renderRightPane`'s two calls → `foldGroup(g.linked, NAV_GROUP_FOLD_LIMIT, hideCompleted)` — rebuilt, then: **684 pytest passed, 61 node passed.** Restoring the exact behaviour the feature exists to remove is invisible to the entire suite. `grep -rn "renderContextGroup\|hideCompleted\|CONTEXT_GROUP_FOLD_LIMIT\|isItemHidden" desktop/tests/ tests/` returns nothing.

This is round 1's F3 in a different place: the pure helper is guarded, the decision at the call site is not. The fix shape already exists in this repo — the source-grep assertion used by `nothing pushes except a person clicking` — and would cost one assertion per surface.

### N3 — mode 3's F8 hardening is unguarded, and the two surfaces' invariant tests are inverted (medium)

Both edge-case fixes in `completed-work.ts` can be deleted with the suite green:

- delete `const cap = Number.isFinite(limit) ? Math.max(0, …)` → `const cap = limit` → **61 node tests pass**
- delete `if (!items) return []` → **61 node tests pass**

The node invariant test still sweeps limits `[1, 8, 12, 1000]` and shapes that never include `null`/`undefined` — i.e. exactly the inputs the fix was not about. The mode-1 twin, guarded from Python, sweeps `[-1, 0, 1, 8, 12, 1000]`. So the surface that owns the canonical implementation is the one whose hardening is untested, and mode 1's own null-tolerance is likewise unguarded (removing `|| []` from `openFirst` leaves 51 passed). Both are one line in an existing loop.

### N4 — retracted numbers survive in the places a session actually reads (medium)

`SNAPSHOT.yaml` is the canonical machine-readable context (LIFECYCLE.md), and it carries **all four** retracted claims, uncorrected:

| line | text |
|---|---|
| `focus.note` | "91% of this corpus is complete", "0 of 5 severity buckets", "I saw 264 rows" |
| `FEAT-0056.note` | "At 91% complete a state filter is not a filter" |
| `TASK-0268.note` | "0 of 5 severity buckets" |
| `TASK-0269.note` | "the largest group measured anywhere is 11 items, so there is no wall to scroll past" |

That last one is the sentence F1 asked to delete or implement, still present verbatim in the file every session opens first.

`renderer.ts:7767-7772` is worse than uncorrected — it *asserts* the refuted claim ("the largest group measured anywhere in the corpus is 11 items. There is no wall to scroll past.") and then retracts it eight lines later at 7777. A comment that argues both sides in one block tells the next reader nothing. The correction was appended rather than applied.

Figures that still do not reproduce:

| claim | where | measured |
|---|---|---|
| "11 of 3192 context groups exceed it" | renderer.ts ×3, cockpit.js, PHASE-022, TASK-0269, CHG | **11 of 3266** (per direction, templates excluded); 19 of 3309 with templates; 14 of 2875 merged by type. None is 18/3217 |
| "requirements 96%" | PHASE-022 | **100%** — 22 `implemented` + 3 `retired` of 25, and no requirement is touched by this diff, so it is not a before-state figure either |
| "then ten 1s" | renderer.ts:2597, cockpit.js:305 | **nine** 1s (19/10/5/3/2/2/2/2/2 + 1×9 = 56 ✓) |
| "12 cases" in the node block | TST-0023 | **11** |
| "91% complete" | renderer.ts:7765, fleet-health.test.mjs:990/1023, test_completed_work_ordering.py:3 | PHASE-022 line 32 says this figure "was neither figure… corrected at review" — the correction did not reach the two test files or the renderer |
| "`test` 96%" | renderer.ts:7771 | **100%** (23/23) |
| "0 of 5 severity buckets" / "264" | test_completed_work_ordering.py module docstring | 4 buckets; 270 rows — both already corrected elsewhere |
| "87.8% across every note type" | PHASE-022, FEAT-0056 | reproduces only as 600/684 = **87.7%**, whose denominator is every note including templates and statusless ones. 93.6% over statused non-template notes |

The pattern is consistent: the notes under `docs/` were corrected and the code comments, the test docstrings and the snapshot were not. Half a correction is worse than none, because a later reader finds two figures and no way to tell which pass produced which.

### N5 — mode 3's context-pane fold row is unstyled (low, user-visible)

`renderer.css` scopes both new rules under `.ws-nav-content`:

```css
.ws-nav-content .nav-item.nav-more { … }
.ws-nav-content .nav-more-btn { … }
```

The context pane mounts in `#right-pane-content`, not `.ws-nav-content`, and `renderContextGroup` emits the same `li.nav-item.nav-more` / `button.nav-more-btn`. There is no other `nav-more` rule in the file, so the right pane's `… N more` renders as a default UA button — system font, grey chrome, centred — inside `.right-pane-group`. Mode 1's equivalent rules are unscoped and do cover both panes, so the two surfaces disagree on exactly the row this round added.

### N6 — the new dangling-link guard rejects the link form LIFECYCLE.md prefers (low)

`test_the_dangling_link_guard_can_actually_fail` requires the raw `phase:` text to equal a phase note's **filename stem**. `LIFECYCLE.md` says *"Prefer `[[PHASE-####]]` links where first-class phase notes exist."* Setting FEAT-0051 to `phase: "[[PHASE-016]]"` — which `_phase_target` and `_resolve_phase` handle correctly and which `validate-docs.sh` passes — fails the guard as a stale slug. The guard also does not strip a `#heading` anchor. It will fire on a correct change; the note it lives beside should say the corpus convention is full slugs, or the guard should accept a bare ID that resolves.

### N7 — smaller things

- `renderer.ts:7437` — *"Neither can return nothing: `foldGroup` always yields at least one row for a non-empty group"*. False, and made false by this same commit: a fully settled group under `collapse` cuts to **zero** rows, which `completed-work.ts`'s own docstring and PHASE-022's close-out both state as the deliberate change. Stale comment from the pre-rework version.
- [[TASK-0268]]'s first DoD bullet still reads *"A group sorts on `(has no open work, natural axis)` — so PHASE-022 (active) precedes PHASE-001 (done)"*. Features now sort on the three-band `_phase_group_rank`, and PHASE-022 is `done`. The Notes section explains the change; the DoD was not updated to match — the same defect F9 filed against TASK-0270.
- Removing `_settled_last` from the **risk** buckets leaves the suite green (every risk is open, and the adversarial fixture has no risks). Cheap to close in the fixture.
- `test_the_phase_in_flight_leads_the_features_navigator` recomputes the rank with `[]` for `records`, where production passes the group's records. It catches today's mutations (verified), but it never exercises the unresolvable-phase fallback that the `records` argument exists for.
- `cockpit.js:302-311` — two comment headers are stacked with no separator, the first (`// The fold's own row. The count is never optional…`) belonging to `appendMoreRow`, which is now the *second* function below it.
- `CHG-20260802-Completed-Work-Collapses` carries `review_verdict: changes-requested` while `status: merged`. That is honest about round 1 but is now the record of a superseded pass.

### What I checked and found correct

`appendCtxMoreRow`'s `list.replaceChild(frag, li)` is right: the DOM replace algorithm expands a `DocumentFragment` in place, `li` is a child of `list`, and `openFirst(allItems).slice(folded.head.length)` is exactly the withheld remainder in the same order — so the revealed rows land between the linked run and the divider rather than at the end of the list, which is why it must not use `replaceChildren` the way `appendMoreRow` does. The split between the two helpers is justified. `foldGroup`'s head/hidden arithmetic is correct on both surfaces at every input I tried. `renderNavGroup` / `renderSubgroup` / `renderContextGroup` return `null` only for genuinely empty groups. `dist/` is current with `src/` and `tsc --noEmit` is clean.

### Independence

Fresh context, separate session, no memory of authoring this. **Same model family as the author** (`model:claude-opus-5`), recorded in `reviewed_by` — per [[project-os-dev#ADR-0013]] that is provenance, not the gate; what makes this pass independent is that it started from the notes and the diff. Round 1 was also `model:claude-opus-5` from a third session, so a reader should treat the model as held constant across all three and the context as the only variable.
