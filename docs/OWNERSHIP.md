---
type: reference
id: OWNERSHIP
status: active
owner: user:edwin
created: 2026-05-07
updated: 2026-05-07
tags: [ownership, teams, groups, users]
---

# Ownership registry

Single-maintainer project. Edwin Dankert (`user:edwin`) owns everything by default. The `owner:` frontmatter field on any note may set a specific owner if delegation happens later.

## Owner ID formats
- Users: `user:<handle>` (individuals)
- Groups: `group:<name>` (cross-team rotations) — defined here only if used
- Systems: `system:<name>` (automation identities)
- Unassigned: `unassigned`

## Users

### `user:edwin`
- Name: Edwin Dankert
- Owns: render server (FEAT-0001), live reload (FEAT-0002), embedded terminal (FEAT-0003), project-os adapter (FEAT-0004), downstream pilot (FEAT-0005), all infrastructure files in this repo.

## Systems

### `system:llm`
- Purpose: LLM/agent edits via Claude Code / Codex. Acts on behalf of `user:edwin`. Used as `owner:` only for items the user explicitly delegates to autonomous-agent maintenance.

## Inherited ownership

Files synced from `~/Dev/repos/project-os/` (`tools/instructions/*`, `tools/skills/*`, `docs/__templates__/*`, `docs/__bases__/*`) carry their upstream owner labels. Edits to those files belong upstream — fix in `project-os` and re-sync via `tools/scripts/sync-project-os.sh ../project-os`.
