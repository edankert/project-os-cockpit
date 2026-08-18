---
type: "[[task]]"
id: TASK-0521
aliases: ["TASK-0521"]
title: "Retire "walk" from the product and the prose; one verb covers both populations"
status: backlog
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
parent: "[[FEAT-0126-A-Rendered-Mark-Is-A-Check-Mark]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# Retire "walk" from the product and the prose; one verb covers both populations

DES-0012 D5. TASK-0495 changed `Run` → `Walk` because a person walks a procedure and a machine runs a command. D2 (`command:` only) removes that premise, so one verb serves both.

**Invert the guard**, do not delete it: `test_one_verb_names_the_human_act_across_every_owed_kind` currently asserts `Walk` and forbids `Run`.
