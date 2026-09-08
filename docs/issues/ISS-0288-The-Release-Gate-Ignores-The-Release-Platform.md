---
type: "[[issue]]"
id: ISS-0288
aliases: ["ISS-0288"]
title: "The release page filters its contents by the release's platform and grades its gate against every platform, so a two-ledger repo is told every check it has ever passed is owed again"
status: fixed
phase: ""
owner: user:edwin
created: 2026-09-08
updated: 2026-09-08
source: ["Edwin, 2026-09-08, walking your-trainer's 2.2.0 release: 'I can still not run the acceptance tests, the release-gate says that there are 635 checks todo ...'"]
severity: high
component: publication
parent: ""
related: ["[[ISS-0261-A-Release-Is-Offered-Features-Its-Platform-Cannot-Ship]]", "[[ISS-0286-A-Check-Is-Owed-On-Every-Platform-That-Has-A-Ledger]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[DES-0012-Tests-In-Two-Flows]]"]
tests: []
---

# One page, two platform rules

## Problem

`publication.release_payload` asks the platform question twice and answers it two different ways.

`shipping_in` reads `_platform_of_release` and filters the release's contents by it — that is [[ISS-0261-A-Release-Is-Offered-Features-Its-Platform-Cannot-Ship]], fixed. Twelve lines later the same function calls `acceptance.gate_payload` with **no platform at all**, so the gate falls to the union rule: a check clears only where *every* platform with a ledger cleared it.

The union rule is right and deliberate ([[DES-0012-Tests-In-Two-Flows]] D4): *"a release that has not said which platform it ships takes them all"*. The defect is that this release **has** said, in the frontmatter the same function already read, and the gate is not asking.

## Measured

`../your-trainer`, 2026-09-08, one Android release open (REL-0017, `platform: android`) and 636 acceptance checks:

| what the gate is given | checks reading unsettled |
| --- | --- |
| nothing — the union | **635** |
| `android`, the release's own platform | **67** |

Its Android ledger resolves 569 checks and its iOS ledger holds one entry, so the intersection is empty and the page reports a repo that has walked 569 checks as having walked none.

## Why it matters more than a wrong number

The gate is what a person walks a release down against. At 635 it is unusable: every check that ever passed is back on the list, the release can never go green, and there is no signal left in the count. Edwin hit exactly this preparing a real release and could not proceed.

A single-platform repo is unaffected — the union over one ledger is that ledger — which is why this survived: eleven of twelve fleet repos have at most one.

## Expected

`release_payload` passes the release's platform to `gate_payload`, the same value `shipping_in` already uses. A release with no `platform:` keeps the union, unchanged, because that is D4's rule and it is correct.

## Notes

The renderer has the same omission twice more: `mountReleaseGate` (`renderer.ts:1668`) and `renderChecksPage` (`:9130`) fetch `/api/cockpit/acceptance` with no `platform`, though the endpoint accepts one and `verdictPlatform()` already computes it. Those are the Tests page and the gate band; this issue fixes the release page's own payload, which is the one that has a release to read the platform from. The renderer pair is [[ISS-0286-A-Check-Is-Owed-On-Every-Platform-That-Has-A-Ledger]]'s neighbourhood and is not fixed here.

## Fixed 2026-09-08

`release_payload` passes `_platform_of_release(index, _rel_id)` to `gate_payload` — the same value `shipping_in` twelve lines above already uses. One argument.

`tests/test_release_gate_platform.py` pins three cases and **fails without the fix**: an Android release graded on the Android ledger (the regression, and the only one that goes red when the argument is removed), an iOS release graded on the iOS ledger, and a release naming no platform still taking the union. Two ledgers in the fixture, because one cannot tell a platform-scoped gate from a platform-blind one.

Verified against `../your-trainer` with REL-0017 open: **635 → 67**, and the nine PHASE-021 checks are offered for the features 2.2.0 carries.
