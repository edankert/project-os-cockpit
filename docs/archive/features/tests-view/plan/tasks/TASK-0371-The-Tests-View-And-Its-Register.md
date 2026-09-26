---
type: "[[task]]"
id: TASK-0371
aliases: ["TASK-0371"]
title: "A Tests view listing every test in the corpus, with its manual-run obligation"
status: done
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[FEAT-0086-Tests-Becomes-A-View]]"]
parent: "[[FEAT-0086-Tests-Becomes-A-View]]"
effort: M
due: ""
depends: ["[[TASK-0369-The-Obligation-Registry]]"]
blocks: ["[[TASK-0372-The-Runner-Moves]]", "[[TASK-0373-The-Tier-Suite-And-The-Release-Gate]]"]
related: ["[[FEAT-0018-Verification-Health-Surface]]", "[[ISS-0024-Status-Surfaces-Outside-The-Parity-Guard]]", "[[ISS-0069-Review-Verdict-Vocabulary-Is-Unguarded]]", "[[ISS-0063-Dead-Stat-Tiles]]", "[[ISS-0128-Three-Types-Have-No-Stated-Obligation-And-Risk-Is-Claimed-By-Two-Views]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
---

# The Tests view and its register

## Definition of Done
- [x] A Tests view lists every `TST-*`, grouped so what is verified and what is not is legible at a glance — evidence: `test_the_view_holds_the_whole_test_corpus` (set equality against `notes_by_type("test")`, not non-emptiness), `test_every_test_appears_in_exactly_one_group`; live payload `Stale · over 90 days · 2` and `Verified · 21`
- [x] Both storage locations appear — feature-scoped `plan/tests/` and system-wide `docs/tests/` — without the split leaking into the reader's mental model — evidence: `test_both_storage_locations_reach_the_view`, which first asserts the corpus still holds both so it cannot pass vacuously; a row names the **feature** it verifies, never its directory (`test_a_row_says_which_feature_it_verifies`)
- [x] `test @ ready` and manual is the view's obligation, from the registry, with the badge — evidence: `test_the_needs_a_run_group_is_the_registrys_count` asserts the group and `obligations.counts()['tests']` are the same number by two different code paths; `test_the_tests_badge_maps_to_the_tests_mode` pins the registry view name to the button's `data-mode`
- [x] Staleness uses the project's existing threshold and config source, not a second one — evidence: `test_staleness_reads_the_projects_config_key`, `test_the_default_threshold_is_the_validators`, `test_the_renderers_second_staleness_rule_is_gone`, `test_the_scope_panel_is_graded_by_the_same_rule`

## Steps
- [x] Add the view and its nav mode; reuse `_tests_register`, which already reads the whole corpus
- [x] Group by verification state first, then by owning feature
- [x] Point the overview's Tests stat tile here instead of `~review`

## Notes
23 tests across 16 feature directories plus `docs/tests/`, and until now no surface that simply shows them. The register already exists on the desk and moves whole.

Inventing a parallel staleness rule is [[ISS-0024]]/[[ISS-0069]]; use the configured threshold.

## Done 2026-08-10

### The register did not move whole — it was reused, and the grouping is new

`_tests_register` reads the corpus and was left where it is for [[TASK-0372]] to move with the runner. What this task added is `_tests_groups`, which asks a different question: the register is a flat list ordered by id, and the view has to say *what needs doing*. Five groups, each **absent when empty** — `Needs a run` · `Failing` · `Stale` · `Never verified` · `Verified` — and `test_an_empty_group_is_absent_rather_than_zero` carries a vacuity guard so it is asserting absence rather than passing on a corpus that happens to fill all five.

Two of the five have never been non-empty here. That is the point of listing them: a kind that is empty today is indistinguishable from a kind that does not exist, which is exactly how `change` and `release` went missing from the obligation registry ([[ISS-0128]]).

**"Then by owning feature" is the order inside a group, not a second level of grouping.** 23 tests across 16 directories would have produced eighteen groups of one or two rows. The state is the group; the feature orders it, and a system-wide test sorts last rather than first — an empty sort key would put the two least specific rows at the top of every group.

### The staleness rule was already duplicated, and the two disagreed

The DoD said *"not a second one"*. There were already two.

| | field | threshold | scope |
|---|---|---|---|
| `validate-docs.py`, and the overview's `unproven` marker | `last_verified` | `DEFAULT_STALENESS_DAYS = 90`, overridable by `SNAPSHOT.yaml verification.staleness_days` | every test |
| `renderer.ts` `MANUAL_TEST_STALE_DAYS` | `last_run` | 60, hard-coded | manual only |

Measured across this corpus on 2026-08-10: **the project's rule calls 2 tests stale** (TST-0001 and TST-0002, last verified 2026-05-08, 94 days). The renderer's called **0**, because both are automated. So the verification panel read "all fresh" beside a validator that would have said otherwise — [[ISS-0024]]/[[ISS-0069]] in a third place.

Resolved by deleting the renderer's constant rather than adding a third: the server ships `stale` on every test row, computed by `_test_is_stale`, which delegates to `_is_stale_verification` — literally the same function the marker uses. `test_staleness_reads_the_projects_config_key` grades one note against `staleness_days: 30` and `staleness_days: 99999` and requires it to change groups, so a hard-coded 90 fails it as surely as a hard-coded 60.

One deliberate carry-over, because it is written down: an **absent** date is not stale. The validator already errors on a manual test with no `last_verified` (`TEST-FIELDS`), and reporting the same corpus defect as staleness would say the wrong thing about it on a surface that cannot explain itself.

### `last_verified` or `last_run`, because the corpus writes both

22 of 23 tests carry `last_verified`; TST-0022 carries only `last_run`. Reading one field would have filed that note under `Never verified` — a claim about the record dressed up as a claim about the test.

### Found while grouping: a pytest command offered a manual stepper

`_is_unproven` already treats a recorded `command` as decisive — *"executable: the runner stamps it, not a human"*. `_is_manual_test` never looked at the field, so **TST-0022**, whose frontmatter reads `command: .venv/bin/pytest tests/test_surface_ownership.py -q`, was classed manual on the strength of its checklist-shaped body: offered a `Run ▸` stepper on the desk, and counted among the tests a scope asks a person to walk.

Swept across all twelve repos the cockpit renders: **1 of 92 tests**, and it is this repo's own. Fixed by giving `_is_manual_test` the same first question the other function asks.

### Two stat tiles pointed at the wrong place, and one of them was mine

The step said "repoint the Tests tile". Checking the neighbours found the **Risks** tile still pointing at `issues` — where risks stopped appearing earlier the same day, when [[ISS-0128]] moved them to the constraints view. That is [[ISS-0063]] re-created, by moving a type without re-checking who pointed at it, and it had been live for a commit.

The guard could not have caught it. `test_the_dead_stat_tiles_gained_a_destination` asserted the mode *string* — `'issues'` was exactly what it demanded. So it was replaced by `test_every_stat_tile_lands_where_its_type_lives`, which renders the mode each tile points at and requires the tile's own type to be among the rows, against the real corpus. **A test that pins the mechanism passes happily while the destination rots.**

The records that cited the old destinations were corrected rather than rewritten: [[REQ-0025]] criterion 2, [[PHASE-010]] exit criterion 3, and [[FEAT-0047]], which gained a supersession section — its premise (risks and issues are "the same question in different tenses") is the thing Edwin's decision refuted, and its achievement (the type has a navigable home at all) still stands.

### The Verified group is not filed behind a divider

Every test in this corpus is `passing`, so the navigator's settled-group rule would have rolled the whole view into one collapsed *"settled"* line — the Tests view answering "what do we verify" with a divider. `groupNamesStateThemselves` already exists for exactly this and `tests` joins `tasks` in it: these groups **are** the states.

### Verification

`882 passed, 2 skipped`; `validate-docs: OK`; desktop `tsc --noEmit` clean and `dist/` rebuilt. Fourteen new assertions in `tests/test_tests_view.py`, adequacy checked by mutation rather than by reading — each of these was applied and the expected test failed, then reverted:

| mutation | killed by |
|---|---|
| `days = DEFAULT_STALENESS_DAYS` instead of the config key | `test_staleness_reads_the_projects_config_key` |
| revert `_is_manual_test`'s `command` check | `test_a_recorded_command_means_the_machine_runs_it` |
| drop `stale` from `scope_tests_payload` | `test_the_scope_panel_is_graded_by_the_same_rule` |
| make the bucket chain non-exclusive (`elif` → `if`) | `test_every_test_appears_in_exactly_one_group` |
| restrict the view to `features/` paths | `test_the_view_holds_the_whole_test_corpus` + 2 others |

**Not verified: the pixels.** The payload is asserted against the real corpus and the renderer against its own source, but no one has looked at the pane. Edwin's cockpit window was live with a terminal session attached, and reloading it to take a screenshot costs more than the check is worth; [[TST-0011]]'s manual steps are where that belongs, and [[TASK-0372]] updates them.

### Left alone: the browser front door

Mode 1 carries four modes (`library`, `features`, `issues`, `recent`) and has never had `review`, so it never had the test register either — adding the view there is alignment work, not a regression, and [[PHASE-029]] owns it (blocked on [[ADR-0010]], still `proposed`). `mode=tests` **is** served, so the payload is reachable by URL today, and `ROLLUP_NOUNS` in `cockpit.js` gained its entry so the parity guard keeps the two tables honest.
