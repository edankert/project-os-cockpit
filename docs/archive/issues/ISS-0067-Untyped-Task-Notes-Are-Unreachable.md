---
type: "[[issue]]"
id: ISS-0067
aliases: ["ISS-0067"]
title: "Three task notes carry no frontmatter and reach no surface — ISS-0062's mechanism, surviving for the task type because the fix was applied to plans only"
status: fixed
phase: "[[PHASE-012-Attention-In-The-Strip]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["independent review of PHASE-010, round four (2026-07-30)"]
severity: low
component: cockpit-nav
related: ["[[ISS-0062-Most-Plans-Are-Invisible]]", "[[REQ-0025-No-Type-Loses-Its-Surface]]", "[[TASK-0235-Plan-Lookup-By-Path]]", "[[TASK-0037-Exclude-Canonical-Container-Dirs]]"]
tests: []
reviewed_by: "model:claude-opus-5"
review_date: 2026-07-30
review_verdict: "approved"
---

# Untyped task notes are unreachable

## Problem

Three task notes have no frontmatter at all:

- `docs/features/overview-scopes/plan/tasks/TASK-0182-Nest-Children-By-Shared-Phase.md`
- `docs/features/agent-hooks/plan/tasks/TASK-0183-Revive-Ended-Session-On-Activity.md`
- `docs/features/embedded-terminal/plan/tasks/TASK-0187-Restart-Console-Action.md`

`notes_by_type("task")` therefore misses them, and `features` is a `DOC_TREE_EXCLUDED_ROOTS` root ([[TASK-0037]]), so they do not join the Docs tree either. They reach no surface in the cockpit — exactly [[ISS-0062]]'s mechanism, which PHASE-010 fixed for plans and not for tasks.

```
$ find docs/features -path '*/plan/tasks/TASK-*.md' | wc -l
247
$ python -c "... len(list(idx.notes_by_type('task')))"
244
```

## Why this is `low` and was not caught by REQ-0025

[[REQ-0025]] is written about **types**, and the type is fine: 244 of 247 task notes are reachable in the Tasks mode, so no type lost its surface and the gate was correct to pass. This is the residue that a type-level guarantee does not cover — individual notes, not a category.

That distinction is the useful part. [[ISS-0062]] was found by counting a type's members against the filesystem; this was found by sweeping *notes* rather than types, which the reviewer only began doing in round four. A per-type count would never surface it, because 244 is not suspicious.

## Expected

Every `TASK-*.md` under `features/<slug>/plan/tasks/` is reachable from its feature or from the Tasks mode, whether or not it carries frontmatter.

## Next Actions

- [ ] Decide the shape. The two options are the same pair [[ISS-0062]] weighed, and it is worth deciding the same way or knowingly differently:
  - **Read the path** — `features/<slug>/plan/tasks/TASK-*.md` already encodes the parent, exactly as `plan/PLAN.md` did. This is what [[TASK-0235]] did for plans, and its argument applies unchanged: typing should not be a precondition for visibility.
  - **Add the frontmatter** to the three files. Cheap, and [[ISS-0062]] rejected the equivalent because it "passes the count while leaving the mechanism dependent on frontmatter nobody is required to write". Three files is a weaker case for the mechanism argument than nineteen was, so this may genuinely be the right call here — but it should be a decision, not a default.
- [ ] Whichever wins, consider a validator rule instead: a `TASK-*.md` with no `type:` is arguably a corpus defect the validator should name, which would fix the class rather than the instances.

## Notes

Filed against [[PHASE-999-Future]], not [[PHASE-010]] — that phase is `done` and nothing in it is incomplete. This is adjacent work its fix made visible.

Worth recording that the reviewer surfaced this *and* declined to allocate an ID for it, on the grounds that a reviewer records findings and a planner allocates. That is the right line, and it is why this note exists rather than a verdict comment.

## Fixed 2026-07-30 — read the path, as ISS-0062 did

Option 1: `_task_records(index)` unions `notes_by_type("task")` with untyped notes at `features/<slug>/plan/tasks/TASK-*.md`. The Tasks mode reads it instead of the type lookup.

**Union, not a path-only sweep.** A task note living somewhere else is still a task, and the type is the claim wherever it is written; the path is only the fallback for a note that makes no claim. A path-only rule would have silently dropped any task outside that layout.

Verified: 247 `TASK-*.md` on disk, 244 typed, `_task_records` returns **247**, and `TASK-0182` / `TASK-0183` / `TASK-0187` all appear in the Tasks mode in the running app.

Deliberately **not** done: adding frontmatter to the three files. Same reasoning as [[ISS-0062]] — it would pass the count while leaving visibility dependent on frontmatter nobody is required to write, and it would hide whether the path fallback works.

Guarded by `test_every_task_note_on_disk_is_reachable`, asserted against a filesystem glob rather than a literal, and mutation-verified by removing the fallback.

Note for whoever fixes the class rather than the instances: the validator already warns `PLAN-UNTYPED` for untyped plans. There is no equivalent for tasks, which is why these three were invisible to it as well as to the UI.

## Independent review — 2026-07-30 (model:claude-opus-5, fresh context, separate session) — approved

Approved, verified rather than accepted. `_task_records` returns 247 against 247 `TASK-*.md` on disk (244 typed), `_tasks_groups` yields 247 items, and `TASK-0182` / `TASK-0183` / `TASK-0187` appear in the `unset` group with filename-derived titles and working `/docs/...` urls — so they reach a surface and are clickable, which is the claim. The union-not-path-sweep reasoning is right: a path-only rule would drop a task written outside that layout, and the type is the claim wherever it appears.

`test_every_task_note_on_disk_is_reachable` is one of the two genuinely adequate new guards in this range — asserted against a filesystem glob, so a type-based subset cannot satisfy it, and the second assertion (`typed < on_disk | typed`) correctly fails if the path fallback stops being exercised, which is what keeps the first assertion from passing vacuously.

Two boundaries worth recording, neither a defect in this fix: `stats_payload` still uses `index.notes_by_type("task")` (`cockpit.py:880`), so these three are reachable in the Tasks mode but remain absent from the phase strip and the task counts — consistent with the issue's scope, which is reachability. And the note for whoever fixes the class rather than the instances is the useful half of this note: there is no `TASK-UNTYPED` counterpart to `PLAN-UNTYPED`, which is why the validator was as blind as the UI.
