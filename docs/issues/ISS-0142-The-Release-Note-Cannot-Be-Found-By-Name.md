---
type: "[[issue]]"
id: ISS-0142
aliases: ["ISS-0142"]
title: "Releases are the one note type the quick-switch corpus has never carried — typing REL-0001 into the bar that says 'files, IDs, or commands' finds nothing"
status: "fixed"
severity: low
owner: user:edwin
created: 2026-08-11
updated: "2026-08-14"
phase: "[[PHASE-026-The-Returning-Human]]"
features: ["[[FEAT-0072]]"]
tasks: []
related: ["[[REL-0001-The-Human-Has-Levers]]", "[[ISS-0164-Phases-Are-The-Second-Type-The-Palette-Cannot-Find]]"]
tags: [issue, navigation]
---

# The release note cannot be found by name

## What was found

2026-08-11, trying to open [[REL-0001]] in the live harness to look at its gate band. `REL-0001` into the top bar — *"Search files, IDs, or commands…"* — returns **No matches**. So does `releases/`, and so does the note's title.

Everything else answers:

| query | result |
|---|---|
| `TASK-0315` | the task |
| `DES-0009` | the design |
| `CHG-20260811` | two change notes |
| `ACCEPTANCE` | the suite reference, and a requirement |
| `ISS-0139` | the issue |
| **`REL-0001`** | **No matches** |

## Why

`buildQuickCorpus` builds from `QUICK_CORPUS_MODES` — `features`, `issues`, `intent`, `library` — and **no nav mode carries releases.** `library`'s Docs tree is the ten top-level standing documents, not the subdirectories, so `docs/releases/` is not reached that way either.

The interesting part is that the function already knows this problem: it has two explicit patches, one fetching the review queue's test register and one fetching `/api/cockpit/changes`, under the comment *"Changes and tests have no nav mode — they live on the overview and the review desk. Both are still worth finding by name."* **Releases are a third case of exactly that, added by [[FEAT-0072]] four days after the comment was written, and nobody went back to it.**

## Reachable, just not findable

There is a route: the overview's record column carries `Unreleased · N` and the REL note is one click from it, which is the surface [[FEAT-0072]] built and whose acceptance criteria never claimed the palette. This is a gap in a *second* affordance, not an orphaned note — which is why it is `triage` and `low` rather than a defect against a shipped feature.

## Resolution, when it is picked up

Either give releases a nav home (they are few and permanent, so a group rather than a mode), or add the third patch beside the other two. The second is minutes; the first is the better answer if release notes are ever going to be more than one.

## Decision record

> [!note] Accept — 2026-08-13 (user:edwin)
> Is this still an issue?

## Fixed — 2026-08-14: a nav home, which turned out to be the cheap option too

Still real when re-checked today — `QUICK_CORPUS_MODES` was `features`, `issues`, `intent`, `library`, and none reached `docs/releases/`.

This note offered two answers and called the better one more expensive. That had stopped being true. `_design_groups` builds the `intent` view from a loop over `(key, label, types)` tuples, so releases became **one entry in that loop**:

```python
("releases", "Releases", ("release",)),
```

Because the quick corpus is built *from* nav modes, one line makes releases navigable **and** findable, and inherits the template-exclusion, standing-manifest dedup, platform filter and owed flags that a third `buildQuickCorpus` patch would each have had to restate beside the two the code already apologises for. Releases sit on `intent` for the reason decisions and risks do: few, permanent, project-level.

Verified against the live payload — `REL-0001` now resolves to `/docs/releases/REL-0001-The-Human-Has-Levers.md`.

## The title was wrong, and finding that out is worth more than the fix

*"The one note type the quick-switch corpus has never carried."* That was measured by hand, one type at a time, which is how this was found in the first place — somebody typed an id and got nothing.

Measuring **every** type at once, to verify the fix:

| type | notes | findable |
|---|---|---|
| task / issue / feature / requirement | 716 | 716 |
| adr / design / risk / decision | 36 | 36 |
| release | 1 | 1 ✓ |
| **phase** | **34** | **0** |

There were two, not one — and phases outnumber releases 34 to 1. Filed as [[ISS-0164]] rather than folded in here, because the answer differs: `intent` is right for releases and wrong for phases, whose home is the overview strip.

`test_every_id_bearing_type_is_findable_in_the_palette` now measures all types in one pass and requires any zero to be **named with a reason**. That guard is this issue's real product: the bug was found by hand twice, and a type added later would have made it three. Mutation-checked — removing the `releases` line fails it.

**Re-homed out of [[PHASE-999]] on closing.** [[FEAT-0072]] built the release surface and lives in [[PHASE-026]]; this was a gap in that surface's second affordance, so that is where it belongs. The fix itself landed in the intent view ([[FEAT-0087]]), but the phase a defect belongs to is the one whose deliverable it was a hole in.
