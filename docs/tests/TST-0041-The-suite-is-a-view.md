---
type: "[[test]]"
id: TST-0041
aliases: ["TST-0041"]
title: "The suite is a view — the same list, the same marks, and a repaint that does not move the reader"
status: passing
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
last_verified: 2026-08-17
last_run: 2026-08-17
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
scope: feature
verifies: ["[[FEAT-0114-The-Suite-Is-A-View]]"]
automated: true
command: ".venv/bin/pytest tests/test_checks_view.py -q"
requirements: []
related: ["[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]"]
---

# The suite is a view

Automated, in `tests/test_checks_view.py`.

Edwin's contract verbatim: *"We can then present them still as the same list with the same tick options for me to go through before a release."* So the assertions are about **continuity**, and about the one property four rounds of work bought on the old surface.

## What it pins

**That every check appears, in suite order**, counted against the loader's own total rather than a literal — a guard pinning 34 becomes a guard about a number the first time somebody adds a check.

**That every filter comes from a field.** The old suite could be filtered only by whatever a section heading happened to say, and `missing_issue_refs` reported 158 of 158 because it could not read the form the headings used ([[ISS-0173]]).

**That marking holds the reader's position** — twice, once synchronously and once inside the animation frame, because layout lands a frame after the children are replaced ([[ISS-0188]]).

**That one walk layer serves both surfaces**, asserted as *no second `postJson`* in either caller rather than as a name appearing somewhere.

## Adequacy

Mutation: emptying `id`/`rel` on a row fails two assertions here; disabling the note-shape branch of `load` fails seven across this module and the tests view.
