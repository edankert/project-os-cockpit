---
type: "[[issue]]"
id: ISS-0124
aliases: ["ISS-0124"]
title: "One note type carries a `status:` nothing validates — 14 `reference` notes read `active` against no table, and nothing asks whether a type the corpus uses has an entry"
status: "fixed"
phase: ""
owner: user:edwin
created: 2026-08-10
updated: "2026-08-14"
source: ["Session 2026-08-10: deciding whether `architecture` should be a first-class note type for the Intent view surfaced that its status was never checked"]
severity: low
component: "validator"
parent: ""
related: ["[[ISS-0155]]", "[[ISS-0163]]", "[[ISS-0147]]", "[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]", "[[ISS-0023-Status-Vocabulary-Drift]]", "[[REQ-0025-No-Type-Loses-Its-Surface]]"]
tests: []
---


# One type carries an unvalidated status

*Re-measured and rewritten 2026-08-14. Filed on 2026-08-10 as "four note types, 21 notes"; two of the four have since resolved themselves and the headline exhibit is fixed. What is left is smaller, still real, and unchanged in kind.*

## Problem

`ALLOWED_STATUS` covers 14 types. Nothing checks the other direction — **whether every type the corpus actually uses has an entry.** `_check_values` guards table against table, and errors when an internal table names a type `ALLOWED_STATUS` lacks:

> `%s is compared against note type '%s', which has no entry in ALLOWED_STATUS; one table knows a type the other does not`

That is table-versus-table. **Corpus-versus-table is the direction a real note travels, and it is unchecked.**

## Measured 2026-08-14 (templates excluded)

| type | notes | carrying a `status:` |
|---|---|---|
| `reference` | 21 | **14**, all `active` |
| `architecture` | 1 | 0 |

Fourteen notes, one type. A typo, a retired value, or a status meaningless for that type passes silently on every one.

The fourteen are the directory signposts — `docs/issues/README.md`, `docs/phases/README.md` and eleven siblings — plus `ACCEPTANCE_TESTS.md`, `COCKPIT-API.md` and one migration note.

## What changed since filing, and why the note shrank

- **`architecture` no longer carries a status.** `docs/ARCHITECTURE.md` read `status: draft` from 2026-05-07, which was this issue's headline evidence. [[FEAT-0091]]'s standing-document work removed it and brought `updated:` current. The type still has no table; there is now nothing for one to check.
- **`glossary` is gone from the corpus entirely.**
- **`dashboard` survives only as a template**, which the walk excludes.

Two of the four resolved without anyone acting on this issue. That is worth stating plainly: had it been fixed on filing, half the work would have been aimed at notes that were about to change anyway.

## Why it still matters

The shrinking is the argument, not a reason to close. This issue's own exhibit was fixed by an unrelated change and **nothing reported either state** — not the three months of `draft`, and not the day it stopped. A status contract that cannot see a type is silent in both directions, and silence on the way in is what let `draft` sit unchallenged for a quarter.

## The rule to decide first

`architecture` and `dashboard` carry **no** status, and `reference` carries exactly one value on every note that has one. That is evidence for **two** answers, not one:

1. a status table per type; or
2. an explicit *"these types carry no lifecycle status"* set, with `reference` given a one-value table (`active`).

The second looks right. `dashboard` already behaves that way, and inventing a lifecycle for a directory signpost would be vocabulary nobody asked for — the [[ISS-0023]] failure in a new place.

## Where the fix has to live

`tools/scripts/validate-docs.py` is **template-owned**, and `tests/test_status_vocabulary.py` asserts `validate_docs_bundled.py` is a verbatim copy of it — so a downstream fix fails this repo's own suite. This is upstream work, batched with [[ISS-0155]], [[ISS-0163]] and [[ISS-0147]].

## Next Actions

- [ ] Decide the rule: a table per type, or an explicit status-free set (recommended)
- [ ] Add the corpus-versus-table check upstream, in the direction `_check_values` does not cover
- [ ] Give `reference` its one-value table, or place it in the status-free set

## Not this issue

Whether `architecture` should be a **first-class type** is a separate measurement, and [[TASK-0379]] already chose to make it a design instead. This issue is only that whatever types exist should have their statuses checked.

## Fixed upstream — 2026-08-14

`STATUS-TYPE` is in the template validator (`project-os` `0a44cdd`), reporting a note type that appears in `docs/` with no entry in any status table — the corpus-versus-table direction `_check_values` never covered.

**Its first version reported nothing, and why is the interesting part.** Written over `note_index`, which is keyed by IDs matching `ID_PREFIXES` — `ADR`, `DES`, `FEAT`, `ISS`, `PHASE`, `REL`, `REQ`, `RISK`, `TASK`, `TST`, `WF`. The notes this check exists for carry none of them: `ARCHITECTURE.md` is `ARCH`, the glossary is `GLOSSARY`, a signpost is `DOCS-README`. **The types with no status table are exactly the types with no ID prefix, and for the same reason: nobody tabulated them.** It walks `docs/` directly now.

The rule chosen was this note's option 2, and measurement settled it:

- `reference` → `{"active"}` — 206 `active` fleet-wide, 14 with no status
- `glossary` → `{"active"}` — 10 `active`, nothing else
- `STATUS_FREE_TYPES = {"architecture"}` — one member, because one is what the fleet has

`glossary` sat in the status-free set for about ten minutes on the strength of a guess, until the check's first run reported project-os's own `GLOSSARY.md` carrying a status. `dashboard` came out: it exists only as a template, which the walk excludes, so listing it would be a rule about a note that does not exist.

A status-free type that *acquires* a status is also reported, so the exemption cannot become the hiding place this check exists to close.
