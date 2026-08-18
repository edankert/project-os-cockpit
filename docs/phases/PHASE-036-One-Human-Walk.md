---
type: "[[phase]]"
id: PHASE-036
aliases: ["PHASE-036"]
title: "Three axes — what a test exercises, who runs it and what it gates stop being one word, and gating is derived from `covers:` at any granularity"
status: planned
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

- [ ] **`kind:` is gone from the schema.** `command:` answers who runs a test, and nothing else claims to. Baseline 2026-08-18: 22 notes carry `kind: manual` outside `level: acceptance` — 5 here, 15 in `your-trainer`, 2 in `your-health`.
- [ ] **An item of any type can be gated by a test, through `covers:` alone** — a task, an issue, a requirement, a feature and a release, with no rule anywhere keyed on the test's level or on who runs it.
- [ ] **The derived gate reproduces the tier gate exactly** before the tier rule is retired, measured per repo. Baseline: 0 / 56 / 60 blocking. **Precondition: 83 of 669 acceptance tests carry an empty `covers:` and gate nothing until backfilled.**
- [ ] **Re-arming follows execution**: every test with no `command:` re-arms by `invalidated_by:`, at any level, and the 90-day threshold no longer applies to it.
- [ ] **One predicate answers "who runs this."** `cockpit._is_manual_test` and `obligations._is_owed` agree on every test in every repo — they disagree on **8 of 788** today.
- [ ] **`Needs a run` is gone as a population**, and what a person owes is unsettled Tier 1/2 rows. The Tests badge in every repo reads a number derived from the tiers, and it is not larger than the number it replaced.
- [ ] **Tier 1 and Tier 2 open different pages**, and the filter survives back/forward because it is in the address.
- [ ] **The acceptance page leads with the checks.** Measured today: 164 filter chips above the first row on `your-trainer`, 65 over 34 checks here — 1.9 chips per check, which is the worse ratio of the two.
- [ ] **A swept check is readable by the repo it was written into**, asserted on a migrated corpus rather than on a `check`-typed fixture.
- [ ] **The known duplicate is gone**: `TST-0011` item 7 and `TST-0064`/`TST-0065` no longer describe the same behaviour in two records.
- [ ] An independent review, from the corpus rather than from these notes.

## What this phase must not do

**It must not put acceptance rows on a badge.** [[ADR-0027-The-Registry-Counts-What-Needs-A-Person]] forbids per-check obligations and that survives ADR-0033 untouched: retiring `Needs a run` means the *manual* population stops asking individually, not that 669 acceptance rows start.

**It must not decide [[ISS-0200]] by accident.** Whether the verdict stays a character or becomes a word is a separate decision with its own evidence, and touching every note in the corpus is exactly the moment somebody would fold it in silently. [[ADR-0034-Three-Axes-Not-One-Word]] asks for *one outcome vocabulary* and deliberately does not say what it is written as.

**It must not let the gate get quieter.** The derived gate replaces a rule that has no holes with one that has 83 of them until the backfill lands. A gate that goes quiet during a migration is the failure this project has already paid for once, in a repo where nobody was looking.
