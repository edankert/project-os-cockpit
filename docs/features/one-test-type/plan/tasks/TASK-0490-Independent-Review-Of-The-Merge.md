---
type: "[[task]]"
id: TASK-0490
aliases: ["TASK-0490"]
title: "The independent review of the whole programme, against the corpus rather than against the plan"
status: done
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0119-The-Merge-Migration]]"]
parent: "[[FEAT-0119-The-Merge-Migration]]"
effort: M
depends: ["[[TASK-0485-Backfill-Automation-From-The-Prose]]", "[[TASK-0488-Drop-The-Feature-Tests-Field-And-The-Path-Fallback]]"]
blocks: []
related: []
tests: []
---

# Independent review of the merge

Owed under QUALITY.md: two ADRs, four features reaching `done`, new `TST-*` notes and a `CHG-*`. Clean context, from the notes and the diff — never this session's reasoning ([[project-os-dev#ADR-0013]]).

**Review the result against the corpus, not this plan.** The plan's own figures — 669, 203, 15 of 60, 20 of 61, zero inbound `CHK-*` references, 10 to backfill — are all re-derivable, and the last review of this subject corrected five figures in the note it was reviewing. Re-derive them.

Specific questions worth putting to it: did the badge move in any repo; is the twelve-tag delta on `your-trainer` genuinely unchanged; is there any surviving predicate on the retired type; did the VERIFY inversion change which violations fire; and is [[REQ-0039-A-Covering-Test-Settles-The-Check]] actually satisfied — how many checks were discharged by a covering test, measured, and not how many *could* be.

Done when: a verdict is recorded on the features and on this note, and anything it returns as `changes-requested` is fixed or filed rather than argued with.

## Independent review

`model:claude-opus-5`, 2026-08-18. **Verdict: `changes-requested` on all four features.** Fresh context, separate session, working from the notes and the diff of `3d3ad5b`/`ab5f173` (plus `project-os eb10a45`) — never the author's reasoning trace. What is *not* independent and is recorded rather than inferred: the reviewer is the same model family as the author (`reviewed_by` says so on each note). Per [[project-os-dev#ADR-0013]] context is the gate and family is not, so this satisfies QUALITY.md; a human pass would still be stronger.

Gates run by the reviewer, not taken on trust: `bash tools/scripts/validate-docs.sh` → **OK** (0 errors, 42 warnings). `.venv/bin/pytest tests/ -q` → **1663 passed, 1 skipped** (the notes say 1660/2; the delta is the two navigation guards plus one, and is not a defect).

### Blocking findings

**1. The Tests badge moved: 1 → 3, not "3 both before and after".** [[REQ-0037-The-Badge-Never-Admits-Acceptance-Tests]] criterion 1 is false as measured. Running the pre-merge code against the pre-merge corpus, `obligations.owed_items(index)["tests"]` returns **one** row (`TST-0024`); after the merge it returns **three** (`TST-0024`, `TST-0029`, `TST-0030`). All three were `ready`/`kind: manual` before *and* after — but TST-0029/0030 were **quiet** before, and are owed now.

The cause is a missed rename, not the acceptance notes: `obligations.SUBJECT_FIELDS["test"]` is still `("verifies", "features", "requirements")` and was never given `covers:`. [[ADR-0032-The-Verification-Link-Has-One-Direction]] deleted the first two fields from every test in this repo, so `subject_ids()` now resolves **nothing for 77 of 77 tests** (before: 2 of 43). `subject_is_in_flight` treats a subject-less note as live by design — *"a note naming no subject asks"* — so the in-flight quieting [[FEAT-0101-Obligations-Route-By-The-State-Of-Their-Subject]] exists to provide is **disabled for the entire test population**. Adding `covers` to `SUBJECT_FIELDS` restores the badge to 1. Nothing guards this; `test_obligation_routing.py` was edited in `ab5f173` for the tier groups and does not assert subject routing.

**2. `criteria.debt_payload` still reads the retired `verifies:` field.** `src/project_os_cockpit/criteria.py:281` builds `verified_ids` from `frontmatter.get("verifies")`. 23 tests declared `verifies:` before the migration; **0 do now**. Measured through the module: the acceptance-debt surface's *unverified requirements* count goes **31 → 37**, `unresolved` 8 → 6, `evidence_free` 0 → 2, total 39 → 45. The `covers:` rename was applied in `cockpit._test_feature_ids` and `scope_tests_payload` and missed here.

**3. `tests:` is not gone from the feature.** [[ADR-0032-The-Verification-Link-Has-One-Direction]] decision 2 and [[REQ-0040-One-Verification-Link]] criterion 1 say a feature no longer carries the field. Measured now: **81 of 121 feature notes in this repo still declare `tests:`**, 22 edges are non-empty across 17 features, and `docs/__templates__/feature.md` still ships `tests: []` — upstream removed it in `eb10a45`, the downstream template was never hand-merged, and `sync-project-os.sh --dry-run` reports `feature.md` as `LOCAL-CONTENT` diverged. So the scaffold still creates the field the ADR abolished. "Removed from 30 features and 10 snapshot entries" is literally true as a count of what the commit deleted; "gone from `feature.md`" is not.

**4. FEAT-0117's claim on TST-0043 was not dropped.** `docs/features/acceptance-checks/FEAT-0117-One-View-Per-Item.md:19` still reads `tests: ["[[TST-0043]]"]`, and TST-0043 covers FEAT-0116 only. It is the one surviving unreciprocated edge in this repo, so [[REQ-0040-One-Verification-Link]]'s "zero unreciprocated edges remain… there is no second side to reciprocate" is false on both halves.

**5. `docs/__templates__/SCHEMAS.md` never came down.** [[FEAT-0118-The-Test-Type-Absorbs-The-Check]] lists SCHEMAS.md among the template-owned files that "land upstream and sync down before a single note changes type". It was not in `3d3ad5b`'s staged paths and the sync reports it as `MERGE`-owned and left alone, so this repo's schema of record still documents `tests` on the feature and `features:`/`verifies:` on the test, and does not document `covers:`, `level: acceptance`, or the acceptance field block. `feature.md` is likewise absent from that list although `eb10a45` changed it.

**6. `covered_by:` semantics are wider than every note describing them.** Measured on synthetic notes through `acceptance.load`: (a) with two covering tests, one `passing` and one `failing`, the check is **settled** — `covered_by_passing` is `any(...)`, so a passing cover masks a failing one, while `Item.settled`'s docstring, [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] and [[TASK-0482-Covered-By-Reaches-The-Gate]] all state flatly that a failing cover un-settles; (b) a **manual** `passing` test with no `command:` settles an acceptance row — [[FEAT-0120-The-Automation-Path]] says the link is "refused unless the id resolves to a test carrying a `command:`", but that is the unwritten write path, and the read path applies no constraint. Self-referential and unresolvable `covered_by:` are both safe (they block). Neither (a) nor (b) is guarded.

**7. TASK-0482 is `done` with two of its three "Done when" clauses unmet.** It requires that a failing cover "re-enters [the gate] **naming the test**" and that "the count of checks discharged this way is **reported on the gate** rather than inferred". `covered_by` appears nowhere outside `Item`/`settled` — no facet, no gate line, no renderer site (`grep -rn covered_by src desktop` finds only `sweep.py:346`, which writes `[]`). A check discharged by a covering test simply vanishes from `blocking()` with no explanation, which is the failure the task's own body says must not happen. The stale-cover third state it names is also not implemented.

### Corrected figures

Re-derived across all twelve `SNAPSHOT.yaml`-bearing repos, from note frontmatter (templates and bases excluded), pre-merge state reconstructed from `git archive 4c02731`.

| claim | as written | measured | verdict |
|---|---|---|---|
| 34 migrated, parity on six dimensions | 34 | **34**; items/marks/tiers/`covers` multiset/blocking/titles all identical, bodies byte-identical, only `id`/`type`/`aliases` changed and `level`/`kind`/`merged_from` added | ✅ |
| obligation badge before → after | 3 → 3 | **1 → 3** | ❌ (finding 1) |
| tests carrying `covers:` | 43 | **43** non-acceptance test notes (77 including the 34 acceptance) | ✅ |
| `tests:` removed from features / snapshot entries | 30 / 10 | **30 / 10** removed — but **81 features still carry the field**, 22 edges live | ⚠️ |
| tests resolving by path alone, fleet-wide | 3 | **3** (`TST-0017`, `TST-0018`, `TST-0019`, all here, all now carrying `covers:`) | ✅ |
| unreciprocated feature→test edges in this repo | 8, 7 resolved in the feature's favour | **8**, and **7** in the feature's favour (TST-0011 now covers nine features, TST-0023 three) | ✅ |
| unreciprocated edges fleet-wide | 20 (8 here, 10 `your-health`, 2 `project-os-dev`) | **8**, all in this repo. `your-health` has 9 feature→test edges and **all 9 are reciprocated**; `project-os-dev` has 2 and **both are reciprocated** | ❌ |
| feature→test edges fleet-wide | 61 (ADR-0032) / 62 (REQ-0040, SCHEMAS.md) | **61** (60 in notes, 61 unioned with snapshot entries) | ADR ✅, REQ/SCHEMAS off by one |
| `tests:` edges on task/issue/requirement | 330 | **259** (138 task + 74 requirement + 47 issue). 281 including `change` and `phase`; 314 including the 33 surviving feature edges. 330 is not reproducible under any definition tried | ❌ |
| tests declaring no feature / 3 path / 7 by feature edge / 25 by neither | 35 / 3 / 7 / 25 | **14 / 3 / 0 / 11** on the most natural reading (`features`+`verifies`+`validates`). Only the 3 reproduces | ❌ |
| tests fleet-wide / naming >1 feature | 117 / 20 | **116 / 24** | ⚠️ |
| VERIFY findings across twelve repos | 56 → 57 | **4 → 5** | ❌ base, ✅ delta |
| `your-trainer` errors | 599 → 600 | **599 → 600** | ✅ |
| `your-trainer` prose automation annotations | 203 | **203** only as the intersection of "says automat\*" **and** "names a `*Test` class". The sentence's own reading ("name their covering test") measures **260**; the union measures **282**; band 181–286 | ⚠️ strictest reading |
| blocking checks in `your-trainer` that say a machine covers them | 15 of 60 | **16 of 60** (60 blocking confirmed: tier 1 = 41, tier 2 = 19). 17 on the widest heuristic | ❌ off by one |
| `automation:`/`covered_by:` empty on all checks | both empty | `covered_by:` **empty on all 579** ✅; `automation:` is **`manual` on all 579**, not empty ❌ | ⚠️ |
| CHK notes: 579 + 56 + 34 = 669 | 669 checks | arithmetic ✅, but the 34 here are `TST-*` now — 635 are `CHK-*` | ⚠️ |

### The VERIFY inversion (question 4)

**Behaviour-preserving as claimed, and the delta is exactly the one named** — but the evidence base is an order of magnitude smaller than the note implies. Running `validate-docs.py` at `4c02731` and at `HEAD` against each of the twelve repos: obsidian-supernote-sync keeps its one finding (`FEAT-0001` / stale `TST-0001`, preserved only by the forward-field fallback), `your-trainer` keeps its three and gains `ERROR [VERIFY] FEAT-0086 is done but linked test TST-0013 is 'ready', not passing`, and no other line in any repo changes. The new finding is **genuine**: `FEAT-0086` is `done`, `TST-0013` is `status: ready` and names FEAT-0086 in `features:`; FEAT-0086's own `tests:` is empty, which is why the old lookup was blind to it.

Two qualifications. **The forward-field fallback does not re-create the duplication** — every name it reads (`features`/`verifies`/`validates`) points test → subject, and a feature's own `tests:` is deliberately not read; it is a rename transition, correctly. But it is `if not _subjects:` **first non-empty field wins**, so a partially migrated note carrying `covers: [A]` and `validates: [B]` silently loses B, and `features: [A]` plus `validates: [B]` loses B likewise. Second, `TST-0013` names **nine** features of which **eight** are `done`; only FEAT-0086 fires because the other seven are absent from `your-trainer`'s `SNAPSHOT.yaml` `items.features`. The gate walks snapshot items, so its reach is bounded by snapshot membership, not by the corpus.

### REQ-0037, attacked (question 2)

**The `command:` exemption is not safe, and it opens on exactly the path the phase exists to create.** Reproduced end to end on a copy of the corpus: give `TST-0044` a `command:` and `status: ready` — the state [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] decision 3 and [[FEAT-0120-The-Automation-Path]] are built to make reachable, and the state `STATUSES.md` prescribes for a test defined but not yet executed — and `validate-docs.py` reports **OK**, while `obligations.owed_items(index)["tests"]` goes **3 → 4** with `TST-0044` on the badge.

`_is_owed`'s test branch is `status in ob.states` **and** `"manual" in kind+level+runner`. All 34 migrated notes carry `kind: manual` (the migration added it and never revisits it), so the manual filter does not exclude them — the only thing keeping 669 rows off the badge is that they hold `active`, and `ACCEPTANCE-STATUS` deliberately stops guarding the moment a `command:` appears. A bulk automation pass — which is precisely [[TASK-0485-Backfill-Automation-From-The-Prose]]'s shape, over 203+ annotated notes — walks straight into the several-hundred-rows-on-a-badge failure [[ADR-0027-The-Registry-Counts-What-Needs-A-Person]] forbids. Without a `command:` the guard does fire correctly (`ERROR [ACCEPTANCE-STATUS] TST-0044 …`), so the unautomated half is sound.

The **review gate** is currently off these notes for a different reason than the one claimed: the REVIEW rule walks `SNAPSHOT.yaml` `items.tests` (25 entries here) and the 34 acceptance notes are not registered. Status is not what is holding it back, so the protection would evaporate if they were ever added to the snapshot — which the merge makes natural, since they are now `test` notes.

### Undocumented consequences

- **`metrics.counts.tests_total` went 43 → 77** and the overview's *Tests passing* tile (`templates.py:707`) now reads **40 / 77** where it read 40 / 43. `ADR-0030` had recorded the opposite intent — *"No `checks_*` metric exists and none should: a count of acceptance rows on the overview is a number nobody acts on"* — and the merge created exactly that by folding the rows into the `TST` prefix. In `your-trainer` this tile would read ~18 / 597. No note mentions it.
- **Three new validator warnings** in this repo, none filed: `PLAN-FOLLOWS` (`docs/features/one-test-type/plan/PLAN.md` is `draft` while FEAT-0118 is `done`) and `REQ-PREMATURE` × 2 (REQ-0038 and REQ-0039 are `draft` while FEAT-0119/0120 are being implemented).
- **`tools/scripts/merge-checks-into-tests.py` has no test coverage and is a line-regex frontmatter editor.** It produced a correct result here, but for the fleet legs: block-style `aliases:` is rewritten into unparseable YAML; a note without frontmatter is destroyed while parity stays green; single-quoted ids leak their quotes into `aliases`/`merged_from`; the value is passed as an `re.sub` *replacement* so a backslash sequence is interpreted; the parity fingerprint compares `covers` as a **set** rather than a multiset and guards 6 of ~22 fields; and the "refusal" happens **after** every file has been written and every `CHK-*` unlinked. It also takes `git rev-parse HEAD` with no dirty-tree guard — the defect `6db2bc1` fixed for `migrated_from` in the sibling script. Fields the fleet will actually populate (`invalidated_by`, `verdict_reason`, `burden`) are empty on all 34 here, so the pilot did not exercise the parity check on them.
- **`docs/__templates__/feature.md`, `docs/__templates__/SCHEMAS.md`** — see findings 3 and 5. `tools/scripts/merge-checks-into-tests.py` is reported by the sync as `GONE` (downstream-only), so the two repos still to migrate have no copy of it.

### What holds

The bundled validator is **byte-identical** to `tools/scripts/validate-docs.py` (`diff` clean), so the cockpit and the canonical gate cannot disagree. The migration itself is clean: 34 → 34 with every guarded dimension identical and bodies unchanged, `merged_from: CHK-nnnn @ 4c02731` pointing at a commit that genuinely contains the notes, `migrated_from` preserved verbatim on all 34. `_test_feature_ids`' path fallback was deleted on a correct measurement (exactly 3 dependents, all backfilled) and is guarded. The coverage read path's four states are asserted on real notes and the guards fail if `settled` is reverted. Both navigation fixes are real: `renderChecksPage` arms `suppressLandingOnce` before `setNavMode` (the ordering, which is the fix, is what the guard asserts), and `commitVirtualPage` hoists the five lines with `refreshActiveNavRow()` added, across nine call sites. The `ISS-0194` guard is the stronger of the two — its `currentRel = normalised;\n currentDispatchHistory = null;` regex fails on any *new* hand-rolled branch, which is the shape that lost the line originally; the `ISS-0193` guard is weaker, since it pins one flag and one ordering inside `renderChecksPage` and would not notice the same defect reappearing on another virtual page. Neither is defeatable by simply reverting the fix. `TASK-0480` and `TASK-0481` are honest about being blocked and why; `your-sudoku` is clean, confirming it was returned as found, and neither it nor `your-trainer` has run the merge migration.

## What the review changed (2026-08-18)

`changes-requested` on all four features, and it was right on every blocking finding. Fixed rather than argued with:

| finding | fix |
|---|---|
| **The badge moved 1 → 3.** `SUBJECT_FIELDS["test"]` named three fields ADR-0032 deleted, so `subject_ids` resolved nothing for 77 of 77 tests and ADR-0028's in-flight quieting switched off for the whole population | `covers` added, badge back to **1**, guarded by `test_a_tests_subject_fields_track_the_link_rename` |
| **`criteria.py` still read `verifies:`** — unverified requirements 31 → 37 | reads `covers:` first; back to 29 |
| **`tests:` still on 81 of 121 features**, and still in `feature.md` | removed from all 81 (22 live edges) and from the template. **The cause was a false report**: the removal regex needed a trailing newline the last frontmatter line does not have, so `re.sub` replaced nothing while `re.search` matched and the run printed "30 cleaned" having cleaned none |
| **FEAT-0117's unfounded claim on TST-0043 survived** | gone with the field |
| **`SCHEMAS.md` never came down** (it is `merge`-owned) | hand-merged |
| **The `command:` exemption was unsafe** — reproduced: `command:` + `ready` gave a green validator and a badge of 4 | `ready` is now forbidden **even with** a `command:`; only `passing`/`failing` are exempt, because those are the runner's own output |
| **`covered_by` was `any`, not `all`** — one passing + one failing settled | `all(...)`, with an emptiness check first, guarded |
| **A manual passing test counted as coverage** | the covering test must declare a `command:`, guarded |
| **The migration script had zero coverage** and refused *after* writing everything | preconditions before the first write; frontmatter-less notes, block-style `aliases:` and a dirty tree all refused; fingerprint widened 6 → 13 fields; five guards written |
| **`tests_total` 43 → 77**, undoing ADR-0030's explicit refusal to count acceptance rows on the overview | acceptance tests excluded from every metric; back to 43 |
| Three unfiled warnings | plan advanced, REQ-0038/0039 approved; one `PLAN-FOLLOWS` remains and is honest — the plan covers four features at two statuses |

**Figures corrected in the notes rather than left standing:** the fleet drift was **10 of 61**, not 20 (`your-health`'s ten reciprocate; the first pass read only `features:`); the other-type `tests:` edges are **248**, not 330; `automation:` is `manual` on all 579 rather than absent. The VERIFY base depends on whether waivers are counted — 4 errors plus 52 waived — and the delta of **+1** holds either way.

**What the review confirmed:** the migration itself is clean and reversible by record; the bundled validator is byte-identical; both navigation fixes are real; TASK-0480/0481 are honest about being blocked.

**Still owed and now correctly labelled:** TASK-0483/0484/0485, the fleet migration, and a discharged check saying *which* test discharged it.