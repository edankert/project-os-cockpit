---
type: "[[issue]]"
id: ISS-0270
aliases: ["ISS-0270"]
title: "A release page still offers cancelled and superseded features, and two issues a commit said it filed were never written"
status: open
owner: user:edwin
reported_by: review
created: 2026-08-30
updated: "2026-09-19"
severity: medium
component: docs
phase:
source: ["Independent review of 46d6593..c861414, 2026-08-30, model:claude-opus-5, fresh context"]
related: ["[[ISS-0265-A-Retired-Check-Still-Gates-The-Release]]", "[[TASK-0591-Retiring-Removes-The-Obligation]]", "[[ISS-0262-Marking-A-Check-Clears-The-Filter-You-Are-Walking]]", "[[ISS-0261-A-Release-Is-Offered-Features-Its-Platform-Cannot-Ship]]", "[[ISS-0264-A-Write-Is-Not-Readable-By-The-Next-Request]]", "[[ISS-0113-SNAPSHOT-Still-Quotes-The-Retracted-Figures]]"]
tests: []
---

# Two promised issues were never filed, and one of them is a live defect

A release page still offers features whose status is `cancelled` or `superseded`, as if they were done and waiting to ship. ISS-0261 said this was filed separately, and it was not. ISS-0264 made the same promise about the other write endpoints: a tick, a status change or a new note can still read back as unchanged for about 50 ms after the save answers. Four published figures (the blocking count 104/103 and the 623-row suite) are also wrong, in two notes, a source comment and a test docstring.

## How this was recomputed

`../your-trainer` is a live corpus that moved twice on 2026-08-30 while this work was being written, so a comparison against it today proves nothing either way. Every figure below is recomputed against `git archive fb99a751` — the last `your-trainer` commit (15:55) before these two cockpit commits (15:56, 15:57) — materialised into a scratch tree and read with the code at `46d6593` (pre-fix) and at `c861414` (post-fix). That is the corpus the author was looking at.

## 1. The gate

| | measured |
|---|---|
| suite items, pre-fix | **625** |
| blocking, pre-fix | **101** (`TST-0075` among them) |
| suite items, post-fix | **624** |
| blocking, post-fix | **100** |

Published:

- [[ISS-0265]] body: *"went on BLOCKING the release — 104 blocking, `TST-0075` among them."*
- `src/project_os_cockpit/acceptance.py`, the `_is_retired` comment: *"still in the `unclear` filter and still in the blocking 104."*
- `tests/test_checks_view.py`, `test_a_retired_check_does_not_block_the_release`: *"still in the blocking 104."*
- [[TASK-0591]] table: *"gate total 103 → 100."*

The **after** figure is right. The **before** figure is published as two different numbers in four places and is neither of them. The table also fails on its own arithmetic without any corpus at all: exactly one check was retired, so the gate cannot fall by three.

## 2. `623 rows`

ISS-0262 says *"put the whole 623-row suite back after every single tick"*, and the same figure is now a source comment in `renderChecksPage`. The suite the reader would have been shown was **625** rows before the retire and **624** after. Low consequence, but it is now in two places, one of them code.

## 3. `303 of 1,432`

The census itself reproduces almost exactly, against the same commit and excluding `__templates__`: 1,432 total ✓, `android` 818 ✓, `cross` 15 ✓, `web` 12 ✓, `marketing` 10 ✓, `all` 3 ✓, `docs` 1 ✓, `both` 1 ✓, and **`shared` 0 ✓** — the load-bearing claim, exact. Two columns are one out: the empty column is **287**, not 288, and `ios` is **285**, not 284. (288 is the empty count *including* the templates directory, which the other columns exclude.)

`303` is the figure the argument rests on, and it is not a column. ISS-0261 attributes it to *"the empty column alone"*, which is 287; TASK-0587 attributes it to *"`cross`, `all`, `both` and every unset note"*, which is 306. `303` is `288 + 15` — the with-templates empty count plus `cross`, dropping the `all` and `both` the sentence names.

**And the population is not the one the predicate reads.** `_ships_on` is applied only to FEATURE notes in the done-but-unshipped set. The feature-level census at that same commit is 45 `android`, 44 empty, 12 `ios`, 1 `cross` — no `all`, no `both`, 102 features. What equality would have cost on the population that reaches this code is **45 of 102 features**, not 303 of 1,432 notes. The conclusion is unaffected and remains right: 44 unset features is a large enough share that an equality rule would have quietly emptied release pages. The number offered as its evidence measures a different thing, an order of magnitude wider.

## 4. What did reproduce

TASK-0587's *"Effect on `../your-trainer`"* is exact at that corpus state: the derived card holds 13, ten leave (`FEAT-0026`, `0029`–`0036` and `FEAT-0098`, all `platform: ios`), and `FEAT-0037`, `FEAT-0057` and `FEAT-0101` remain, with the stated reasons. `tsc --noEmit` is clean. The 1 ms / 50 ms timings in ISS-0264 were taken on a scratch repo that is not in the tree and were not re-checked.

## 5. Two follow-ups declared filed, and never filed

- ISS-0261: *"`superseded` and `cancelled` satisfy `statuses.is_completed()` … it is filed separately."* No such note exists. The highest issue id in the repo at `c861414` is ISS-0265, and none of ISS-0261..0265 is that issue. This one is load-bearing: TASK-0587's own effect table says `FEAT-0057` *"leaves when `superseded`/`cancelled` stop counting as shippable, which ISS-0261 files separately"*.
- ISS-0264: *"Every other write endpoint has the same shape — `release-contents`, `release-verified`, `release-prepare`, `mark-released`, the status writes. None was reported and none is fixed … Filed rather than swept in."* No such note exists either. Eighteen `POST /api/notes/*` endpoints write; two reindex. (The enumeration is also short: `attach`, `acceptance-run`, `test-run`, `tick-owed`, `seal-ledger`, `create`, `transition`, `tick`, `decide`, `review`, `choose-variant` and `check-toggle` are not in it.)

*"Filed separately"* is a promise a later reader will act on — it is the sentence that makes it safe not to fix something now. Two of them in one commit, neither kept.

## Next Actions

- [ ] Correct the four gate figures to 101 → 100, in all four places including the source comment and the test docstring.
- [ ] Correct `623` in ISS-0262 and in `renderChecksPage`.
- [ ] Restate the census sentence against the population `_ships_on` actually reads, and fix the two ±1 columns.
- [ ] File the two follow-ups, or delete the sentences that say they were filed.

## Checked against the code, 2026-09-19: still true, kept

**What a user notices:** A release prepared in the cockpit lists cancelled or superseded features among "What shipped" candidates. After ticking a box or changing a status, a page that re-reads at once can still show the old value.

Evidence: `statuses.py:67-75` puts `cancelled` and `superseded` in the `archived` band, and `statuses.py:114` makes `COMPLETED_STATUSES` = done band plus archived band. `cockpit.py:2319` (`unreleased_payload`) keeps any feature where `statuses.is_completed()` is true, and `publication.py:1118-1130` offers those rows to a release. `server.py:2563` `_reindex` is called by mark-check, retire-check, release-update, release-abandon and release-settle only; `_serve_note_tick`, `_serve_note_transition`, `_serve_note_create`, `_serve_mark_released`, `_serve_release_contents` and `_serve_check_toggle` have no `_reindex` call (grep over each handler). No issue after ISS-0264 names `is_completed` or a missing reindex (`grep -l is_completed docs/issues/*.md`). The wrong figures are still at `acceptance.py:1041` ("blocking 104"), `tests/test_checks_view.py:627` ("blocking 104"), `desktop/src/renderer/renderer.ts:9940` ("623-row suite"), ISS-0265 line 27 and ISS-0262 line 37.

**Belongs to:** no feature (the release-page half belongs with the release pages, the reindex half with ISS-0264's fix). **Next:** Split into two issues: the cancelled/superseded release candidates (small: `unreleased_payload` should use the done band only, with a test) and the six write endpoints that skip `_reindex` (bigger); correct the four figures in the same commit as either.

Checked as part of project-os-dev FEAT-0036 (TASK-0141).
