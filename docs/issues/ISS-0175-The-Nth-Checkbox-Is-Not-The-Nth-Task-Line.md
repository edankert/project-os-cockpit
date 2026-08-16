---
type: "[[issue]]"
id: ISS-0175
aliases: ["ISS-0175"]
title: "The Nth rendered checkbox is not the Nth task line, so 285 of 542 rows in your-trainer's suite carry another row's `data-raw` — and any control keyed on checkbox position writes to the wrong check"
status: "open"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
source: ["Found 2026-08-16 while building FEAT-0104's check map — the map's own counts did not agree with the render"]
severity: high
component: cockpit-server
parent: ""
related: ["[[ISS-0137]]", "[[FEAT-0104-The-Suite-Is-The-Surface]]", "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"]
tests: []
---

# The Nth rendered checkbox is not the Nth task line

## Problem

`renderer._annotate_checkbox_source` carries each checkbox's raw source text onto its rendered `<input>` as `data-raw`, and states the assumption in its own docstring:

> *"The correspondence is ordinal — the Nth rendered checkbox is the Nth task-list line in the source — the same walk `server._toggle_task_at` has always relied on."*

**It does not hold.** Measured on `your-trainer/docs/tests/ACCEPTANCE_TESTS.md`:

- `acceptance.parse` finds **579** checks
- `note_writes._criterion_text` accepts the same **579** source lines
- the rendered HTML contains **542** `input[type=checkbox]`

37 task lines never become checkboxes. The annotator zips the two lists positionally, so from the first divergence — rendered box **#257**, source line 413 — every subsequent box is labelled with a *different row's* text. **285 of 542 rows carry a `data-raw` that is not their own.**

## Why it matters

`data-raw` exists because [[ISS-0137]] found that recovering a criterion from `textContent` produces a string the source does not contain, and `note_writes.resolve_criterion` matches the source **exactly and deliberately** — ambiguity there is a refusal rather than a guess. That refusal is the safety property, and it is now being fed a value that is confidently wrong rather than absent.

Two consequences, one live and one blocked:

- **Live:** any long document where the counts diverge mislabels its boxes. The tick prompt would resolve against another criterion's text — refused if lucky, wrong if not.
- **Blocked:** [[FEAT-0104]]'s check map cannot be keyed on checkbox position, which is the whole mechanism the agreed design needs. `check_map` therefore ships **addresses only**, with no DOM index, and the interaction is unbuilt.

## Not yet established

**Which 37 lines, and why.** They are not indented (0 of 579 carry leading whitespace), so the obvious cause — nested task lists — is refuted. Fenced blocks are skipped by both readers. The cause is unknown and must be found before a fix, because a repair aimed at the wrong cause would restore the assumption without restoring the correspondence.

## Expected

1. The cause of the 37 is identified, not guessed.
2. A box carries its **own** source line, or carries none. A wrong `data-raw` is worse than an absent one — absence degrades to the pre-ISS-0137 behaviour, which merely failed to resolve.
3. Whatever mechanism results is keyed on something the renderer emits **during** rendering, not reconstructed afterwards by counting.
4. A guard asserts the counts agree on this repo's own suite, and fails loudly when they do not.
