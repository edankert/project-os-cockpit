---
type: "[[issue]]"
id: ISS-0096
aliases: ["ISS-0096"]
title: "No surface answers what a piece of work actually changed, so acceptance has the notes and the app but never the diff between them"
status: open
severity: medium
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-05
source: ["Comparison against t3.codes, 2026-08-05: ReviewService offers diff preview and file contents as a first-class surface"]
component: desktop-renderer
related: ["[[FEAT-0063-The-Acceptance-Runner]]", "[[FEAT-0066-Visual-Evidence]]", "[[FEAT-0052-History-Timeline]]"]
fixed_by: []
tests: []
---

# No surface says what changed

## What

History shows *status transitions grouped by commit* — deliberately, and correctly, since [[FEAT-0052]] measured that touches lie where transitions do not. What no surface shows is the **shape of a change**: this task touched 6 files, 4 of them notes, 2 of them CSS.

T3 Code has `ReviewService` — diff preview and file contents behind a typed contract, rendered per thread.

## Why this matters for the docs-first reader

This is not "read the code". For a human who governs through documentation, the useful question at acceptance time is *did this touch what it claims to touch* — a task promising a CSS fix that rewrote the validator is visible in one line of shape, and invisible in prose.

[[FEAT-0063]]'s runner asks the human to judge criteria with the notes and the running app in hand. The missing third input is what actually moved. [[FEAT-0066]] adds pictures of the result; this adds the extent of the cause.

## Fix

A scoped change view keyed to a note: the files a task's commits touched, grouped by kind (notes / source / tests / assets), counts not contents by default, with the full diff one deliberate click away. Reachable from the note and offered inside an acceptance run.

## Out of scope

A general diff viewer or code review surface — the cockpit is not an editor, and the persona is not reading implementations. Shape first; contents only on request.

## Evidence it is fixed

Opening a closed task answers "what did this touch" without leaving the cockpit, and an acceptance run offers the same view beside the criteria.
