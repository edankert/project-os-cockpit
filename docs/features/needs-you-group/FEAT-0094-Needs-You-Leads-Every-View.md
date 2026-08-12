---
type: "[[feature]]"
id: FEAT-0094
aliases: ["FEAT-0094"]
title: "Needs you leads every view — the same set the badge counts, gathered at the top of the navigator and on the overview"
status: done
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-12
updated: 2026-08-12
source: ["Edwin 2026-08-12: 'For each of the intent, features, issues and tests view it would be good to have a triage (or whatever word is more appropriate) section at the top which shows the items that need my/human decisions/confirmations. As well as showing this on the desk page.'"]
goal: "What needs a person is the first thing in every view's navigator and is on the overview — one registry, one predicate, four surfaces that cannot disagree."
requirements: []
tasks:
  - "[[TASK-0393-The-Needs-You-Group]]"
  - "[[TASK-0394-The-Owed-Mark-In-Place]]"
  - "[[TASK-0395-Needs-You-On-The-Overview]]"
related: ["[[ADR-0025]]", "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[FEAT-0092]]"]
tests: []
---

# Needs you leads every view

## Goal

The badge says a number, the landing page lists it, and the navigator — the pane a person actually works in — gathers it only in the two views that happened to be built that way. This makes it four for four.

## Out of scope

- **A second group for Issues and Tests.** `Needs triage` and `Needs a run` already gather the same set under names that say more than "needs you". Adding one would duplicate where duplication buys nothing, which [[ADR-0025]] permits and does not require.
- **New obligation kinds.** The registry is the source; this renders what it already knows.
- **Acting in bulk.** Each row goes to the note that carries its actuator, as the landing pages do.

## Acceptance

- [x] `Needs you` is the **first** group in Features and Intent when anything is owed, and **absent** when nothing is — never a zero.
- [x] Its count equals that view's badge, from the same walk (`obligations.owed_items`), so the three surfaces cannot disagree.
- [x] Each row names its verb from the registry — `Approve`, `Decide`, `Confirm` — never "items".
- [x] The structural copy is **marked** as owed where it sits, so meeting it in the tree is not a surprise ([[ADR-0025]]).
- [x] The overview carries the same set, grouped by view, with each row one click from its note.
- [x] Intent's rel-path dedupe guard still holds everywhere except the owed group, and the exception is asserted rather than implied.


## Evidence — 2026-08-12

| view | first group | items | badge |
|---|---|---|---|
| features | `Needs you` | 1 | 1 |
| intent | `Needs you` | 5 | 5 |
| issues | `Needs triage` (its own) | 9 | 9 |
| tests | none owed, so none shown | — | 0 |

**Intent is why the group is not just `owed_items`.** It came out **3 against a badge of 5**: two of the five are standing documents, whose subject is a manifest entry rather than a note, so the registry's row walk has nothing for them. Those rows exist in the standing group already carrying `owed` and their verb, and are taken from there rather than recomputed — the count matches the badge for the same reason the badge matches itself.

**The structural mark needed no code.** `REQ-0032` already carried `owed: True, owed_verb: "Approve"` in the features tree, so [[ADR-0025]]'s condition for permitting the copy was met before it was written down.

**Eleven tests failed on the first run and every one was worth reading.** Nine were positional — `groups[0]` meaning "the standing set" or "the designs list" — and are now selected by key. The other two were the hazard this decision introduces, caught immediately: `test_a_proposed_adr_is_this_views_obligation` and `test_the_standing_obligation_reaches_the_intent_badge` **counted owed marks**, which double-counts once a row can appear twice. They count distinct ids now, which is the rule any future surface must follow.
