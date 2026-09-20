---
type: "[[issue]]"
id: ISS-0314
aliases: ["ISS-0314"]
title: "FEAT-0139 is done while four of its acceptance criteria are still unticked, so nobody can tell what was actually verified"
status: open
phase: []
owner: unassigned
created: 2026-09-20
updated: 2026-09-20
source: ["project-os-dev ISS-0075, found while reconciling the two test runners on 2026-09-20"]
reported_by: review
question: ""
severity: medium
component: "docs"
parent: ""
related: ["[[REQ-0058-An-Automated-Test-Carries-No-Verdict]]", "[[ADR-0038-The-Suite-Is-The-Verdict]]"]
tests: []
---

# FEAT-0139 is done while four of its acceptance criteria are still unticked

## Problem

`docs/features/derived-test-model/FEAT-0139-The-Suite-Is-The-Verdict.md` is `status: done`, and four of its acceptance boxes are empty. A reader cannot tell whether the work was verified and nobody ticked, or whether it was closed without being verified.

The four:

- [ ] `run-tests.py --write` changes no note's `status:`, `last_run:` or `exit_code:`
- [ ] A note with a `command:` holding `passing` is a validator **error**
- [ ] A feature reaching `done` against an automated test is gated on the command resolving, not on a stamped status
- [ ] The 49 stamped notes carry no verdict, per repo, measured before and after

The first is now partly obsolete: as of 2026-09-20 this repo runs the template's runner, which has no `--write` at all (project-os-dev ISS-0075). The criterion needs rewording as well as evidence.

## Evidence

`grep -n "^- \[ \]" docs/features/derived-test-model/FEAT-0139-*.md` on 2026-09-20 returns four lines, under a note whose frontmatter reads `status: done`.

Found while reconciling this repo's forked `run-tests.py` with the template's. Not caused by that work, and not fixed by it.

## Why it matters

A ticked box is this project's unit of evidence. A `done` feature with empty boxes either overstates what happened or understates it, and both readings are available to whoever opens it next. The same validator that warns about a stale review verdict says nothing here.

## What a fix looks like

Walk the four criteria against today's code and tick them with the evidence, or say in the note why each cannot be ticked. Reword the `--write` one first, since the flag it names no longer exists here.
