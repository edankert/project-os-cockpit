---
type: instruction
id: INSTR-OBSIDIAN
status: active
owner: group:maintainers
created: 2026-01-26
updated: 2026-04-05
tags: [instructions, obsidian]
---

# Obsidian-enabled conventions (optional)

## Cockpit Layout

project-os provides a three-pane cockpit layout for Obsidian:

| Pane | File | Purpose |
|---|---|---|
| Left sidebar | `docs/NAV.base` | Browse features, phases, and issues |
| Center | Editor | View/edit the selected note |
| Right sidebar | `docs/CONTEXT.base` | Shows tasks, requirements, issues, and tests related to the active note |

### How it works
- `NAV.base` shows tabbed views (Features, Phases, Issues) for navigation
- `CONTEXT.base` uses `this.file` to dynamically filter items that reference the active editor note via `implements`, `fixes`, `affects`, `specifies`, `validates`, or `phase`
- Switching notes in the center editor automatically updates the right sidebar

### Workspace setup
1. Open `docs/NAV.base` and drag it to the **left sidebar**
2. Open `docs/CONTEXT.base` and drag it to the **right sidebar**
3. Save the layout as a workspace: `Cmd/Ctrl+P` → "Manage workspaces" → Save as "Cockpit"
4. Restore anytime via "Manage workspaces" → Load "Cockpit"

## Linking
- Prefer Obsidian wiki links using the **filename without `.md`** (e.g. `[[TASK-0001-Foo]]`), not full paths.
- This implies filenames should be unique across the docs set; if a filename is not unique, use a path-qualified link.

## Properties
- Property keys should generally be **single names** (single token; avoid spaces). Prefer simple keys over verbose variants.
- Use **links** in properties instead of bare IDs whenever the target is another note in this docs set.

## Aliases
- Every note must include `aliases: ["<id>"]` in frontmatter (e.g., `aliases: ["FEAT-0007"]`).
- This allows linking by either the full filename (`[[FEAT-0007-Relationship-Model]]`) or just the ID (`[[FEAT-0007]]`).
- Agents must set the alias when creating notes from templates — replace the placeholder ID in both the `id` and `aliases` fields.

## Naming
- Filenames should include the stable ID plus a short descriptor:
  - Issues: `ISS-0001-Short-Problem.md`
  - Features: `FEAT-0001-Short-Name.md`
  - Tasks: `TASK-0001-Short-Action.md`
  - Tests: `TST-0001-Short-Description.md`
  - Phases: `PHASE-001-Short-Name.md`
  - Changes: `CHG-YYYYMMDD-Short-Description.md`
  - Risks/Reqs/ADRs/Workflows: same pattern (`ID-Short-Description.md`)
