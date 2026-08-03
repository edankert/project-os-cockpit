---
type: "[[feature]]"
id: FEAT-0062
aliases: ["FEAT-0062"]
title: "The desk's dangling flows close: changes-requested reaches re-review, and a question gets its answer written back"
status: planned
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["Review 2026-08-03: the 10 changes-requested sit with no flow that resolves them; a question's answer path is the terminal"]
goal: "Every obligation the desk shows has its resolution on the same surface: request re-review dispatches the reviewer with the note and its prior findings; answering a question writes the answer where the asking agent will read it."
requirements: []
tasks:
  - "[[TASK-0285-Request-Re-Review]]"
  - "[[TASK-0286-Answer-In-Place]]"
release: ""
related: ["[[FEAT-0058-One-Shape-Per-Navigator]]"]
tests: []
---

# Desk resolution flows

## Goal

The desk shows obligations; PHASE-022 gave it the right shape; this gives each row its verb. **Re-review**: a changes-requested entry gains the action; it dispatches the independent-reviewer with the note, the prior verdict and findings — the same dispatch machinery the terminal uses, aimed by a button. **Answer**: a question entry gains an inline answer field; submit resolves the queue entry through the existing `review-resolve` with the answer as its outcome, and the asking session's dispatch channel carries it back.

## Out of Scope

- Auto-resolving changes-requested when the note changes. Whether the change answers the findings is the reviewer's judgment — that is what the re-review is.
- Threaded discussion. One question, one answer; a conversation belongs in a session.
