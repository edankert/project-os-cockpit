---
type: "[[task]]"
id: TASK-0512
aliases: ["TASK-0512"]
title: "When a release names contents, its gate reports what blocks THAT release"
status: backlog
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
parent: "[[FEAT-0129-A-Release-Names-Its-Own-Contents]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# When a release names contents, its gate reports what blocks THAT release

`blocking_for(subjects)` already exists with a production caller. This passes the release's own feature ids.

Must not widen or narrow any existing release's gate: absence of named contents keeps the whole-suite gate.
