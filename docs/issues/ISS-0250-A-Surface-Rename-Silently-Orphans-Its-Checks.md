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
