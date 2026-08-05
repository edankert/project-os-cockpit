---
type: "[[task]]"
id: TASK-0339
aliases: ["TASK-0339"]
title: "The supervision payload — digest, queue, approvals, and nothing else"
status: backlog
phase: "[[PHASE-028-Borrowed-Capability]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-05
source: ["[[FEAT-0079-Supervision-From-A-Phone]]"]
parent: "[[FEAT-0079-Supervision-From-A-Phone]]"
effort: M
depends: ["[[TASK-0338-The-Authenticated-Path]]"]
blocks: []
related: ["[[FEAT-0071-Since-You-Looked]]"]
tests: []
---

# The supervision payload

## Definition of Done

- A narrow responsive surface: the since-you-looked digest, the desk queue (questions, approvals, awaiting-acceptance), and the principal's actions on those items — served by the same endpoints the desktop uses, with no second vocabulary.
- Enumerated by allow-list, not by exclusion: an endpoint reachable over the paired path is one that was named, so a future endpoint is remote-invisible until someone decides otherwise.
- Reads well on a phone without a native client; the acceptance runner and the note editor are deliberately absent.
