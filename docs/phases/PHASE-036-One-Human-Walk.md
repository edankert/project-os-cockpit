---
type: "[[phase]]"
id: PHASE-036
aliases: ["PHASE-036"]
title: "One human walk — the manual/acceptance split ends, and the surfaces stop carrying two of everything"
status: planned
order: 36
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
goal: "Finish what ADR-0031 started: collapse the two human-walked populations into one, so that a person sees one verb, one verdict field and one re-arming model — and fix the surfaces that still show the suite as two things or offer it in one undifferentiated list."
features:
  - "[[FEAT-0122-One-Human-Walked-Population]]"
  - "[[FEAT-0123-The-Walk-Surfaces-Say-One-Thing]]"
issues: ["[[ISS-0200-Marks-Versus-Statuses]]", "[[ISS-0201-Walk-And-Run-Vocabulary]]", "[[ISS-0202-Needs-A-Run-Versus-The-Tiers]]", "[[ISS-0203-Tier-Selection-Does-Not-Change-The-Page]]", "[[ISS-0204-The-Acceptance-Filter-Bar-Is-Congested]]", "[[ISS-0205-The-Sweep-Writes-Notes-A-Migrated-Repo-Cannot-Read]]"]
related: ["[[ADR-0033-A-Manual-Test-Is-An-Acceptance-Test]]", "[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[PHASE-035-Acceptance-Checks-Are-Notes]]", "[[TESTING-MODEL]]"]
---

# One human walk

## Why this is a phase and not an issue

Its goal is stateable without listing its parts — *a person walking a test sees one thing, not two* — and its exit criteria are measurements rather than a restatement of the task list. It is also not [[PHASE-035-Acceptance-Checks-Are-Notes]] reopened: that phase closed having merged the **types**, and this one exists because merging the types left two **populations** behind. Widening a closed phase to absorb its own consequence is how a phase stops ever closing.

## Where it came from

Edwin, reading the model note PHASE-035 produced: *"I think a manual test is always an acceptance test and can be marked as complete/ticked or if changes happen can be unticked."* [[ADR-0033-A-Manual-Test-Is-An-Acceptance-Test]] records why that is right and what the corpus says about it.

Five further concerns from the same reading became [[ISS-0200-Marks-Versus-Statuses]]..[[ISS-0204-The-Acceptance-Filter-Bar-Is-Congested]], and an independent review of those added a sixth: the sweep writes notes a migrated repo cannot read ([[ISS-0205-The-Sweep-Writes-Notes-A-Migrated-Repo-Cannot-Read]]), which is live in this repo and four times over in `your-trainer`.

## Order

1. **[[ISS-0205]] first, and out of band.** The sweep is writing invisible notes *now*. It does not wait for a decision.
2. **[[FEAT-0122-One-Human-Walked-Population]]** — the migration and the rules, gated on ADR-0033.
3. **[[FEAT-0123-The-Walk-Surfaces-Say-One-Thing]]** — the surfaces, which can only be simplified once there is one population to show.

## Exit criteria

- [ ] **No note in any repo carries `kind: manual` outside `level: acceptance`**, and the validator refuses the combination. Baseline 2026-08-18: 22 fleet-wide, 5 here, 15 in `your-trainer`.
- [ ] **One predicate answers "who runs this."** `cockpit._is_manual_test` and `obligations._is_owed` agree on every test in every repo — they disagree on **8 of 788** today.
- [ ] **`Needs a run` is gone as a population**, and what a person owes is unsettled Tier 1/2 rows. The Tests badge in every repo reads a number derived from the tiers, and it is not larger than the number it replaced.
- [ ] **Tier 1 and Tier 2 open different pages**, and the filter survives back/forward because it is in the address.
- [ ] **The acceptance page leads with the checks.** Measured today: 164 filter chips above the first row on `your-trainer`, 65 over 34 checks here — 1.9 chips per check, which is the worse ratio of the two.
- [ ] **A swept check is readable by the repo it was written into**, asserted on a migrated corpus rather than on a `check`-typed fixture.
- [ ] **The known duplicate is gone**: `TST-0011` item 7 and `TST-0064`/`TST-0065` no longer describe the same behaviour in two records.
- [ ] An independent review, from the corpus rather than from these notes.

## What this phase must not do

**It must not put acceptance rows on a badge.** [[ADR-0027-The-Registry-Counts-What-Needs-A-Person]] forbids per-check obligations and that survives ADR-0033 untouched: retiring `Needs a run` means the *manual* population stops asking individually, not that 669 acceptance rows start.

**It must not decide [[ISS-0200]] by accident.** Whether the verdict stays a character or becomes a word is a separate decision with its own evidence, and touching every note in the corpus is exactly the moment somebody would fold it in silently.
