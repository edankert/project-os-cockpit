---
type: reference
id: TEMPLATES-SCHEMAS
status: active
owner: team:docs
created: 2026-01-27
updated: 2026-01-27
tags: [templates, schema]
---

# Template schemas (frontmatter fields)

This document defines the intended meaning of the frontmatter fields used by the note templates in `docs/__templates__/`.

Conventions (naming, linking, property rules): `../../tools/instructions/OBSIDIAN.md`.

## Common fields (most templates)

- (required) `type` (link string): Obsidian link identifying the note type, e.g. `type: "[[task]]"`.
  - Used by tools/automation to classify notes; the snapshot references these types.
- (required) `id` (string): Stable identifier (should match the filename prefix).
  - Used for traceability and for `SNAPSHOT.yaml` keys.
- (required) `aliases` (list of strings): Must contain the `id` value. Enables Obsidian to resolve `[[FEAT-0007]]` to `FEAT-0007-Relationship-Model.md`.
  - When creating a note, set `aliases: ["<id>"]` (e.g., `aliases: ["FEAT-0007"]`).
  - Agents and skills must set this when creating notes from templates.
- (recommended) `title` (string): Human-friendly title for dashboards and summaries.
  - Keep short; no need to repeat the ID.
  - Keep it consistent with `SNAPSHOT.yaml` where possible.
- (required) `status` (string): Lifecycle state; each note type has its own allowed values.
- (optional) `phase` (list of links): Development phase(s) for milestone grouping. Link to phase notes, e.g. `phase: ["[[PHASE-001-Foundation]]"]`.
  - Enables machine-filtering, automated progress tracking, and dashboard grouping.
  - Leave as empty list for items not tied to a specific phase.
- (optional) `platform` (string): Target platform for multi-platform projects.
  Allowed: `ios`, `android`, `shared`, `""` (empty = not platform-specific).
  Use `shared` for items spanning all platforms. Leave empty for platform-agnostic items.
- (required) `owner` (string): Accountable person/team (can be `unassigned`).
  - Values must be defined in `[[OWNERSHIP]]` (or be `unassigned`).
- (required) `created` (date string): Creation date; keep stable.
- (required) `updated` (date string): Last material edit date; bump when meaningfully changed.
- (optional) `related` (list of links/strings): Cross-links to other notes and/or repo paths.
  - Prefer links (`[[...]]`) when pointing to other notes in this docs set.
- (optional) `source` (list of strings/links): Provenance for imported/derived items.
  - Use for links to external trackers, changelogs, or source documents.

## `adr.md` (`type: [[adr]]`)

Purpose: capture “why we chose X” with alternatives and consequences.

Fields:
- (required) `decision` (string): One-sentence decision statement.
- (required) `context` (string): One-sentence reason/background for the decision.
- (optional) `alternatives` (list): Options considered (strings or links).
- (optional) `consequences` (list): Key impacts/tradeoffs (strings or links).
- (optional) `supersedes` (string/link): Link to the ADR replaced by this one (prefer `[[ADR-....]]`).
- (optional) `superseded` (string/link): Link to the ADR that replaces this one (prefer `[[ADR-....]]`).

Where used:
- Referenced from `../decisions/README.md` for organization.

## `change.md` (`type: [[change]]`)

Purpose: durable “what shipped and why” note.

Naming:
- Filename should be `CHG-YYYYMMDD-Short-Description.md`.
- `id` should match the filename without `.md` (same `CHG-...-Short-Description` string).

Fields:
- (optional) `commit` (string): Commit hash.
- (optional) `pr` (string): PR/MR identifier or link.
- (recommended) `impacts` (list of strings): Affected areas/paths/flows (keep short).
- (optional) `issues` (list of links): Issues associated with the change.
- (optional) `features` (list of links): Features associated with the change.

Where used:
- Tracked in `SNAPSHOT.yaml` (`items.changes`) for agent context and linked from change notes.

## `feature.md` (`type: [[feature]]`)

Purpose: a work package describing a capability. Child items (tasks, requirements, tests) link back to the feature via their relationship fields — the feature note does not maintain child lists.

Fields:
- (required) `goal` (string): Short outcome statement.
- (optional) `release` (string): Milestone/release label.

Where used:
- Tracked in `SNAPSHOT.yaml` (`items.features`) for agent context and linked from feature notes.
- Related tasks use `implements`, requirements use `specifies`, tests use `validates`, issues use `affects` to link back.

## `issue.md` (`type: [[issue]]`)

Purpose: canonical problem report / gap / bug.

Fields:
- (required) `severity` (string): e.g. `low|medium|high|critical` (project-defined).
- (recommended) `component` (string): Subsystem/area label (project-defined).
- (optional) `affects` (list of links): Feature(s) where this issue was found (`[[FEAT-...]]`).
- (optional) `tests` (list of links): `[[TST-...]]` links used to reproduce/verify the issue.

Where used:
- Tracked in `SNAPSHOT.yaml` (`items.issues`) for agent context and linked from issue notes.

## `requirement.md` (`type: [[requirement]]`)

Purpose: acceptance criteria that features/tasks must satisfy.

Fields:
- (required) `priority` (string): e.g. `low|medium|high` (project-defined).
- (optional) `scope` (string): Short scoping label (area/domain).
- (required) `acceptance` (list): Acceptance criteria statements (strings).
- (optional) `specifies` (list of links): Feature(s) this requirement constrains (`[[FEAT-...]]`).
- (optional) `verifies` (list of links/paths): Proof/verification pointers (workflows/tests/repo paths).
- (optional) `tests` (list of links): `[[TST-...]]` links that verify this requirement.

Where used:
- Tracked in `SNAPSHOT.yaml` (`items.requirements`) for agent context and linked from requirement notes.

## `risk.md` (`type: [[risk]]`)

Purpose: track hazards + mitigations.

Fields:
- (required) `likelihood` (string): e.g. `low|medium|high` (project-defined).
- (required) `impact` (string): e.g. `low|medium|high` (project-defined).
- (recommended) `mitigation` (list): Mitigation actions (strings or links to tasks).

Where used:
- Tracked in `SNAPSHOT.yaml` (`items.risks`) for agent context and linked from risk notes.

## `task.md` (`type: [[task]]`)

Purpose: actionable unit of work with a Definition of Done.

Fields:
- (optional) `implements` (list of links): Feature(s) this task delivers (`[[FEAT-...]]`).
- (optional) `fixes` (list of links): Issue(s) this task resolves (`[[ISS-...]]`).
- (optional) `effort` (string): Size label (e.g. `XS|S|M|L`).
- (optional) `due` (string/date): Due date.
- (optional) `depends` (list of links): Tasks/issues that must complete first.
- (optional) `blocks` (list of links): Tasks/issues blocked by this task.
- (optional) `tests` (list of links): `[[TST-...]]` links used to verify completion.

Note: A task should have at least one of `implements` or `fixes` set.

Where used:
- Tracked in `SNAPSHOT.yaml` (`items.tasks`) for agent context and linked from task notes.

## `test.md` (`type: [[test]]`)

Purpose: describe how to verify behavior (manual or automated) and provide durable coverage mapping.

Fields:
- (required) `scope` (string): `feature|system` (controls where the test note is stored).
- (required) `kind` (string): `manual|automated`.
- (recommended) `level` (string): `unit|integration|system|e2e`.
- (optional) `entrypoint` (string): Repo-relative command/script to run (or blank for purely manual tests).
- (optional) `validates` (list of links): Feature(s) or requirement(s) this test verifies (`[[FEAT-...]]`, `[[REQ-...]]`).
- (optional) `artifacts` (list): Expected artifacts/logs.
- (optional) `evidence` (list): Evidence from the last run (paths/log excerpts).
- (optional) `last_run` (string): Timestamp/label for the last execution.

Where used:
- Tracked in `SNAPSHOT.yaml` (`items.tests`) for agent context and linked from test notes.

## `release.md` (`type: [[release]]`)

Purpose: record what was shipped, when, and with what verification evidence.

Naming:
- Filename should be `REL-####-Short-Name.md`.
- `id` should match the filename without `.md`.

Fields:
- (required) `version` (string): Semantic version or release label (e.g. `1.2.0`).
- (recommended) `tag` (string): Git tag for the release (e.g. `v1.2.0`).
- (recommended) `date` (string): Release date (ISO 8601).
- (required) `features` (list of links): Features included in this release (`[[FEAT-...]]`).
- (optional) `changes` (list of links): Change notes included (`[[CHG-...]]`).
- (required) `tests_verified` (list of links): Acceptance tests verified for this release (`[[TST-...]]`).
- (optional) `previous_release` (string/link): Link to the prior release note (`[[REL-...]]`).

Where used:
- Tracked in `SNAPSHOT.yaml` (`items.releases`) for agent context and linked from release notes.
- The release-verification skill creates/updates REL-* notes as part of the release gating workflow.

## `phase.md` (`type: [[phase]]`)

Purpose: a development milestone grouping features, tasks, and other items into a coherent delivery stage.

Naming:
- Filename should be `PHASE-###-Short-Name.md`.
- `id` should match the filename without `.md`.

Fields:
- (required) `order` (integer): Sort order for dashboards (1, 2, 3...).
- (required) `goal` (string): What this phase delivers.

Statuses: `draft`, `active`, `completed`.

Where used:
- Tracked in `SNAPSHOT.yaml` (`items.phases`) for agent context.
- Other notes link to phase notes via `phase: ["[[PHASE-001-...]]"]`.
- The CONTEXT.base sidebar filters on `phase contains this.file` to show all items in a selected phase.

## `workflow.md` (`type: [[workflow]]`)

Purpose: canonical “front door” for a repo activity (what to run, inputs/outputs).

Fields:
- (recommended) `entrypoints` (list): Main scripts/commands (repo-relative).
- (optional) `prereqs` (list): Prerequisite tools/env/licenses (strings or links).
- (optional) `inputs` (list): Required inputs (paths/links).
- (optional) `outputs` (list): Expected outputs/artifacts/log locations.

Where used:
- Tracked in `SNAPSHOT.yaml` (`items.workflows`) for agent context and linked from workflow notes.

## `plan.md` (`type: [[plan]]`)

Purpose: per-feature delivery sequence — the ordered list of tasks that land the feature, plus dependencies and open questions to pin during implementation.

Naming:
- Filename should be `PLAN.md`, located under `docs/features/<slug>/plan/PLAN.md`.
- `id` should be `PLAN-FEAT-####` matching the parent feature's ID.

Fields:
- (required) `implements` (list of links): The feature this plan delivers (`[[FEAT-...]]`). Typically a single entry.
- (optional) `related` (list of links): Other features/plans this plan touches.

Statuses: `draft`, `active`, `done`.

Where used:
- Read alongside the feature note before any task starts.
- Not tracked individually in `SNAPSHOT.yaml`; the parent feature's tasks carry the status the snapshot reports.

## `dashboard.md` (`type: [[dashboard]]`)

Purpose: a curated overview page — typically embedded `.base` views and narrative pointers — that a human uses as a landing page for a slice of the project.

Naming:
- No fixed filename pattern. Singletons (`DASHBOARD.md` at the repo's docs root) and per-area dashboards (`docs/dashboards/Features.md` etc.) are both fine.

Fields:
- Minimal frontmatter — `type` and `title` are typically the only required keys.
- (optional) `id` / `aliases`: only when the dashboard needs to be wikilink-targetable beyond its filename.

Where used:
- Not tracked in `SNAPSHOT.yaml` — dashboards are presentation, not artefacts.
- Bases dashboards (`docs/__bases__/*.base`) carry their own filter logic; a `dashboard.md` is the human-readable wrapper that embeds them.
