---
type: "[[issue]]"
id: ISS-0216
aliases: ["ISS-0216"]
title: "The acceptance suite parser matches rows per physical line, so a hard-wrapped bullet loses everything after its first line — six migrated notes in your-trainer are truncated, one body is the word \"From\""
status: fixed
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: high
component: tooling
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]", "[[PHASE-035-Acceptance-Checks-Are-Notes]]", "[[ISS-0215-One-Hundred-And-Forty-Rows-Outside-The-Suite]]"]
---

# The migration silently truncated six notes

## Problem

`acceptance.parse` (`src/project_os_cockpit/acceptance.py:579`) iterates `body.splitlines()` and matches `_ITEM_RE` against each **physical** line. A line that does not match is discarded outright:

```python
item = _ITEM_RE.match(line)
if not item:
    continue
```

There is no continuation handling. A checklist bullet hard-wrapped across several lines therefore parses as *its first line only*, and every subsequent line is dropped without a warning, a count, or an entry in the migration's `problems` list.

`migrate-acceptance-checks.py` builds every note body from that parse, so the truncation is written into the corpus permanently.

## Evidence

Six notes in `your-trainer/docs/tests/acceptance/`, all from the `ACCEPTANCE_TESTS.md` migration at `5976a658`:

| note | body |
| --- | --- |
| `TST-0596` | `From` |
| `TST-0592` | `Ride through Riders → Workouts → cockpit` |
| `TST-0597` | `Power cards show interval bars` |
| `TST-0593`, `TST-0594`, `TST-0595` | likewise truncated at the first physical line |

`TST-0596-Chrome-Reachable-From-Every-Pre-Ride.md` has a one-word body. It is titled *"Chrome reachable from every pre-ride screen (ISS-0361 / ISS-0362)"* and its entire procedure is the word `From`.

## Repro

Parse any suite containing a bullet whose text continues on the next physical line; the returned `Item.text` stops at the first line break.

## Why the damage was survivable, and why that is not a fix

The full text exists only because `build_readme` copies the source document's prose verbatim into the checks directory README. That is luck, not design — the README is prose for humans, not a record any tool can reunite with the truncated note.

## Expected

A hard-wrapped bullet parses as one item carrying its full text. A line the parser cannot classify is **counted and reported**, never silently dropped — the same fail-loud posture the mark vocabulary already takes on an unrecognised value.

## Next actions

- [x] Continuation handling in `acceptance.parse` — the row is held open and closed by what follows it, so the join happens **before** `_NAME_RE` runs.
- [x] Lazy wraps reported rather than dropped; `migrate-acceptance-checks.py` prints them before applying.
- [x] Proved on a hard-wrapped fixture, and mutation-proven against three plausible wrong fixes.
- [x] The six `your-trainer` notes repaired from the README prose — through the *fixed* parser, each recovery asserted to start with the truncated text. **Uncommitted in that repo**: 58 files of other work in flight.

## Fixed 2026-08-19

The exclusion rule ended up wider than this issue proposed. Independent review measured what *"indented and not a bullet"* still let through — an ordered-list step, a table row, an indented heading, a block quote — and each folded into the row's prose, inventing a sentence nobody wrote. It is five shapes now, and the four extra are parametrised guards.
