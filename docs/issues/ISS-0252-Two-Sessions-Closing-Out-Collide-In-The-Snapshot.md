---
type: "[[issue]]"
id: ISS-0252
review_verdict: approved
review_date: 2026-08-21
reviewed_by: model:claude-opus-5
aliases: ["ISS-0252"]
title: "Close-out requires naming `SNAPSHOT.yaml` and the snapshot is one hand-curated shared file, so two agent sessions closing out at once interleave in it — three collisions in one afternoon, two of which turned `--as-committed` red"
status: fixed
owner: user:edwin
created: 2026-08-20
updated: "2026-08-21"
source: ["hit three times while closing out PHASE-037 alongside a second session, 2026-08-20"]
severity: medium
component: tooling
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0251-A-Test-Backdates-A-Shared-Source-File]]", "[[FEAT-0055-Git-Assist]]"]
tests: []
---

# One file, two sessions, and the close-out rule points both at it

## Problem

`close-out-commit.sh` refuses to run with no paths — deliberately, because staging everything is *"`git add -A` wearing a different name"* ([[FEAT-0055-Git-Assist]]). But **`SNAPSHOT.yaml` is a path every close-out must name**: `sync-snapshot.py` writes counters and metrics into it at pre-commit, and the validator errors if they are stale.

So every session commits the same file, and two properties make that unsafe:

1. **`sync-snapshot.py` computes derived fields from the WORKING TREE**, which contains the other session's uncommitted edits.
2. **Membership — which items the snapshot carries — is hand curation the script deliberately leaves alone** (`CLAUDE.md`). So an item another session registers by hand sits in the shared file until *somebody* commits it, and that somebody may not be the session holding its note.

## Actual — three collisions, 2026-08-20

| # | what happened | effect |
|---|---|---|
| 1 | Pre-commit `sync-snapshot` computed `metrics.counts.issues_open` from the other session's uncommitted `ISS-0248` status change | `--as-committed` **red** (`METRICS`); self-healed when they committed |
| 2 | `3f62631` swept in their hand-written `PHASE-040:` entry while the note was still untracked | `--as-committed` **red** (`ITEM-FILE`); does **not** self-heal — a dangling reference stays dangling |
| 3 | The fix for 2 removed the entry — but between diagnosis and fix they had committed the note, so the removal deleted a **valid** registration | `--as-committed` **green**, and wrong |

**Collision 3 is the one to learn from.** The repair for a stale diagnosis was applied against a `git log` sixty seconds old, in a repo where a second session was committing. And the local check could not catch it: a snapshot entry with no note is an **error**, a note with no entry is a **warning**, so the asymmetry that caught the first mistake was silent on its over-correction.

## Expected

Two sessions closing out concurrently either both succeed, or the second is told to rebase — not silently commit half of the other's state.

## Evidence

- `3f62631`, `b1ec653`, `9d66d89` and the commit restoring the entry, in that order.
- `close-out-commit.sh` refuses with no paths; `sync-snapshot.py` reads the working tree; `CLAUDE.md`: *"which items the snapshot carries … are curation the script deliberately leaves alone."*
- [[ISS-0251]] is the same class in the test suite — a shared mutable file, two processes, a false red.

## Next Actions

- [x] **Built 2026-08-21: `close-out-commit.sh` names what it changes in `SNAPSHOT.yaml`'s `items:` membership** — added, removed, and separately the **dangling** case, in stderr and in the commit message. *"Collision 2 was visible in `git diff` and nobody looked."*
- [x] **The collision was constructed and the report watched firing.** `tests/test_close_out_snapshot_report.py`: a real git repo, an entry registered against a note that is in no commit, the report naming it `DANGLING`.
- [~] **A lock does not close collision 1, and that is a measurement rather than a decision.** See below. Whether concurrent sessions are a supported mode remains Edwin's call, and the answer changes nothing about what was built.
- [~] **Whether a note with no snapshot entry should stay a warning** stays a question. Widening it is `tools/instructions/SNAPSHOT.md`'s retention rule and it would fire on every pruned terminal item — that is a template-owned change with a fleet-wide blast radius and it is not this issue's to make.


## Fixed 2026-08-21 — the reporting half, and why the lock is not the other half

### What the script now prints

When `SNAPSHOT.yaml` is among the staged paths, it diffs `items:` membership between `HEAD` and the **index** — what this commit will actually contain — and prints:

```
close-out-commit: SNAPSHOT.yaml items: membership changed (ISS-0252):
  added:   PHASE-0040
  DANGLING (the note is in no commit; --as-committed will fail ITEM-FILE and it does not self-heal):
    PHASE-0040 -> docs/phases/PHASE-0040-P.md
```

…and puts the same text in the commit message, so `git log` carries it.

**The dangling case is named separately because it is the one that does not self-heal.** Collision 1 was a metrics mismatch that cleared itself when the other session committed. Collision 2 left a reference that stays dangling until somebody notices, and **the local validator cannot see it**: it reads the working tree, where the note exists. Only the committed state is missing it.

**It reports and never refuses.** A close-out that stops because a shared file moved under it is automation people disable — the same reason dirty files outside the scope are reported and left alone rather than treated as an error. `test_it_reports_and_never_refuses` pins that.

### The lock would not have prevented collision 1, and this is measured rather than argued

Next Action 1 offered a lock as the cheap fix *"if concurrent sessions are not a supported mode"*. Working through it:

**A lock serialises COMMITS. The collision is in the WORKING TREE.** `sync-snapshot.py` computes `metrics.counts` from the files on disk at pre-commit, and the other session's uncommitted edits are on that disk whether or not anybody holds a lock. Collision 1 — `issues_open` computed over another session's unsaved status change — reproduces exactly the same way with a lock in place.

So a lock buys serialised commits and nothing else, and the failure it is offered against is not a commit-ordering failure. **That does not make concurrent sessions a decided question** — it makes the lock the wrong answer to it. If they are unsupported the fix is procedural, not a mutex; if they are supported the snapshot has to stop being one hand-curated file, which is [[project-os-dev#ADR-0009]]'s territory and a much larger change.

Recorded here rather than acted on: an ADR-shaped decision is Edwin's, and this issue closes on the half that is mechanical and unambiguous.

### Collision 3 is still the one to learn from

The repair for a stale diagnosis deleted a **valid** registration, and the local check was silent — a snapshot entry with no note is an error, a note with no entry is only a warning, so the asymmetry that caught the first mistake said nothing about the over-correction. `test_a_removed_entry_is_named_too` makes a removal visible for that reason; the asymmetry itself is the open question above.

## Independent review — 2026-08-21

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `f5ca55b..07602db`; the author's reasoning trace was not available to it. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — same model as the author, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant rather than read.


**Verdict: approved.**

- **The dangling case is genuinely guarded.** I replaced `if hit.returncode != 0:` with `if False:` in `tools/scripts/close-out-commit.sh`; `test_an_entry_whose_note_is_in_no_commit_is_named_as_dangling` failed with the DANGLING line absent. The membership report itself still printed, which is the right split — the two are reported independently.
- **`git ls-files` resolves correctly.** The script does `cd "$ROOT"` at line 23 before the Python block runs, so the relative `file:` paths are interpreted against the repo root rather than the caller's cwd.
- **Reports, never refuses** — `test_it_reports_and_never_refuses` pins it, and that is consistent with the existing treatment of dirty files outside scope. A close-out that aborts because a shared file moved is automation people disable.
- The line-oriented YAML reader is the right call inside a commit-hook path (no PyYAML dependency, degrades to silence on a parse failure).

Correctly left open as an ADR-shaped question: whether concurrent close-out sessions are supported at all. Reporting the collision is not the same as preventing it, and this note says so.

No changes requested.

## Independent review — second pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `07602db..b635c39` — the first pass's findings and the author's reasoning trace were not available to it, only the seven claims as the notes state them. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]): same model as the author and as the first reviewer, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant.

**Approved, confirming the first-pass verdict.** No first-pass finding attached to this note; this commit added a review section only, and `close-out-commit.sh` is unchanged in `07602db..b635c39`. Not re-litigated in this pass.

## Independent review — third pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `b635c39..c9d6a82`; neither the author's reasoning trace nor either earlier reviewer's working was available to me beyond what these notes themselves record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran both earlier passes, recorded in `reviewed_by` as provenance. Every count below was re-measured from the tree and every guard re-executed against a constructed mutant. **This verdict supersedes the second pass's on this note.**

**Approved.** This commit adds a review section only; `close-out-commit.sh` is unchanged in `b635c39..c9d6a82`. Not re-litigated. The validator is green and `--as-committed` passes the full CI step set.

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
**Verdict: approved.** Untouched by this range beyond the review section, and its disposition is the honest one: the collision is real, a lock was measured and does not close it, and the note says so rather than shipping a mitigation that would look like a fix. `close-out-commit.sh` naming its membership changes — and the dangling case separately, because that is the one that does not self-heal — is the part that is buildable, and it is built and guarded.

### The headline question: did fixing round three break anything

**No.** Test functions were extracted by name, file by file, at `f5ca55b`, `c9d6a82` and `9a75f11` and the sets diffed. `c9d6a82..9a75f11` **removes nothing**: three functions are added to `tests/test_observed_coverage.py` and no other file changes its set, 1835 → **1838**. Across the whole phase range `f5ca55b..9a75f11` the only removals anywhere are the seven `covered_by:`/promotion tests in `tests/test_checks_view.py`, each replaced in the same file by one guarding the mechanism's absence — that file's count is unchanged at 22 — so 1761 → 1838 with a net `+77` accounted for entirely by five new files (6 + 31 + 17 + 13 + 10).

**The emitter was run in loops rather than read.** Twelve scenarios against a temporary repo, counting ledger entries: `pass` then four `<skipped/>` runs → **2** entries (one `pass`, one invalidation); three skipped runs with no standing verdict → **0**; `pass`, skip, then three passing runs → **3**; declaration deleted, four runs → **2**; declaration moved to another file under the same name, four runs → **1**; moved *and* renamed, four runs → **1**; a `.kt`-declared check across five `.py` runs → never invalidated; `pass` then five failing runs → **2**; a passing sibling with a skipped sibling, four runs → **2**; a `manual` verdict under four skipped runs → **1** (untouched); a `manual` verdict under four failing runs → **2**. Every one is bounded, and the bound is structural: `resolve()` pops an invalidated check out of `verdicts()`, so both the `stale` and the `failing` branch leave the set by construction on the next run. Round three's finding 1 is genuinely closed.

**The three new tests are not passengers.** Reverting `elif seen and not held` to `elif seen` fails `test_a_skipped_sibling_is_not_laundered_into_a_pass` and nothing else. Restoring the round-two `stale` rule verbatim fails `test_a_skipped_test_invalidates_once_not_once_per_run` and `test_a_check_with_no_verdict_is_never_invalidated`. The two earlier repairs still hold their ground: `_withdrawn` returning `True` unconditionally fails the two toolchain tests, and returning `False` for a vanished declaration fails `test_deleting_the_covering_test_puts_its_check_back_on_the_run_list`.

**Round three's finding 3 reproduces exactly, every figure.** Driving the rule's own predicates over `git archive f5ca55b`: **56** owed, **51** terminal, **5** non-terminal, `30 done / 8 merged / 4 implemented / 9 fixed`, earliest `review_date` **2026-07-30** on **eight** notes — `CHG-20260730-Two-Features-Closed`, `FEAT-0045`, `ISS-0037`, `ISS-0057`, `ISS-0068`, `ISS-0069`, `PHASE-011`, `PHASE-013`. All 8 `merged` findings are `CHG-*`. The rule reports 51 at HEAD.

**Suite, validator, CI step set, all observed rather than reported.** `2063 passed, 3 skipped` in 269s; `validate-docs: OK`; `--as-committed` reports *"HEAD passes the full CI step set"* — validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `9a75f11`.
