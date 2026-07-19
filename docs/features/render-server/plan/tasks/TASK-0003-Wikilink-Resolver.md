---
type: "[[task]]"
id: TASK-0003
aliases: ["TASK-0003"]
title: "Implement [[wikilink]] resolver (titles + aliases + project-os IDs)"
status: done
phase: "[[PHASE-001-MVP]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: []
parent: "[[FEAT-0001]]"
fixes: []
effort: M
due: ""
depends: ["[[TASK-0002]]"]
blocks: ["[[TASK-0004]]"]
related: []
tests: []
---

# Wikilink resolver

## Definition of Done
- [x] At server startup, walk the docs tree and build an in-memory index keyed by every `id`, alias, filename-stem, and title.
- [x] Markdown body wikilinks rewritten via a `markdown.InlineProcessor` (registered as `WikilinkExtension`) — code blocks are left alone for free because the markdown parser handles fence protection before inline patterns run.
- [x] Frontmatter-string wikilinks resolved too (e.g. `related: ["[[FEAT-0001]]"]` → clickable in the metadata strip) via `wikilinks.resolve_text_to_html`.
- [x] Project-os ID pattern matches via the alias / `id` lookup tables — no separate regex check needed; the convention `aliases: ["FEAT-0001"]` makes every ID a first-class index key.
- [x] Unresolved targets render as `<span class="broken-wikilink" title="unresolved wikilink">[[Foo]]</span>` styled per Obsidian convention (faded text + dotted underline, no background).
- [x] `Index.update_path(path)` provided so the FEAT-0002 watcher (TASK-0005) can incrementally invalidate; not yet wired (watcher doesn't exist).

## Steps
- [x] `index.py`: `Index.build(docs_root)` populates four lookup tables (`_by_id`, `_by_alias`, `_by_filename`, `_by_title`) plus a per-path `NoteRecord` (frontmatter + body shell — TASK-0007 extends this with link graph).
- [x] `wikilinks.py`: shared regex (`\[\[([^|\]\n]+)(?:\|([^\]\n]+))?\]\]`), `resolve_text_to_html` for non-markdown contexts, and `WikilinkExtension` registering an `InlineProcessor` at priority 175 (above stdlib `link` 160 and `reference` 170 so `[[X]]` claim-jumps the standard link patterns).
- [x] Resolution order: `id` → `aliases` → filename → title (matches REQ-0002 precedence; collisions resolve to the higher-priority table since each table is checked in order).
- [x] CSS: `.broken-wikilink` with muted color + dotted underline (Obsidian-aligned). Resolved wikilinks render as plain `<a>` — intentionally indistinguishable from regular markdown links.
- [x] Verified: 87/87 markdown files render without errors; spot checks confirm body wikilinks, frontmatter list wikilinks, display aliases (`[[X|Y]]`), code-fenced wikilinks (preserved), and unresolvable targets (broken-styled).

## Notes
This task also fixed an upstream taxonomy gap: project-os was missing `plan.md` and `dashboard.md` templates. They now exist upstream (`~/Dev/repos/project-os/docs/__templates__/`) plus their schema sections in `SCHEMAS.md`, were synced down via `tools/scripts/sync-project-os.sh ../project-os`, and the three ADR notes that mistakenly used `type: "[[decision]]"` were corrected to `type: "[[adr]]"`. See [[CHG-20260507-Wikilink-Resolver]] for the full landing.

**Verification gap (same as TASK-0002):** no `TST-*` notes — verification is a 87-file render sweep + targeted spot checks, not formal unit tests. Test infrastructure first lands with the cockpit feature (FEAT-0006).

**Index seeding for TASK-0007:** the cockpit's "shared note index + backlink graph" task was specified to *build* the index. With TASK-0003 done, the lookup tables already exist; TASK-0007 just adds the inbound/outbound link graph alongside. Update the task note when starting TASK-0007 to reflect that.
