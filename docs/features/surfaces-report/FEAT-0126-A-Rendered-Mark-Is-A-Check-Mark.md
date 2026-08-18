---
type: "[[feature]]"
id: FEAT-0126
aliases: ["FEAT-0126"]
title: "A rendered mark is a check mark on every surface, whatever the file stores"
status: doing
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
requirements: ["[[REQ-0045-Storage-Is-Words-Display-Is-Glyphs]]"]
tasks: ["[[TASK-0505-Route-Three-Sites-Through-Mark-Glyph]]", "[[TASK-0521-One-Verb-Again]]"]
issues: ["[[ISS-0211-The-Mark-Picker-Shows-Words-Where-The-Check-Mark-Was]]"]
related: ["[[ISS-0200-Marks-Versus-Statuses]]"]
tags: [feature]
---

# Words in the file, check marks on the screen

[[ISS-0200]] was right and stays: `mark: done` in the note is greppable, unambiguous, and survives an editor that eats a `[ ]`. It was never a decision about display, and three render sites read `mark` directly instead of through `MARK_GLYPH`.

The fix is small. What matters is the **guard**: this is the second vocabulary change in two phases to leave a live surface on a stale key, and both were found by a person looking at a screen. A test that fails when any surface emits a raw mark word is what makes the third time impossible.

## Acceptance

- [ ] The picker, the canceled-row styling and the gate tooltip all render glyphs.
- [ ] A guard fails on a raw mark word reaching any surface.
