---
type: "[[change]]"
id: CHG-20260821-Coverage-Is-Observed-Not-Declared
review_verdict: changes-requested
review_response: "2026-08-21: the impact list was short by two files (TAXONOMY.md, migrate-acceptance-checks.py) and both are now corrected and listed; the emitter's `--by` filter is removed."
review_response_date: 2026-08-21
review_date: 2026-08-21
reviewed_by: model:claude-opus-5
aliases: ["CHG-20260821-Coverage-Is-Observed-Not-Declared"]
title: "A test declares the check it covers and the run emits the verdict — `covered_by:` and `cover_check` are removed, and deleting a covering test puts its check back on the run list"
status: merged
owner: user:edwin
created: 2026-08-21
updated: "2026-08-21"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[FEAT-0138-Coverage-Is-Observed-Not-Declared]]", "[[REQ-0057-Coverage-Is-Observed-From-A-Run]]", "[[REQ-0039-A-Covering-Test-Settles-The-Check]]", "[[TASK-0542-The-Test-Declares-The-Check]]", "[[TASK-0543-The-CI-Emitter-Writes-Into-The-Working-Ledger]]", "[[ISS-0249-Two-Check-Write-Paths-Reach-No-Front-Door]]", "[[ISS-0198-Automation-And-Covered-By-Are-Empty-On-All-669-Checks]]", "[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]", "[[ADR-0037-A-Verdict-Is-An-Event]]"]
tags: [change, acceptance, ledger]
---

# Coverage is observed, not declared

## What changed

**A test declares the check it covers, in its own source.**

```python
def test_every_guarded_endpoint_refuses_a_remote_peer(remote_server):
    # Covers: TST-0076
```

One comment prefix per language (`.py`, `.kt`, `.java`, `.swift`), findable by `grep -rn "Covers: TST-" .`, and no annotation library in either toolchain.

**A run emits the verdict.** `tools/scripts/emit-coverage.py` reads the run's **JUnit XML** — pytest writes it with `--junitxml`, gradle writes it natively — and appends to the working ledger for its platform:

| what the run saw | what it appends |
|---|---|
| every declaring test passed | `mark: pass`, `method: automated`, `by:` naming the tests |
| a declaring test failed | an **invalidation** |
| a check this emitter covered, not observed at all | an **invalidation** |

**`covered_by:` is gone**, from `acceptance.Item`, from `Item.settled`, from the loader, and from `note_writes` — `cover_check` is deleted. [[REQ-0039]] is `superseded` by [[REQ-0057]].

**New:** `tools/scripts/coverage-declarations.py` (`--scan` / `--check`) and `.github/workflows/observed-coverage.yml`.

**Two files were stranded by the removal and are corrected** (found by independent review, 2026-08-21):

- `tools/instructions/TAXONOMY.md` still stated *"a `passing` test named in another's `covered_by:` settles it"* — false the moment `_resolve_coverage` was deleted. It is template-owned, so the correction is owed upstream and is made here because a reference describing a removed mechanism is worse than a sync divergence.
- `tools/scripts/migrate-acceptance-checks.py` still wrote `covered_by: []` into every note it produced, a field this repo's validator refuses (`LEDGER-MOVED-FIELD`). It has already run everywhere it was needed, which is why nothing caught it.

## Why

`covered_by:` was a **standing claim** and it rotted silently: rename, delete or `@Ignore` the covering test and the note kept asserting coverage while the check left the run list **permanently, with no signal**. That is worse than a stale verdict, because a stale verdict still asks.

It had also never worked. The field held nothing on **671 of 671** checks fleet-wide ([[ISS-0198]]), and the one function that could have filled it was reachable from no front door ([[ISS-0249]]) — so the mechanism was correct, tested, and had never settled a single check anywhere.

## The failing-test decision, made rather than defaulted

[[TASK-0543]] named two options and the answer is a third.

`mark: fail` is a **walk** verdict in the blocking vocabulary, so emitting it would put a machine-driven population straight into the release gate — the change [[ADR-0031]] recorded as a risk rather than discovering later. Emitting **nothing** leaves the last green run's `pass` standing over a test that now fails, which is the stale-verdict shape this phase exists to remove.

An **invalidation** says what is true: the evidence no longer holds. `ledger.resolve` already clears a standing verdict on one, so no vocabulary was added.

## Behaviour a caller can see

- `note_writes.cover_check` **no longer exists**. A caller gets `AttributeError`.
- `note_writes.retire_check` lost its `promote` parameter, and writes its reason into the note **body** rather than into `verdict_reason:` — a field this repo's validator refuses.
- A hand-written `covered_by:` no longer settles a check on any surface.
- Two new scripts and one new workflow; neither script pushes anything.

## Limits, stated

[[ISS-0209]] is unresolved: **the acceptance gate runs in no repo that holds a check.** The emitter runs in `project-os-cockpit` and nowhere the fleet's data lives, so *"deleting a covering test puts its check back on the run list"* is proved **here** and the fleet is not covered. The workflow's own header says so.

Three checks are declared today — [[TST-0069]], [[TST-0075]], [[TST-0076]] — each mapped by reading the check against the test. The other 31 are person-facing walks and are deliberately undeclared: an undeclared check stays on the run list, which is the conservative direction.

## Independent review — 2026-08-21

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `f5ca55b..07602db`; the author's reasoning trace was not available to it. What was independent is the **context**, not the model family ([[project-os-dev#ADR-0013]]) — same model as the author, recorded in `reviewed_by` as provenance. Every number below was re-measured and every guard re-executed against a constructed mutant rather than read.


**Verdict: changes-requested.** The inversion is the right design, the removal of `covered_by:` is safe and honestly measured, and the headline criterion is genuinely proved. Two defects remain in the emitter, one of them the same class of silent rot this feature exists to end.

### What survived refutation

- **The `covered_by:` removal is safe.** Re-measured across all 12 `SNAPSHOT.yaml`-bearing repos under `~/Dev/repos/`, against `git archive HEAD` as well as the working tree: **671 acceptance checks at HEAD**, of which 635 carry the key and **every single value is the literal `[]`**. Zero non-empty values anywhere, in either tree. No `.base` view, no `.ts`/`.js`, and no script *reads* the field — the only code touching the name refuses it (`LEDGER_MOVED_FIELDS`) or strips it. Removing it changes no repo's gate, exactly as claimed.
- **The headline criterion is proved, not asserted.** `test_deleting_the_covering_test_puts_its_check_back_on_the_run_list` settles a check by a run, deletes the test file, runs again, and asserts the check is blocking. That is a real construction.
- **A `manual` walk survives the stale path.** Constructed: a `method: manual` verdict, then the covering test deleted. The emitter printed *"nothing changed"* and the verdict stood.

### Finding 1 (medium) — the invalidation set is keyed on `--by`, so renaming the CI job makes every prior verdict permanently un-invalidatable

`plan()` computes:

```python
stale = sorted(check for check, verdict in current.items()
               if verdict.method == "automated" and verdict.by == by
               and check not in passing and check not in failing)
```

`by` comes from `--by`, and `.github/workflows/observed-coverage.yml` passes the literal `"ci:observed-coverage"` — a string tied to the workflow's name.

Constructed and executed: settle a check with `--by ci:test`; delete the covering test; run again with `--by ci:renamed-job`. Output was *"nothing changed (0 check(s) observed passing)"* and the check stayed **settled and non-blocking**, with no covering test in the repo.

This note already records catching this class once — *"the invalidation set was computed from the declarations, so deleting the test … removed the check from the set that could be invalidated"*. Keying on `by` is the same defect through a different field: the set that can be invalidated depends on something that can change independently of the evidence. Renaming a CI job is an ordinary edit, and the failure is silent and permanent.

### Finding 2 (medium) — *"Only this emitter's own verdicts"* is false on the failing branch

`plan()`'s docstring states: *"**Only this emitter's own verdicts.** A person's `manual` walk and a `migration` backfill are not the emitter's to overturn."* The `failing` loop in `main()` carries no `method`/`by` filter at all:

```python
for check, tests in sorted(failing.items()):
    if check not in current:
        continue
    ... _ledger.append(..., invalidated_by=run, ...)
```

Constructed: a `method: manual`, `by: user:edwin` verdict, then a run in which a declaring test fails. The emitter invalidated the person's hand walk and the check became blocking.

The *behaviour* is defensible — the evidence is contradicted, and invalidating is the conservative move. The **documented claim is not**, and nothing tests it: `tests/test_observed_coverage.py` never constructs a `manual` or `migration` verdict. Either narrow the code to match the docstring or narrow the docstring to match the code, and add the case.

### Finding 3 (low) — the documentation impact list is short by two files

The `CHG` note's impact list names neither:

- `tools/instructions/TAXONOMY.md:61`, which still states *"a `passing` test named in another's `covered_by:` settles it"*. This commit deleted `_resolve_coverage`, so that sentence is now false. It is template-owned and present in four fleet repos, so the fix belongs upstream — but it should be *named*.
- `tools/scripts/migrate-acceptance-checks.py:149`, which still writes `covered_by: []` into every note it emits while `LEDGER_MOVED_FIELDS` refuses the field in any ledger-keeping repo. Pre-existing rather than introduced here, but this change is what strands it, and eight of twelve repos have not migrated.
