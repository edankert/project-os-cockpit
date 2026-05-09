---
type: "[[task]]"
id: TASK-0031
aliases: ["TASK-0031"]
title: "Index: extract bare project-os IDs from curated link-bearing frontmatter fields"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-09
updated: 2026-05-09
source: []
implements: ["[[FEAT-0006]]", "[[REQ-0002]]"]
fixes: []
effort: S
due: ""
depends: []
blocks: []
related: []
tests: ["[[TST-0001]]"]
---

# TASK-0031 — Bare-ID extraction in link-bearing frontmatter fields

## Definition of Done
- [x] Frontmatter values in a curated set of link-bearing fields (`parent`, `phase`, `scope`, `affects`, `specifies`, `related`, `implements`, `fixes`, `depends`, `blocks`, `tests`, `validates`, `verifies`, `previous_release`, `next_release`, `supersedes`, `superseded_by`, `impacts`, `causes`, `mitigates`, `references`, …) are scanned for bare project-os IDs (`FEAT-####`, `CHG-YYYYMMDD-...`, etc.) in addition to the existing `[[wikilink]]` extraction.
- [x] Self-reference fields (`id`, `aliases`) and free-text fields (`tags`, `commit`, `pr`, body) are NOT walked for bare IDs.
- [x] Bare IDs that fall inside a `[[…]]` span are skipped to avoid double-counting.
- [x] Existing tests still pass; new tests cover bare-ID extraction + non-duplication when both forms coexist.

## Steps
- [x] Added `PROJECT_OS_ID_RE = re.compile(r"\b(?:FEAT|TASK|REQ|ISS|CHG|ADR|RISK|TST|REL|PHASE|WF|PLAN)-[\w-]+")` in `index.py`. Greedy on the slug so a CHG id like `CHG-20260509-Cockpit-Card-Subtitles` resolves as one unit.
- [x] Added `_LINK_BEARING_FRONTMATTER_FIELDS` (frozenset of ~22 known link-bearing keys).
- [x] New `_link_targets_in_frontmatter(fm)` walks each top-level key. For all keys it yields `[[wikilinks]]` (existing behaviour). For keys in the curated set it ALSO yields bare IDs that aren't inside a wikilink span.
- [x] `_rebuild_links` switched from `_wikilinks_in_frontmatter` to `_link_targets_in_frontmatter`. The old function is kept as a back-compat shim.
- [x] New `_all_frontmatter_strings(value)` recursive scalar walker.
- [x] Tests: bare ID in `previous_release` resolves; same ID in `[[…]]` form not double-counted.

## Notes
- 22 frontmatter fields is the scope today. New fields a project invents won't be covered without an update — by design (the curated list is the safety net against false positives).
- `WIKILINK_RE.finditer(s)` is now run twice per string when the field is link-bearing; could be cached but performance is non-issue at current corpus sizes.

## Verified
- `your-trainer/docs` — REL-0002 right pane now shows `REL-0001` in linked (via bare `previous_release: "REL-0001"`) and `REL-0003` in backlinks (whose `previous_release` points to REL-0002). Pre-fix: empty link / backlink for the chain.
- This repo — no functional change since most frontmatter already uses `[[…]]`.
