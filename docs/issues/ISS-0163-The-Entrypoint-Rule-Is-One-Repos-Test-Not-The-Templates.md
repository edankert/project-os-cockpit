---
type: "[[issue]]"
id: ISS-0163
aliases: ["ISS-0163"]
title: "The entrypoint rule is one repo's pytest guard; the other eleven have no check that an automated test can be re-run"
status: "fixed"
phase: "[[PHASE-011-Unproven-Claims]]"
owner: user:edwin
created: 2026-08-13
updated: "2026-08-14"
source: ["[[ISS-0130]]'s fourth Next Action, which asked for a validator check and got a local test instead"]
severity: low
component: "docs-system"
parent: ""
related: ["[[ISS-0130-Nine-Automated-Tests-Cannot-Be-Re-Run-By-The-Machine]]", "[[ISS-0066-Test-Coverage-Registers-Drift-By-Hand]]", "[[ADR-0010]]", "[[project-os-dev#ADR-0011]]"]
tests: []
---

# The entrypoint rule stops at this repo's boundary

## Problem

[[ISS-0130]] asked for *"a validator check: an `automated` test at `passing` with no `command` cannot be re-verified"*. It got `tests/test_test_entrypoints.py` — correct for this repo, and unavailable to the other eleven, because `tools/scripts/validate-docs.py` is **template-owned** and editing it downstream is divergence the next sync reports.

The swept number that motivated the rule was itself fleet-wide: **1 of 92 tests across twelve repos** declared itself manual ([[FEAT-0086]]'s 2026-08-10 sweep). The other 91 are automated by the product's own predicate, and nothing anywhere checks that they can be executed.

## Shape of the fix

A `TEST-ENTRYPOINT` check beside the existing `TEST-FIELDS`, of the [[project-os-dev#ADR-0011]] shape — **a warning with a date**, not an error. It has to be a warning at first: turning it on as an error would fail twelve repos on day one for a condition none of them knew was a rule, which is the [[ISS-0057]] mistake.

`validate_docs_bundled.py` already has the two facts it needs in one loop: `command` and `status`.

## Homed in [[PHASE-011]] — after a day in [[PHASE-999]], and the detour was correct

Filed 2026-08-13 into [[PHASE-999]] because [[PHASE-011]] had reopened for [[ISS-0130]] and re-closed the same day: parking an *open* proposal inside a done phase is what `PHASE-CHILDREN` exists to catch, and nothing scheduled this.

It was scheduled the next morning and shipped, so it rejoins the phase whose subject it shares. A test that cannot be re-run is a claim nothing checked, which is PHASE-011's whole goal, and this is [[ISS-0130]]'s upstream half — same defect, the other eleven repos.

## Why it is filed rather than done

This repo does not own the validator, and an upstream change lands in twelve repos at once. That deserves the proposal it is getting rather than a downstream edit that a sync silently reverts.

## Expected

A repo that cannot re-run its own automated tests is told so by the same gate that already tells it a manual test has gone stale.

## Fixed upstream — 2026-08-14

`TEST-ENTRYPOINT` is in the template validator (`project-os` `0a44cdd`): a test at a runner status, not declared manual, with no `command:` — nothing can re-run it, so its status cannot be refreshed by machine.

A **warning with room to land**, per [[project-os-dev#ADR-0011]]. Measured with the new check across all twelve repos:

| repo | findings |
|---|---|
| yourtrainer-mcp | 15 |
| your-sudoku | 12 |
| your-health | 11 |
| obsidian-supernote-sync | 4 |
| your-trainer | 1 |
| **project-os-cockpit** | **0** |

**43 across five repos.** Erroring on day one would have failed all five for a rule none of them knew existed — [[ISS-0057]]'s mistake. This repo reads 0 because [[ISS-0130]] fixed its 22 notes the day before, which is the evidence the check is satisfiable rather than inert.

The exemption is narrow by design: a note must *say* it is manual. Silence does not exempt, because silence is the condition the check exists to find.
