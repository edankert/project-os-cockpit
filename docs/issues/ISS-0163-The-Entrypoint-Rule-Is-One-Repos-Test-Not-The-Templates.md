---
type: "[[issue]]"
id: ISS-0163
aliases: ["ISS-0163"]
title: "The entrypoint rule is one repo's pytest guard; the other eleven have no check that an automated test can be re-run"
status: "open"
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-08-13
updated: "2026-08-13"
source: ["[[ISS-0130]]'s fourth Next Action, which asked for a validator check and got a local test instead"]
severity: low
component: "docs-system"
parent: ""
related: ["[[ISS-0130-Nine-Automated-Tests-Cannot-Be-Re-Run-By-The-Machine]]", "[[ISS-0066-Test-Coverage-Registers-Drift-By-Hand]]", "[[ADR-0010]]", "[[ADR-0011]]"]
tests: []
---

# The entrypoint rule stops at this repo's boundary

## Problem

[[ISS-0130]] asked for *"a validator check: an `automated` test at `passing` with no `command` cannot be re-verified"*. It got `tests/test_test_entrypoints.py` — correct for this repo, and unavailable to the other eleven, because `tools/scripts/validate-docs.py` is **template-owned** and editing it downstream is divergence the next sync reports.

The swept number that motivated the rule was itself fleet-wide: **1 of 92 tests across twelve repos** declared itself manual ([[FEAT-0086]]'s 2026-08-10 sweep). The other 91 are automated by the product's own predicate, and nothing anywhere checks that they can be executed.

## Shape of the fix

A `TEST-ENTRYPOINT` check beside the existing `TEST-FIELDS`, of the [[ADR-0011]] shape — **a warning with a date**, not an error. It has to be a warning at first: turning it on as an error would fail twelve repos on day one for a condition none of them knew was a rule, which is the [[ISS-0057]] mistake.

`validate_docs_bundled.py` already has the two facts it needs in one loop: `command` and `status`.

## Homed in [[PHASE-999]], deliberately

[[PHASE-011]] reopened for [[ISS-0130]] and re-closed the same day; parking an upstream proposal inside it would have left a done phase carrying unresolved work, which is what `PHASE-CHILDREN` exists to catch. Nothing currently schedules this, and [[PHASE-999]] is the honest way to say so.

## Why it is filed rather than done

This repo does not own the validator, and an upstream change lands in twelve repos at once. That deserves the proposal it is getting rather than a downstream edit that a sync silently reverts.

## Expected

A repo that cannot re-run its own automated tests is told so by the same gate that already tells it a manual test has gone stale.
