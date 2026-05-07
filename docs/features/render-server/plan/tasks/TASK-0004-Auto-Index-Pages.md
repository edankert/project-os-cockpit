---
type: "[[task]]"
id: TASK-0004
aliases: ["TASK-0004"]
title: "Auto-generated index pages (features, tasks, requirements, etc. by status)"
status: done
phase: "[[PHASE-001-MVP]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: []
implements: ["[[FEAT-0001]]", "[[REQ-0007]]"]
fixes: []
effort: S
due: ""
depends: ["[[TASK-0003]]"]
blocks: []
related: []
tests: []
---

# Auto-index pages

## Definition of Done
- [x] `GET /index/features` returns features grouped by status with links.
- [x] Same for `/index/tasks`, `/index/requirements`, `/index/issues`, `/index/risks`, `/index/decisions` (→ `type: [[adr]]`), `/index/changes`, `/index/releases`, `/index/workflows`, `/index/tests`, `/index/phases` — all 11 mapped via `INDEX_TYPE_PLURALS` in `server.py`.
- [x] Landing page (`/`) lists all 11 index types with counts (zero-count types still appear).
- [x] Each grouped section is a `<details>`/`<summary>` (collapsible, no JS) ordered by `STATUS_RANK` in `templates.py`: active/doing/in-progress first, backlog/triage middle, done/closed/verified last. Done-ish groups default-collapsed.

## Steps
- [x] `index.py`: `NoteRecord` extended with `note_type` (normalised — strips `[[ ]]`, lowercased) and `status`. New: `notes_by_type()`, `type_counts()`. Templates excluded by default to keep placeholder IDs out of the lists.
- [x] `server.py`: `/` → landing handler; `/index/<plural>` → index handler; `/index` redirect to `/`.
- [x] `templates.py`: `landing_page_html()` and `index_page_html()` plus `STATUS_RANK` and `COLLAPSED_BY_DEFAULT`.
- [x] Landing also surfaces `focus.*` from `SNAPSHOT.yaml` when present, with wikilinks resolved.
- [x] CSS: `.index-group`, `.index-items`, `.index-id`, `.muted-count`, `.meta-heading`, plus the rotation and layout for the `<details>` summary.

## Notes
Templates under `__templates__/` are intentionally indexed (so `[[feature]]` resolves) but excluded from the user-facing index lists (so the placeholder `FEAT-0000` etc. don't pollute counts).

`/index/decisions` maps to `type: [[adr]]` — directory naming matches the project-os convention even though the canonical type label is `adr`.

`plan` and `dashboard` types are NOT in `INDEX_TYPE_PLURALS` because they weren't in the original DoD list. Easy to add (`/index/plans`, `/index/dashboards`) when needed.

**Verification gap:** still no formal `TST-*` notes — verified via 88-file render sweep + endpoint probes. Same flag as TASK-0002 / TASK-0003. With FEAT-0001 now complete, it's worth deciding whether to retro-fit Tier 1 acceptance tests for the renderer / wikilink resolver / index pages before moving on to FEAT-0002.
