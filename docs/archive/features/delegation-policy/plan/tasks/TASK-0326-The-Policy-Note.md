---
type: "[[task]]"
id: TASK-0326
aliases: ["TASK-0326"]
title: "DELEGATION.md — what is delegated, what escalates, approved through the gate it configures"
status: done
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0075-The-Delegation-Policy]]"]
parent: "[[FEAT-0075-The-Delegation-Policy]]"
effort: M
depends: []
blocks: ["[[TASK-0327-Role-Checks-Consult-Policy]]"]
related: []
tests: []
---

# The policy note

## Definition of Done

- Format per DES-0009: `delegate:` entries (judgment, to whom, threshold) and `escalate:` entries (kind, timeout, default); a template ships with everything commented out — the empty policy delegates nothing.
- The note is approved through the actuator row (requirement-style approve), and only an **approved** policy is consulted; a draft policy is no policy.
- Amending it re-enters draft and re-approval — authority does not drift by edit.

## Done — 2026-08-11

`src/project_os_cockpit/delegation.py` plus `docs/__templates__/delegation.md`.

**The property everything else rests on: no policy → no delegation → no worker.** A missing `DELEGATION.md` must not read as "delegate everything" or even "delegate the safe things" — it reads as *nobody has said yes to anything*, because **a default that grants authority is authority nobody granted**. Every path in `permits()` returns False unless something explicitly says yes; there is no branch that grants on absence.

**A draft policy is no policy.** The note passes through the gate it configures — only `status: approved` is consulted, and an unparseable status is treated as unapproved, because guessing in the permissive direction is the one mistake this module cannot afford. An agent that could write its own policy and have it obeyed would be delegating to itself.

The template ships everything commented out, and says why in its own words: *"there is no line to delete to withhold authority, because withholding is the state you start in."* It also lists what is **never** delegated — accepting a design or requirement, answering a permission prompt, rewinding a checkpoint, pushing — recorded rather than inferred from what is absent.

### The bug the template test caught on its first run

`test_the_shipped_template_delegates_nothing` failed immediately. The parser skipped **code fences** but not **HTML comments**, and the template ships its examples inside `<!-- -->` — so the shipped default would have delegated `everything → any-delegate` **on install**, through the one file every repo copies.

That is precisely the permissive-default failure this module exists to prevent, arriving by the least visible route. Fixed, and guarded twice: once against the real template file, once against a synthetic comment.
