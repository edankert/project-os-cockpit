---
type: "[[issue]]"
id: ISS-0164
aliases: ["ISS-0164"]
title: "Phases are the second note type the quick palette cannot find — 34 notes, the same defect [[ISS-0142]] described for releases and claimed was the only one"
status: "open"
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-08-14
updated: "2026-08-14"
source: ["Found while fixing [[ISS-0142]], 2026-08-14 — the per-type reachability measurement that verified the release fix reported a second type at zero"]
severity: low
component: navigation
parent: ""
related: ["[[ISS-0142-The-Release-Note-Cannot-Be-Found-By-Name]]", "[[FEAT-0072]]"]
tests: []
---

# Phases are the second type the palette cannot find

## What was found

[[ISS-0142]]'s title calls releases *"the one note type the quick-switch corpus has never carried"*. That was measured by hand, one type at a time. Measuring **every** type at once, while verifying its fix:

| type | notes | findable by id |
|---|---|---|
| task | 417 | 417 |
| issue | 163 | 163 |
| feature | 100 | 100 |
| requirement | 36 | 36 |
| adr / design / risk / decision | 36 | 36 |
| release *(fixed 2026-08-14)* | 1 | 1 |
| **phase** | **34** | **0** |

Typing `PHASE-011` into the bar reading *"Search files, IDs, or commands…"* returns **No matches**, for the same reason `REL-0001` did: `QUICK_CORPUS_MODES` is `features`, `issues`, `intent`, `library`, and no nav mode carries phases.

## Not in scope for [[ISS-0142]], deliberately

That issue was scoped to releases and fixed as scoped. This is filed rather than folded in because the answer is genuinely different: releases belong on `intent` — few, permanent, project-level, beside decisions and risks — and **phases do not**. A phase is neither a constraint nor a record of intent; it is the plan's spine, and its home is the overview's phase strip.

So this needs a decision about *where*, not a one-line addition to an existing loop.

## Options

1. **A third explicit fetch** beside the two `buildQuickCorpus` already carries for changes and tests. Honest about phases having no nav mode, and adds a fourth thing to keep in step.
2. **Phases join `library`** with the standing documents — they are permanent records of the project's shape, which is close to what that mode holds.
3. **Leave it.** Phases are reachable from the overview strip and from `docs/PHASES.md`, and 34 rows in the palette may cost more than they return.

## What is guarded meanwhile

`test_every_id_bearing_type_is_findable_in_the_palette` measures all types at once and names this gap explicitly, so a **third** instance cannot appear silently the way this one did. That guard is the actual product of [[ISS-0142]]: the bug was found by hand twice, and a type added later would have made it three.

## Not a defect: plans

54 `plan` notes are also unreachable by id, and correctly so — `PLAN.md` carries no `id:` field at all. They are reached by path through their feature. Recorded so the next measurement does not re-file them.
