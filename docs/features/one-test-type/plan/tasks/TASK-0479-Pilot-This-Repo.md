---
type: "[[task]]"
id: TASK-0479
aliases: ["TASK-0479"]
title: "Pilot: this repo's 34 checks, with the gate and the view walked afterwards"
status: done
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0119-The-Merge-Migration]]"]
parent: "[[FEAT-0119-The-Merge-Migration]]"
effort: M
depends: ["[[TASK-0478-Renumber-Into-The-TST-Space]]", "[[TASK-0488-Drop-The-Feature-Tests-Field-And-The-Path-Fallback]]"]
blocks: []
related: []
tests: []
---

# Pilot: this repo

34 checks, 0 blocking, all settled — the smallest suite in the fleet and the one whose corpus this session knows best. Migrate, assert parity through the reader, then **walk the surfaces**: the Tests navigator groups, the `~checks` page, the release gate, the sweep, and the Publication view's acceptance subgroup.

**The badge is the first thing to check, not the last** — [[REQ-0037-The-Badge-Never-Admits-Acceptance-Tests]]. This repo's Tests badge reads 1 on 2026-08-18. If it reads 35 afterwards, stop and do not proceed to the fleet.

Done when: parity green, badge unchanged at 1, the gate still reports 0 blocking, and every acceptance surface renders from the merged notes.

## Done

34 notes migrated, and **parity held on all six dimensions through the reader**: 34 notes, `{x: 33, /: 1}`, tiers unchanged, `covers:` targets unchanged, 0 blocking, titles identical.

**The badge was checked first, not last** ([[REQ-0037-The-Badge-Never-Admits-Acceptance-Tests]]): `obligations.owed_items` returns **3** tests owed — `TST-0024`, `TST-0029`, `TST-0030`, the same three manual notes that were `ready` before the migration. **Zero of the 34 reached it.** The construction holds: they rest at `active`, and the `Run` obligation is keyed on `ready`.

**Three collisions [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] did not name, all found by running it rather than reading it:**

1. **`TEST-FIELDS` demands `last_verified:` on a manual test** — 34 errors the moment the notes became tests. An acceptance test records when it was walked in `verdict_date:`, beside the `mark:` that says what the walk found; writing the same fact into both fields is the duplication this phase removes. `verdict_date:` now satisfies the rule at `level: acceptance`. **The ADR's five collisions were all about gates keyed on a STATUS; this one is keyed on a FIELD, and no amount of resting at `active` avoids it.**
2. **`_tests_groups` rendered all 34 twice** — once in a `Verified` bucket and once under a tier. Free before the merge, because `notes_by_type("test")` could not see a check; now the exclusion has to be written down. Caught by the ISS-0068 guard, which is exactly what it was written for.
3. **Six navigator and view assertions separated the two populations by TYPE.** Each now separates them by `level:`, which is the honest translation — and one of them, `test_the_view_holds_the_whole_test_corpus`, would have passed either way while quietly describing a different corpus.
