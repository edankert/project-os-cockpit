---
type: "[[issue]]"
id: ISS-0096
aliases: ["ISS-0096"]
title: "No surface answers what a piece of work actually changed, so acceptance has the notes and the app but never the diff between them"
status: fixed
severity: medium
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-11
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

## Fixed — 2026-08-11

`GET /api/notes/shape?id=<ID>` and a **Changed** card in the note's context pane.

Measured against this repo's own work: `ISS-0135` touched **14 files — 6 notes, 4 source, 3 tests, 1 other**. That sentence did not exist anywhere before, and it is exactly the acceptance-time question — *did this touch what it claims to?*

**Why `commits_payload` could not answer it.** It walks `--name-only` and then drops every path not ending `.md`, deliberately, because its question is *what moved* and [[FEAT-0052]] measured that touches lie where transitions do not. Correct for that question and useless for this one: the two CSS files in a "CSS fix" are precisely what it discards.

**Counts, not contents**, per this note's own out-of-scope line. The card shows the kind breakdown and the last four commits with their file counts; the full diff stays a deliberate click away. The cockpit is not an editor and the persona is not reading implementations.

Bucketed by the question rather than by the tree — `tests` before `source` so a test-only change reads as one, and `assets` catching `.css`/`.png`/`.svg` wherever they live.

**Absent when git has nothing**, not `Changed · 0`: a permanent zero on every unbuilt note is the shape of thing a reader learns to stop seeing, which this surface has been taught twice ([[ISS-0068]], the review desk's empty registers).

One guard worth naming: an **empty id** returns unavailable rather than matching everything. `git log --grep=` with an empty pattern matches every commit, so the shape of "no note" would have been the shape of the whole repository — plausible-looking and completely wrong.
