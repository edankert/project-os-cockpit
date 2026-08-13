---
type: "[[task]]"
id: TASK-0416
aliases: ["TASK-0416"]
title: "Generalise the note-less obligation — one walk that yields a count and its rows, with standing documents as its first caller"
status: backlog
owner: unassigned
created: 2026-08-13
updated: 2026-08-13
phase: "[[PHASE-030-Obligations-Go-Home]]"
source: ["[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]"]
parent: "[[FEAT-0100-Unpushed-Work-Needs-A-Person]]"
effort: M
depends: []
blocks: ["[[TASK-0417-Publication-Enters-The-Registry]]"]
related: ["[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[FEAT-0091]]"]
tests: []
---

# Generalise the note-less obligation

The registry enumerates by note type, which is its best idea and stays. But one obligation already has no note behind it — the standing document, whose subject is a manifest entry — and it is carried by **two special cases**: an addition inside `counts_by_kind()`, and a second inside `_needs_you_group()` because `owed_items()` yields no rows for it.

That seam has already failed: *"Intent's group came out 3 against a badge of 5."* Publication would be the second note-less obligation, and adding it the same way makes the third and fourth places for a number to disagree with itself.

## Definition of Done

- [ ] A note-less obligation is declared **once**, and yields its count and its rows from **one walk** — the same property the note-typed path already has, and the reason `counts_by_kind` is asserted against `owed_items` rather than computed separately.
- [ ] The standing-document obligation is expressed through it, and its two bolt-ons are gone. This is a refactor with an existing subject before it is a foundation for a new one — if it does not simplify standing, it is the wrong shape.
- [ ] The completeness test gains a sibling: **every declared note-less source is enumerated**, so a source that ships without rows fails a test rather than producing a badge nobody can explain.
- [ ] `badges_payload`'s total still equals the sum of what the badges show, with note-less sources included.
- [ ] Vocabulary comes from the server: each source declares its noun (singular/plural) and verb, per [[TASK-0357]]'s rule that the renderer picks a string and never owns a plural rule.

## Steps

- [ ] Define the source protocol: given the index and the workspace, return `{kind, view, verb, noun, rows}` where the count is `len(rows)`.
- [ ] Port the standing document to it; delete both special cases.
- [ ] Extend the completeness test.
- [ ] Leave publication's own registration to [[TASK-0417]] — this task must be provable with one caller.
