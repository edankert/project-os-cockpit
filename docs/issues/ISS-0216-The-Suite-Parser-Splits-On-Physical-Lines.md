---
type: "[[issue]]"
id: ISS-0216
aliases: ["ISS-0216"]
title: "The acceptance suite parser matches rows per physical line, so a hard-wrapped bullet loses everything after its first line — six migrated notes in your-trainer are truncated, one body is the word \"From\""
status: open
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

- [ ] Add continuation handling to `acceptance.parse`: a non-matching, indented line following an item appends to that item's text.
- [ ] Report unclassified lines rather than dropping them, and surface the count in the migration's `problems` output.
- [ ] Prove it on a hard-wrapped fixture **before any repo runs a migration again** — this is a [[PHASE-038]] exit criterion.
- [ ] Repair the six `your-trainer` notes from the README prose, one at a time, recording the source address.
