---
type: "[[issue]]"
id: ISS-0082
aliases: ["ISS-0082"]
title: "Two code paths read the phase link differently, so renaming PHASE-016 during the merge forked its children into a phantom group in the features navigator while the overview showed them correctly"
status: fixed
severity: medium
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-02
source: ["Found 2026-08-02 while measuring the features view for [[PHASE-022]] — a PHASE-016 group appeared twice, once unresolvable"]
component: server
related: ["[[ISS-0077-Phase-Granularity-Collapsed-To-One-Per-Request]]", "[[PHASE-016-The-Overview-Answers-Questions]]"]
fixed_by: ["[[TASK-0268-Groups-With-Open-Work-Sort-First]]"]
tests: ["[[TST-0023-Completed-Work-Ordering]]"]
---

# A rename forked a phase group

## What

`e98d53b` (my own merge, ISS-0077) renamed `PHASE-016-Errors-Become-Work` to `PHASE-016-The-Overview-Answers-Questions` and updated the phase note's own `features:` list. It did **not** update the five notes pointing back at it, which still carried the old slug (shown unlinked, because they are evidence rather than links):

```
docs/features/errors-as-work/FEAT-0051-…            phase: PHASE-016-Errors-Become-Work
docs/features/errors-as-work/plan/tasks/TASK-0252-… phase: PHASE-016-Errors-Become-Work
docs/features/errors-as-work/plan/tasks/TASK-0253-… phase: PHASE-016-Errors-Become-Work
docs/features/errors-as-work/plan/tasks/TASK-0254-… phase: PHASE-016-Errors-Become-Work
docs/phases/PHASE-017-…                             depends: PHASE-016-Errors-Become-Work
```

The features navigator therefore renders **two** PHASE-016 groups: the real one, and a phantom labelled with the raw dead slug, unresolvable, sorted last because it has no `order`.

## Why it happened, and why it will happen again

Two functions read the same frontmatter field and disagree:

| | reads | on a renamed link |
|---|---|---|
| `_phase_id_of` (overview) | `_PHASE_RE` → `PHASE-016` | resolves — correct group |
| `_phase_target` (features navigator) | `_strip_wikilink` → the whole slug | fails to resolve — phantom group |

That is why the bug was invisible on the overview and visible in the navigator. The data fix repairs today's corpus; only making both paths key on the canonical `PHASE-####` ID stops the next rename doing it again. **A phase's identity is its ID, not its title** — the title is prose and is expected to change.

The validator does not catch it: `PHASE-CHILDREN` checks the phase's `features:` list, which the merge *did* update, and nothing asserts the reverse direction resolves.

## Fix

1. `_phase_target` returns the canonical `PHASE-####`, matching `_phase_id_of`. A group can then never fork on a rename.
2. Repair the five stale links, so the notes say what is true.
3. A guard: every `phase:` link in the corpus resolves to a phase note that exists.

## Evidence it is fixed

The features navigator shows one PHASE-016 group; the guard fails if a link is pointed at a slug with no note behind it.
