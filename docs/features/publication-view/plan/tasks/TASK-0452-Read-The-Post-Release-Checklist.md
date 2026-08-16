---
type: "[[task]]"
id: TASK-0452
aliases: ["TASK-0452"]
title: "Read the post-release checklist every release note already carries — 37 unticked boxes across eight releases"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0110-Still-Owed-By-A-Shipped-Release]]", "Measured against ../your-trainer on 2026-08-16"]
parent: "[[FEAT-0110-Still-Owed-By-A-Shipped-Release]]"
effort: S
depends: []
blocks: ["[[TASK-0453-Three-Verdicts-And-An-Offered-Tick]]"]
related: []
tests: []
---

# Read the post-release checklist

## Why

Eight of `../your-trainer`'s twelve release notes carry a `## Post-Release Actions` section of real `- [ ]` boxes, and **37 are unticked**. The release page reads `## Known issues` from the same note already and walks straight past the only section that contains outstanding work.

## What

The same heading-and-checkbox read `_known_issues` performs, against a different heading, returning the **unticked** boxes with their text and their position in the file.

## How

- Match the heading with the tolerance the corpus needs: `Post-Release Actions`, `Post release actions`, `Follow-up`, case-insensitively.
- Section ends at a heading **at or above** its own level — the [[ISS-0172]] rule, which this repo has already had to learn once.
- Return the position so [[TASK-0453]] can offer a write against it.
- A note with no such section returns nothing and renders nothing. Four of the twelve.

## The trap this repo has already hit

**Markdown lazy continuation.** A task list opening immediately after a paragraph line with no blank line renders **zero** checkboxes while a line-based reader counts every one. That is [[ISS-0175]], and it left 285 of 542 rows carrying another row's text. Whatever reads these boxes must agree with what is rendered, or refuse — the mismatch check `_annotate_checkbox_source` now performs is the pattern.

## Done when

- [x] unticked boxes returned with text and position, from all four heading spellings
- [x] a subsection inside the checklist is part of it, not a terminator
- [x] a note with no section renders nothing — no empty heading
- [x] a lazy-continuation list is either read correctly or refused, never silently mis-addressed
- [x] measured against `../your-trainer`: 8 notes, 37 unticked, and both asserted
