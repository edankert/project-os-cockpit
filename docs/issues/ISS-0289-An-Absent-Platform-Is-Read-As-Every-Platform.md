---
type: "[[issue]]"
id: ISS-0289
aliases: ["ISS-0289"]
title: "The acceptance endpoint reads an absent platform as `all`, so the Tests page and the gate band grade a two-ledger repo against every platform and report every check it has ever passed as owed"
status: fixed
phase: ""
owner: user:edwin
created: 2026-09-08
updated: 2026-09-08
source: ["Edwin, 2026-09-08, after ISS-0288 fixed the release page: 'Why do I still see 544 unchecked tests for your trainer! (this needs to be one step and this should be possible to automate)'"]
severity: high
component: publication
parent: ""
related: ["[[ISS-0288-The-Release-Gate-Ignores-The-Release-Platform]]", "[[ISS-0286-A-Check-Is-Owed-On-Every-Platform-That-Has-A-Ledger]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]"]
tests: []
---

# Not saying which platform is not the same as asking for all of them

## Problem

`/api/cockpit/acceptance` collapsed two different requests into one answer:

```python
_platform = (parse_qs(parsed.query).get("platform", [""])[0]).strip().lower()
if _platform == "all":
    _platform = ""
```

A person choosing **All** and a client that simply **did not send the parameter** both arrived as `""`, which is the union rule: a check clears only where every platform with a ledger cleared it.

Both of the renderer's callers are that second client. `mountReleaseGate` (`renderer.ts:1668`) and `renderChecksPage` (`:9130`) fetch the endpoint with no query string at all; the platform picker feeds `/api/cockpit/nav` and `/api/cockpit/context` and has never reached this route.

## Measured

`../your-trainer`, 2026-09-08, one open Android release and two ledgers:

| what the endpoint was given | unchecked |
| --- | --- |
| nothing — read as the union | **544** (445 feature + 99 regression) |
| `android`, its open release's platform | **67** (63 + 4) |

[[ISS-0288]] fixed the release *page's* own payload the same day. This is the same defect one layer out, and it is why the number on the Tests page and in the gate band did not move when that landed.

## Why it is worth a rule rather than a parameter

Edwin: *"this needs to be one step and this should be possible to automate."* Requiring every caller to remember the platform is a rule each new caller gets wrong once — the renderer got it wrong twice in the same file. The record already knows the answer: an open release says which platform it ships, and the release page has read that field since [[ISS-0288]].

## Fix

An **absent** `platform` parameter now asks the open release. `all` still means the union, because a person choosing it has said so, and a repo with no open release still gets the union, which is the correct fail-closed default from [[DES-0012-Tests-In-Two-Flows]] D4.

No client changed. Both renderer callers get the right number by asking the same question the release page asks.

## Guard

`tests/test_acceptance_platform_default.py`: absent resolves to the open release's platform, explicit `all` stays the union, an explicit platform overrides the open release, and no open release falls back to the union. The first case fails without the fix.
