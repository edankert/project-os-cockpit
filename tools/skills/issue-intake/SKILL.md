---
type: skill
id: SKILL-ISSUE-INTAKE
status: active
owner: group:maintainers
created: 2026-01-27
updated: 2026-01-27
tags: [skills, issues]
---

# Skill: Issue intake

## When to use
- A prompt reports a bug, mismatch, broken workflow, unclear documentation, or unexpected behavior.

## Inputs
- User prompt, repro steps/logs, and any affected repo paths.

## Outputs
- `../../../SNAPSHOT.yaml` updated (`items.issues` + links to affected features/tasks).
- A new/updated `../../../docs/issues/ISS-####-Short-Description.md` note.
- Optional: new `TASK-*` entries/notes if work can be immediately planned.

## Checklist
1. Assign the next `ISS-####` (use `../../../SNAPSHOT.yaml -> counters.ISS`).
2. **Determine phase (optional)**:
   - If the issue is tied to a specific milestone, assign a `phase` (consult `../../../docs/PHASES.md` and relevant `../../../docs/phases/PHASE-*.md` notes).
   - If the issue affects an existing feature, inherit phase from that feature.
   - Leave `phase` empty for issues not tied to a specific milestone.
3. Update `../../../SNAPSHOT.yaml`:
   - add `items.issues.<ISS-####>` with `title`, `status`, `severity`, `component`, `phase` (if applicable), `file`
   - link to impacted `features` and/or planned `tasks`
   - if `phase` is a `PHASE-*` ID, add the issue/task IDs to `items.phases.<PHASE-####>` and the phase note
   - set `focus.issue` if this is the current work
4. Create/update the issue note from `../../../docs/__templates__/issue.md`:
   - set `phase` in frontmatter if applicable
   - include repro, expected vs actual, evidence paths
5. If the fix requires implementation:
   - ensure there is a parent `FEAT-*` (create if needed)
   - create one or more `TASK-*` under the feature and link them in snapshot + notes
   - tasks inherit phase from the issue or parent feature
6. **Impact analysis:**
   - If the issue links to existing features, run `../impact-analysis/SKILL.md` to check whether the proposed fix may conflict with existing requirements.
   - If conflicts are found, stop and present resolution options before implementation.
7. **Risk scan:**
   - Review the issue against risk scan triggers in `../../instructions/LIFECYCLE.md`.
   - If any trigger applies, run `../risk-scan/SKILL.md` and create/update `RISK-*` notes.
8. If verification is needed, create a `TST-*` note (use `../test-authoring/SKILL.md`) and link it from the issue/task/requirement as appropriate.
