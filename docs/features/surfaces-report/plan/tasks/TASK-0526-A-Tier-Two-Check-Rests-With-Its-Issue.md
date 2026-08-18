---
type: "[[task]]"
id: TASK-0526
aliases: ["TASK-0526"]
title: "A Tier 2 check goes quiet when the issue it guards is closed, and wakes when the issue reopens"
status: backlog
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
parent: "[[FEAT-0131-The-Suite-Is-Refined]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# A Tier 2 check rests with its issue

Edwin: *"there should be very few tier-2 items active at any given time, so should not overwhelm."*

**This reconciles a contradiction rather than inventing a rule.** `TESTING.md` says Tier 2 is *"kept permanently"*; Edwin says few should be active. Both are right, and they are about different things — the check is **kept**, and it is not **asked about**.

That is exactly [[ADR-0028]]'s in-flight rule, which already quiets a test whose subject is not in flight. What is new is the subject: the acceptance suite has never read an `ISS-*` as one.

So there is no new mechanism to build. `covers:` names the issue, the in-flight rule reads it, and a closed issue's guard rests — **visible, counted, not owed**. It wakes if the issue reopens, which is the case a permanent-retirement rule could not express and is the reason this is resting rather than retiring.

Depends on [[TASK-0525-Relink-Tier-Two-To-Its-Issue]]: a check cannot rest with its issue if it does not name one.

## Done when

- [ ] A Tier 2 check whose `covers:` names a `fixed` issue is quiet.
- [ ] Reopening the issue wakes it, without an edit to the check.
- [ ] Nothing is deleted and nothing is hidden — the check is still listed, still counted, still walkable.
