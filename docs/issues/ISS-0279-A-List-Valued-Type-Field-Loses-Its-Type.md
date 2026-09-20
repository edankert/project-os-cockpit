---
type: "[[issue]]"
id: ISS-0279
title: "A note whose type: is written as a list gets no type, so the Library shows no Character, Page or Location groups for Edwin's vault"
status: fixed
phase:
owner: unassigned
reported_by: agent
created: 2026-09-06
updated: "2026-09-20"
source: ["Measured 2026-09-06 while writing [[project-os-deck#REFERENCE-SURFACE-ARCHITECTURE-OPTIONS]]: the sidecar run against ~/Notes returned a Library with a Panel group of zero"]
severity: medium
component: index
parent: ""
related: ["[[project-os-deck#REFERENCE-SURFACE-ARCHITECTURE-OPTIONS]]", "[[ISS-0023]]"]
tests: []
fixed_by: "[[TASK-0632-Fix-The-Seven-Defects-From-The-Issue-Review]]"
---

# A note whose type is a list shows up untyped

When a note's `type:` is written as a YAML list, as Obsidian does, the cockpit treats the note as having no type at all.

## Problem

The indexer reads a note's `type:` only when it is a string. Obsidian writes a list-valued property as a YAML list, and the notes in Edwin's Comics project carry `type:` that way (a line `type:` followed by `- "[[@Character]]"`). Those notes reach the cockpit with no type at all, so the Library's auto-discovered groups are empty for exactly the types the vault is built on, and the parent nesting that `cockpit.py` already supports for `world`, `story`, `chapter` and `page` never runs.

The vault's own `CLAUDE.md` warns that properties come in both forms and asks anything processing notes to search for both. The cockpit does not.

## Repro

```
.venv/bin/python -m project_os_cockpit ~/Notes --port 8791
curl -s 'http://127.0.0.1:8791/api/cockpit/nav?mode=library'
```

The Library payload returns four groups: Docs tree, Daily, Default Note, Panel. The Panel group has zero items. No Character, Page, Location, Chapter or Story group appears.

## Expected

A `type:` given as a one-element list is the same type as the string form. `[[@Character]]` as a list item and `"[[@Character]]"` as a string both index as `@character`. A multi-element list needs a rule (first element, or all of them); the project-os templates never write one, and the vault's `Story` template writes a one-element list.

## Actual

`_normalise_type` in `src/project_os_cockpit/index.py` returns `None` for any non-string value, so the note is indexed as untyped.

## Evidence

Measured on 2026-09-06 over `~/Notes` with `.obsidian`, `.trash` and attachment folders excluded:

| what | count |
| --- | --- |
| Markdown notes | 407 |
| `type:` as a string | 90 |
| `type:` as a list | 99 |
| no `type:` | 218 |
| notes under `03 Projects/Comics` | 137 |
| of those, `type:` as a list | 37 |
| of those, `type:` as a string | 9 |

Types seen in Comics by first element: Page 11, Panel 11, @Character 10, Location 8, Chapter 2, Story 1. The two `panel` notes typed as a bare string are the ones that appear.

The same function handles `status:`, and one Comics note carries a status list copied from its template (`draft, review, final, cancelled`); that is a template defect in the vault rather than a cockpit bug, but the reader of this issue should know the list form appears there too.

## Next Actions

- [x] Accept a list in `_normalise_type`, taking the first element, and say so in the docstring.
- [x] Decide what a multi-element list means, and add a test with both forms.
- [~] Re-run the Library payload against the vault and record the groups it returns.

## Checked against the code, 2026-09-19: still true, kept

**What a user notices:** Opening Edwin's `~/Notes` vault, the Library has no Character, Page, Location, Chapter or Story groups, and the Panel group is empty, although 99 notes carry those types.

Evidence: `src/project_os_cockpit/index.py:657-658` in `_normalise_type`: `if not isinstance(raw, str): return None`. The function is unchanged since 5b38bd3 (FEAT-0001).

**Belongs to:** no feature. **Next:** Small fix: accept a list in `_normalise_type`, take the first element, and add a test with both forms.

Checked as part of project-os-dev FEAT-0036 (TASK-0141).

## Fixed 2026-09-20 (TASK-0632)

**What changed.** `_normalise_type` in `src/project_os_cockpit/index.py` now accepts a list and returns the first element that normalises to something. A note whose `type:` is `["[[@Character]]"]` indexes as `@character`, exactly as the string form does, so the Library draws a group for it.

**The multi-element rule, decided.** The first usable element wins. Neither the project-os templates nor the vault's own ever write a second one, so there is nothing to preserve; taking the first is what the one-element case already implies and it never invents a type the list does not name. An empty string in the list is skipped rather than returned, and an empty list is still untyped. The docstring says so.

**Which test guards it.** `tests/test_index.py::test_a_type_written_as_a_list_is_the_same_type_as_the_string` and `::test_the_first_usable_element_of_a_type_list_wins`. Both go through `Index.build` and `type_counts()` rather than calling the helper, because the Library's group is what a reader notices.

**Run both ways.** With the fix: `18 passed`. With `index.py` reverted (`git stash push src/project_os_cockpit/index.py`): `2 failed, 16 passed`, the first on `note_type is None` where `@character` was expected.

**Not re-run against the vault.** The Library payload over `~/Notes` was not measured again — that needs Edwin's vault and a running sidecar, and the counts in the Evidence table above are what the fix was sized on. The `- [~]` box records it as cut rather than done.

Commit: see the repository history for `ISS-0279`.
