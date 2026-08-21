---
type: "[[issue]]"
id: ISS-0249
aliases: ["ISS-0249"]
title: "`retire_check` and `cover_check` are complete write paths that no front door reaches — the answer to TASK-0518 has nowhere to be recorded"
status: fixed
owner: user:edwin
created: 2026-08-20
updated: "2026-08-21"
reviewed_by: model:claude-opus-5
review_date: 2026-08-21
review_verdict: approved
review_response: "2026-08-21: test_no_public_write_in_note_writes_is_unreachable counted a substring and was vacuous for 4 of 13 writes, retire_check among them - `_serve_retire_check` contains `retire_check(`. It resolves ast.Call sites now, and the mutant (the real call replaced by a nonexistent one) fails it. || Second pass 2026-08-21: the ast.Call fix is confirmed non-vacuous (all 13 writes become reportable when their call sites are broken; the old predicate leaves exactly the 4). Finding A - two live tests deleted by that same rewrite - is restored."
review_response_date: 2026-08-21
source: ["[[TASK-0363]] cross-check against `note_writes`' callers, 2026-08-20"]
severity: medium
component: cockpit
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[TASK-0518-Review-Tier-Two-For-One-Time-Fixes]]", "[[FEAT-0131-The-Suite-Is-Refined]]", "[[ADR-0035-A-Release-Page-Reports]]", "[[TASK-0363-The-Read-Only-Guard]]"]
tests: []
---

# Two write paths, no caller

## What was measured

[[TASK-0363]]'s last step is *"cross-check against `note_writes`' documented callers"*. Walking the POST dispatch with `ast` and resolving every `note_writes.*` call inside each handler gives a clean answer to the question the task asked — **19 routes call `note_writes`, all 19 are loopback-guarded, and no unguarded route calls it at all.**

The same walk, run in reverse, answers a question the task did not ask. Of `note_writes`' public functions, these have **no caller anywhere outside `tests/`**:

| function | what it writes | reached by |
|---|---|---|
| `retire_check` | sets a check to `retired`, optionally promoting its replacement | nothing |
| `cover_check` | writes `covered_by:` on a check | nothing |

`resolve_note` is an internal helper used inside `note_writes` itself, and `legal_actions` / `next_issue_id` / `next_release_id` / `read_design_comments` are reads. Those four are accounted for. `retire_check` and `cover_check` are not: they are **writes**, they are tested (`tests/test_checks_view.py` exercises both, including their refusals), and no HTTP route, no renderer control and no CLI path invokes either.

## Why this is not merely tidy-up

**It is the missing half of a decision already on the table.** [[TASK-0518]] asks whether any of the 83 rested regression checks should *retire* rather than rest. Whatever the answer is, there is no way to record it: the function that performs a retirement exists and is correct, and nothing can call it. The decision would have to be executed by hand-editing 83 notes — which is the failure mode [[ADR-0009]] exists to prevent, since a hand edit is a write the record cannot attribute.

The same holds for `cover_check`: [[FEAT-0131]]'s premise is that the suite gets refined, and `covered_by:` is how one check subsumes another. `ledger.py:318` documents the guard `cover_check` applies. The guard is live prose about a function nothing calls.

## Why nothing flagged it

A write path with no caller is invisible to every check this repo runs. The validator walks *notes*, not code. The loopback enumeration walks the *dispatch*, so a function absent from the dispatch is absent from its domain by construction — it cannot report what it cannot see. And the tests pass, because the tests call the functions directly.

This is the [[REQ-0059]] shape once more, from a new angle: the guard's question is *"does every routed write check its caller?"*, and **"is every write routed?"** is a different question that nothing was asking.

## Not a security finding

Worth stating plainly, because the issue arrives out of a security cross-check. Unreachable from the dispatch means unreachable from the LAN: these two functions are the *safest* things in `note_writes`. The defect is that a capability was built and never connected, not that it is exposed.

## Options

1. **Wire both into `~checks`** behind the existing `_require_loopback` guard, as two more verdict-style actions. Smallest change; puts the retirement lever where the checks already are.
2. **Wire `retire_check` only**, and leave `cover_check` until [[FEAT-0131]] needs it. Answers [[TASK-0518]] without building ahead of a decision.
3. **Delete both** and their tests, on the grounds that a capability nobody asked for is debt. Rejected on sight for `retire_check` — [[TASK-0518]] is exactly someone asking for it — but it is the honest option for `cover_check` if the suite is never refined that way.

Recommendation: **option 2**, and take `cover_check` up with [[FEAT-0131]]. `retire_check`'s caller should land with [[TASK-0518]]'s answer rather than before it, so the button and the decision arrive together.

## Links

- Found by: [[TASK-0363]] — the read-only guard's `note_writes` cross-check
- Blocks the execution of: [[TASK-0518]]

## Independent review 2026-08-20 — approved

Fresh context, separate session; same model family, recorded in `reviewed_by`. Reproduced from scratch rather than read.

Walking `_route_post` with `ast` and resolving `note_writes.<fn>` calls per handler gives **19 routes calling `note_writes`, all 19 guarded, none unguarded** — exact.

The reverse walk over all 29 public `note_writes` functions confirms the table. `retire_check` and `cover_check` are the only two with no caller anywhere in `src/`, including inside `note_writes` itself. The four the note sets aside are accounted for as it says: `resolve_note` has 13 internal uses, `next_issue_id` and `next_release_id` one each, `read_design_comments` is called from `cockpit.py` — and every remaining public function is called from `server.py`. The only other references to the two are `tests/test_checks_view.py` and the prose at `ledger.py:318`. "Not a security finding" is right for the reason given, and the options are stated fairly.

**One correction.** `related:` links `[[TASK-0518-Rest-Or-Retire]]`, but that note is `TASK-0518-Review-Tier-Two-For-One-Time-Fixes.md` and its `aliases:` carry only `TASK-0518`. The validator resolves the reference by ID, so nothing errors; a reader clicking it lands nowhere.


## Fixed 2026-08-21 — one wired, one deleted, and the general form guarded

**`retire_check` was wired.** `POST /api/notes/retire-check`, loopback-guarded like the other 27, and a `Retire` control beside the mark on `~checks`. The dispatch partition test moved 27 -> 28 deliberately, and the sweep drives the new route over a real socket and requires a 403.

[[TASK-0518]] closed with *"retire nothing today"*, and this note's own recommendation was that the caller should land **with** that decision. It lands now for the reason that task records: *"if the answer here ever changes, there is no button to press."* A decision that changes later must not find that there is nothing to press.

**`cover_check` was deleted**, which is option 3 — and this note named the condition for it: *"the honest option for `cover_check` if the suite is never refined that way."* [[FEAT-0131]] — *the suite is refined* — closed `done` without ever needing it, so it never was. And [[FEAT-0138]]/[[REQ-0057]] end the field it wrote outright: nothing declares coverage in a note.

### The thing found while wiring it, which is this issue's point restated

`retire_check` wrote **`verdict_reason:`** — one of the seven fields [[ADR-0037]] moved into the ledger, and one this repo's validator **refuses** (`LEDGER-MOVED-FIELD`). So the function would have failed the commit it was part of, on its first real use, in a repo that keeps ledgers.

Nothing caught it, and nothing could: the unit tests call it directly and never validate the result, and every other check walks the corpus, which the function had never touched. **An unreachable write path is an untested one however many unit tests it has** — that is a sharper statement than the one this note filed, and it is the one the wiring produced.

The reason goes in the note **body** now (`## Retired <date>`), where a reader sees it.

`promote` went too. It wrote `tier: 3`, and [[ADR-0039]] decided there is no Tier 3 — `tier:` is read by no section and by no gate decision. A parameter whose only effect is a field nothing reads is a lever that moves nothing, and offering it from a front door would have been worse than leaving it unreachable.

### The general form, so the next one is caught by a test

`test_no_public_write_in_note_writes_is_unreachable` (`tests/test_checks_view.py`) walks `note_writes` with `ast`, takes every public function that calls `_write` — **13 of them** — and requires each to be named somewhere other than its own definition.

That is the question this issue found nobody was asking. The loopback enumeration walks the **dispatch**, so a function absent from it is absent from that rule's domain *by construction*: it cannot report what it cannot see. *"Is every write routed?"* is a different question, and it has a test now.

### Correction applied

`related:` linked `[[TASK-0518-Rest-Or-Retire]]`, a slug that note does not carry. It resolves by ID so nothing errored; a reader clicking it landed nowhere. Now `[[TASK-0518-Review-Tier-Two-For-One-Time-Fixes]]`.

## Independent review — 2026-08-21

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `f5ca55b..07602db`; the author's reasoning trace was not available to it. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — same model as the author, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant rather than read.


**Verdict: changes-requested.** The specific fix is correct and well guarded. The *general* guard built beside it — the part this note is proudest of — cannot detect its own subject.

### What holds

- `retire_check` is routed at `POST /api/notes/retire-check` (`server.py:758`), guarded like every other write. The count moved 27 → 28 in both `test_every_guarded_endpoint_refuses_a_remote_peer` and `test_no_guard_call_has_its_answer_discarded`, and the first drives the route **over a real socket** rather than asserting on source.
- `cover_check` is deleted, pinned by `assert not hasattr(note_writes, "cover_check")` — a runtime assertion, not a text match.

### Finding (high) — `test_no_public_write_in_note_writes_is_unreachable` is vacuous for 4 of 13 write paths

The guard's predicate is:

```python
unreachable = sorted(name for name in writes if callers.count("%s(" % name) <= 1)
```

`callers` is the concatenated **text** of six modules, and the count is a raw substring count. The handler for a write is named `_serve_<write>`, and `_serve_retire_check` **contains `retire_check(` as a substring** — twice, at its `def` line and its dispatch line. So the real call is not needed to satisfy the threshold.

Constructed and executed: I replaced `result = note_writes.retire_check(` in `server.py` with a call to a non-existent function, leaving no comment behind. `test_no_public_write_in_note_writes_is_unreachable` **passed**. It also passed when the call was replaced by a bare comment mentioning `retire_check(`.

Simulating the removal of every real `note_writes.<name>(` call, the guard still reports "reachable" for:

| write path | server.py hits | real calls | guard |
|---|---|---|---|
| `mark_released` | 3 | 1 | **vacuous** |
| `release_contents` | 3 | 1 | **vacuous** |
| `retire_check` | 3 | 1 | **vacuous** |
| `seal_ledger` | 3 | 1 | **vacuous** |

The remaining nine are genuinely guarded (2 hits, one of which is the definition). **`retire_check` and `release_contents` are the two write paths this very commit is about**, and both are in the vacuous set.

This is the pitfall the phase note names in its own closing section — *"a text assertion passes on a rule whose normalisation is in a comment"* — committed by the guard written to generalise this issue.

### What to change

Count **call sites**, not substrings: parse each caller module with `ast` and look for `ast.Call` whose func is an `ast.Attribute` named `<write>` on `note_writes` (the same technique the test already uses to find the writes, and the one `test_no_guard_call_has_its_answer_discarded` uses for `_require_loopback`). Then re-run against the mutant above and confirm it fails.

## Independent review — second pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `07602db..b635c39` — the first pass's findings and the author's reasoning trace were not available to it, only the seven claims as the notes state them. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]): same model as the author and as the first reviewer, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant.

**The `review_response:` above is accurate and the fix itself is sound; the verdict is `changes-requested` for what the same commit did to the file the fix lives in.**

**The guard is now real, and it is not vacuous in a new way.** The concern that a 617-name `called` set could swallow everything does not hold. I resolved the write set the same way the test does (13 public functions in `note_writes.py` calling `_write`), then for each name in turn rewrote **every resolved call site** of it across the six caller files to a nonexistent function and recomputed `writes - called`: **all thirteen become reportable**, each from a single real site (`note_writes.<name>(` in `server.py`). Under the old substring predicate the same mutants leave exactly `mark_released`, `release_contents`, `retire_check`, `seal_ledger` unreported — the 4-of-13 the response claims, reproduced independently. Residual, not a defect today: the guard would still pass silently for a *future* write whose name collides with any of the 617 attribute names called in those files.

**Finding A (high) — two live regression guards were deleted by this commit and nothing says so.** `tests/test_checks_view.py` went from 22 test functions to 20: `test_the_page_groups_by_surface_and_not_as_one_flat_list` ([[TASK-0520]] / [[ISS-0223]] / [[ISS-0234]]) and `test_a_stale_tick_is_not_drawn_as_done` ([[ISS-0234]]) are gone, and `grep -rn` over `tests/ src/ docs/` at `b635c39` finds neither name anywhere. They were not retired and they were not failing: `git diff --stat 07602db..b635c39 -- desktop/` is empty, and I re-executed both tests' assertion sets against `renderer.ts` at HEAD — all seven strings (`checks-area`, `for (const area of areas)`, `checkPercent(area.items)`, `checkProgress` absent, `items.filter((i) => i.stale)`, `stale} stale`, `(done.length / total)`) still hold. Both would have passed. Repo-wide `def test_` went 1829 → 1830, because three tests were added in `test_observed_coverage.py`, so the deletion is invisible in the headline. The removed block sits immediately after the rewritten tail of `test_no_public_write_in_note_writes_is_unreachable`, which is consistent with an over-wide edit. This is the phase's own signature defect one step worse than the version it was fixing: not a check that cannot fire, a check that no longer exists.

`test_no_public_write_in_note_writes_is_unreachable` is the last test in the file at `b635c39`; the deleted block followed it at `07602db`. Nothing in this note, in [[PHASE-037]] or in either `CHG-20260821-*` mentions a test removal.

## Independent review — third pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `b635c39..c9d6a82`; neither the author's reasoning trace nor either earlier reviewer's working was available to me beyond what these notes themselves record. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — the same model authored the work and ran both earlier passes, recorded in `reviewed_by` as provenance. Every count below was re-measured from the tree and every guard re-executed against a constructed mutant. **This verdict supersedes the second pass's on this note.**

**Approved.** Both halves check out, and I re-executed rather than read.

**The `ast.Call` guard is non-vacuous for exactly the names that were vacuous before.** For each of `retire_check`, `mark_released`, `release_contents` and `seal_ledger` in turn I rewrote its single real call site in `server.py` to a nonexistent function and ran `test_no_public_write_in_note_writes_is_unreachable`: **all four fail**. Under the old substring predicate they were the four that passed. The write set resolves to 13 and the test now asserts `len(writes) >= 13`, so a predicate that stops finding writes fails loudly instead of passing on an empty set.

**Finding A is discharged.** Both deleted tests are restored byte-identically from `07602db` — I extracted and diffed the functions — and `tests/test_checks_view.py` is back to 22 `def test_` functions. Neither is a passenger: four separate mutants against `renderer.ts` kill them. The deletion is recorded in [[PHASE-037]]'s closing section under its own heading rather than tidied away, which is the right disposal.

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
**Verdict: approved**, and I re-established it rather than inheriting it. The `ast.Call` predicate is non-vacuous for exactly the names the substring predicate let through: breaking the single real call site of `retire_check`, `mark_released`, `release_contents` or `seal_ledger` in `server.py` makes the test fail in each case. The write set resolves to 13 and the assertion has a floor, so a predicate that stops finding writes fails loudly instead of passing on an empty set. Finding A is discharged for good: both deleted functions are back, `tests/test_checks_view.py` is at 22 test functions, and — the thing worth checking a second time — **`c9d6a82..9a75f11` removes no test function from any file**, which I established by extracting and diffing the name sets rather than by comparing totals.

### The headline question: did fixing round three break anything

**No.** Test functions were extracted by name, file by file, at `f5ca55b`, `c9d6a82` and `9a75f11` and the sets diffed. `c9d6a82..9a75f11` **removes nothing**: three functions are added to `tests/test_observed_coverage.py` and no other file changes its set, 1835 → **1838**. Across the whole phase range `f5ca55b..9a75f11` the only removals anywhere are the seven `covered_by:`/promotion tests in `tests/test_checks_view.py`, each replaced in the same file by one guarding the mechanism's absence — that file's count is unchanged at 22 — so 1761 → 1838 with a net `+77` accounted for entirely by five new files (6 + 31 + 17 + 13 + 10).

**The emitter was run in loops rather than read.** Twelve scenarios against a temporary repo, counting ledger entries: `pass` then four `<skipped/>` runs → **2** entries (one `pass`, one invalidation); three skipped runs with no standing verdict → **0**; `pass`, skip, then three passing runs → **3**; declaration deleted, four runs → **2**; declaration moved to another file under the same name, four runs → **1**; moved *and* renamed, four runs → **1**; a `.kt`-declared check across five `.py` runs → never invalidated; `pass` then five failing runs → **2**; a passing sibling with a skipped sibling, four runs → **2**; a `manual` verdict under four skipped runs → **1** (untouched); a `manual` verdict under four failing runs → **2**. Every one is bounded, and the bound is structural: `resolve()` pops an invalidated check out of `verdicts()`, so both the `stale` and the `failing` branch leave the set by construction on the next run. Round three's finding 1 is genuinely closed.

**The three new tests are not passengers.** Reverting `elif seen and not held` to `elif seen` fails `test_a_skipped_sibling_is_not_laundered_into_a_pass` and nothing else. Restoring the round-two `stale` rule verbatim fails `test_a_skipped_test_invalidates_once_not_once_per_run` and `test_a_check_with_no_verdict_is_never_invalidated`. The two earlier repairs still hold their ground: `_withdrawn` returning `True` unconditionally fails the two toolchain tests, and returning `False` for a vanished declaration fails `test_deleting_the_covering_test_puts_its_check_back_on_the_run_list`.

**Round three's finding 3 reproduces exactly, every figure.** Driving the rule's own predicates over `git archive f5ca55b`: **56** owed, **51** terminal, **5** non-terminal, `30 done / 8 merged / 4 implemented / 9 fixed`, earliest `review_date` **2026-07-30** on **eight** notes — `CHG-20260730-Two-Features-Closed`, `FEAT-0045`, `ISS-0037`, `ISS-0057`, `ISS-0068`, `ISS-0069`, `PHASE-011`, `PHASE-013`. All 8 `merged` findings are `CHG-*`. The rule reports 51 at HEAD.

**Suite, validator, CI step set, all observed rather than reported.** `2063 passed, 3 skipped` in 269s; `validate-docs: OK`; `--as-committed` reports *"HEAD passes the full CI step set"* — validator OK, `sync-snapshot: up to date`, `generate-adapters: all 36 artifacts current`. Working tree clean at `9a75f11`.


## Independent review — fifth pass, 2026-08-21

Fresh context, separate session, `model:claude-opus-5`. Started from the notes and the diff `9a75f11..991838e`, widened to `f5ca55b..991838e`; no memory of authoring any of this and no access to the author's reasoning trace. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]). **This supersedes the fourth pass's verdict on this note.**

**Verdict: approved on this note's own subject, with one observation that belongs on [[PHASE-037]].** `retire_check` is routed and `cover_check` is deleted, as claimed. The observation: `retireCheckRow`'s docstring says the control *"lives on `~checks`, never on a release page ([[ADR-0035]])"*, and `renderer.ts:7610` puts it on every check row of `~release/<id>/<ITEM-ID>` by calling `buildCheckRow(item)` with `manual` defaulting to `true`. That is filed as the phase's exit-criterion-1 finding rather than as a change request here, because the routing this note delivered is correct — it is the claim about *where* the front door appears that is not.

**Suite, validator, CI step set — observed.** **2066 passed, 3 skipped** in 269s; `validate-docs: OK`; `--as-committed` reports *"HEAD passes the full CI step set"*. Working tree clean at `991838e`. The phase itself is `changes-requested` at this pass on two findings that do not touch this note — see [[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]].
