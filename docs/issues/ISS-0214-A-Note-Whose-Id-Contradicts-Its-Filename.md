---
type: "[[issue]]"
id: ISS-0214
aliases: ["ISS-0214"]
title: "Nothing checks that a note's `id:` matches its filename — 23 task notes carried `id: TASK` and every gate passed"
status: open
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: medium
component: tooling
phase: "[[PHASE-999-Future]]"
related: ["[[ADR-0009]]", "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"]
---

# `id: TASK` on 23 notes, and everything reported green

Found 2026-08-18 while writing [[PHASE-037]]'s tasks. A shell helper derived the id with `${1%%-*}`, which strips from the **first** hyphen — so `TASK-0525-Relink-Tier-Two-To-Its-Issue` yielded `TASK`.

**23 notes were written with `id: TASK` and `aliases: ["TASK"]`.** `validate-docs.sh` reported OK, `sync-snapshot.py` was content, the pre-commit hook let every one of them through, and they were committed across four commits.

## Why nothing saw it

Identity is taken from the **filename** almost everywhere — the indexer, the counters, `PARENT-BACKLINK`, `SNAPSHOT-MEMBERSHIP`. So the frontmatter `id:` is, in practice, decorative: it is read by surfaces and by wikilink resolution, and never checked against the path it lives at.

That is a reasonable design — the filename is unambiguous and cannot drift silently — but it makes the `id:` field a place where a wrong value survives every gate.

## Why it matters

Two `id: TASK` notes in one corpus are **two notes claiming one identity**. Wikilink resolution, `by_id` lookups and any surface reading frontmatter can serve one where the other was meant. It did not bite here only because nothing linked to them by id before they were fixed.

It is also the second identity-collision class this project has met: [[ISS-0142]] was a note carrying an id no route reached.

## Done when

- [ ] A note whose frontmatter `id:` disagrees with the `<TYPE>-<NNNN>` prefix of its filename is a validator error.
- [ ] The rule is upstream, since every repo's notes are written the same way.
- [ ] The check names both values, so the fix is obvious from the message.
