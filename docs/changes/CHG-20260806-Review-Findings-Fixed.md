---
type: "[[change]]"
id: CHG-20260806-Review-Findings-Fixed
aliases: ["CHG-20260806-Review-Findings-Fixed"]
title: "The seven review findings fixed: an API-error placeholder stops being a turn, the corrected figures become a command, and a relationship declared on one end is now checked on both"
status: merged
owner: user:edwin
created: 2026-08-06
updated: 2026-08-06
source: ["review:independent"]
commit: ""
pr: ""
impacts: ["src/project_os_cockpit/session_cache.py", "src/project_os_cockpit/validate_docs_bundled.py", "tools/scripts/validate-docs.py", "tools/scripts/scan-cache-economics.py", "tools/GRANDFATHERED.yaml", "desktop/src/renderer/cache-temperature.ts", "desktop/src/renderer/renderer.ts", "desktop/src/renderer/renderer.css", "desktop/src/renderer/validation-rows.ts"]
issues: ["ISS-0106", "ISS-0107", "ISS-0108", "ISS-0109", "ISS-0110", "ISS-0111", "ISS-0112"]
features: ["FEAT-0081"]
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[FEAT-0081-What-A-Session-Costs-To-Keep-Alive]]", "[[CHG-20260806-Session-Cache-Economics]]", "[[CHG-20260806-Cold-Sessions-Read-Grey]]"]
---

# The seven review findings fixed

## Summary

The independent review of the two 2026-08-06 commits returned `changes-requested` with seven findings. All seven are fixed. The review's own numbers were confirmed rather than taken on trust — 33 `<synthetic>` entries, the `_read_tail` mutant surviving all 26 tests, `$336/$6,731 = 5.0%`, FEAT-0081 absent from its own commit.

**The correctness defect (ISS-0106, high).** Claude Code writes an assistant entry with `model: "<synthetic>"` and all-zero usage when a request fails. The reader took all 33 as real turns, so a placeholder became the *previous* turn — a retry seconds after a reset made a 151-hour idle gap read as 52 seconds and filed it as a model switch. Rejection is now on the **shape of the data** (no tokens consumed) as well as the sentinel, so a future placeholder under another name cannot reintroduce it. Both filters are guarded, by a case only each can catch.

**The figures (ISS-0111).** Two of the seven quoted numbers had *fallen* on re-derivation, which counts of past events cannot do — proof they came from throwaway logic that never shipped. `tools/scripts/scan-cache-economics.py` now produces them from the shipped module, so notes and product cannot diverge again. Corrected everywhere: **8 model switches of 14 sub-hour re-writes**, not 11 of 17. And "staleness" now means one thing — TTL expiry, **3.7%** of input-side spend — with all avoidable re-writes named separately at **4.9%**. The old sentence defined staleness as the larger figure and quoted the ratio of the smaller.

**The guards (ISS-0109, ISS-0110).** Eleven mutants that survived now die, including `_read_tail`'s seek — the test counts bytes off the disk rather than asserting the answer came out right. On the renderer side the judgment moved out of the DOM: `railKey`, `attentionIds` and `cacheBadge` join `cacheTemperature` in the plain-script module the node suite can evaluate, so deleting ISS-0105's behaviour now turns the suite red. No jsdom; the standing decision against a JS test framework holds.

**The badge (ISS-0107, ISS-0108).** A model switch was derived from the last turn and never decayed, so `warm`/`cooling`/`cold` never rendered again for the life of that transcript and a warm session was painted in the alarm colour. The announcement now expires on the same clock the temperature uses, and the colour always follows the real temperature — a fresh switch gets its own. A turn with no usable timestamp yields no badge at all, instead of `cold` with an age of 56 years.

**The note, and the gate that could not see it (ISS-0112).** FEAT-0081 was `done` while listing three of five tasks, none of the issues it fixed, and no acceptance criteria for half its delivered behaviour. It now carries all of it. The generalisable half is a new validator check.

## Impact

- **New:** `PARENT-BACKLINK` — a task or issue declaring `parent: FEAT-X` must be named back by that feature in `tasks:` / `fixes:` / `issues:`. Deliberately narrow: a check that accepted any mention (`related:` counts) would pass the drift it exists to catch, and there is a test asserting exactly that.
- **New:** `tools/scripts/scan-cache-economics.py`, and a note in FEAT-0081 that `/api/cockpit/session-cache` answers the same question for **one workspace** — a reader could otherwise mistake one for the other.
- **Changed:** `session_cache.py` — placeholder rejection, timestampless guard, `MODEL_SWITCH_NOTICE_SECONDS`.
- **Changed:** `cache-temperature.ts` gains `railKey` / `attentionIds` / `cacheBadge`; the three call sites and the strip renderer became adapters.
- **Ledgered:** 69 pre-existing `PARENT-BACKLINK` violations in `tools/GRANDFATHERED.yaml`. New drift errors; standing debt warns. Each entry is a small backlog item and the ledger only shrinks.

## Documentation Coverage (All Types Considered)

- features: updated — FEAT-0081 gains its second surface, both rounds of tasks, all nine fixed issues, and six new acceptance criteria
- requirements: not-applicable
- tasks: new — TASK-0348 … TASK-0353
- issues: [[ISS-0106]] … [[ISS-0112]] all `fixed`
- tests: new — `tests/test_parent_backlink.py` (7); `tests/test_session_cache.py` 19 → 39; `desktop/tests/cache-temperature.test.mjs` 9 → 19. Every new guard was verified by re-running the mutation it exists to catch.
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: this note; figures corrected in both earlier notes
- snapshot: updated — counters, items, statuses

## What this round did not fix

- **A re-review is owed.** The verdict on record for FEAT-0081 and both earlier change notes is still `changes-requested`. Per `independent-review/SKILL.md` step 5 the loop closes with a *re*-review, not with the author declaring the findings fixed — so FEAT-0081 stays `doing` and PHASE-007 stays `active`.
- **69 grandfathered backlink violations** remain as warnings.
- The DOM adapters themselves are still unguarded — a much smaller surface than before, but not zero.
- `CACHE_TTL_MS` still duplicates `TTL_1H` with nothing detecting drift.

## Follow-ups

- [ ] Re-review, then close FEAT-0081 and PHASE-007 on the new verdict.
- [ ] Work down the grandfathered `PARENT-BACKLINK` ledger.
- [ ] Propose `PARENT-BACKLINK` upstream to project-os — the drift it catches is not specific to this repo.
