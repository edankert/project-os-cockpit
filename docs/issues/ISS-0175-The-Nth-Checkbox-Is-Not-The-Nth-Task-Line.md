---
type: "[[issue]]"
id: ISS-0175
aliases: ["ISS-0175"]
title: "The Nth rendered checkbox is not the Nth task line, so 285 of 542 rows in your-trainer's suite carry another row's `data-raw` — and any control keyed on checkbox position writes to the wrong check"
status: "fixed"
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

## Cause, established 2026-08-16

**Markdown lazy continuation — not a parser bug at all.**

A task list that opens immediately after a paragraph line, with no blank line between, is absorbed into the paragraph and renders **zero** checkboxes. `_criterion_text` is line-based and counts every one. Demonstrated:

```
## H                              ## H

See the note.                     See the note.
                                  - [x] **A:** one.     <- swallowed
- [x] **A:** one.
        1 checkbox                        0 checkboxes
```

Found by binary-searching rendered-vs-source counts over growing prefixes of the suite: the first divergence is at **line 413**, immediately after `line 412`, a prose line following the `## 1.17` heading with no blank line before the list. The pattern accounts for the whole gap.

The lines were not indented, which is why the nested-list hypothesis was refuted — the mechanism has nothing to do with indentation.

## Fixed 2026-08-16

**The counts must agree, or nothing is labelled.** `_annotate_checkbox_source` compares rendered boxes against source task lines and, on a mismatch, attaches no `data-raw` at all and logs why.

That is the principle the function already stated for its over-count branch — *"leaving the attribute off degrades to the old behaviour rather than mislabelling a box with somebody else's text"* — applied to the whole document, because a count mismatch means the alignment is **unknowable**, not merely short.

Measured after: `your-trainer`'s suite goes from **285 of 542 rows carrying another row's text** to **0 rows carrying any**. The tick prompt now fails to resolve rather than resolving to the wrong criterion, which is the direction `resolve_criterion` was designed to fail in.

Three guards in `tests/test_release_record.py`: the cause itself, the refusal, and — deliberately — that a well-formed document still gets its labels, so the refusal is narrow.

## What this does NOT unblock

[[FEAT-0104]]'s cycling mark still cannot be keyed on checkbox position **in a document that has the mismatch**, because those checks genuinely have no checkbox to click. The remedy there is a blank line in the source, which belongs to the repo that owns the suite — `your-trainer`, not this one. The dangerous half (writing to the wrong check) is closed; the blocked half is a source-formatting question.
