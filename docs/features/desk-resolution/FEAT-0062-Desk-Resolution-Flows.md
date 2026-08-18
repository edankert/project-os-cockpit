---
type: "[[feature]]"
id: FEAT-0062
aliases: ["FEAT-0062"]
title: "The desk's dangling flows close: changes-requested reaches re-review, and a question gets its answer written back"
status: cancelled
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["Review 2026-08-03: the 10 changes-requested sit with no flow that resolves them; a question's answer path is the terminal"]
goal: "Every obligation the desk shows has its resolution on the same surface: request re-review dispatches the reviewer with the note and its prior findings; answering a question writes the answer where the asking agent will read it."
requirements: []
tasks:
  - "[[TASK-0285-Request-Re-Review]]"
  - "[[TASK-0286-Answer-In-Place]]"
release: ""
related: ["[[FEAT-0058-One-Shape-Per-Navigator]]"]

---

# Desk resolution flows

## Goal

The desk shows obligations; PHASE-022 gave it the right shape; this gives each row its verb. **Re-review**: a changes-requested entry gains the action; it dispatches the independent-reviewer with the note, the prior verdict and findings — the same dispatch machinery the terminal uses, aimed by a button. **Answer**: a question entry gains an inline answer field; submit resolves the queue entry through the existing `review-resolve` with the answer as its outcome, and the asking session's dispatch channel carries it back.

## Out of Scope

- Auto-resolving changes-requested when the note changes. Whether the change answers the findings is the reviewer's judgment — that is what the re-review is.
- Threaded discussion. One question, one answer; a conversation belongs in a session.

## Cancelled — 2026-08-11

**Edwin's decision, via [[ISS-0126]]**: *"I have set ISS-0126 to declined but I meant that the feature should be cancelled as suggested."*

Both verbs this feature would have built address states that do not occur, on a surface that no longer exists. Re-measured against the live corpus on the day of the decision:

| | |
|---|---|
| `changes-requested` notes | 10 |
| …whose subject is **not** terminal — the only genuine obligation | **0** |
| review-ledger entries | 8 |
| …of kind `question` | **0** |

And [[ADR-0020]] retired the desk that "the same surface" referred to; [[FEAT-0090]] removed it.

**What is not lost.** The dispatch machinery this would have used already exists. And the inverse case is preserved by [[ISS-0121]]'s fix: a `changes-requested` note whose subject is *not* terminal **is** a genuine obligation, and if one ever appears it surfaces in the view that owns the note's type — which is where [[ADR-0020]] puts it, rather than on a desk.

If a question is ever written to the ledger, [[ADR-0020]] already says where that decision belongs: *as a decision, not a discovery*.

Cancelled rather than deleted — the note is the record of why this was not built.
