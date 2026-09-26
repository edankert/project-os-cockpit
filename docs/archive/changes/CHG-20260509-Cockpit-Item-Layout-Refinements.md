---
type: "[[change]]"
id: CHG-20260509-Cockpit-Item-Layout-Refinements
aliases: ["CHG-20260509-Cockpit-Item-Layout-Refinements"]
title: "Cockpit item-layout refinements: typed-rare reverted to id+title, references show filename, right-aligned status chip"
status: merged
owner: user:edwin
created: 2026-05-09
updated: 2026-05-09
source: ["[[TASK-0025]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/cockpit.py"
  - "src/project_os_cockpit/static/cockpit.js"
  - "src/project_os_cockpit/static/cockpit.css"
  - "tests/test_cockpit.py"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[CHG-20260509-Cockpit-Library-Refinements]]", "[[REQ-0012]]", "[[REQ-0016]]"]
---

# Cockpit item-layout refinements

## Summary
Follow-up to [[CHG-20260509-Cockpit-Library-Refinements]] after a quick visual review on `your-trainer/docs`. Three coupled tweaks:

1. **Typed-structured rare items revert to `id + human title`.** TASK-0022 swapped the title to the filename and added a parent-dir subtitle for *all* rare types. That was over-applied — Decisions, Releases, Risks, Tests, Workflows, and Plans have meaningful frontmatter titles and live in conventional dirs (`decisions/`, `risks/`...), so the filename and path were noise. They now look like they used to: `[icon] [ID] [Human Title]`.
2. **References show the filename in the `id` slot.** References are loose docs that often lack a real project-os ID. The filename takes the mono `id` slot; the frontmatter title renders below in the regular row, and is suppressed when it duplicates the filename stem.
3. **Status chip is right-aligned.** Now that the type icon anchors the left edge, the status chip belongs at the right. Applies to `navItem` (Features/Tasks/Issues/Recent), `navItemStacked` (Pinned + rare types), and `ctxItem` (right-pane relationships).

## Impact

### Server (`cockpit.py`)
- `_rare_item` restored to its pre-TASK-0022 shape (id + title + type, no subtitle). Used by Pinned + every typed-structured rare-type group (adr, release, risk, test, workflow, plan).
- New `_reference_item` — filename in `id`, frontmatter title in `title` (suppressed when normalised title matches the file stem).
- `_library_groups` routes `type_name == "reference"` to `_reference_item`; everything else to `_rare_item`.

### Client JS (`cockpit.js`)
- `navItem` topLine reordered to `[icon][id][title][status]` — `nav-title` already has `flex: 1 1 auto`, so the status sits naturally at the right edge.
- `navItemStacked` topLine reordered to `[icon][id][spacer][status]` — added a `.nav-line-spacer` span (flex grow) so the chip is pushed right even when there's only an id beside the icon.
- `ctxItem` topLine reordered to `[icon][id][spacer][priority][status]` — both chips now anchor the right edge in priority order.
- `navItemStacked` no longer renders an empty title `<p>` when the server emits `title=""` (References whose human title equals the filename stem).

### CSS (`cockpit.css`)
- New `.nav-line-spacer { flex: 1 1 auto; }`.
- Removed `margin-left: auto` from `.ctx-priority` — the spacer now does the right-alignment work.
- `.nav-title-stacked` no longer carries the `mono` class on the JS side (it picks up regular weight per the existing rule).

### Tests
- The TASK-0022 assertion that *every* rare item uses filename-as-title is gone — that was the over-applied behaviour.
- New `test_nav_payload_library_references_show_filename_in_id_slot` asserts the references shape.
- New `test_nav_payload_library_typed_rare_keeps_id_and_title` synthesises an ADR fixture and asserts the typed-rare shape (project-os ID in `id`, human title in `title`, no subtitle).
- 33 cockpit cases passing (was 32; net +1 after the rewrite).

### Verified
- `curl /api/cockpit/nav?mode=library` against `your-trainer/docs`:
  - `rare:adr` → `id="ADR-0001"`, `title="Terrain-Only Workout Editor with Direct Manipulation"`.
  - `rare:reference` → `id="ARCHITECTURE.md"`, `title="Architecture (Reference)"`.
- 45 passed, 1 skipped on the full suite.

## Follow-ups
- [ ] Visual eyeball of the right-aligned status chip on narrow side panes — needs to wrap or shrink gracefully when the title is long. Currently the title has a 2-line clamp; the chip should still cling to the right.
- [ ] If References without any frontmatter title look too sparse on a single line, consider showing the file extension or modified-date as a subtle subtitle.
- [ ] `.nav-subtitle-stacked` CSS is now unused (no caller emits a subtitle in stacked layout); cleanup candidate next time we touch this file.

## Documentation Coverage (All Types Considered)
- features: not-applicable
- requirements: not-applicable
- tasks: new ([[TASK-0025]])
- issues: not-applicable
- tests: updated (`tests/test_cockpit.py`)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (TASK 24→25, focus.task → TASK-0025, metrics tasks_total 24→25 / tasks_done 18→19, items.changes addition)
