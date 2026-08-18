---
type: "[[task]]"
id: TASK-0495
aliases: ["TASK-0495"]
title: "One verb for one act — the registry carries `Run` and `Walk` over the same type today"
status: backlog
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0123-The-Walk-Surfaces-Say-One-Thing]]"]
parent: "[[FEAT-0123-The-Walk-Surfaces-Say-One-Thing]]"
effort: S
depends: ["[[TASK-0492-Retire-The-Manual-Run-Obligation]]"]
blocks: []
related: []
tests: []
---

# One verb

The registry carries both simultaneously: `test → Run` and `release gate → Walk`, over one type. Live on `your-trainer` as **`Run 5 tests`** and **`Walk 1 release gate`** on the same screen.

The split made sense while they were different types. Under [[ADR-0031-One-Test-Type-Acceptance-Is-A-Level]] they are one type on a scale, so the surface has two words for one act separated by a field the reader cannot see — and it shows: the group called **`Needs a run`** contains only the NON-acceptance tests, while the population a person actually walks sits under `Tier 1/2/3` with no verb at all.

Pick one deliberately. *Walk* describes what a person does to a checklist; *Run* describes what a machine does to a command — which is an argument for `Walk` on the human side and `Run` staying with `command:`. Apply it to the registry verbs, the group headings and the buttons in one pass, or the two words simply move.

Done when: one verb names the human act everywhere, and `run` refers only to something a machine does.
