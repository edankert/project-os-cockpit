---
type: "[[reference]]"
id: TESTING-MODEL
aliases: ["TESTING-MODEL"]
title: "The testing model — one type, a level scale, and who runs what"
status: active
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
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

The order matters and was a fix: a test with a pytest `command:` and a checklist-shaped body used to be offered a manual stepper and counted among the tests a scope asks a human to walk. One rule for *who runs this*, not two.

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

`note_writes.cover_check` writes the link behind four refusals; the load-bearing one is that the named test must declare a `command:`.

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

**Reads** — `## Runs` parses back, so a partly-walked procedure can say which steps stand: a step's state is its result in the most recent run that **mentions** it, so a partial walk does not un-prove what it never reached.

## What is not true yet

**Nothing in the fleet is discharged by automation.** `your-trainer` has 203 notes whose bodies name 54 JVM test classes, and not one names a `TST-*` id — so the gate has nothing to check. The mechanism is proven; the corpus has not been given data it can act on.

**Release membership does not exist for tests.** A check cannot be marked as belonging to a release, so `your-trainer`'s iOS-only checks sit in the same undifferentiated blocking set as everything else. See [[ISS-0202-Needs-A-Run-Versus-The-Tiers]].
