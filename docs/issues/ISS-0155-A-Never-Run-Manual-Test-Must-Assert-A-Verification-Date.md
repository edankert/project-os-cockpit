---
type: "[[issue]]"
id: ISS-0155
aliases: ["ISS-0155"]
title: "A manual test that has never been run cannot satisfy the schema without asserting a verification date"
status: "fixed"
owner: user:edwin
created: 2026-08-13
updated: "2026-08-14"
source: ["Hit while authoring [[TST-0024-Remote-SSH-Workspace-Walk]], 2026-08-13"]
severity: medium
component: docs-validator
parent: ""
related: ["[[TST-0024-Remote-SSH-Workspace-Walk]]", "[[ADR-0010]]", "[[FEAT-0018]]"]
tests: []
---

# A never-run manual test must assert a verification date

## Problem

`TEST-FIELDS` requires every manual test — any test with no `command:` — to carry a non-empty `last_verified:`, regardless of status:

```
ERROR [TEST-FIELDS] TST-0024 is a manual test with no last_verified:; record when the procedure was last performed, or give it a command: so it can be executed (docs/tests/TST-0024-Remote-SSH-Workspace-Walk.md)
```

But `ready` is documented as the state a new test note is created in — *"`ready` means defined but not yet executed"* (`docs/__templates__/test.md`). A manual test therefore cannot legally exist in the state the template says it starts in. The only ways out are to type a date for a run that never happened, or to give a genuinely manual procedure a fake `command:`.

## Why it matters

The field is the staleness clock (`STATUSES.md`, "Staleness"). Seeding it with an authoring date makes the record say *verified on this day, going stale from this day* about a procedure nobody performed — which is the class of unproven claim [[FEAT-0018]] exists to surface, produced here by the validator itself.

It is not hypothetical: [[TST-0024]] was authored on 2026-08-12 with `last_verified: "2026-08-12"` and a paragraph in its body explaining that the date did not mean what the field means. The prose disclaimer is the workaround, and prose is not what any tool reads.

## Expected

One of:

1. `last_verified:` is required only when `status:` is a settled/verified state, not at `ready`/`draft`; or
2. an explicit "never run" value is legal and renders as unverified rather than stale; or
3. the requirement is stated as it actually behaves, and the templates stop saying `ready` means not-yet-executed.

## Actual

Any manual test must name a date, so "never run" and "run once long ago" are indistinguishable in the field the staleness signal reads.

## Notes

`tools/scripts/validate-docs.py` is **template-owned** — the fix belongs upstream in `~/Dev/repos/project-os/`, and editing it here would be reported as divergence at the next sync. Filed here per `CLAUDE.md` ("file what the validator reports and you cannot fix"); dedup key `(TEST-FIELDS, TST-0024)`.

## Fixed upstream — 2026-08-14

`TEST-FIELDS` now exempts a `ready` manual test, and **this is a restoration, not a new rule.**

The exemption was added upstream on **2026-08-01** (`5a487ad`, *"a `ready` test is not missing a verification date"*) and removed by **`59bd47c`** three weeks later — not by decision, but by a whole-file overwrite from a downstream copy that predated it. `5a487ad`'s own commit message had predicted exactly this:

> *"Two fixes that had been made downstream and never pushed up, so every sync reported them as local divergence and they were one `--force` away from being lost."*

They were then lost, and this issue is the bill: [[TST-0024]] was authored on 2026-08-12 with a verification date for a walk nobody had performed, plus a paragraph explaining that the field did not mean what the field means.

Restored in `project-os` `0a44cdd`, with that history in the code comment so the next overwrite has to read it. Demonstrated both ways: a `ready` manual test with no `last_verified` no longer errors; flipped to `passing` it errors exactly as before.

**Not fixable here** — `tools/scripts/validate-docs.py` is template-owned and `test_bundled_validator_matches_the_canonical_one` asserts the bundled copy is verbatim, so a downstream edit fails this repo's own suite. Synced down as a patch rather than a file copy; see [[CHG-20260814-The-Upstream-Batch]].
