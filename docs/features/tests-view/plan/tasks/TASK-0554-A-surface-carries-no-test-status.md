---
type: "[[task]]"
id: TASK-0554
aliases: ["TASK-0554"]
title: "A surface carries no test status"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0128-The-Tests-View-Leads-With-The-Work]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# [[ISS-0226]]

See the issue for the reasoning and the suggested fix; its `Done when` is this task's definition of done.

## Done 2026-08-19

`status` is gone from a surface row. It carried the runner's `ready`/`passing` for a place in the application that is not run, and it was a second encoding of the bar besides. The surface's checks keep their own statuses, as children.
