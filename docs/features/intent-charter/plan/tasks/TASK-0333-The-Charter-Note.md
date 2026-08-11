---
type: "[[task]]"
id: TASK-0333
aliases: ["TASK-0333"]
title: "The charter note — goals, non-goals and taste constraints, drafted from the record, approved by the principal"
status: backlog
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["[[FEAT-0077-The-Intent-Charter]]"]
parent: "[[FEAT-0077-The-Intent-Charter]]"
effort: M
depends: ["[[TASK-0332-DES-0003-Revised]]"]
blocks: []
related: []
tests: []
---

# The charter note

## Definition of Done

- An INTENT note per repo: what this project is for, what it must never become, and the taste rules its record has already paid for — first draft dispatched from the corpus's ADRs, phase close-outs and design-system notes, never invented.
- Approved through the actuator row; only an approved charter can be named by a delegation's `acceptance:` line.
- Amendment re-enters approval, and the charter's sha is stamped on every judgment made under it — the delegation-authority pattern, applied to intent.

## Partially done — 2026-08-11

**The gate is built; the charter's content is not written, and deliberately not by me.**

`charter.py` loads and gates `INTENT.md`: only an `approved` charter is usable, an incomplete one is refused with the missing section named, and its sha pins every judgment made under it. Amendment re-enters approval by construction — any edit changes the sha, so a judgment cannot silently inherit a standard that moved.

**What is not done is the charter itself**, and the DoD says why it cannot be: *"first draft dispatched from the corpus's ADRs, phase close-outs and design-system notes, **never invented**"* ([[FEAT-0051]]'s rule applied to intent). A charter I wrote from my own reading would be the tool authoring the standard it is judged against — which is the exact thing the approval gate exists to prevent, arrived at one step earlier.

It also needs approving through the actuator row, which is [[REQ-0026]]'s human-owned territory.

So this task is **the mechanism, done; the content, dispatched**. `docs/__templates__/` deliberately ships no INTENT template, because a template with placeholder intent is worse than none: it would read as a charter and mean nothing.
