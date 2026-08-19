---
type: "[[issue]]"
id: ISS-0221
aliases: ["ISS-0221"]
title: "`_notes_at` matched `CHK-` only and never followed ADR-0031's renumber, so `suite_at` returned `None` at every post-migration ref — including HEAD — and the release delta has silently reported `not comparable` since 2026-08-18"
status: fixed
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: high
component: cockpit-server
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
related: ["[[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]]", "[[TASK-0545-Suite-At-Gets-A-Third-Shape]]", "[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ISS-0219-Two-Checks-Claiming-One-Address]]"]
---

# A filter that outlived the ids it filtered

## Problem

`acceptance._notes_at` selected blobs with:

```python
if not path.rsplit("/", 1)[-1].startswith("CHK-") or not path.endswith(".md"):
    continue
```

[[ADR-0031]] renumbered every acceptance check from `CHK-*` into the `TST-*` space on 2026-08-18. **This filter never followed.** From that commit onward it matched nothing, `_notes_at` returned `None`, `suite_at` returned `None`, and every consumer read that as *"the suite could not be read at this ref"*.

Measured 2026-08-19, before the fix:

```
HEAD     -> None
HEAD~40  -> None
```

**`None` at HEAD.** Not at some distant tag — at the commit the repo is sitting on.

## What it cost

`suite_at` is what the release delta reads: `_chronic` (*the oldest tag at which a row was already unsettled*) and the baseline comparison. With it returning `None`, the delta reports **`comparable: false`** at every post-migration ref, so the release surface has been saying *"no baseline"* rather than *"25 since v2.0.5, 14 since v2.0.0"* for a day, in every migrated repo.

## Why it survived two migrations

**It fails in the direction that makes a surface say less rather than something wrong.** `comparable: false` is a legitimate state — a tag from before the suite existed produces it — so the surface rendered a plausible answer and nobody had a reason to look. The one test that would have caught it, `test_gate_delta`, exercises `your-trainer`'s twelve *historical* tags, and every one of them predates the migration and holds the **file** shape, which the other branch reads correctly.

That is the same shape as [[ISS-0219]], found the same day: a defect that only appears once the corpus moves past the state the tests fixture it in.

## Fix

Match `TST-` **and** `CHK-`. Both, permanently: a tag is immutable, so the twelve refs holding `CHK-*` notes will hold them forever, and dropping the old prefix would move the blind spot rather than close it.

Fixed as part of [[TASK-0545]], which was already opening this function to add the ledger read — the third shape a historical ref can hold.

## Fixed 2026-08-19

- [x] `_notes_at` matches both prefixes.
- [x] `suite_at` returns 34 items at HEAD, and reads the notes' own marks at refs before the ledger.
- [x] Guarded by `test_suite_at_reads_all_three_shapes`, which asserts against real refs in this repo rather than a fixture — the fixture is what hid it.
