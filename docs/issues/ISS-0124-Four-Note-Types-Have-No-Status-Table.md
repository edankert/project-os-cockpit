---
type: "[[issue]]"
id: ISS-0124
aliases: ["ISS-0124"]
title: "Four note types have no status table, so 21 notes carry a `status:` nothing validates — ARCHITECTURE.md has read `draft` for three months unchallenged"
status: triage
phase: ""
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["Session 2026-08-10: deciding whether `architecture` should be a first-class note type for the Intent view surfaced that its status was never checked"]
severity: low
component: "validator"
parent: ""
related: ["[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]", "[[ISS-0023-Status-Vocabulary-Drift]]", "[[REQ-0025-No-Type-Loses-Its-Surface]]"]
tests: []
---

# Four note types have no status table

## Problem

`ALLOWED_STATUS` in the validator covers 14 types: `adr`, `change`, `decision`, `design`, `feature`, `issue`, `phase`, `plan`, `release`, `requirement`, `risk`, `task`, `test`, `workflow`.

The corpus contains four more. Their `status:` values are read, rendered, coloured and sorted — and **never validated**:

| type | notes | statuses present |
|---|---|---|
| `reference` | 18 | `active` |
| `architecture` | 1 | `draft` |
| `glossary` | 1 | `active` |
| `dashboard` | 1 | *(none)* |

21 notes in total. A typo, a retired value, or a status that means nothing for that type would all pass silently.

## The shape of the gap

The validator *does* guard this vocabulary — but only against itself. `_check_values` errors when an internal table names a type `ALLOWED_STATUS` does not have:

> `%s is compared against note type '%s', which has no entry in ALLOWED_STATUS; one table knows a type the other does not`

So table-versus-table is checked. **Corpus-versus-table is not.** Nothing asks whether every type the notes actually use has an entry, which is the direction a real note travels.

## Evidence

`docs/ARCHITECTURE.md` has read `status: draft` since **2026-05-07** — three months — and nothing has ever reported it. Its `updated:` still says 2026-05-07 while line 80 describes the desktop shell and sidecar, neither of which existed then, so the note was edited without its date being touched. Both facts are exactly what a status contract is supposed to make loud.

```
python3 -c "
import sys; sys.path.insert(0,'src')
from project_os_cockpit import validate_docs_bundled as v
for t in ('architecture','reference','glossary','dashboard'):
    print(t, 'covered' if t in v.ALLOWED_STATUS else 'NO TABLE')
"
```

## Expected

Every note type present in the corpus either has a status table, or is explicitly recorded as status-free.

## Actual

Four types are neither. The absence is silent, and it is silent in the direction that matters.

## Not the same as the type question

Whether `architecture` should become a **first-class type** — template, taxonomy entry, upstream proposal — is deliberately *not* this issue. That is a measurement to take after [[FEAT-0087]]'s Intent view exists and we can see whether architecture documents get written; one note in three months is the same evidence pattern that retired the `delivered` band ([[ADR-0006]]). This issue is only that whatever types exist should have their statuses checked.

## Next Actions

- [ ] Decide the rule: a table per type, or an explicit "these types carry no lifecycle status" set — `dashboard` already carries none, which suggests the second is real and not a workaround
- [ ] Add the corpus-versus-table check so a type appearing in notes without an entry is reported, in the direction `_check_values` does not currently cover
- [ ] Fix `docs/ARCHITECTURE.md`: `type: architecture` → the `[[architecture]]` form every other note uses, a correct `updated:`, and either resolve `draft` or say why it stands
- [ ] Consider proposing the check upstream — the gap is in template-owned validator logic, so every project-os repo has it
