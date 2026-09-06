---
type: "[[issue]]"
id: ISS-0279
title: "A note whose `type:` is a YAML list is indexed as untyped — 99 of the 407 notes in Edwin's vault, including nearly every character, page and panel in the Comics project"
status: triage
phase:
owner: unassigned
created: 2026-09-06
updated: 2026-09-06
source: ["Measured 2026-09-06 while writing [[REFERENCE-SURFACE-ARCHITECTURE-OPTIONS]]: the sidecar run against ~/Notes returned a Library with a Panel group of zero"]
severity: medium
component: index
parent: ""
related: ["[[REFERENCE-SURFACE-ARCHITECTURE-OPTIONS]]", "[[ISS-0023]]"]
tests: []
---

# A list-valued `type:` loses its type

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

- [ ] Accept a list in `_normalise_type`, taking the first element, and say so in the docstring.
- [ ] Decide what a multi-element list means, and add a test with both forms.
- [ ] Re-run the Library payload against the vault and record the groups it returns.
