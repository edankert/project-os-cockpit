---
type: "[[issue]]"
id: ISS-0207
aliases: ["ISS-0207"]
title: "`entrypoint:` holds runnable commands and prose in the same field, so 37 tests carry a way to run them that nothing can read"
status: open
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: low
component: docs
phase: "[[PHASE-999-Future]]"
related: ["[[ADR-0034-Three-Axes-Not-One-Word]]", "[[REQ-0041-One-Answer-To-Who-Runs-This]]"]
---

# `entrypoint:` is two fields wearing one name

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
