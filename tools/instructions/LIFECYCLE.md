# Lifecycle rules (LLM-maintained documentation system)

This documentation system is designed to be maintained by an LLM across the full lifecycle of work: intake → plan → implement → verify → close.

## Source of truth
- `../../SNAPSHOT.yaml` is the **canonical, machine-readable active context** for agents/LLMs.
- Notes under `../../docs/` are the durable human-readable record; keep their frontmatter consistent with the snapshot.
- Bases dashboards are for human consumption: they render views over note frontmatter and are not canonical for agents.

## Test storage (hybrid)
- Feature-scoped tests belong under the feature they verify:
  - `docs/features/<feature-slug>/plan/tests/TST-####-*.md`
- System-wide or cross-feature tests belong under:
  - `docs/tests/TST-####-*.md`

## Statuses
- Allowed statuses and transitions are defined in `STATUSES.md`.

## Preflight (must happen before code changes)
When a prompt implies work (bugfix, feature, refactor, behavior change):
1. **Classify** the prompt as one (or more) of: issue, feature, requirement, risk, chore/docs-only.
2. **Orchestration check** (multi-agent projects):
   - If your orchestration layer (e.g., Claude Code Agent Teams, Codex parallel) assigns a specific task, verify it exists in `../../SNAPSHOT.yaml` and that its status allows work (e.g., `backlog`, `next`, not already `done`).
   - If working without orchestration, select work based on `focus` and item statuses.
3. **Update `../../SNAPSHOT.yaml` first**:
   - allocate IDs (increment `counters`)
   - create/update `items.*` entries and relationships
   - set `focus` to the active work
4. **Create/update the relevant notes (from templates)**:
   - Issue: `../../docs/issues/ISS-####-*.md`
   - Requirement: `../../docs/requirements/REQ-####-*.md`
   - Feature: `../../docs/features/<slug>/FEAT-####-*.md` plus `plan/PLAN.md`
   - Task: `../../docs/features/<slug>/plan/tasks/TASK-####-*.md` (must have `parent`)
   - Risk: `../../docs/risks/RISK-####-*.md`
5. **Impact analysis** (when creating or modifying requirements):
   - Run `../skills/impact-analysis/SKILL.md` to check for tensions with existing requirements on overlapping features.
   - If conflicts are found: STOP and present resolution options to the user before proceeding with implementation.
6. Ensure note frontmatter is consistent with the snapshot (IDs/statuses/links) so Bases dashboards reflect reality.
7. For multi-platform projects: set `platform` in new notes when work is platform-specific.
   Infer from parent item, code paths, or tags. Leave empty if truly cross-cutting.

If the prompt is purely a question/explanation (no work requested), you may skip preflight.

## Phase alignment (optional gating)
When the project uses phase-gated development (see `../../docs/PHASES.md`):
1. **Verify phase**: Check the `phase` property in the task/feature frontmatter before starting work.
2. **Consult registry**: Review `../../docs/PHASES.md` to understand the boundaries and context of that phase.
3. **Prevent phase bleeding**: Do not introduce implementations from future phases prematurely.
   - Example: Don't build Phase 4 export logic while working on a Phase 2 core engine task.
4. **Flag scope concerns**: If a task requires future-phase dependencies, document it and discuss before proceeding.
5. **Track active phase**: Keep `focus.phase` in `../../SNAPSHOT.yaml` aligned with the current development milestone.

## Mandatory Automated Documentation
Agents are REQUIRED to automatically keep the documentation system in sync with code changes.
- **No Orphaned Code:** Every functional code change must have a corresponding Task under `../../docs/features/<slug>/plan/tasks/`.
  - Functional code changes include: new features, bug fixes, refactors that alter behavior, API changes, and dependency updates.
  - Excluded: typo fixes, comment-only edits, formatting changes, and pure documentation updates (these may be tracked via `CHG-*` notes if significant).
- **The Atomic Sync Rule:** The global `../../SNAPSHOT.yaml` and relevant Markdown notes MUST be updated in the same turn or immediately following the code implementation.
- **Counter Integrity:** Always increment the relevant `counters` in `../../SNAPSHOT.yaml` when creating new IDs.

## Execution (implementation phase)
- Only start code changes once planning artifacts exist (issue/feature/tasks as appropriate).
- Keep snapshot `focus` aligned with what is actually being worked.

## Close-out (must happen after work)
After completing a task/issue/feature:
1. Update the Markdown note status (`done` / `fixed` / `closed` / `done`).
2. Update `../../SNAPSHOT.yaml` to reflect:
   - updated statuses
   - new/changed relationships (links)
   - updated focus/metrics
3. Add a change note (`../../docs/changes/CHG-YYYYMMDD-Short-Description.md`) when repo behavior/paths change.
4. If new hazards were introduced (new dependency, env var, contract), add/update a `RISK-*` and link it.
5. Do not delete completed notes; use status + links to preserve history.
6. Apply verification gating (see `QUALITY.md`): only close/verify/done when required `[[test]]` notes are `status: passing`.
7. **Acceptance test maintenance** (see `TESTING.md`):
   - After implementing a feature: ensure Tier 1 acceptance tests exist for the user-visible behavior.
   - After fixing an issue: create a Tier 2 regression test that reproduces the original bug scenario.
   - After any code change: uncheck acceptance tests whose scope overlaps with the changed code.

## Release (must happen before shipping)
When preparing a release:
1. **Triage open issues:** For each open `ISS-*`, decide: fix before release, or ship as known issue.
2. **Verify acceptance tests:** All Tier 1 and Tier 2 tests must be checked (passing). See `QUALITY.md` for gating rules.
3. **Create release note:** `../../docs/releases/REL-####-v<version>.md` from template. Include scope (features, fixed issues), known issues, verification summary, and user-facing release notes.
4. **Update SNAPSHOT:** Add `items.releases.<REL-ID>`, set `focus.release`, increment `counters.REL`.
5. **Version bump:** Update the application version (versionCode + versionName or equivalent).
6. **Build:** Create signed release artifact.
7. **Tag:** `git tag -a v<version> -m "Release <version>"` and push.

After release is deployed:
1. Update `REL-*` status to `published`.
2. Remove Tier 3 acceptance tests (verified by unit tests).
3. Clear SNAPSHOT focus and set to next milestone.
4. Open issues become the backlog for the next release.

## Snapshot retention (active + recent)
- Keep `../../SNAPSHOT.yaml` focused on active + recent items.
- Do not keep the entire history in the snapshot; the notes are the long-term record.
- Retention details live in `SNAPSHOT.md`.

## Risk scan triggers (create/update a `RISK-*`)
- New external toolchain/runtime dependency or version constraint
- New required env var or configuration surface
- Directory layout / artifact path changes
- Performance/runtime increase, new long-running steps
- Security/credential/license exposure risk
