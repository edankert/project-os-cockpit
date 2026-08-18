---
type: "[[phase]]"
id: PHASE-036
aliases: ["PHASE-036"]
title: "Three axes — what a test exercises, who runs it and what it gates stop being one word, and gating is derived from `covers:` at any granularity"
status: done
order: 36
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
goal: "Separate the three things `level: acceptance` currently means — what a test exercises, who runs it, and what it gates — so that any test can gate any item through `covers:`, re-arming follows execution rather than level, and the surfaces show one population instead of two."
features:
  - "[[FEAT-0122-One-Human-Walked-Population]]"
  - "[[FEAT-0124-Gating-Is-Derived-From-Covers]]"
  - "[[FEAT-0123-The-Walk-Surfaces-Say-One-Thing]]"
issues: ["[[ISS-0200-Marks-Versus-Statuses]]", "[[ISS-0201-Walk-And-Run-Vocabulary]]", "[[ISS-0202-Needs-A-Run-Versus-The-Tiers]]", "[[ISS-0203-Tier-Selection-Does-Not-Change-The-Page]]", "[[ISS-0204-The-Acceptance-Filter-Bar-Is-Congested]]", "[[ISS-0205-The-Sweep-Writes-Notes-A-Migrated-Repo-Cannot-Read]]"]
related: ["[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ADR-0033-A-Manual-Test-Is-An-Acceptance-Test]]", "[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[PHASE-035-Acceptance-Checks-Are-Notes]]", "[[TESTING-MODEL]]"]
reviewed_by: model:claude-opus-5
review_date: 2026-08-18
review_verdict: changes-requested
---

# Three axes

## Why this is a phase and not an issue

Its goal is stateable without listing its parts — *a person walking a test sees one thing, not two* — and its exit criteria are measurements rather than a restatement of the task list. It is also not [[PHASE-035-Acceptance-Checks-Are-Notes]] reopened: that phase closed having merged the **types**, and this one exists because merging the types left two **populations** behind. Widening a closed phase to absorb its own consequence is how a phase stops ever closing.

## Where it came from

Edwin, reading the model note PHASE-035 produced: *"I think a manual test is always an acceptance test and can be marked as complete/ticked or if changes happen can be unticked."* [[ADR-0033-A-Manual-Test-Is-An-Acceptance-Test]] recorded why that is right.

**Then he rejected that ADR's own reasoning**, which is why this phase was re-scoped before any of it was built: *"Manual tests are not different to acceptance tests or other tests, they should be able to gate at any granularity. I think we don't need necessarily acceptance tests any more in that case?"* ADR-0033 had written *"manual tests gate a feature, acceptance tests gate the release"* as an accepted cost — the conflation restated as a consequence. [[ADR-0034-Three-Axes-Not-One-Word]] supersedes it, and the research backs him: **ISTQB** keeps level and type independent and holds manual/automated out of both, and the **Agile Testing Quadrants** are business-facing/technology-facing by supporting/critiquing — *manual versus automated is not an axis in either.*

Five further concerns from the same reading became [[ISS-0200-Marks-Versus-Statuses]]..[[ISS-0204-The-Acceptance-Filter-Bar-Is-Congested]], and an independent review of those added a sixth: the sweep writes notes a migrated repo cannot read ([[ISS-0205-The-Sweep-Writes-Notes-A-Migrated-Repo-Cannot-Read]]), which is live in this repo and four times over in `your-trainer`.

## Order

1. **[[ISS-0205]] first, and out of band.** The sweep is writing invisible notes *now*. It does not wait for a decision.
2. **[[FEAT-0122-One-Human-Walked-Population]]** — the axes stop implying each other: `kind: manual` goes, one predicate answers who-runs-this, the 22 notes move to a level that describes what they exercise, and `invalidated_by:` is keyed on execution.
3. **[[FEAT-0124-Gating-Is-Derived-From-Covers]]** — and it is **gated on the backfill**, not on the ADR. 83 of 669 acceptance tests have an empty `covers:` and would gate nothing; the derived gate must be proven to reproduce the tier gate before the tier rule is retired.
4. **[[FEAT-0123-The-Walk-Surfaces-Say-One-Thing]]** — the surfaces, which can only be simplified once there is one population to show.

## Exit criteria

- [x] **`kind:` is gone from the schema**, from every note fleet-wide (727 demonstrable from history) and from all four `test.md` templates — the three fleet templates still carried it when this was first claimed, so the scaffold went on creating the deleted field.
- [x] **An item of any type can be gated by a test through `covers:` alone** — `Suite.blocking_for(subjects)`, with `blocking()` as its `subjects=None` case, and a production caller in the per-scope panel: FEAT-0011 shows 13 blocking against 60 for the release. `tier:` is read as **lifetime** (does this still apply), never as a kind of test.
- [x] **The derived gate reproduces the tier gate** by membership, per repo: 0 / 56 / 60, identical sets. The 83 unattributed turned out to be 74 Tier 3 and 9 Tier 1/2, all settled; they are not backfilled and the gate fails closed on them instead.
- [x] **Re-arming follows execution**: a test with no `command:` re-arms by `invalidated_by:` at any level, and the 90-day threshold no longer applies to it.
- [x] **One predicate answers "who runs this."** `obligations._is_owed` calls `cockpit._is_manual_test`, which is now `not command:` with no fallback — four heuristics collapsed to the one question the corpus can answer. 788 tests fleet-wide, **0** disagreements; it was 8.
- [~] **`Needs a run` is gone** — renamed `Needs a walk`, and one verb now names the human act everywhere. **Reconciled on the second clause**: what a person owes is still the manual population rather than unsettled Tier 1/2 rows, because folding acceptance rows into that count is what ADR-0027 forbids. Badges per repo: 1→0 here (TST-0024 correctly quieted), 0→1 in `your-sudoku` (TST-0013 claimed automated with no way to run), 5→5, 2→2.
- [x] **Tier 1 and Tier 2 open different pages** — `~checks/tier/N`, parsed by the route and preselected, so back/forward move between tiers. The other four filter axes remain click-only, recorded on [[REQ-0042-The-Suite-Is-Addressable]].
- [x] **The acceptance page leads with the checks.** `CHIP_CAP = 8`; wider axes collapse to a `<details>` carrying their value count and their selection count. 164 chips → 8 on `your-trainer`, 65 → 4 here — which was the worse ratio at 1.9 per check.
- [x] **A swept check is readable by the repo it was written into.** `test_the_sweep_writes_a_note_the_reader_can_see` reads the sweep's own output back through `acceptance.load` on a migrated corpus, and is the only guard that fails when the writer reverts — the other 22 assert fields.
- [~] **The known duplicate is not gone.** `TST-0011` still holds a 13-item checklist whose item 7 is `TST-0064`/`TST-0065`. Reconciled rather than cut: [[ADR-0034-Three-Axes-Not-One-Word]] superseded the decision that would have split it, and under the axes it is a `level: system` test that legitimately covers nine features. Splitting it is now a content judgement, not a schema consequence.
- [x] **An independent review, from the corpus rather than these notes** — returned `changes-requested` with six blocking findings, every one fixed. It caught a live user-visible break (the surfaces still keyed on characters), a fail-safe I had inverted, four behaviours that survived deletion, and two criteria ticked for things that had not happened.

## What this phase must not do

**It must not put acceptance rows on a badge.** [[ADR-0027-The-Registry-Counts-What-Needs-A-Person]] forbids per-check obligations and that survives ADR-0033 untouched: retiring `Needs a run` means the *manual* population stops asking individually, not that 669 acceptance rows start.

**It must not decide [[ISS-0200]] by accident.** Whether the verdict stays a character or becomes a word is a separate decision with its own evidence, and touching every note in the corpus is exactly the moment somebody would fold it in silently. [[ADR-0034-Three-Axes-Not-One-Word]] asks for *one outcome vocabulary* and deliberately does not say what it is written as.

**It must not let the gate get quieter.** The derived gate replaces a rule that has no holes with one that has 83 of them until the backfill lands. A gate that goes quiet during a migration is the failure this project has already paid for once, in a repo where nobody was looking.

## Independent review — 2026-08-18, `model:claude-opus-5`, changes-requested

**What was independent, and what was not.** Fresh context, separate session: this pass started from the notes under `docs/` and the four commits (`438caa5`, `1f5cafd`, `27e215c`, `b59ba1b`) plus the three fleet commits, and never saw the authoring session's reasoning. The author was not consulted, and nothing here reconstructs intent charitably — where a claim cannot be justified from the notes and the diff, that is recorded as a finding about the notes. What was **not** independent is the model: the work and this review are both Opus 5, recorded in `reviewed_by:` as provenance. Per [[project-os-dev#ADR-0013]] a shared model correlates capability and a shared *context* correlates commitment; only the second is the gate, and it is broken here.

**Everything was re-derived.** Ran in this repo: `bash tools/scripts/validate-docs.sh` (OK) and `.venv/bin/pytest tests/ -q` (**1688 passed, 3 skipped**). Ran each fleet repo's **own** validator: `your-sudoku`, `your-trainer`, `your-health` all OK.

### Confirmed as claimed

Badges **1 / 0 / 5 / 2** exactly, from `obligations.counts_by_kind`. The **5 → 8** rise in `your-trainer` reproduced by putting the three frozen suites back to `ready` (8) and returning them to `retired` (5). **8 of 788** disagreements reproduced exactly against the pre-change corpora, and the eight are the ones [[TASK-0493]] names — `your-health` TST-0007..0011 and the three frozen suites; 788 is the fleet test-note count across all twelve snapshot-bearing repos excluding templates. Blocking **0 / 56 / 60**, identical sets. **83** empty-`covers:` checks in `your-trainer`, **74** Tier 3 and **9** Tier 1/2, and all 9 settled. `VERIFY-ACCEPTANCE` fires **6** times in `your-sudoku` (FEAT-0025 against TST-0028..0033) and 0 in the other three — the rule is reachable, not silently crashing. The twelve-tag `your-trainer` delta is **byte-identical** before and after, recomputed with the pre-migration code against the pre-migration corpus (59/1/0, 58/2/0, 58/2/0, 58/1/1, 57/2/1, 55/4/1, 51/8/1, 37/22/1, then 13/47/0 four times). **164** facet values on `your-trainer` and **65** rendered chips here, falling to **8** and **4** under `CHIP_CAP`. The mark distribution survived the migration exactly: 546 `done` + 122 `todo` + 1 `incomplete` = 669, matching the pre-migration 546 `x` + 122 `" "` + 1 `/`. **No acceptance row reaches any badge** in any of the four repos. All 120 `your-trainer` gate rows carry a `rel` that exists on disk. `~checks/tier/N` is emitted and routed. The human-walked population is **30** (5 / 0 / 18 / 7), not 22.

### Figures that do not reproduce from the record

`kind:` was deleted from **727** notes demonstrable in history, not 731 — `your-trainer` is **593**, not 597. The four missing are `TST-0015`..`TST-0018`, which were untracked when the script ran and were committed alongside. The same four explain the badge baseline: the committed pre-change state gives `your-trainer` **3**, not 5. Both figures are true of the working tree of the day and unreproducible from the repository, which is a consequence of finding 9 below.

### Findings

1. **The mark vocabulary migrated in the model and not in the surfaces.** `acceptance.MARK_MEANING` and the renderer's `MARK_GLYPH`, `MARK_TITLE`, `MARK_CLASS`, `VERDICT_FOR` and `MARK_CHOICES[].mark` are still keyed on the retired characters while every live note carries a word. Measured: every mark filter chip in all three migrated repos renders the label **`unrecognised`**; the row control renders `[done]` / `[todo]` instead of `[x]` / `[ ]`; `MARK_CLASS[mark] ?? 'unknown'` costs every check its colour; `MARK_TITLE[mark] ?? ''` empties the tooltip **and the `aria-label`** on every row of the checks view and the release page; and `choice.mark === opts.current` never matches, so the dialog no longer shows which mark the row carries. Writes are unaffected — the client posts `verdict`, the server maps through `VERDICTS`. [[ISS-0200]]'s own review named exactly these tables as what a word vocabulary "has to reproduce or it fails open"; the server half was reproduced and the client half was not. The three renderer guards in `tests/test_acceptance_marks.py` stay green because they assert the tables' *contents* and never that the tables' keys match the vocabulary the corpus carries.

2. **`normalise_mark` strips, which inverts the fail-safe the code says it preserves.** `item_from_note` classified without stripping until this change; it now calls `normalise_mark`, which does `.strip()` first. `mark: " x"` and `mark: "x "` moved from *unrecognised → blocking* to `done` → *settled → not blocking*. The comment two lines below the call still reads *"`[ x]` staying unrecognised is the point of the row parser's own refusal to strip (ISS-0141)"*, and `parse()`'s docstring calls this transformation "the failure this whole regex exists to stop, inverted". Unlikely input, but it is a gate getting quieter, which this phase says it must not do.

3. **Four central behaviours survive deletion.** Control run of the corpus tree: 17 failed / 1669 passed / 5 skipped (the 17 are artefacts of running outside a git checkout). Identical totals for every mutant: (a) `Suite.blocking_for` ignoring `subjects` entirely — gating not derived from `covers:` at all — passes `tests/test_derived_gate.py` (5 passed, 2 skipped) and the whole suite, because with `subjects=None` the covers clause short-circuits and the "equivalence by membership" test compares `tier in {1,2} and not settled` with the identical expression; (b) deleting the fail-closed "covers nothing blocks" clause passes, because its only guard does `if orphan.settled: continue` and **all 9** gating orphans are settled; (c) reverting `sweep._write_new_check` to `type: "[[check]]"` — the [[ISS-0205]] defect itself — passes all 22 tests in `tests/test_acceptance_sweep.py`, because the sweep reads back through `acceptance.load_notes(dir)` and never through the `or` branch that hid it, so ISS-0205's third done-when is not met; (d) making `_test_is_stale`'s walked branch always return `False` passes 118/118 of the four most relevant files — the new guard asserts only that a command-less test is *not* aged, and nothing asserts an invalidated walk *is* stale. With 0 invalidations anywhere in the fleet the branch is untested in practice as well as in the suite.

4. **[[REQ-0041]] criteria 2 and 3 are ticked for things that did not happen.** `kind: manual` is still on line 11 of `docs/__templates__/test.md` in `your-sudoku`, `your-trainer` and `your-health` — only this repo's template was edited, and the guard scans this repo's `docs/` alone. `automation:` still answers who-runs-this, is read *first* by `_is_manual_test`, is written by the sweep as `automation: manual`, is documented in the template, is carried by **671 of 788** fleet test notes and is load-bearing on **466** of them — the guard's `banned` tuple is `("kind","mode","method")` and omits it. It is latent exactly as the 8 were. And the Tests badge is **not** derived from the tiers: it is still `test @ ready` filtered by the manual predicate, so [[TASK-0492]]'s own "Done when: the clause is gone, the badge is derived" is unmet while the task is `done`.

5. **[[REQ-0043]] criterion 2 is ticked and the code contradicts it.** `Suite.blocking_for` opens with `if item.tier not in GATING_TIERS`, so `tier:` decides whether a check gates; removing it changes the blocking set. [[TASK-0501]]'s prose is candid ("not deleted; it is subsumed") and the requirement's box is not. Separately the two implementations of "the one rule" disagree by construction: `blocking_for` is tier-filtered and `VERIFY-ACCEPTANCE` reads no tier at all.

6. **"One rule gates every item type" is not what the validator does.** `terminal = None` for `requirements` (ADR-0007, deliberate) and for `checks`, so a requirement cannot be gated by a test — yet the exit criterion above and REQ-0043's first box both name a requirement among the gated types. `blocking_for(subjects)` has **no production caller**: nothing in `src/` or `desktop/` passes `subjects`, and the release-as-union-of-its-contents' covered set is not implemented anywhere.

7. **`VERIFY-ACCEPTANCE` exists in exactly one repo's gate.** The three fleet repos' own `tools/scripts/validate-docs.py` are 95,883 bytes from 12:30 and contain zero occurrences; this repo's and upstream's (130,051 bytes) carry it. `your-sudoku`'s six true findings therefore appear at no pre-commit, in no CI, and not on the cockpit's validation screen — `validation.py` prefers the browsed repo's own copy. Upstream `~/Dev/repos/project-os/tools/scripts/validate-docs.py` is **uncommitted**, so the canonical copy of the rule lives in a dirty working tree. No test anywhere exercises the rule; the two-note corpus that caught the out-of-scope `rel` was not committed, so the crash-instead-of-fire mode has no regression guard.

8. **Two definitions of "settled" and two of "stale" now coexist.** `validate-docs._acceptance_is_settled` claims to read "the same three `acceptance.Item.settled` reads"; `Item.settled` reads **four**, and the missing one is `covered_by_passing`. Harmless today only because all 669 checks carry `covered_by: []` — which also means ADR-0031's "whole return" is dead data. And `cockpit._test_is_stale` requires `invalidated_by` to be a dict with a non-empty `change` and has no `checked` conjunct, while `acceptance.Item.stale` accepts the legacy scalar form, treats a `reason`-only invalidation as one, and requires `checked` — so on a `mark: rerun` note, which is now what every invalidation writes, the two answer differently.

9. **The fleet commit bundles unrelated work.** `your-trainer` `49cf2ce9`, titled "ADR-0034: kind: deleted", changes 637 files with 4,399 insertions: FEAT-0104, PHASE-020, REL-0013, twelve issues, nine tasks, four test notes, two change notes and four `.ips` crash logs, none of it ADR-0034. `CLAUDE.md`'s close-out rule was written against this exact repo for this exact reason, and it is what makes the figures in finding "does not reproduce" unverifiable.

10. **Record state.** `docs/__templates__/test.md` still documents the retired vocabulary (`mark: " "   # THE VERDICT: " " | x | / | - | ! | ?`, `verdict_reason: ""   # required for / - ! ?`), so a hand-scaffolded check arrives with a character; `TESTING.md` never states the word vocabulary. `SNAPSHOT.yaml` `focus` still names PHASE-035 / FEAT-0118 / TASK-0473 / ISS-0195 — four commits of this phase landed without preflight step 3. This phase is `planned` with two features `done`. [[ISS-0200]] and [[ISS-0205]] are `open` although their work landed; [[ISS-0203]] and [[ISS-0204]] are `open` and homed at `PHASE-999-Future` while this note's `issues:` claims them and TASK-0496/0497 are `done`. `sweep._write_new_check` returns an in-memory `Item(mark=" ")` while writing `mark: todo`. [[TASK-0491]] is `done` with "the duplicate is gone rather than moved" unmet — `TST-0011` still carries its thirteen items, item 7 still duplicating `TST-0064`/`TST-0065` — and its Done section does not say so.

**Verdict: changes-requested** on this phase and on [[FEAT-0122-One-Human-Walked-Population]], [[FEAT-0123-The-Walk-Surfaces-Say-One-Thing]] and [[FEAT-0124-Gating-Is-Derived-From-Covers]]. Findings 1–6 are blocking. The engineering underneath is sound and the hard numbers hold; what fails is the join between the model and the surfaces (1), the direction of one fail-safe (2), and the gap between what the requirement boxes assert and what the code and the guards do (3–6).

## Closed 2026-08-18

Three features, eleven tasks, three requirements, seven issues — and a decision superseded inside the phase for the second time in two days, which is on the record rather than smoothed over.

**What it set out to do.** `level: acceptance` carried three independent claims — *a person walks it*, *its verdict is `mark:`*, *it gates the release* — and none followed from the word. ISTQB and the Agile Testing Quadrants both say so, which is why the decision was researched rather than argued. The three are separated: `level:` says what a test exercises, `command:` says who runs it and how it re-arms, `covers:` says what it gates.

**And ISS-0200 with it**: seven words for six characters, plus `rerun` — the state the corpus always had and could never say, because an invalidated check was written `mark: " "` beside an `invalidated_by:` block.

**Two exit criteria are reconciled**, both narrowly and both filed rather than waved: the tier is in the address and the other four filter axes are not, and a check still cannot be scoped to a release ([[ISS-0206-A-Check-Cannot-Belong-To-A-Release]]).

## What this phase should be remembered for

Not the merge. **Three separate changes reported success having done nothing**, and each was caught by a different mechanism:

1. A removal regex that needed a trailing newline the last frontmatter line does not have — it printed *"30 features cleaned"* having cleaned none. Caught by independent review counting the corpus.
2. A script that raised before its `write_text`, so a behaviour-preservation proof compared a file with itself and reported *identical*. Caught by asking which single repo's finding **should** have moved.
3. A new gate rule that referenced an out-of-scope variable and would have crashed rather than fired — every real repo reported **0 findings**, which is indistinguishable from working. Caught by building a two-note corpus that had to fail.

And a fourth shape: **four behaviours survived deletion with the whole suite green**, because each guard asserted something adjacent to the property it was named for. The equivalence test passed `subjects=None`, where the filter short-circuits — a tautology. The fail-closed guard skipped, because every orphan was settled. The sweep's tests asserted a note's fields rather than whether the suite could load it.

The lesson is one sentence: **a green result is evidence about the test, not about the code**, and the only way to learn which is to make the test fail on purpose.
