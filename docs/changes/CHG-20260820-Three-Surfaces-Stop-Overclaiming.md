---
type: "[[change]]"
id: CHG-20260820-Three-Surfaces-Stop-Overclaiming
aliases: ["CHG-20260820-Three-Surfaces-Stop-Overclaiming"]
title: "A section head counts what it holds, an automated area reports no progress, and a gate row is a link rather than a disarmed control"
status: active
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0242-Two-Different-Things-Are-Both-Called-Automated-Tests]]", "[[ISS-0243-The-Automated-Checks-Page-Is-A-Walk-Page]]", "[[ISS-0244-The-Gate-Rows-Wear-A-Mark-That-Does-Nothing]]", "[[ISS-0241-The-Section-Head-Restates-Its-Own-Arithmetic]]", "[[CHG-20260820-The-Section-Head-Says-What-Is-Owed]]", "[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ADR-0039-Three-Sections-Derived-Not-Filed]]"]
tags: [change, cockpit, ui]
---

# Three surfaces stop overclaiming

> **Basis of every `your-trainer` figure in this note: its WORKING TREE on 2026-08-20, not `HEAD`.** Corrected after independent review, which caught the phase's own recorded lesson being repeated. The difference is not a rounding: at `HEAD` that repo has **581 items, 68 blocking, and ZERO command-bearing checks** — so there is **no automated section there at all**, and the 89 checks, their empty `evidence:`, the nine at `mark: todo` and the shared 22-character command prefix exist only in the 591-file working tree. Its Feature tests head reads `65 of 507 outstanding` at `HEAD` against `49 of 411` in the tree.
>
> **The findings do not depend on the basis; the numbers do.** A head that miscounts, a percentage over checks with no result, and a uniform glyph are defects of the code, reproducible on any corpus that has the shape. What the working tree supplies is the *scale*.

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
- `desktop/src/renderer/renderer.ts` and `desktop/src/renderer/renderer.css` — `buildCheckRow`, the area loop, `gateGroup`; `gateMark` deleted, and the `.gate-mark` rule with it (it was a pre-built hook: the reviewer re-added a glyph using that class and every guard stayed green).
- `tests/` — nine new guards, three re-anchored.

## Independent review — 2026-08-20

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `222e19e..6cc7f72`; the author's reasoning trace was not available to it. Verdict: **changes-requested**.

The three before/after rows for this repo were re-derived from `_tests_groups` and are exact. The `progress.done` → `statuses.is_completed` account is correct and both readings are genuinely guarded (mutant executed).

Two guard holes, both in the class this note says it closed:

1. **The mark guards miss a reintroduction that does not reuse the old name.** A `<span class="gate-mark is-static">` carrying `MARK_GLYPH[item.mark]`, prepended to every gate row, passes all 165 guard tests. See `ISS-0244`.
2. **`test_both_front_doors_read_head_counts` passes with the desktop suppression deleted.** See `ISS-0241`.

*"A text guard failed on its own explanation, twice in one sitting"* is accurate and the comment-line exclusion is the right repair — but it repairs *false alarms*, not *false passes*, and both holes above are the second kind.

**Shared finding — every `at HEAD` measurement in this range is a working-tree measurement.** `your-trainer` carries 591 dirty files under `docs/`. Re-measured against a `git archive HEAD` and a fresh `--shared` clone: tier1 total **496** (not 406), tier2 **85** (not 86), and **zero** command-bearing acceptance checks — so at HEAD that repo emits *no automated section at all* and the 89/9-todo/`evidence: []` population does not exist there. The gate is **68** blocking at HEAD (43 covering a `FEAT`, ten features, 40 out of scope), not 59/39/nine/36. Every figure quoted reproduces exactly against the working tree. No note in this range carries a basis caveat, while `CHG-20260820-The-Suite-Is-The-Verdict` — the note six prior review rounds spent on this exact point — carries 24.

## Independent review — second pass, 2026-08-20

**This supersedes the first-pass verdict above. Current verdict: changes-requested.** Same reviewer, same conditions — fresh context, separate session, `model:claude-opus-5` — re-run against the working tree after the first pass's findings were acted on. Every claim below was re-measured or re-executed rather than read.

One of the two first-pass holes is closed; the other is not, and the breakdown guard has a new one.

- **Closed**: the desktop `head_counts` suppression is now genuinely guarded (mutant executed, fails).
- **Open**: a mark can still be put back on every gate row — in the gutter via `li.prepend`, or after the id via a second `li.appendChild` — with all 165 guard tests green. See `ISS-0244`.
- **New**: the lossless guard still admits a row-dropping tally. See `TASK-0503`.

Residue: the `Where` list still omits `desktop/src/renderer/renderer.css`, which this change also edited.
