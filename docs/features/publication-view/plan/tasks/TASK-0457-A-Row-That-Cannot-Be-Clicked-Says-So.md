---
type: "[[task]]"
id: TASK-0457
aliases: ["TASK-0457"]
title: "A row that cannot be clicked says so — the 37 checks Markdown never renders a box for"
status: done
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0104-The-Suite-Is-The-Surface]]", "[[ISS-0175-The-Nth-Checkbox-Is-Not-The-Nth-Task-Line]]"]
parent: "[[FEAT-0104-The-Suite-Is-The-Surface]]"
effort: S
depends: []
blocks: []
related: ["[[ISS-0172-A-Manual-Test-With-Subsections-Has-No-Runnable-Steps]]", "[[ISS-0184-Clicking-A-Checkbox-In-The-Acceptance-Suite-Writes-To-A-Different-Row]]"]
tests: []
---

# A row that cannot be clicked says so

## Why

37 of `../your-trainer`'s 579 acceptance rows render **no checkbox at all**: their task list opens immediately after a paragraph line and Markdown's lazy continuation absorbs it. They are in the gate's count, they are real work, and there is nothing on screen to click.

Today they are simply absent, which is [[ISS-0172]]'s lesson in a different surface: *an affordance that vanishes silently is worse than one that explains itself.*

## What

The suite's rendered view names them — how many, and where — with the one-line remedy stated, because the fix belongs to whoever owns the document and not to the cockpit:

> **37 checks cannot be ticked here.** Their list opens directly under a paragraph, so Markdown renders no checkbox. Add a blank line above each list to make them clickable.

## Deliberately not

**No auto-fix, and no writing into the suite to repair formatting.** The cockpit renders the record; reformatting somebody's document because it would be more convenient to click is a different act, and it would rewrite 37 places in a file the gate reads. Name it, count it, let the owner decide.

**No inventing a phantom checkbox** for those rows. A control that writes to a line with no visible box is exactly [[ISS-0184]] wearing a friendlier face.

## Done when

- [x] the rendered suite states how many checks have no clickable box, or says nothing when the count is zero
- [x] the message names the cause and the remedy in one sentence
- [x] the count is computed by comparing rendered boxes to parsed rows — never a second parser with its own idea of the answer
- [x] a suite where every row renders shows no message at all
- [x] asserted against `../your-trainer`: 579 rows, 542 boxes, 37 named

## Done 2026-08-17

The notice is emitted **server-side**, by the same treeprocessor that stamps the addresses, so the count is the difference between rows parsed and rows actually stamped. It cannot drift from the thing it describes, because there is no second computation to drift from.

Measured: `your-trainer`'s living suite says *"6 of 579 checks cannot be marked here"*, its v2.1.0 delta says *"36 of 300"*, and this repo's own suite shows nothing at all because every row is clickable.

**The number came down on its way here, twice, and neither drop was the document changing.** It read 70 while the matcher split names on the first colon, and 509-of-579 while addresses were emitted from two places at once. Both were mine. The remaining 6 are the document's.
