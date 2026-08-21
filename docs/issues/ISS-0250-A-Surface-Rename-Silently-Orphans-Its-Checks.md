---
type: "[[issue]]"
id: ISS-0250
aliases: ["ISS-0250"]
title: "A check names its surface by copying its title, so renaming a surface silently orphans every check on it — and an orphaned surface is indistinguishable from an uncovered one"
status: fixed
owner: user:edwin
created: 2026-08-20
updated: "2026-08-21"
reviewed_by: model:claude-opus-5
review_date: 2026-08-21
review_verdict: approved
source: ["measured while closing FEAT-0130, 2026-08-20"]
severity: medium
component: cockpit
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[FEAT-0130-Surfaces-Are-A-First-Class-Type]]", "[[TASK-0515-Consolidate-Your-Trainer-Surfaces]]", "[[TASK-0516-Surfaces-On-The-Design-View]]", "[[REQ-0049-A-Surface-Exists-Whether-Or-Not-A-Test-Names-It]]"]
tests: []
---

# The join is a string comparison, and its failure mode is silence

## Problem

`surface_coverage()` (`src/project_os_cockpit/cockpit.py`) joins a surface to its checks on the **lower-cased title**:

```python
key   = str(item.area or "").strip().lower()     # the check
title = str(record.title or "").strip().lower()  # the surface
counts[record.note_id or ""] = areas.get(title, 0)
```

There is no link, no id, and no reverse check. So editing a surface's `title:` moves its count to **zero** and moves nothing else.

**Measured rather than assumed, and the first version of this note got it wrong.** The join lower-cases and strips both sides, so it *survives* the two edits I first named — `Riding — routes` -> `Riding — Routes` and surrounding whitespace both stay at 3 of 3. What breaks it is any other character: `Riding — routes` -> `Riding - routes`, **an em dash typed as a hyphen**, drops 3 to 0. That is the worst possible case to have got backwards, because **8 of `your-trainer`'s 15** surface titles contain an em dash — `Data — backup/export`, `Integrations — AI`, `Integrations — Strava`, the three `Riding —` and the two `Workouts —` — and every one of them is otherwise ordinary words a person would retype. Constructed and executed, three checks against one surface:

| surface `title:` | coverage | design view head |
|---|---|---|
| `Riding — routes` | 3 | `Surfaces` |
| `Riding — Routes` | 3 | `Surfaces` |
| `&nbsp;Riding — routes&nbsp;` | 3 | `Surfaces` |
| `Riding - routes` | **0** | `Surfaces · 1 with no checks` |
| `Riding — routes & free ride` | **0** | `Surfaces · 1 with no checks` |

The design view then shows the surface under `Surfaces · N with no checks`, which is **the exact row [[FEAT-0130]] built the type to produce**: a place in the product nobody has tested.

**The two states render identically.** A surface with genuinely no checks and a surface whose 91 checks were orphaned by a rename both read *"no checks"*. The renamed one is the more urgent of the two and is the one the surface tells you least about.

`area:` values naming no surface are equally invisible from the other end: nothing walks them, so a check can sit on a name no surface has and never be reported.

## Repro

In `your-trainer` (working tree, 2026-08-20), change `docs/surfaces/SUR-0011-Riding-routes.md` `title:` from `Riding — routes` to `Riding - routes` — one em dash retyped as a hyphen. `surface_coverage` drops that surface from **91 to 0**. No validator error, no test failure; the design view head count rises by one and says the surface has no checks.

## Expected

A rename is either impossible to get wrong (the check names the surface by **id**) or it is **reported** (a validator rule names any `area:` value that matches no surface, in a repo that has surfaces).

## Actual

Silent. The only signal is a number changing on a screen nobody is looking at for that reason.

## Evidence

- The join, quoted above, and its own docstring: *"a surface whose title matches no `area:` reads as zero, which is correct rather than a gap in the join."* True at the moment it was written and it is precisely the ambiguity above.
- [[TASK-0515]] recorded this as the thing it left: *"the join is by name — so renaming a surface silently orphans 91 checks. Closing that is a schema change on the check (`area:` becomes a link), which is [[FEAT-0130]]'s endpoint rather than this task's."*
- **The corpus is clean right now — in a working tree, and in no commit.** Measured in `your-trainer` 2026-08-20: **15** surface titles, **15** distinct non-empty `area:` values, and `comm -23` over the two sorted sets returns **nothing** — no area names a surface that does not exist. **`git log --all -- 'docs/surfaces/*'` returns nothing too**: those fifteen notes have never been committed on any branch, and at that repo's HEAD there are zero surfaces and 579 checks naming none of them. So *"the corpus is clean"* is true of one machine's disk and of no commit — which does not change the affordability argument (a rule fires against what is there) but does mean the clean state is not yet durable. The two `level: acceptance` notes outside the directory (`TST-0015`, `TST-0018`) carry `area: ""` and are the empty case a rule must skip rather than report.
- No other fleet repo holds a `SUR-*` note, so a rule guarded on *"this repo has surfaces"* is silent in eleven of twelve.

## Next Actions

- [x] **Decided 2026-08-21: the rule.** `SURFACE-ORPHAN` in `tools/scripts/validate-docs.py`, reporting an `area:` that names no surface, guarded on *"this repo has surfaces"*. The schema change — `area:` becomes a `[[SUR-####]]` link — is still the real fix and is **not** done: it touches 579 notes in a repo whose fifteen surfaces are in no commit, so it is a migration and it needs that repo committed first. Recorded below rather than left implied.
- [x] **The rename was constructed and the check watched firing.** `tests/test_surface_orphan.py::test_a_renamed_surface_orphans_its_checks_and_the_rule_says_so`: one em dash retyped as a hyphen, three checks, one finding naming the old area.

## Independent review — fresh-context pass, 2026-08-20 (`b4b9c50` / `4521a7a`)

Separate session, `model:claude-opus-5`, starting from the notes and the diff with no access to the author's reasoning. Same model family as the author, recorded in `reviewed_by`; the independence claimed here is **context**, not weights ([[project-os-dev#ADR-0013]]).

**Verdict: approved.** Reproduced end to end on the real corpus, against a copy of `your-trainer`'s `docs/` — that repo was not modified.

Driving `surface_coverage` over `SUR-0011` with its `title:` rewritten:

| `title:` | coverage |
|---|---|
| `Riding — routes` | **91** |
| `Riding — Routes` | 91 |
| `RIDING — ROUTES` | 91 |
| `␠␠Riding — routes␠␠` | 91 |
| `Riding - routes` (em dash -> hyphen) | **0** |
| `Riding — routes & free ride` | 0 |

So the correction this note makes to its own first version is right: case and surrounding whitespace survive, the em dash does not, and the drop is **91 to 0** exactly as the Repro says. The design-view head moves to *"1 with no checks"* in the failing cases.

*"**8 of `your-trainer`'s 15** surface titles contain an em dash"* — confirmed by enumerating `docs/surfaces/SUR-*.md`: `Data — backup/export`, `Integrations — AI`, `Integrations — Strava`, `Riding — routes`, `Riding — simulation`, `Riding — structured`, `Workouts — authoring`, `Workouts — execution`. Eight.

*"the corpus is clean right now — 15 titles, 15 distinct non-empty `area:` values, no orphan on either side"* — confirmed; the two sets are equal.

One case found that the note does not list and that its own wording already covers (*"any other character"*): internal double-spacing around the em dash, `Riding␠␠—␠␠routes`, also drops to 0. Only *surrounding* whitespace is stripped.

### One addition to the Evidence, which bears on the Next Actions

The **Repro** correctly says *"working tree"*. The **Evidence** bullet — *"Measured in `your-trainer` 2026-08-20: 15 surface titles, 15 distinct non-empty `area:` values"* — does not, and the distinction matters here more than usual: `git ls-tree HEAD docs/surfaces/` in that repo returns nothing and `git log --all -- 'docs/surfaces/*'` returns nothing. The fifteen `SUR-*` notes exist **in no commit, ever**.

So *"the corpus is clean right now, which is what makes a day-one error affordable"* holds for the working tree and inverts for the committed state: at `HEAD` that repo has **zero** surfaces and 579 checks whose `area:` values name none of them. A `SURFACE-ORPHAN` rule guarded on *"this repo has surfaces"* would be silent there in CI — not because the corpus is clean, but because the population is invisible.

That does not change the shape of either option in Next Actions, and it is an argument for the rule being guarded on *"this repo has surfaces"* rather than against it. It does mean the affordability argument should be re-measured once those notes are committed.


## Fixed 2026-08-21 — the rule, and what it deliberately does not do

**One finding per orphaned NAME, not per check.** A rename orphans every check on the surface at once; 91 identical errors describe one edit and leave a reader unable to tell how many surfaces are broken. The finding names the count and up to three ids.

**Guarded on "this repo has surfaces."** Eleven of twelve fleet repos hold no `SUR-*` note, and a rule that fires on every check in a repo that never opted into the type is a rule people turn off.

**It reports one direction only.** An `area:` naming no surface is a finding; a surface no check names is **not**. That second one is the row [[FEAT-0130]] built the type to produce — *a place in the product nobody has tested* — and reporting it as a defect would make the type's own purpose an error.

**Warned, with a promotion date.** Measured in this repo on the day it landed: **21 distinct `area:` values over 34 checks** name no surface, because only `SUR-0001` was ever written. That is one `SUR-*` note per surface to clear — [[TASK-0515]]'s shape, a body of work rather than a line edit — so [[project-os-dev#ADR-0011]] clause 3 forbids erroring over it. `PROMOTIONS["SURFACE-ORPHAN"] = "2026-11-18"`.

### The second implementation is forced, so it is pinned

The validator is stdlib-only and standalone: it cannot import `cockpit.surface_coverage`, so the join now exists twice, which is [[REQ-0059]]'s forbidden shape unless something ties the two together.

`test_the_rule_and_the_join_agree_on_normalisation` **drives both over the same strings** and requires the same answer — identical, case, surrounding whitespace, em dash retyped as a hyphen, internal double-spacing, a suffix — rather than matching text in either. A text assertion passes on a rule whose `.strip().lower()` is in a comment, which is this repo's own recorded mutation-testing pitfall. Mutating **both copies** to drop `.lower()` fails it; mutating one fails the byte-identity test instead.

### Three mutants, three catches

| mutant | caught by |
|---|---|
| the rule stops normalising case | `test_case_and_surrounding_whitespace_survive_both` |
| the *"this repo has surfaces"* guard is dropped | `test_a_repo_with_no_surfaces_is_silent` |
| an empty `area:` is reported | `test_an_empty_area_is_not_an_orphan` |

### What is left, and it is a migration rather than a fix

The join is still a string comparison. **Making `area:` a link is the durable answer** and it is out of scope here for the reason the Evidence already records: `your-trainer`'s fifteen `SUR-*` notes exist **in no commit, ever**, and 579 checks there name areas at a `HEAD` that has zero surfaces. A schema migration cannot start against a corpus that is not committed. When it is, this rule is what will report the gap it leaves.

## Independent review — 2026-08-21

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `f5ca55b..07602db`; the author's reasoning trace was not available to it. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — same model as the author, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant rather than read.


**Verdict: approved.** Every number in this note reproduces exactly, and the guard against the defect the rule could itself commit is the strongest one in this commit.

- **21 distinct names over 34 checks reproduces precisely.** The validator emits 21 `SURFACE-ORPHAN` warnings, and the per-name check counts sum to exactly **34**. That is *every* acceptance check in this repo (34 notes at `type: "[[test]]"` + `level: acceptance`; a 35th `level: acceptance` hit is a code block inside `ADR-0037`). `SUR-0001`'s title — *"The tests view — the suite as sections, and what a person still owes"* — matches no `area:` value, so the 100% orphan rate is correct rather than a join bug.
- **The two-implementation risk is guarded by driving, not by matching text.** I broke the **cockpit** side only (`cockpit.surface_coverage`, dropping `.lower()`) and left `validate-docs.surface_key` intact: `test_the_rule_and_the_join_agree_on_normalisation` failed on `'Riding — routes'`. Breaking the validator side instead also failed it. This is the correct answer to [[REQ-0059]]'s forbidden shape and it is what the rest of this commit should have copied.
- **The bundled copy is byte-identical** for the new rule, and `test_the_bundled_copy_carries_the_rule` fired when I mutated only one of the two.
- Warning-with-a-promotion-date is right under ADR-0011 clause 3: 21 `SUR-*` notes is a body of work, not a line edit.

No changes requested.

## Independent review — second pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `07602db..b635c39` — the first pass's findings and the author's reasoning trace were not available to it, only the seven claims as the notes state them. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]): same model as the author and as the first reviewer, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant.

**Approved, confirming the first-pass verdict.** No first-pass finding attached to this note; this commit added a review section only. `SURFACE-ORPHAN` and the shared `surface_key` normalisation are outside the scope of the seven findings and were not re-litigated here; the first pass's own construction against `test_the_rule_and_the_join_agree_on_normalisation` is recorded above and I did not find cause to reopen it.

## Independent review — third pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `b635c39..c9d6a82`; neither the author's reasoning trace nor either earlier reviewer's working was available to me beyond what these notes themselves record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran both earlier passes, recorded in `reviewed_by` as provenance. Every count below was re-measured from the tree and every guard re-executed against a constructed mutant. **This verdict supersedes the second pass's on this note.**

**Approved.** This commit adds a review section only; `SURFACE-ORPHAN` and the shared `surface_key` normalisation are untouched in `b635c39..c9d6a82`. Not re-litigated — the earlier passes' constructions against `test_the_rule_and_the_join_agree_on_normalisation` are recorded above and I found no cause to reopen them. The validator is green and `--as-committed` passes the full CI step set.

### What survived refutation

- **Finding A's restoration is verbatim and the tests are not vacuous.** I extracted both functions from `07602db` and from `c9d6a82` and diffed them: byte-identical. `tests/test_checks_view.py` is back to **22** `def test_` functions. Both guards kill mutants: flattening `for (const area of areas)` and deleting `checkPercent(area.items)` each fail `test_the_page_groups_by_surface_and_not_as_one_flat_list`; changing `(done.length / total)` to `(settled.length / total)` fails `test_a_stale_tick_is_not_drawn_as_done`.
- **Nothing else was lost anywhere in `f5ca55b..c9d6a82`.** I parsed every `tests/**/*.py` at all four commits and diffed the `def test_` sets file by file. The only removals in the whole range are the seven `covered_by:`/promotion tests at `07602db`, every one of them a test for the mechanism `REQ-0057` deleted, replaced in the same commit by seven guarding its absence; the two at `b635c39`, restored here. No test file was deleted at any point. Totals 1761 → 1829 → 1830 → **1835**.
- **Finding B's own tests are real.** Restoring the absence rule (`check not in passing and check not in failing`) fails `test_two_runs_covering_different_toolchains_do_not_retract_each_other` and `test_a_run_that_never_reached_the_test_leaves_it_alone`; deleting the skipped branch fails `test_disabling_the_covering_test_does_the_same` and the latter; folding skipped back into absence fails two. I also built the alternating-toolchain loop myself — `TST-0001` by a `.py` test, `TST-0002` by a `.kt` test, one platform, three full cycles — and counted **two** ledger entries, both `pass`, no retraction.
- **Finding C's test is real.** Restoring `and standing.by == args.by` fails `test_a_second_machine_saying_pass_adds_nothing` and nothing else.
- **Finding E's claim is true.** `validate_moved_verdict_fields` returns early unless `docs/releases/ledgers/` exists *and* holds a `*.json`, so the twelve `LEDGER_MOVED_FIELDS` are refused only in a ledger-keeping repo. The enumeration is right at its stated arity: all ten named fields are written by `note_text`, `covered_by` is not, and the twelfth (`merged_from`) is correctly absent from both lists.
- **Finding G is done.** The false closing clause is gone from `ISS-0213`'s `review_response`.
- **Suite, validator, CI step set.** `2060 passed, 3 skipped` (268s), `validate-docs: OK`, and `validate-docs.sh --as-committed` reports *"HEAD passes the full CI step set"* — validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `c9d6a82`.

## Independent review — fourth pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `c9d6a82..9a75f11`; I have no memory of authoring any of this and had no access to the author's reasoning trace or to any earlier reviewer's working beyond what these notes record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran all three earlier passes, recorded in `reviewed_by` as provenance rather than as a compliance token. Every count below was re-measured from the tree and every claim about behaviour was established by running the code, not by reading it. **This verdict supersedes the third pass's on this note.**
**Verdict: approved.** Nothing in `c9d6a82..9a75f11` touches this issue's mechanism, and the mechanism survives re-inspection: `SURFACE-ORPHAN` walks the note index for `type: test`, treats an empty `area:` as un-placed rather than orphaned, and joins on the same normalisation the cockpit uses — with the two implementations driven over the same strings by a test rather than matched as text, which is the right answer to this repo's own recorded pitfall. The rule is dated to 2026-11-18 under ADR-0011 clause 3 because the durable fix is a migration, and that is honestly stated on the note.

### The headline question: did fixing round three break anything

**No.** Test functions were extracted by name, file by file, at `f5ca55b`, `c9d6a82` and `9a75f11` and the sets diffed. `c9d6a82..9a75f11` **removes nothing**: three functions are added to `tests/test_observed_coverage.py` and no other file changes its set, 1835 → **1838**. Across the whole phase range `f5ca55b..9a75f11` the only removals anywhere are the seven `covered_by:`/promotion tests in `tests/test_checks_view.py`, each replaced in the same file by one guarding the mechanism's absence — that file's count is unchanged at 22 — so 1761 → 1838 with a net `+77` accounted for entirely by five new files (6 + 31 + 17 + 13 + 10).

**The emitter was run in loops rather than read.** Twelve scenarios against a temporary repo, counting ledger entries: `pass` then four `<skipped/>` runs → **2** entries (one `pass`, one invalidation); three skipped runs with no standing verdict → **0**; `pass`, skip, then three passing runs → **3**; declaration deleted, four runs → **2**; declaration moved to another file under the same name, four runs → **1**; moved *and* renamed, four runs → **1**; a `.kt`-declared check across five `.py` runs → never invalidated; `pass` then five failing runs → **2**; a passing sibling with a skipped sibling, four runs → **2**; a `manual` verdict under four skipped runs → **1** (untouched); a `manual` verdict under four failing runs → **2**. Every one is bounded, and the bound is structural: `resolve()` pops an invalidated check out of `verdicts()`, so both the `stale` and the `failing` branch leave the set by construction on the next run. Round three's finding 1 is genuinely closed.

**The three new tests are not passengers.** Reverting `elif seen and not held` to `elif seen` fails `test_a_skipped_sibling_is_not_laundered_into_a_pass` and nothing else. Restoring the round-two `stale` rule verbatim fails `test_a_skipped_test_invalidates_once_not_once_per_run` and `test_a_check_with_no_verdict_is_never_invalidated`. The two earlier repairs still hold their ground: `_withdrawn` returning `True` unconditionally fails the two toolchain tests, and returning `False` for a vanished declaration fails `test_deleting_the_covering_test_puts_its_check_back_on_the_run_list`.

**Round three's finding 3 reproduces exactly, every figure.** Driving the rule's own predicates over `git archive f5ca55b`: **56** owed, **51** terminal, **5** non-terminal, `30 done / 8 merged / 4 implemented / 9 fixed`, earliest `review_date` **2026-07-30** on **eight** notes — `CHG-20260730-Two-Features-Closed`, `FEAT-0045`, `ISS-0037`, `ISS-0057`, `ISS-0068`, `ISS-0069`, `PHASE-011`, `PHASE-013`. All 8 `merged` findings are `CHG-*`. The rule reports 51 at HEAD.

**Suite, validator, CI step set, all observed rather than reported.** `2063 passed, 3 skipped` in 269s; `validate-docs: OK`; `--as-committed` reports *"HEAD passes the full CI step set"* — validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `9a75f11`.


## Independent review — fifth pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `9a75f11..991838e`, widened to `f5ca55b..991838e`; no memory of authoring any of this and no access to the author's reasoning trace. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]). **This supersedes the fourth pass's verdict on this note.**

**Verdict: approved.** Unchanged in `9a75f11..991838e` beyond frontmatter. Worth recording next to it, because it is the same shape one layer down: the coverage emitter now has its own silent-orphan path — a declaration whose file cannot be matched to a report `classname` is neither observed nor invalidated, so a standing automated verdict survives a rename of the enclosing structure with no signal. Filed against [[FEAT-0138]] / [[TASK-0543]].

**Suite, validator, CI step set — observed.** **2066 passed, 3 skipped** in 269s; `validate-docs: OK`; `--as-committed` reports *"HEAD passes the full CI step set"*. Working tree clean at `991838e`. The phase itself is `changes-requested` at this pass on two findings that do not touch this note — see [[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]].
