---
type: "[[reference]]"
id: TESTING-MODEL
aliases: ["TESTING-MODEL"]
title: "The testing model — one type, a level scale, and who runs what"
status: active
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
reviewed_by: model:claude-opus-5
review_date: 2026-08-18
review_verdict: changes-requested
scope: tests
related: ["[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[ADR-0032-The-Verification-Link-Has-One-Direction]]", "[[ADR-0029-The-Acceptance-Mark-Vocabulary-Is-Minimals]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[ADR-0028-Work-Has-Three-Phases]]", "[[PHASE-035-Acceptance-Checks-Are-Notes]]"]
---

# The testing model

**Written down at Edwin's request, 2026-08-18, after PHASE-035 closed.** It describes what is *implemented*, not what was intended — where the two differ, the difference is named. The open questions this raised are [[ISS-0200-Marks-Versus-Statuses]] … [[ISS-0204-The-Acceptance-Filter-Bar-Is-Congested]].

## One type, one scale

There used to be two types. There is now one — `[[test]]` — and a scale, `level:`, running `unit → integration → system → e2e → acceptance`.

A note moves **along** that scale rather than **between** types, and that is the point: adding a `command:` is how a hand-walk becomes automated, without changing what the note is or breaking anything that points at it. Before [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]], a check could not be automated at all — the asymmetry that caused the merge.

## Who runs it: `command:` decides

`cockpit._is_manual_test` asks, in order:

1. **Does it declare a `command:`?** → the machine runs it. Full stop.
2. Otherwise, does `kind`/`automation`/`mode`/`method` say manual? → a person.
3. Otherwise, does the body have a Steps section? → a person.

The order matters and was a fix: a test with a pytest `command:` and a checklist-shaped body used to be offered a manual stepper and counted among the tests a scope asks a human to walk.

**But there are two rules, not one, and this note claimed otherwise.** `obligations._is_owed` decides the `Run` obligation — the thing that fills `Needs a run` and the badge — with its own predicate: *does `kind`/`level`/`runner` contain "manual"*, and it never reads `command:` at all. **8 of 788 fleet tests disagree between the two.** None involves a `command:`, so it is latent rather than live. [[REQ-0041-One-Answer-To-Who-Runs-This]] closes it.

## Two populations, one type

| | **executable test** | **acceptance test** (`level: acceptance`) |
|---|---|---|
| run by | `tools/scripts/run-tests.py`, from `command:` | a person, in `~checks` |
| result in | `status:` — `passing`/`failing`, **written by the runner from the exit code** ([[project-os-dev#ADR-0010]]) | `mark:` — `" " x / - ! ?`, with `verdict_date:` and `verdict_reason:` |
| rests at | `ready` (defined, never executed) | `active` |
| terminal | `retired` | `retired` |
| goes stale by | **time** — `last_verified:` against a threshold | **change** — `invalidated_by:` against `verdict_date:` |
| gates | a task/issue/feature reaching terminal (VERIFY) | the release (Tier 1/2 unsettled ⇒ blocked) |
| appears in | `Needs a run` when manual and `ready` | `Tier 1/2/3` groups, and `~checks` |

**Walking an acceptance test never touches `status:`.** That one rule carries the design.

## Why that rule is load-bearing

Three gates key on statuses an acceptance test does not hold, so all three stay off several hundred notes **by construction rather than by exemption**:

- the **independent-review gate** fires at `passing` — it rests at `active`;
- the **runner-only rule** governs `passing`/`failing` — its verdict is not a status;
- the **`Run` obligation** fires at `ready` — it rests at `active`.

The third is the dangerous one: it is what keeps a self-re-arming suite off a badge nobody could act on ([[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]). Because it is a construction and not a rule, one careless status write disarms it — so `ACCEPTANCE-STATUS` is a validator **error** if an acceptance test holds `ready`/`passing`/`failing`. `passing`/`failing` are excused **only** with a `command:`, since the runner then owns them. **`ready` is never excused**: that is the status the badge counts.

## The automation path

```yaml
covered_by: ["[[TST-0016-Seat-Resolution]]"]
automation: full
```

`Item.settled` is: the mark is settled **or** every test in `covered_by:` is `passing`. So automating a check discharges it. Three properties, each corrected during review:

- **all covers must pass, not any** — one passing and one failing used to settle it;
- **only an executable test counts** — a manual `passing` would let one hand-walk launder itself into another's automation;
- **resolved at load, never stored** — which is why a *failing* cover un-settles the check, and why a `ready` cover settles nothing. *"Not failing"* is not coverage.

`note_writes.cover_check` writes the link behind **six** refusals — empty `covered_by`, an automation value outside `full`/`partial`, `partial` without a reason, an unresolvable id, a target that is not a test, and a target with no `command:`. The last is the load-bearing one.

## The verification link

[[ADR-0032-The-Verification-Link-Has-One-Direction]]: **one encoding, one direction — the test's `covers:`**. A feature does not list its tests; surfaces derive that from a reverse index. The previous arrangement had three encodings (the directory path, the test's `features:`, the feature's `tests:`) and 10 of 61 edges already disagreed.

## What the cockpit implements today

**Tests view** — both populations, separated by `level:`, never mixed:

- `Needs a run` — **non-acceptance** manual tests at `ready`. Badge-bearing.
- `Resting · no feature in flight` — owed by type, quiet because their subject is not live ([[ADR-0028-Work-Has-Three-Phases]]).
- `Failing` / `Stale` / `Never verified` / `Verified`.
- `Tier 1/2/3` — the acceptance population.

**`~checks`** — the walk: tier → area → rows in `ordinal` order, the six-mark dialog, and filters over mark, tier, area, covers and automation.

**Writes** — mark, *Needs re-run* (clears the mark and names the invalidating change in one write), *Covered by*, promote (Tier 2 → 3) and retire. Each refuses rather than accept a claim nobody can check.

**Reads** — `## Runs` parses back, so a partly-walked procedure can say which steps stand. *(This belongs to the executable/manual half, not the acceptance surface it is filed under here: 14 notes fleet-wide carry a `## Runs` section, all in this repo, none at `level: acceptance`.)* A step's state is: a step's state is its result in the most recent run that **mentions** it, so a partial walk does not un-prove what it never reached.

## What is not true yet

**Nothing in the fleet is discharged by automation.** `your-trainer` has 203 notes whose bodies name 54 JVM test classes. **Four do name a `TST-*` id** (`TST-0050`, `TST-0051`, `TST-0364`, `TST-0586`) — this note originally said none did — but 199 do not, so the gate has almost nothing to check. The mechanism is proven; the corpus has not been given data it can act on.

**Release membership does not exist for tests.** A check cannot be marked as belonging to a release, so `your-trainer`'s iOS-only checks sit in the same undifferentiated blocking set as everything else. See [[ISS-0202-Needs-A-Run-Versus-The-Tiers]].

## Independent review

**2026-08-18, `model:claude-opus-5`, fresh context — the notes, the diff of `2c79393`, the code and the live payloads on `:8765`/`:8766`. Verdict: `changes-requested`.** Not because the model is wrong — most of it verified exactly — but because five statements are refutable as written and three material facts are missing. Same model family as the author, different session, no access to the authoring reasoning (ADR-0013).

### Verified against the code, unchanged

- **`_is_manual_test` precedence** — `cockpit.py:2609`. `command:` first, then `automation`/`kind`/`mode`/`method`, then a Steps section. The order is as documented. (One thing the summary omits: an explicit `automated`/`auto`/`ci` on any of those four keys returns *machine* before the Steps fallback is reached.)
- **The three gates and `ACCEPTANCE-STATUS`** — `REVIEW_SETTLED_STATUSES = {"tests": ("passing",)}`, `TEST_RUNNER_STATUSES = ("passing","failing")`, `OBLIGATIONS["test"] = Obligation(("ready",), …, "Run")`. `ACCEPTANCE_FORBIDDEN_STATUSES = ("ready","passing","failing")`; with a `command:` the forbidden tuple drops the two runner statuses and keeps `ready`. It is `report.error` unless grandfathered. Exactly as written.
- **`Item.settled` / `_resolve_coverage`** — all-covers-must-pass (`bool(...) and all(...)`, empty tuple first), executable-only (a cover without `command:` resolves to the literal `not-executable`), resolved at load and never stored. All three hold.
- **The Tests view group list** — six buckets plus the tier groups, each absent when empty, acceptance excluded by `level`. Correct.
- **A step's state is its result in the most recent run that *mentions* it** — `manual_test_step_state` walks runs oldest-first and overwrites per step text. Correct.
- **Nothing in the fleet is discharged by automation** — 669 of 669 acceptance notes carry `covered_by: []` (34 + 56 + 579). Verified, and sharper than the note puts it: `cover_check` refuses any test without a `command:`, and **`your-trainer` has exactly 2 tests fleet-eligible to be named** (`LicenseSeatResolverTest`, `Migration34To35Test`). 50 tests carry a `command:` across all twelve repos, 38 of them in this one.

### Refuted

1. **"`note_writes.cover_check` writes the link behind four refusals."** It is **six** — empty `covered_by`, an automation value outside `full`/`partial`, `partial` without a reason, an id the index cannot resolve, a target that is not a test, and the `command:` one. (A seventh `raise` is an I/O error.)
2. **"not one names a `TST-*` id"** — four `your-trainer` acceptance bodies do: `TST-0050`, `TST-0051` (naming TST-0009), `TST-0364` (TST-0010), `TST-0586` (TST-0008). The *point* survives — all four name manual tests, none is a `covered_by:` link — but the sentence is false and this document says it describes what is implemented.
3. **"One rule for *who runs this*, not two."** There are two. `obligations._is_owed` decides whether a person owes a `Run` with its own predicate — `"manual" in (kind|level|runner)` — which never reads `command:`. It is that rule, not `_is_manual_test`, that fills `Needs a run` and the Tests badge. Measured: **8 of 788 fleet tests disagree between the two predicates** today, none of them involving a `command:`, so the divergence is latent rather than live — but a note with a `command:` and `kind: manual` at `ready` would be offered to a person by the badge while `_is_manual_test` calls it automated.
4. **"`Needs a run` — non-acceptance manual tests at `ready`."** Incomplete in the way that matters: the bucket is `_owed_flag(...).owed`, which also requires the subject to be in flight. That missing clause is the whole of [[ISS-0202-Needs-A-Run-Versus-The-Tiers]] — this repo's one row is there *because* two `draft` requirements outvote a `backlog` feature.
5. **"`## Runs` parses back"**, placed under the `~checks` heading, reads as a property of the acceptance surface. It is not: **14 notes in the fleet carry a `## Runs` section, all in this repo, none at `level: acceptance`.** The read-back is real and it belongs to the executable/manual population.

### The staleness row is true of the code and false of the corpus

`Item.stale` implements exactly what the table says. But **all 669 acceptance notes carry `invalidated_by: {}`** — the change-driven half has no data anywhere in the fleet, which is the same caveat this document makes for automation and does not make here.

Worse, the data existed. `your-trainer`'s 54 `RE-RUN` annotations were migrated into `invalidated_by:` by ADR-0030 and were **still populated at the merge commit `0535db82`**. They were cleared afterwards by an uncommitted bulk write — 54 files, all mtime `13:17:41` on 2026-08-18, each diff exactly `invalidated_by: {…} → {}` plus an `updated:` bump. Consequence, measured by parsing the pre-migration suite at `5976a658`: **53 stale Tier 1/2 rows then, 0 now.** The gate's honest figure was 60 blocking + 53 stale; the release page's `Stale evidence` group is now permanently empty. The merge script's own parity fingerprint *does* include `invalidated`, so the merge did not do it — and the pilot could never have caught it either way, because this repo's 34 and `your-sudoku`'s 56 had zero invalidations on both sides. It is recoverable: `git -C ../your-trainer checkout -- docs/tests/acceptance`.

### Materially true and omitted

- **The sweep still writes the retired type, and a migrated repo cannot see what it writes.** `sweep._write_new_check` authors `type: "[[check]]"` with a `CHK-####` id. `acceptance.load` reads `[tests at level: acceptance] or [notes_by_type("check")]` — so in any repo that has migrated, the `or` never evaluates and a swept check is invisible: absent from `~checks`, absent from the tiers, and not blocking. Proved on a two-note corpus (one `TST` at `level: acceptance`, one `CHK`): the reader returns one item. The obligation is live right now — 1 feature owes a Sweep here, 4 on `your-trainer` — and `tests/test_acceptance_sweep.py` cannot fail on it, because its entire fixture is `type: "[[check]]"` notes, which is the branch that no longer exists in the three migrated repos.
- **The release page still speaks the pre-migration address.** `buildGateSection` renders each blocking row by `item.number` (`1.4.20`) and navigates to `/docs/${gate.rel}#${item.anchor}`, where `gate.rel` is the *directory* `tests/acceptance` and the anchor is the old document's. Every row therefore lands on the suite README with a dead fragment, while `item.rel` — the check's own note — sits unused in the same payload. `_acceptance_tier_groups` compensates for the notes shape by sending `~checks`; this call site does not.
- **`suite_rel`'s docstring claims it returns "the generated view" for notes shape.** It returns `CHECKS_REL`, a directory. Only the tier-group caller adds the `~checks` substitution; every other consumer of `rel` inherits the directory.

## Overturned 2026-08-18 — the two populations are one

This note described `Needs a run` and the tiers as two things and offered a distinction: *a manual test verifies a change and retires; an acceptance test names standing behaviour and re-arms.*

Edwin: *"Why would these manual tests not be true in a year? If the feature changes, or code the feature depends upon changes, the test has to be re-run. I think a manual test is always an acceptance test."*

**The first half was fiction and the corpus says so.** `TST-0024` does not retire when FEAT-0099 ships — it re-arms the next time that code changes. `your-trainer`'s `TST-0018`, cited here as the example of a retirement path, says of the half that stays: *"which stays manual permanently."* Zero of 22 manual tests fleet-wide have ever been retired by automation.

And the one genuine verify-this-build-then-stop case — this repo's `TST-0026` and its measured *"64 to 31"* claim — is **a Tier 3 acceptance test**, which TESTING.md already defines as *"one-time checks for a specific build, promoted or removed after a verified release."* It was never a separate kind of note.

[[ADR-0033-A-Manual-Test-Is-An-Acceptance-Test]] records the decision; [[PHASE-036-One-Human-Walk]] carries the work. **Read the two-population tables above as a description of what is implemented today, not as a design.**
