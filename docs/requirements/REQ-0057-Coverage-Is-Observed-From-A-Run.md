---
type: "[[requirement]]"
id: REQ-0057
aliases: ["REQ-0057"]
title: "Coverage is observed from a run and never declared on a note — a deleted covering test puts its check back on the run list"
status: draft
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
priority: medium
scope: "automation coverage"
implements: "[[FEAT-0138-Coverage-Is-Observed-Not-Declared]]"
acceptance:
  - "[ ] No note declares that a machine covers it."
  - "[ ] A test declares the check it covers, in a form one grep finds."
  - "[ ] A CI run appends observed-coverage entries to the working ledger for its platform."
  - "[ ] Deleting or disabling a covering test puts its check back on the run list within one CI cycle, proved."
  - "[ ] The 203 automation annotations are extracted and recorded before `automation:` is removed."
covers: []
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ISS-0198-Automation-And-Covered-By-Are-Empty-On-All-669-Checks]]", "[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]", "[[DES-0012-Tests-In-Two-Flows]]"]
tags: [requirement]
---

# Observed, not declared

## Statement

A claim that a machine covers an acceptance check **shall** be produced by a run that observed it, and **shall not** be asserted in any note's frontmatter.

## Why the inversion, and why it is available only now

A standing `covered_by:` rots **silently**: the covering test is renamed, deleted or `@Ignore`d, the note keeps asserting coverage, and the check leaves the run list permanently with no signal. A stale verdict is better than that, because a stale verdict still asks.

[[ISS-0198]] measured the standing claim and closed with the field deliberately empty on all 669 checks: the 203 annotated bodies name **54 JVM classes and no `TST-*` id**, and the guard correctly refuses a link to something no runner can execute. **That population is precisely the one observed coverage handles** — each class declares its check in its own source, the run emits, and nothing invents a note for an unrunnable command.

The inversion is only available because automation moved into the ledger. It could not have been proposed against a note field.

## The limit, carried from the ADR

[[ISS-0209]]: the acceptance gate runs in **no repo that holds a check**. Until that is resolved the emitter runs here and nowhere the data lives, and criterion 4 is proved in this repo only. That is a stated limit, not a satisfied criterion.

## Acceptance criteria

- [ ] Nothing declares coverage in a note.
- [ ] The test declares the check, greppably.
- [ ] CI emits into the working ledger.
- [ ] A deleted covering test re-arms its check, proved.
- [ ] The 203 annotations survive the removal.
