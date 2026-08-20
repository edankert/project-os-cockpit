---
type: "[[change]]"
id: CHG-20260820-Three-Surfaces-Stop-Overclaiming
aliases: ["CHG-20260820-Three-Surfaces-Stop-Overclaiming"]
title: "A section head counts what it holds, an automated area reports no progress, and a gate row is a link rather than a disarmed control"
status: active
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0242-Two-Different-Things-Are-Both-Called-Automated-Tests]]", "[[ISS-0243-The-Automated-Checks-Page-Is-A-Walk-Page]]", "[[ISS-0244-The-Gate-Rows-Wear-A-Mark-That-Does-Nothing]]", "[[ISS-0241-The-Section-Head-Restates-Its-Own-Arithmetic]]", "[[CHG-20260820-The-Section-Head-Says-What-Is-Owed]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ADR-0039-Three-Sections-Derived-Not-Filed]]"]
tags: [change, cockpit, ui]
---

# Three surfaces stop overclaiming

## What changed

| surface | before | after |
|---|---|---|
| Tests-view section head, this repo | `Feature tests · all 27 done · 1 reconciled` | `Feature tests · 3 of 32 outstanding · 1 reconciled` |
| …and `Automated tests` here | `Automated tests` (count only in the trailing summary) | `Automated tests · 37` |
| …in `your-trainer` | `Feature tests · 45 of 406 outstanding` / `Automated tests · 89` | `49 of 411` / `Automated tests · 91` |
| Automated area heading, generated page | `71%` · `100%` · `0%` — 90% overall | the number of checks the area holds |
| Automated check row | command first, clipped to 22 characters | command under the description, full width |
| Release gate row | `☐ TST-0044  Paid, Key Configured…` | `TST-0044  Paid, Key Configured…` |

## Why

All three are one defect wearing three faces, and it is the phase's widened subject: **a surface stating something the record has nowhere to hold.**

**`all 27 done` was false on this repo's own screen.** [[ADR-0039]] requires one section per name, so non-acceptance `TST-*` rows are merged into the derived sections — and the head was computed *before* the merge. It counted 27 checks over a group holding 32 things, three of them at `ready`. Same shape in `your-trainer`: 5 rows merged into Feature tests and 2 into Automated tests, none counted.

**`90% complete` was computed from `mark:` over 89 checks with `evidence: []` and an empty `verdict_date`** — no recorded result for any of them, nine at `mark: todo`. `checkPercent` ran regardless of whether a person walks the section.

**The command cell distinguished nothing.** `max-width: 22ch` with an ellipsis, and all 89 of `your-trainer`'s commands begin `cd android && ./gradlew` — one distinct value across the page, with the identifying tail exactly what the ellipsis ate.

**The gate mark was a control that had already been disarmed.** [[ADR-0035]] removed the click after [[ISS-0210]] found sixty live marks on the page whose purpose is to report a release is *not* ready; the glyph stayed, identical on every row of the four unsettled lists because those rows are unsettled by construction.

## Two things worth carrying forward

**A wrong predicate shipped inside the fix and was caught by constructing the case.** Outstanding was first read from `progress.done`, which derives from the row's `owed` flag — *does this need a person right now* ([[ADR-0027]]) — which is `False` for a test at `ready`. The head still printed `all 32 done`. It now asks `statuses.is_completed`. Both readings are guarded, so the swap fails a test.

**A text guard failed on its own explanation, twice in one sitting.** `test_one_walk_layer_and_now_exactly_one_surface` stripped one known comment by exact text before searching for `markGateRow`; a second comment naming it broke the guard. The re-anchored mark guard then did the same thing to itself. Both now match live code with comment lines excluded — a guard that fails on the comment explaining it is a guard somebody weakens to make it pass.

## Superseded, not regressed

`test_a_gate_row_wears_the_documents_control_and_no_buttons` asserted the mark was the row's first child. That came from *"if you want you can have the checkbox on the left"* — permissive — and is superseded by *"just show them as a list of tst links like the features below."* Its [[ADR-0035]] half (no buttons, no second vocabulary) is untouched.

Also deleted: the row click handler's `if (ev.target.closest('.acc-mark')) return;`. With no mark on the row it could never fire — the class of defect this phase has now shipped three times.

## Where

- `src/project_os_cockpit/cockpit.py` — `_section_head_label`, the merge rebuild, the standalone section head.
- `desktop/src/renderer/renderer.ts` / `.css` — `buildCheckRow`, the area loop, `gateGroup`; `gateMark` deleted.
- `tests/` — nine new guards, three re-anchored.
