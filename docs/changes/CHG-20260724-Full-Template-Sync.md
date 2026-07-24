---
type: "[[change]]"
id: CHG-20260724-Full-Template-Sync
title: "Full manifest sync from project-os: generated adapter surface, enforcing validator, deferral provenance — with tools/cockpit deliberately not vendored"
status: merged
owner: user:edwin
created: 2026-07-24
updated: 2026-07-24
source: []
commit: ""
pr: ""
impacts: ["tools/", "docs/__templates__/", "docs/__bases__/", ".claude/", ".cursor/", "SNAPSHOT.yaml"]
issues: ["[[ISS-0022-Behind-Template]]"]
features: []
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[CHG-20260724-Model-Routing-Upstreamed]]"]
---

# Full template sync

## Summary

This repo took only a narrow adoption during the 2026-07-24 fleet rollout (model-routing hook and subagents), because upstream was carrying uncommitted work at the time. Upstream is now committed, so the full manifest sync ran: `tools/instructions`, `tools/skills`, `tools/adapters`, `tools/scripts`, `docs/__templates__`, `docs/__bases__`, plus the generated native adapter surface (24 `.claude/skills/`, 8 `.cursor/rules/`) that this repo had never adopted. It also gains `generate-adapters.py` and the manifest-driven `sync-project-os.py`, replacing the old blunt rsync script.

## `tools/cockpit/` deliberately removed

Upstream vendors a copy of this project under `tools/cockpit/` and the manifest marks that path template-owned, so the sync created one here — a 372K duplicate of this very codebase, inside itself, that would immediately drift from `src/project_os_cockpit/`. It was deleted after the sync. **This repo is the canonical source for that code**; the vendored copy flows outward, never inward. project-os-dev's TASK-0049 records the same hazard from the other direction: *"the canonical file otherwise carries newer unrelated work — do not wholesale-copy over it when syncing."*

## Hand-merge: cockpit directives restored to LIFECYCLE.md

`tools/instructions/LIFECYCLE.md` is template-owned, and this repo had locally added two cockpit-focus steps to it (preflight step 7, close-out step 9) that upstream does not carry. The forced sync overwrote them. They were restored on top of upstream's new version, so the always-on cockpit-driving directive documented in `CLAUDE.md` still has its lifecycle hooks. `tools/instructions/COCKPIT.md`, `tools/skills/cockpit-driving/SKILL.md` and `tools/scripts/release-to-project-os.sh` are all repo-specific, are no longer shipped upstream, and were correctly left in place by the sync.

The merge-owned files (`docs/PHASES.md`, `docs/__templates__/SCHEMAS.md`, `ROADMAP.md`) were **not** touched — verified by checksum before and after. That is the `--force` merge-guard shipped upstream earlier today working as intended; before that fix they would have been silently overwritten.

## Error remediation (8 → 0)

The repo's own validator reported OK throughout, because its copy predated these checks. Against the current validator:

- **`DEFER-ORIGIN` / `DEFER-PARENT`** — TASK-0045 (preview tab) and TASK-0065 (build/sign/distribute) were `deferred` while still carrying `parent:`. Per `STATUSES.md` "Deferral and re-adoption", a parked item is descoped: `parent` is replaced by `origin` provenance. Applied in both note frontmatter and `SNAPSHOT.yaml`. Neither parent feature carries a `tasks:` scope list, so no `DEFER-SCOPE` follow-up was needed.
- **`METRICS`** — five counts reconciled (features 35→39 total / 30→34 done, tasks 162→197 total / 164→193 done, issues_open 0→1). The drift is mostly FEAT-0039, which landed after the counts were last computed.

## Impact

- `src/`, `tests/` and `desktop/` are untouched; this is documentation-system and tooling only.
- `/close-out`, `/issue-intake` and the other playbooks are now invocable as native Claude Code skills, including this repo's own `cockpit-driving`.
- The validator now enforces DEFER-*, REQ-*, and the new NOTE-DUP-ID/NOTE-STATUS checks at pre-commit and CI, not just advisory.

## Documentation Coverage (All Types Considered)

- features: not-applicable
- requirements: not-applicable
- tasks: not-applicable (tracked as ISS-0022)
- issues: updated ([[ISS-0022-Behind-Template]] → fixed)
- tests: not-applicable (no code change; validator run is the check)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new
- snapshot: updated (metrics, TASK-0045/0065 origin, ISS-0022)

## Follow-ups

- [ ] `docs/__templates__/SCHEMAS.md` and `docs/PHASES.md` remain merge-owned and stale against upstream; hand-merge when convenient. SCHEMAS.md is the one worth doing — it carries the acceptance-criteria-as-verification-record schema that REQ-BOXES warnings cite.
- [ ] Consider adding `tools/cockpit/` to a per-repo sync exclusion so future syncs do not recreate the self-vendored copy; today it must be deleted by hand each time.
