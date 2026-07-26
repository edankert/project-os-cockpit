---
type: "[[task]]"
id: TASK-0208
aliases: ["TASK-0208"]
title: "Question/revise round-trip — dispatch-queue verbs carry agent questions out and human answers/change-requests back as prompts"
status: done
phase: "[[PHASE-008-State-And-Review-Surfaces]]"
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
source: ["https://claude.ai/code/artifact/3e6b4313-66e9-4fca-b11b-97c3d7a1d1be"]
parent: "[[FEAT-0041-Review-Desk]]"
effort: ""
due: ""
depends: ["[[TASK-0206]]"]
blocks: []
related: ["[[FEAT-0025-Dispatch-Runtime]]", "[[FEAT-0024-Agent-Verbs]]", "[[TST-0013-Verb-Registry]]", "[[TST-0014-Dispatch-Ledger]]"]
tests: []
---

# Question/revise round-trip

## Definition of Done

- [x] New dispatch verbs on the FEAT-0025 runtime: the agent files an answer request (`question`) that lands in the ~review Questions group with its session provenance; the human's reply dispatches back to the originating session (or a fresh one if it ended) as a prompt, with a ledger entry for both legs.
- [x] Request-changes from TASK-0207 rides the same mechanism (`revise`): the reviewer's comment + the unticked set rows compose the prompt.
- [x] Unanswered questions persist across sidecar restarts (they are attention, not ambience — REQ-0018's no-decay rule).
- [x] TST-0013 (verb registry) and TST-0014 (dispatch ledger) are extended to cover the new verbs and the round-trip ledger shape.

## Steps

- [x] Verb registry additions + endpoint plumbing (agent-side filing; the hook/CLI path an agent uses to ask).
- [x] Queue/ledger schema for question entries + persistence.
- [x] Reply composer in ~review; dispatch-back wiring with target-session resolution (live session vs new).
- [x] Test extensions.

## Notes

The dossier frames questions as "the same mechanism in reverse" as Request-changes — build one round-trip primitive with two verbs, not two mechanisms.
