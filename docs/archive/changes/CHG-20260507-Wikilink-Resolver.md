---
type: "[[change]]"
id: CHG-20260507-Wikilink-Resolver
aliases: ["CHG-20260507-Wikilink-Resolver"]
title: "Wikilink resolver + Obsidian-aligned rendering + plan/dashboard templates upstream"
status: merged
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
source: ["[[TASK-0003]]"]
commit: ""
pr: ""
impacts:
  - "src/docs_server/index.py"
  - "src/docs_server/wikilinks.py"
  - "src/docs_server/renderer.py"
  - "src/docs_server/templates.py"
  - "src/docs_server/server.py"
  - "src/docs_server/static/base.css"
  - "docs/__templates__/plan.md"
  - "docs/__templates__/dashboard.md"
  - "docs/__templates__/SCHEMAS.md"
  - "docs/decisions/ADR-0001-*.md"
  - "docs/decisions/ADR-0002-*.md"
  - "docs/decisions/ADR-0003-*.md"
issues: []
features: ["[[FEAT-0001]]"]
related: ["[[REQ-0002]]", "[[TASK-0007]]", "[[CHG-20260507-Render-Pipeline-Online]]"]
---

# Wikilink resolver online

## Summary
docs-server now resolves Obsidian-style wikilinks. At startup it walks the docs tree and builds a multi-table index keyed by `id`, frontmatter aliases, filename stem, and title. Markdown bodies and frontmatter strings both go through the resolver — `[[FEAT-0001]]` clicks through to the file, `[[FEAT-0001|the renderer]]` honours the display alias, and unresolvable targets render as Obsidian-styled broken wikilinks (faded text + dotted underline). Resolved wikilinks are intentionally indistinguishable from regular markdown links — same anchor styling, same hover behaviour.

This change also closed two taxonomy gaps that surfaced while testing the resolver: `plan` and `dashboard` were used as note types but had no templates upstream. Both now exist in `~/Dev/repos/project-os/docs/__templates__/` (with schema sections in `SCHEMAS.md`) and were synced down via `tools/scripts/sync-project-os.sh`. Three ADRs that mistakenly used `type: "[[decision]]"` were corrected to `type: "[[adr]]"`.

## Impact

### Behavioural
- Every `.md` body containing `[[X]]`, `[[X|Y]]`, or `[[X#Heading]]`-style patterns now renders with resolved anchors where targets exist. Code-fenced wikilinks (inside backticks or fences) are left untouched — they're protected by the markdown parser before the inline pattern runs.
- Metadata strip values containing wikilinks resolve too: `phase: "[[PHASE-001-MVP]]"`, `related: ["[[FEAT-0001]]", ...]`, and `type: "[[feature]]"` all become clickable.
- Unresolvable wikilinks render as `<span class="broken-wikilink" title="unresolved wikilink">[[Foo]]</span>` — visible but quiet (faded text + dotted underline).

### Index changes
- `__templates__/` is now indexed (was previously excluded). This is required for type wikilinks (`[[feature]]`, `[[task]]`, etc.) to resolve to their template stubs — matching Obsidian's behaviour. `__bases__/` remains excluded (`.base` files aren't `.md` so it has nothing to index anyway).
- The index exposes `update_path(path)` for incremental invalidation; the FEAT-0002 watcher will call this in TASK-0005.

### Upstream project-os changes
- New: `docs/__templates__/plan.md` (per-feature delivery sequence; `id: PLAN-FEAT-####`).
- New: `docs/__templates__/dashboard.md` (overview pages; minimal frontmatter — `type` + `title`).
- Extended: `docs/__templates__/SCHEMAS.md` with sections for both new types.
- **Downstream impact:** other project-os consumers should run `tools/scripts/sync-project-os.sh <path-to-project-os>` to pick these up. Without the sync, `[[plan]]` and `[[dashboard]]` will keep rendering as broken wikilinks in those repos.

### Resolution priority (per REQ-0002)
1. Frontmatter `id` field
2. Frontmatter `aliases`
3. Filename without extension
4. Frontmatter `title` or first H1

Lookups are first-write-wins per table; tables are checked in priority order. The project-os convention (`aliases: ["<id>"]`) means IDs resolve via two tables but the higher-priority `id` table wins.

## Follow-ups
- [ ] [[TASK-0004]] — auto-generated index pages (`/index/features` etc.); now unblocked.
- [ ] [[TASK-0005]] — file watcher needs to call `Index.update_path(...)` on `.md` change events.
- [ ] [[TASK-0007]] — the cockpit's "build the note index + backlink graph" task: re-scope to *extend* the existing index module rather than build it from scratch. Lookup tables and `NoteRecord` are already in place; the link graph is what's left.
- [ ] Several existing notes still use bare-string `type: dashboard|architecture|glossary|reference` (e.g. `INDEX.md`, `OWNERSHIP.md`, `dashboards/*.md`) — those render as plain text rather than wikilinks. Worth a separate taxonomy pass.
- [ ] Add a `TST-*` note retro-fitting acceptance coverage for the resolver — currently verified by render sweep + spot checks.
