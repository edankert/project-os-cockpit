---
type: "[[issue]]"
id: ISS-0207
aliases: ["ISS-0207"]
title: "Tests that name a runnable command in `entrypoint:` still show as waiting for a person to run them"
status: open
owner: user:edwin
created: 2026-08-18
updated: "2026-09-19"
reported_by: review
severity: low
component: docs
phase: "[[PHASE-999-Future]]"
related: ["[[ADR-0034-Three-Axes-Not-One-Word]]", "[[REQ-0041-One-Answer-To-Who-Runs-This]]"]
---

# Tests with a runnable `entrypoint:` still show as manual

A test whose `entrypoint:` holds a real command, such as a pytest path, but has no `command:` shows in the cockpit as a manual test waiting for a person. The template never says what `entrypoint:` means, so notes use it both for commands and for prose.

Found by the second independent verification of [[PHASE-036-One-Human-Walk]], via a badge that rose in a repo nobody was looking at.

SCHEMAS.md defines it as *"repo-relative command/script to run (or blank for purely manual tests)"* — and the corpus uses it both ways. **37 tests carry an `entrypoint:` and no `command:`**, and the values split:

- genuinely runnable — `obsidian-supernote-sync` TST-0004's `pytest tests/test_markdown_to_pdf.py -v`, `your-sudoku` TST-0011/0013's Kotlin test paths;
- prose — `project-os-cockpit` TST-0026's *"the discovered fleet under ~/Dev/repos"*, TST-0030's *"Publication → Release gate, against a t…"*.

## Why `_is_manual_test` does not read it

[[ADR-0034-Three-Axes-Not-One-Word]] reduced who-runs-this to one field precisely because two fields answering one question drift — `kind:` and `command:` disagreed about 8 of 788 notes. Adding `entrypoint:` as a third would reintroduce that, on a field where **half the values cannot be executed by anything**.

So the classifier is correct and the *notes* are wrong: a test whose entrypoint is a real command is claiming to be machine-runnable in a field nothing runs.

## What it costs today

`obsidian-supernote-sync`'s TST-0004 is `ready` and now reads as owed to a person. That is the honest answer — nothing can run it as written — and it is a badge that rose because a note says one thing in a field and another in its schema.

## Done when

- [ ] Each of the 37 is triaged: a runnable value moves to `command:`, a prose value stays and `entrypoint:` is documented as *where to start reading*, not *what to run*.
- [ ] SCHEMAS.md stops defining one field as both.

## Checked against the code, 2026-09-19: still true, kept

**What a user notices:** Tests that a machine could run appear in the owed-to-a-person counts, and nothing runs them.

Evidence: the template's test note has `entrypoint: ""` with no comment (project-os/docs/__templates__/test.md:12), beside a documented `command:` (line 13); no file in project-os/tools/instructions/ defines it beyond a field list in SNAPSHOT.md:74. Notes with a non-empty `entrypoint:` and no non-empty `command:`, counted per repo on 2026-09-19: your-sudoku 11, obsidian-supernote-sync 5, project-os-cockpit 5, project-os-deck 1, your-trainer 1 (23, down from 37). Values still split: your-sudoku's `android/app/src/test/kotlin/com/yoursudoku/domain/model/` is a runnable path; project-os-cockpit TST-0026's `the discovered fleet under ~/Dev/repos` is prose. This is **bigger**: a template wording change plus triage of 23 notes in five repos.

**Belongs to:** no feature; the template wording belongs in project-os. **Next:** define `entrypoint:` in the template as where to start reading, then move each runnable value to `command:` repo by repo.

Checked as part of project-os-dev FEAT-0036 (TASK-0141).
