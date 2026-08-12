---
type: reference
id: OWNERSHIP
owner: user:edwin
created: 2026-05-07
updated: 2026-08-12
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
- **Owns everything.** 98 features, 33 phases, the sidecar, the shell and every infrastructure file. Listing them was tried and does not survive: this entry named five features — the whole project in May — and stayed unchanged for 97 days while it grew to 98, still naming a *"downstream pilot (FEAT-0005)"* whose shim `tools/project-os-cockpit/` **never existed in any repo**.
- The `owner:` field on a note is what carries ownership. This registry says who the identities are, not what each one holds.

## Systems

### `system:llm`
- Purpose: LLM/agent edits via Claude Code / Codex. Acts on behalf of `user:edwin`. Used as `owner:` only for items the user explicitly delegates to autonomous-agent maintenance.

## Inherited ownership

Files synced from `~/Dev/repos/project-os/` (`tools/instructions/*`, `tools/skills/*`, `docs/__templates__/*`, `docs/__bases__/*`) carry their upstream owner labels. Edits to those files belong upstream — fix in `project-os` and re-sync via `tools/scripts/sync-project-os.sh ../project-os`.
