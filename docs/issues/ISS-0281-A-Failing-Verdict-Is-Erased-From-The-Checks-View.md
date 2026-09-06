---
type: "[[issue]]"
id: ISS-0281
aliases: ["ISS-0281"]
title: "A fail, blocked or question verdict is erased from `~checks` — with no platform named, `apply_ledger` keeps only verdicts that clear on every platform, so three of Edwin's own verdicts in your-trainer read as never walked with no comment"
status: fixed
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-09-06
updated: 2026-09-06
source: ["Edwin, 2026-09-06, after walking v2.1.x's suite in ../your-trainer"]
severity: high
component: server
parent: ""
related: ["[[SUR-0001-The-Tests-View]]", "[[FEAT-0135-Everything-Downstream-Is-A-Query]]", "[[FEAT-0136-The-Cockpit-Reads-And-Writes-The-Ledger]]", "[[DES-0012-Tests-In-Two-Flows]]", "[[ISS-0282-The-Mark-Dialog-Hides-The-Check-It-Marks]]", "[[ISS-0280-The-Checks-Page-Does-Not-Survive-Leaving-The-Project]]"]
tests: []
---

# A failing verdict is erased from the checks view

## Problem

A check Edwin marked `fail` yesterday shows on `~checks` as never walked, with no comment. The ledger holds the verdict and its reason; the page drops both before the row is built. Any verdict that does not clear (`fail`, `blocked`, `question`) is affected. Verdicts that do clear (`pass`, `excused`, `na`, `partial`) reach the row, but the row shows only the current verdict's reason, in an 11px faint meta line, and no surface anywhere shows a check's earlier comments.

> [!quote] As reported — 2026-09-06 (user:edwin)
> I cannot see any comments added to the acceptance tests not the ones which are still open and also not on the closed/completed ones.

## Repro

1. Open `../your-trainer` in the shell. It has one ledger, `docs/releases/ledgers/WORKING-android.json`.
2. Open the Tests view and go to `~checks`.
3. Find TST-0434, TST-0603 or TST-0360.

## Expected

TST-0434 shows `fail`, dated 2026-09-06, with its reason: "This does not work at the moment, on pro removing all the riders results in not being able to add any rider!". TST-0603 shows `fail` (2026-09-05). TST-0360 shows `question` (2026-09-05).

## Actual

All three rows show `todo` and no comment. The counts on the page agree with the rows and disagree with the ledger:

| source | pass | excused | na | partial | fail | question | todo |
|---|---|---|---|---|---|---|---|
| `ledger.verdicts(docs, "android")` | 584 | 15 | 6 | 2 | 2 | 1 | — |
| `acceptance.view_payload` (no platform) | 582 | 15 | 6 | 2 | 0 | 0 | 19 |

### After the fix, same day

The two rows agree on every mark. Re-run against `../your-trainer` after `apply_ledger` stopped dropping non-clearing verdicts:

| source | pass | excused | na | partial | fail | question | todo |
|---|---|---|---|---|---|---|---|
| `ledger.verdicts(docs, "android")` | 586 | 17 | 6 | 2 | 0 | 0 | — |
| `acceptance.view_payload` (no platform) | 584 | 17 | 6 | 2 | 0 | 0 | 15 |

Edwin walked the suite while this was being fixed, so `fail` and `question` are both 0 by the time of the re-run — the three verdicts named above have since been re-marked. The property is held by `test_a_verdict_that_does_not_clear_survives_the_platform_less_view` instead of by the corpus, which is the right place for it.

**The residual 2 is not this defect and is not a drop.** `TST-0015` and `TST-0647` have verdicts in the acceptance ledger and their notes live in `docs/tests/`, not `docs/tests/acceptance/` — they are system-wide tests, so they are not in the walkable suite and never were. 611 resolved verdicts, 2 of them naming something outside the suite, leaves 609 rows carrying one, and 624 − 609 = 15 `todo`. Whether a run should be writing acceptance-ledger entries for a non-acceptance test is a separate question and is not filed here.

## Cause (diagnosed by the main session, 2026-09-06)

`acceptance.apply_ledger` (`src/project_os_cockpit/acceptance.py:1096`) has two branches. With a platform named it uses that platform's resolved verdicts. With no platform named it intersects every platform's ledger and keeps a verdict only `if all(v.clears)`. A non-clearing verdict is dropped entirely, so the check falls to `mark: todo` and `verdict_reason` becomes `""`.

`renderChecksPage` always takes the second branch: it fetches `/api/cockpit/acceptance` with no platform parameter.

That branch is [[DES-0012]] D4's release-gate rule (a release that names no platform takes them all, and a check clears only where every platform clears; [[TASK-0534]]). It is the right rule for *does this check clear the gate*. The walk page asks a different question, *what did the last person record on this check*, and reusing the gate's join answers it with silence.

## What is settled and what is not

Settled: a verdict that does not clear must reach the row with its mark, its date and its reason. For a single-ledger repo, which your-trainer is, there is only one answer to show.

Open, for Edwin: what the no-platform page shows for a check that fails on one platform and passes on another. The two readings lead to different code. Showing the *worst* verdict (fail beats pass) keeps the gate unchanged, since a non-clearing verdict already does not clear, and it repairs the display in one place. Making `~checks` always name a platform (the platform picker exists) removes the intersect from the page entirely, but changes what the page is. The first reading is the one the wording most directly supports and is the assumption the fix should record.

Impact analysis: [[REQ-0054]] (absence is the initial state) and [[REQ-0055]] (no surface reads a verdict from a note) are not touched by either reading; the verdict still comes from the ledger, and a check with no entry still falls to `todo`. The gate query in [[FEAT-0135]] must not weaken: a fail on any platform still blocks. No conflict found.

## The history half

The ledger is append-only and keeps every event on a check. `acceptance.view_payload` carries only the current verdict's `verdict_reason`, and `buildCheckRow` renders it in `.checks-row-meta`. So the "closed/completed" half of Edwin's report is not loss but reach: nothing shows the earlier comments. The payload should carry the check's history (mark, date, author, reason per event) so the row and the mark dialog ([[ISS-0282]]) can show it.

## A second cut on the row, the same day

Promoting the reason to its own quoted line was right for the 99 comments a person wrote and wrong for the 512 the migration wrote. The backfill put an identical paragraph on every check it moved — *"Backfilled from `mark: done`. The verdict predates the ledger…"* — so the first cut quoted it under 379 of 436 visible rows, which is the opposite of making a comment visible. Seen on the live page before it shipped, not reasoned about.

`_row` now carries `verdict_method`, and the row quotes a reason only when a person or a run recorded it. The count in the meta line already excluded the backfill, and so did the dialog's list; the row was the one surface that did not.

## Sibling search

No sibling found on the cause (searched `docs/issues/` for `apply_ledger`, `all(v.clears)`, `intersect`, `no platform`, `verdict_reason`). The nearest family is the rendering of clearing marks ([[ISS-0211]], [[ISS-0244]]), which is a different defect.

## Risk scan

No trigger applies: no new dependency, env var, path or contract. The API payload gains fields; it loses none.

## Next Actions

- [x] `apply_ledger` with no platform keeps a non-clearing verdict (worst wins) instead of dropping it; guard with a test that builds a ledger holding one `fail` and asserts the payload row carries `fail` and its reason.
- [x] The payload carries each check's verdict history; the row shows the current reason and reaches the earlier ones.
- [x] Re-measure the table above on your-trainer after the fix; the two rows must agree.
- [x] Update `docs/reference/cockpit-capability-register.md` in the change-note commit (the payload gains capability: history per check).
