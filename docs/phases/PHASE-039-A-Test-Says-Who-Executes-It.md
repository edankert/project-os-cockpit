---
type: "[[phase]]"
id: PHASE-039
aliases: ["PHASE-039"]
title: "A test says who executes it, and every section is derived"
status: planned
order: 39
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
goal: "A test note records who executes it and what it covers. Nothing records whether an automated test passed, and no section a reader sees is filed by hand."
features: ["[[FEAT-0139-The-Suite-Is-The-Verdict]]", "[[FEAT-0140-Sections-Are-Derived-Not-Filed]]", "[[FEAT-0141-The-Contract-Says-It-Upstream]]"]
requirements: ["[[REQ-0058-An-Automated-Test-Carries-No-Verdict]]", "[[REQ-0059-A-Section-Is-Derived-Never-Filed]]", "[[REQ-0060-A-One-Time-Check-Names-Its-Issue]]"]
tasks: []
issues: ["[[ISS-0237-An-Automated-Check-Still-Blocks-The-Manual-Walk]]", "[[ISS-0238-There-Is-Nowhere-To-Put-An-Automated-Check]]", "[[ISS-0239-The-Runner-Stamps-Failing-On-A-Missing-Device]]"]
related: ["[[ADR-0038-The-Suite-Is-The-Verdict]]", "[[ADR-0039-Three-Sections-Derived-Not-Filed]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ADR-0034-Three-Axes-Not-One-Word]]", "[[DES-0012-Tests-In-Two-Flows]]"]
tags: [testing, schema]
---

# A test says who executes it

## Goal

Two fields already answer every question this corpus asks about a test — `command:` says who executes it, `covers:` says what it is about. A third thing, `tier:`, restated part of the second, and a fourth, `status:`, restated what CI already knows. This phase removes both restatements and derives what a reader sees from what is left.

**Nothing here starts until [[ADR-0038]] and [[ADR-0039]] are accepted.** Both read `proposed`. That is the same gate [[ADR-0030]], [[ADR-0031]], [[ADR-0034]] and [[ADR-0037]] each used: the phase is documented in full, and no note migrates.

## Scope

- An automated test stops carrying a verdict; CI is the verdict ([[ADR-0038]]).
- The three sections — Feature tests, Regression tests, Automated tests — are derived from `covers:` and `command:`, and `tier:` is read nowhere ([[ADR-0039]]).
- `Broken command` becomes a section: an automated test whose `command:` no longer resolves.
- The rules land upstream in `project-os` and sync to the fleet.
- No UI string says *run* or *walk*.

## Out of Scope

- **Making CI execute in the fleet repos** ([[ISS-0209]]). The gate reaches no repo holding a check, and this phase must not claim otherwise.
- **Stripping `tier:` from the 671 notes that carry it.** The field stops being read; removing it is a later migration once the derived sections have been read against for a while.
- **Excavating the 67 destroyed `area:` values** from `your-trainer`'s history.
- Observed coverage ([[FEAT-0138]]), which is the next argument and not this one.

## Exit Criteria

- [ ] No note carrying a `command:` holds `ready`, `passing`, `failing`, `last_run:` or `exit_code:` — checked, not asserted
- [ ] `tier:` is read by no code path; `GATING_TIERS` and `PERMANENT_TIERS` are gone
- [ ] The three sections are derived identically in both front doors
- [ ] The gate delta is measured **per repo** before each gate change lands
- [ ] `TESTING.md` and `STATUSES.md` carry the rules upstream, and the fleet is synced
- [ ] No UI string contains *run* or *walk*
- [ ] Deleting a covering test puts its check back on the list — proved on constructed input, because the corpus holds zero instances
