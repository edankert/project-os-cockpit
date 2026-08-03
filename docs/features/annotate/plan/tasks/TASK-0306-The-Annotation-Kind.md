---
type: "[[task]]"
id: TASK-0306
aliases: ["TASK-0306"]
title: "The queue learns `annotation`, with an anchor schema"
status: backlog
phase: "[[PHASE-025-Design-Before-Code]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0069-Annotate-To-Request]]"]
parent: "[[FEAT-0069-Annotate-To-Request]]"
effort: S
depends: []
blocks: []
related: []
tests: []
---

# The queue learns `annotation`, with an anchor schema

## Definition of Done

- review-request accepts kind `annotation` with subject + anchor (variant + CSS path + offset, or text quote); the store round-trips it; the ledger records it like any request.
