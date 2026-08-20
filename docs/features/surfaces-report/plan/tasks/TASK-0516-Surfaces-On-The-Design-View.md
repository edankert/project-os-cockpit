---
type: "[[task]]"
id: TASK-0516
aliases: ["TASK-0516"]
title: "Surfaces appear on the design view, with a surface carrying zero checks visible as such"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
parent: "[[FEAT-0130-Surfaces-Are-A-First-Class-Type]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Surfaces appear on the design view, with a surface carrying zero checks visible as such

Edwin: *"where should they be visible, probably in the design?"* The design view already holds what bounds the project. A surface with no coverage is the row this whole type exists to make possible.

## Done 2026-08-20

`Surfaces` is a group in the design view's constraints loop, and the head reads **`Surfaces · 1 with no checks`**.

### Why the design view is the right home

Edwin: *"where should they be visible, probably in the design?"* — and it holds for the reason that group exists at all. The design view carries what **bounds** the project; a surface is a place the product has, permanent and project-level, exactly like a decision or a risk.

A group in the loop rather than a fetch of its own also makes surfaces **findable**: the quick corpus is built from nav modes, so one entry answers the palette and the navigator at once. That closes the gap [[TASK-0514]] had to record in `KNOWN_ABSENT`.

### The zero-coverage row went on the head, and the two attempts before it are the point

*"A surface with no coverage is the row this whole type exists to make possible."*

1. **`subtitle` — sent and never drawn.** `buildNavRow` documents it as *deliberately NOT rendered*. That is [[ISS-0225]] exactly, reintroduced **inside the phase that removed it**, and it was caught by reading the renderer rather than by any test: the existing guard scopes to tests-mode rows.
2. **`progress` — drawn, and worse.** It paints a *completion* bar. An uncovered surface has no **unfinished** work; it has no work. A 0% bar over checks that do not exist reads as a job somebody has not started.
3. **The head.** Already carries counts on this pane ([[ISS-0241]]), already drawn, no renderer change. A test asserts the row gains no `progress` and no coverage field, so attempt 2 cannot come back quietly.

### Matched on the title, because that is all there is

`surface_coverage` joins a surface's title against `area:` strings. A check carries `area:` as a **string**; making it a `SUR-*` link is [[TASK-0515]]'s mapping and has not happened. So `SUR-0001` reads zero — and that is **correct rather than a broken join**: at this moment it genuinely covers nothing.

Ten tests, three mutants: dropping the group, dropping the head count, and putting `progress` back on the row.

## Independent review — fourth pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`. Verdict: **approved**. Re-measured or re-executed, not read.

All three claimed mutants re-run, all three genuine catches — no equivalents:

| mutation | caught by |
|---|---|
| drop the `surfaces` group from the design view | `test_the_count_is_not_sent_on_a_field_no_renderer_draws`, `test_a_covered_surface_drops_off_the_head_count` (4 failures) |
| drop the `N with no checks` head count | `test_a_surface_with_no_checks_is_visible_as_such` |
| neuter `surface_coverage` | two tests |

Putting the count on the **head** is the right call and the note's reasoning for it is verifiable: `subtitle` is documented in `buildNavRow` as deliberately not rendered, so the first attempt would have been `ISS-0225` reintroduced inside the phase that removed it; and `progress` paints a completion bar, which an uncovered surface has no meaning for. Computing `surface_coverage` once outside the loop matters — `acceptance.load` walks the suite.
