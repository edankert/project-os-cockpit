---
type: "[[issue]]"
id: ISS-0232
aliases: ["ISS-0232"]
title: "An expanded check shows `passing`/`ready` — the runner's vocabulary on a note whose outcome is a ledger mark, which is ISS-0226's defect one level down"
status: fixed
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: medium
component: cockpit-desktop
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0226-A-Surface-Wears-A-Test-Status]]", "[[ADR-0037-A-Verdict-Is-An-Event]]"]
---

# `passing` is not a state a check can be in

Edwin, 2026-08-19: *"not sure if passing is an official state?"*

**It is not, and the question is exactly right.** `passing` belongs to `statuses.VOCABULARY` and is written by the runner for an executable test. An acceptance check rests at `status: active` and its outcome is a **ledger mark** — `pass`, `partial`, `na`, `excused`, `blocked`, `fail`, `question`, or no entry at all ([[ADR-0037]]).

The child rows carry `passing`/`reconciled`/`ready` because [[ISS-0226]] was fixed on the *surface* row and the same borrowed vocabulary was left one level down, in the same function, on the same day.

## Suggested fix

The expanded check shows its **mark**, right-aligned — the word the ledger holds, drawn with the glyph and colour `MARK_GLYPH`/`MARK_CLASS` already define for it. A check with no entry shows nothing rather than a status, because *no entry* is the state and inventing a word for it is what [[ADR-0037]] decision 5 removed.

## Done when

- [x] An expanded check shows its ledger mark, not a test status.
- [x] No surface in the nav emits a value `statuses.VOCABULARY` owns.

## Fixed 2026-08-19
