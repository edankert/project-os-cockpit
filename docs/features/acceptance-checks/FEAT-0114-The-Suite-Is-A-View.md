---
type: "[[feature]]"
id: FEAT-0114
aliases: ["FEAT-0114"]
title: "The suite is a view — the same list, the same marks, generated from notes, and one walk layer for checks and manual tests"
status: planned
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
source: ["Edwin 2026-08-17: 'we don't need to show the acceptance tests the way they are stored on disk probably the same for normal tests'", "Edwin 2026-08-17: 'We can then present them still as the same list with the same tick options for me to go through before a release'"]
goal: "A reader walking the acceptance tests sees what they saw before — tiers, areas, rows in order, the rules preamble, the same six-mark dialog — generated from CHK notes rather than rendered from a document, and the walk layer is one component that serves checks and manual-test steps alike."
requirements: []
tasks: ["[[TASK-0464-The-Generated-List-View]]", "[[TASK-0465-One-Walk-Layer]]"]
design: ""
release: ""
depends: ["[[FEAT-0113-The-Check-Type-And-The-Migration]]"]
related: ["[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]", "[[FEAT-0104-The-Suite-Is-The-Surface]]", "[[ISS-0185-The-Mark-Control-Sits-Inside-Tasklists-Leftover-Box-And-The-Cycle-Makes-You-Walk-Past-States]]", "[[PHASE-035-Acceptance-Checks-Are-Notes]]"]
tests: []
---

# The suite is a view

## What this is

The display half of the inversion. The cockpit's model everywhere else is a projection over note frontmatter; the acceptance suite was the one surface where the stored artifact *was* the display, and that anomaly is why four rounds of marks-control work taught a rendered document to behave like a control surface. The view keeps Edwin's contract verbatim — *"present them still as the same list with the same tick options for me to go through before a release"* — tier → area → rows in `ordinal` order, rules preamble as header, filters over mark/tier/area/`covers:`/automation, and the same `askForMark` dialog, which the review confirmed is storage-independent.

What gets **retired** is the document plumbing: `mountAcceptanceMarks` and the `li[data-check]`/`data-mark` path exist only because the file was the display and lose their subject with it. The dialog survives; the plumbing does not.

## One walk layer

Edwin's aside — *"probably the same for normal tests"* — is the strongest structural argument for the move: the manual-test runner already presents a TST note as a walkable list of steps with per-step state, and a check is one step of that with a persistent verdict. The walk layer becomes one component, parameterised by what it walks, even if only the acceptance side ships in this phase.

## Acceptance criteria

- [ ] The generated view shows every migrated check in suite order, and a reader who knew the document finds nothing missing — preamble, tiers, areas, counts.
- [ ] Marking a check from the view writes the note's `mark:`/`verdict_date:`/`verdict_reason:` and repaints without moving the reader.
- [ ] `mountAcceptanceMarks` and the document-path plumbing are deleted, not stranded — the unreachable-function guard stays green.
- [ ] The view dices: by mark, tier, area, covering feature, automation — each filter derived from frontmatter, none from prose.
