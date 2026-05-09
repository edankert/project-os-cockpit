---
type: "[[change]]"
id: CHG-20260509-Index-Bare-Id-Frontmatter-Extraction
aliases: ["CHG-20260509-Index-Bare-Id-Frontmatter-Extraction"]
title: "Index: extract bare project-os IDs from curated link-bearing frontmatter fields"
status: merged
owner: user:edwin
created: 2026-05-09
updated: 2026-05-09
source: ["[[TASK-0031]]"]
commit: ""
pr: ""
impacts:
  - "src/project_os_cockpit/index.py"
  - "tests/test_index.py"
issues: []
features: ["[[FEAT-0006]]"]
related: ["[[REQ-0002]]"]
---

# Index: bare-ID extraction in link-bearing frontmatter

## Summary
The right pane was missing references for any frontmatter field whose value was a bare project-os ID without `[[…]]` brackets. Confirmed against `your-trainer/docs` — 2,294 bare-ID frontmatter occurrences, including release-chain links (`previous_release: "REL-0001"`) and CHG `impacts:` paths. The link-graph builder now extracts bare IDs from a curated set of link-bearing fields in addition to the existing wikilink scan.

## Impact

### `index.py`
- New `PROJECT_OS_ID_RE = re.compile(r"\b(?:FEAT|TASK|REQ|ISS|CHG|ADR|RISK|TST|REL|PHASE|WF|PLAN)-[\w-]+")`. Greedy on the slug so a full `CHG-20260509-Cockpit-Card-Subtitles-And-Bucket-Icons` resolves as one unit (the lookup table by_id covers both bare-prefix and full forms).
- New `_LINK_BEARING_FRONTMATTER_FIELDS` (frozenset, 22 keys): `parent`, `phase`, `scope`, `specifies`, `validates`, `verifies`, `affects`, `related`, `implements`, `fixes`, `fixed_by`, `depends`, `blocks`, `tests`, `impacts`, `previous_release`, `next_release`, `supersedes`, `superseded_by`, `causes`, `cause`, `mitigates`, `mitigated_by`, `references`, `source`, `sources`, `reverts`.
- New `_link_targets_in_frontmatter(fm)` walks each top-level key. Yields wikilinks unconditionally; yields bare IDs only when the key is link-bearing AND the bare match isn't inside a wikilink span.
- New `_all_frontmatter_strings(value)` — recursive scalar walker for nested list/dict frontmatter.
- `_rebuild_links` switched from `_wikilinks_in_frontmatter` to `_link_targets_in_frontmatter`. Old function kept as a back-compat shim.
- `import re` added (helper module previously didn't need it).

### Tests
- `test_bare_id_in_link_bearing_frontmatter_field_resolves` — synthesises REL-0098 + REL-0099 with `previous_release: "REL-0098"` (bare). Asserts the link is followed.
- `test_bare_id_inside_wikilink_not_double_counted` — same fixture but with `previous_release: "[[REL-0098]]"`. Asserts the path resolves once (frozenset dedup + the inside-wikilink skip).
- 50 cases passing / 1 skipped (was 48; +2).

### Verified live (your-trainer/docs)
- `curl /api/cockpit/context?this=REL-0002`:
  - linked: `[issue: ISS-0115, release: REL-0001]`
  - backlinks: `[phase: PHASE-006, release: REL-0003]`
- Pre-fix the release chain had empty links since both `previous_release` values were bare strings.

## Follow-ups
- [ ] The curated field list is hard-coded. If a project invents a new link-bearing field (`triggers`, `consumes`, etc.) it won't be picked up until the list is extended.
- [ ] No diagnostic surface yet for unresolved wikilinks. Suggested follow-up: a startup INFO log "X frontmatter wikilinks unresolved across N notes" so typos are visible without DEBUG.
- [ ] CHG `impacts: docs/decisions/ADR-0001-*.md` strings are now extracted (the regex matches `ADR-0001`). Acceptable — the path glob is a real dependency declaration; surfacing it in the right pane is a feature, not a bug.

## Documentation Coverage (All Types Considered)
- features: not-applicable
- requirements: not-applicable (refinement under existing REQ-0002/REQ-0008)
- tasks: new ([[TASK-0031]])
- issues: not-applicable
- tests: updated (`tests/test_index.py`)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (TASK 30→31, focus.task → TASK-0031, metrics tasks_total 30→31 / tasks_done 24→25, items.changes addition)
