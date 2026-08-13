---
type: "[[issue]]"
id: ISS-0142
aliases: ["ISS-0142"]
title: "Releases are the one note type the quick-switch corpus has never carried — typing REL-0001 into the bar that says 'files, IDs, or commands' finds nothing"
status: "open"
severity: low
owner: user:edwin
created: 2026-08-11
updated: "2026-08-13"
phase: "[[PHASE-999-Future]]"
features: ["[[FEAT-0072]]"]
tasks: []
related: ["[[REL-0001-The-Human-Has-Levers]]"]
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
