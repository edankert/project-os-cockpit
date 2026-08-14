---
type: "[[change]]"
id: CHG-20260814-The-Review-Findings
title: "What three independent reviews found, and what it cost to check"
status: merged
owner: user:edwin
created: 2026-08-14
updated: 2026-08-14
source: ["Edwin 2026-08-14: 'simply remove it from the session configuration and continue the independent review cycle' → three parallel independent-reviewer passes, all returning changes-requested"]
commit: ""
pr: ""
impacts: ["dismissals survive a restart", "an unknown publication count is no longer reported as zero", "two new validator warnings gain promotion dates", "328 lines of unreachable renderer code removed"]
issues: ["[[ISS-0165-The-Attention-Card-Reads-A-Second-Git-Walk]]"]
features: ["[[FEAT-0100-Unpushed-Work-Needs-A-Person]]"]
related: ["[[CHG-20260814-The-Upstream-Batch]]", "[[CHG-20260813-Four-Bugs-From-The-Suggested-List]]", "[[CHG-20260813-Every-Automated-Test-Says-How-To-Run-Itself]]", "[[project-os-dev#ADR-0011]]", "[[project-os-dev#ADR-0013]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]"]
---

# What three independent reviews found

## Summary

Three reviews, run in parallel from clean context against [[FEAT-0100]] and three change notes. **All three returned `changes-requested`.** The code was mostly right; what failed was the record's account of it, plus one defect that broke the feature's stated purpose.

## The one a user would have noticed

**Dismissals never survived a restart.** `pruneDismissedAlerts` is reached from a module-level `refreshAttention()` that paints the last-known state before discovery runs, so `workspaces` was `[]` and every restored key failed `workspaces.some(...)`. The store was read back and wiped on the same tick.

Edwin's requirement was *"this should be preserved across application start-ups"*, and [[TASK-0420]]'s Definition of Done asked for exactly this to be **"asserted rather than assumed."** The box was never ticked, no test existed, and the task was `done`.

## Claims that were false

| claim | fact |
|---|---|
| "no repo's verdict changes" | `your-health` **FAIL → OK**. The check looked only for repos that started failing. |
| the `ready` fix was lost "three weeks later" | **three days** — 2026-08-01 to 2026-08-04. |
| the patch protected `DECISION-RULE` | it has never existed here; `DESIGN-GATE` and `ACCEPT-STALE` did and went unnamed. 149 lines, not 146. |
| "1 of 24 test notes could be executed" | true of `run-tests.py` only. **`entrypoint:` is a template field the release skill reads, and six notes carried a runnable command in it.** |
| 54 citations / 38 files / six ids | **53 / 41 / five**. |
| "four occurrences deliberately left bare" | eight, and `ADR-0024` — named as one — contains none. |
| ISS-0139 removed 57 lines of dead code | 50, and the removal was **incomplete**. |

## The rule I cited while breaking it

`TEST-ENTRYPOINT` and `STATUS-TYPE` shipped as **undated** warnings under a comment reading *"A warning with a promotion date, per ADR-0011."* [[project-os-dev#ADR-0011]]'s decision is that a check with no cutover is promoted or deleted — the permanent-warning tier it exists to forbid. Both now route through `promotion_emit` with a **2026-11-12** cutover, verified to warn today and error the day after.

## A guard is not a guard until its mutation fails

Two evidence rows claimed mutations that no longer failed:

- `count(...) >= 2` against three occurrences — ISS-0161 added a third, so deleting the one the row names left two behind.
- `len(bare) == 2` where one match was **a comment**, so a real bare call could be added while a comment was deleted.

**My first repair of the first one was also too loose**: it searched the whole remainder of the function and accepted the *backlog replay's* check as the *attach's*. Caught by re-running the mutation rather than by reading the fix.

## Dead code, and why the compiler could not see it

The review named two orphaned functions from [[ISS-0139]]. The reachability check written to guard their removal found **nine more** — a chain rooted in the pre-[[PHASE-008]] overview, each calling the next, so `noUnusedLocals` saw only functions in use. **328 lines**, confirmed unreachable by `tsc`.

## An assertion that punished honest review

`test_every_row_of_the_rehoming_table_is_reachable` asserted the corpus holds **zero** outstanding `changes-requested`. True of the data when written, placed where a rule goes — so the first honest verdict recorded against this repo broke the suite. [[ISS-0120]]'s class, in the file where that lesson was learned. It now asserts the property those rows are for: an owed verdict is reachable from the view owning its type, and a terminal note does not owe one.

## Behaviour that changed

- A ✕ on an attention card survives a relaunch.
- A repo with a remote but no upstream now says **"No upstream set — nothing can say what is unpublished"**, with no push button, on the History band; the badge counts it; the digest sees it.
- Two validator warnings become errors on 2026-11-12 rather than never.
- Nothing about what may write, what may push, or what is refused.

## Documentation Coverage (All Types Considered)

- features: [[FEAT-0100]] out of `done` → `review`
- requirements: not-applicable
- tasks: not-applicable — three carry unticked DoD boxes and that is recorded on FEAT-0100, not resolved here
- issues: new ([[ISS-0165]])
- tests: not-applicable
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new; three earlier notes corrected and moved `draft` → `merged`
- snapshot: updated

## Evidence

| guard | mutation | result |
|---|---|---|
| `attention-dismissal.test.mjs` (4 cases) | the empty-fleet guard is removed | 1 of 4 fails, the one describing the defect |
| `test_the_terminal_attach_cannot_replay_a_stale_backlog` | delete the check after `terminal.attach` | fails |
| `test_every_terminal_attach_restores_the_keyboard` | bare call added, comment deleted | fails |
| `test_the_renderer_has_no_unreachable_top_level_function` | a mutually-recursive dead pair | fails |
| `test_an_unknown_publication_count_is_not_reported_as_zero` | unknown collapses back to zero | fails |
| ADR-0011 cutover | `_today()` moved to 2026-11-13 | both gates return `error` |

## Follow-ups

- [ ] [[ISS-0165]] — the attention card's second git walk.
- [ ] FEAT-0100's 27 unticked DoD boxes, before it returns to `done`.
- [ ] `CHG` is absent from `ID_PREFIXES`, so change notes never enter `note_index` and their `status:` is validated by nothing — four carried `draft`, which is outside `{merged, reverted}`. Upstream.
