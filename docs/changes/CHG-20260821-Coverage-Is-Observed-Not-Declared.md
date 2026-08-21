---
type: "[[change]]"
id: CHG-20260821-Coverage-Is-Observed-Not-Declared
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
