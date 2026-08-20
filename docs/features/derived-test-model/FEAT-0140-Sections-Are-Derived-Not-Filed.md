---
type: "[[feature]]"
id: FEAT-0140
aliases: ["FEAT-0140"]
title: "Sections are derived, not filed — what a reader sees follows from `covers:` and `command:`, and `tier:` is read nowhere"
status: done
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
source: ["[[ADR-0039-Three-Sections-Derived-Not-Filed]]"]
goal: "Feature tests, Regression tests and Automated tests are computed from what a check covers and whether a machine executes it, in both front doors, with no field anybody files into."
requirements: ["[[REQ-0059-A-Section-Is-Derived-Never-Filed]]", "[[REQ-0060-A-One-Time-Check-Names-Its-Issue]]"]
tasks: ["[[TASK-0565-Derive-The-Three-Sections-And-Stop-Reading-Tier]]", "[[TASK-0566-Resolve-A-Command-And-The-Broken-Command-Section]]", "[[TASK-0567-The-Left-Pane-Six-Sections]]", "[[TASK-0568-The-Generated-Page-Follows-The-Sections]]", "[[TASK-0569-Invalidation-Narrows-To-Feature-Tests]]", "[[TASK-0570-The-Authoring-Rule-And-The-Sixty-Eight]]", "[[TASK-0571-Measure-The-Gate-Delta-Per-Repo]]", "[[TASK-0572-No-UI-String-Says-Run-Or-Walk]]"]
release: ""
acceptance: ""
design: "[[DES-0012-Tests-In-Two-Flows]]"
related: ["[[ADR-0039-Three-Sections-Derived-Not-Filed]]", "[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ISS-0208-Retire-The-Tier-Rule]]", "[[ISS-0237-An-Automated-Check-Still-Blocks-The-Manual-Walk]]", "[[ISS-0238-There-Is-Nowhere-To-Put-An-Automated-Check]]"]
tags: [feature, testing, cockpit]
---

# Sections are derived, not filed

## Goal

A check reached Tier 3 because a person moved it there, and 67 of the 68 that arrived that way now carry an `area:` naming a heading in a deleted document. Filing is the mechanism that failed. Every section this feature builds is computed, so nothing can be filed wrong and nothing has to be re-filed when it changes.

## Scope

- Three derived sections, one predicate each: `covers:` names a `FEAT-*`, `covers:` names an `ISS-*`, `command:` is non-empty.
- `Broken command` — an automated test whose command no longer resolves. **Zero members today**, so it is proved on constructed input.
- Six sections in the left pane, three on the generated page.
- `tier:` read nowhere; `GATING_TIERS` and `PERMANENT_TIERS` deleted.
- Invalidation narrows to Feature tests.

## Out of Scope

- Removing `tier:` from the 671 notes carrying it. It stops being read; the strip is later and separate.
- Repairing the 67 `area:` values.

## Acceptance

- [ ] Every section is computed; no note field selects one
- [ ] `tier:` appears in no read path, and the two tier constants are gone
- [ ] The gate delta is measured per repo before it lands — `your-trainer` 68 open to 59, this repo and `your-sudoku` unchanged
- [ ] A check whose covering test is deleted appears under `Broken command`, proved on constructed input
- [ ] No UI string contains *run* or *walk*
