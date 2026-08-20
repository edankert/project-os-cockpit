---
type: "[[change]]"
id: CHG-20260820-The-Section-Head-Says-What-Is-Owed
aliases: ["CHG-20260820-The-Section-Head-Says-What-Is-Owed"]
title: "A tests-view section head states what is outstanding, once, and claims no CI execution"
status: merged
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0241-The-Section-Head-Restates-Its-Own-Arithmetic]]", "[[ISS-0237-An-Automated-Check-Still-Blocks-The-Manual-Walk]]", "[[ISS-0209-The-Acceptance-Gate-Reaches-No-Fleet-Repo]]", "[[ADR-0039-Three-Sections-Derived-Not-Filed]]"]
tags: [change, cockpit, ui]
---

# The section head says what is owed

> **Basis of every `your-trainer` figure in this note: its WORKING TREE on 2026-08-20, not `HEAD`.** Corrected after independent review, which caught the phase's own recorded lesson being repeated. The difference is not a rounding: at `HEAD` that repo has **581 items, 68 blocking, and ZERO command-bearing checks** — so there is **no automated section there at all**, and the 89 checks, their empty `evidence:`, the nine at `mark: todo` and the shared 22-character command prefix exist only in the 591-file working tree. Its Feature tests head reads `65 of 507 outstanding` at `HEAD` against `49 of 411` in the tree.
>
> **The findings do not depend on the basis; the numbers do.** A head that miscounts, a percentage over checks with no result, and a uniform glyph are defects of the code, reproducible on any corpus that has the shape. What the working tree supplies is the *scale*.

## What changed

The head of a tests-view section in the left pane. Before and after, in `your-trainer`'s **working tree** (not `HEAD` — see the basis note above):

| before | after |
|---|---|
| `Feature tests · 361/406 completed · 45 todo`  ⟨`50 · 1 done`⟩ | `Feature tests · 45 of 406 outstanding` |
| `Regression tests · 72/86 completed · 14 todo`  ⟨`28`⟩ | `Regression tests · 14 of 86 outstanding` |
| `Automated tests · 89 executed by CI`  ⟨`17 · 2 done`⟩ | `Automated tests · 89` |

and on this repo, where a section is finished:

| before | after |
|---|---|
| `Feature tests · 26/27 completed · 1 reconciled`  ⟨`19`⟩ | `Feature tests · all 27 done · 1 reconciled` |

⟨angle brackets⟩ are the trailing summary the front ends appended, now suppressed on these heads.

**`re-check`, `stale` and `reconciled` all survive.** Each is a different thing that happened — an explicit act, a tick standing over overtaken evidence, a decision the release note carries — not one thing counted three ways.

## Why

Three defects in one line, all of them [[PHASE-037]]'s shape: a surface answering a question its reader did not ask.

1. **`45 todo` was `406 − 361`.** `unchecked` is `total − checked − reconciled` by construction, so no input could ever make the two halves disagree. A number that cannot vary against its neighbour *is* its neighbour, printed again.
2. **The trailing number counted a different population.** The label counts **checks**; `groupHeadSummary` counts the group's nav **rows**, which for an acceptance section are area surfaces. `361/406` and `50 · 1 done` sat adjacent, eight times apart, both readable as *how many tests are in here*.
3. **`executed by CI` was derived from `command:` and from nothing else.** The cockpit observes no CI run anywhere.

On the third, measured in `your-trainer`'s **working tree** (not `HEAD` — see the basis note above) on 2026-08-20 — all 89 of the checks that phrase described carry `evidence: []` and an empty `verdict_date`; **nine are `mark: todo`**; and no workflow executes them as checks (`android-tests.yml` runs the underlying gradle tests on `android/**` changes, and nothing maps a result back onto a note, which is why all 89 sit at `status: active`).

So it is [[ISS-0237]] with the sign reversed. That issue found automated checks inside a **blocking** count — the surface claiming a person owed work no person does. The fix moved them to `N executed by CI`, which removed the false obligation and left a **false assurance** standing where it had been: 89 reading as covered-and-green over a record holding no result at all.

## Decisions

- **`outstanding`, not `todo`** — Edwin, 2026-08-20. It is also the word that survives [[ADR-0039]]'s vocabulary: `todo` is a mark, and the head is not reporting a mark.
- **The CI claim is dropped rather than corrected.** `89 automated · no recorded result` was offered and declined: the head is not where the evidence question gets opened, and a second number to keep true is a second number that can go stale. [[ISS-0209]] holds the substantive gap.
- **`Automated tests · 89`, not `· 89 automated`** — the section is already named *Automated tests*, and the word twice is what [[ISS-0089]] and [[ISS-0090]] took off the group heads.
- **A flag from the server, not an inference in the clients.** `head_counts: true` is emitted only by `_acceptance_tier_groups`. For a phase, feature or task group the trailing count is the **only** count its head has; sniffing the rule from the label text would take it away from them the first time one of those labels contained a digit.
- **Scoped to the head.** The generated checks page keeps its `26/27` fraction — that page is where the walk happens, and it was not what this was about. Its `executed by CI` phrase went, because that is a truth claim rather than a layout preference and it should not survive in one front door and not the other.

## Where

- `src/project_os_cockpit/cockpit.py` — `_acceptance_tier_groups`: the label, and the `head_counts` flag.
- `src/project_os_cockpit/static/cockpit.js` — browser nav, suppression.
- `desktop/src/renderer/renderer.ts` and `renderer.css` — desktop nav suppression, the `NavGroupData` field, the checks-page heading, and the row-level command fallback (`'executed by CI'` → `'automated'`, in a branch that can only fire on inconsistent data).
- `tests/test_tests_view.py` — five guards, each proved on a mutant.

## Not changed

`tools/instructions/TESTING.md`, `docs/__templates__/acceptance-tests.md` and [[ADR-0039]] still contain the phrase *executed by CI*. The first two are template-owned — editing them here reports as divergence at the next sync — and the third is a decision record, which describes what was decided at the time and is not rewritten to match a later UI. The claim was only ever wrong as a **statement on a surface** about specific checks; as a description of what the automated class *is for*, it is the intent those documents record.

## Independent review — 2026-08-20

Fresh-context pass, separate session, `model:claude-opus-5`. Started from the notes and the diff `222e19e..6cc7f72`; the author's reasoning trace was not available to it. Verdict: **changes-requested**.

Five of five server-side guards were re-derived and each fires on its mutant (restore the `todo` half; restore `executed by CI`; drop `head_counts`; drop the `_head` pop; drop the `cockpit.js` suppression). The `unchecked = total − checked − reconciled` argument is correct by construction, and the `head_counts`-flag-not-label-sniffing decision is sound and asserted in both directions.

**One guard cannot detect what it names** — `test_both_front_doors_read_head_counts` passes with the desktop suppression deleted, because `head_counts` also appears in the `NavGroupData` interface. Only the build-hash test fires, and it fires on any edit and clears on `npm run build`. See `ISS-0241`.

**The `Where` list is incomplete in one direction that matters**: it does not name `desktop/src/renderer/renderer.css`, which this range also changed.

**Shared finding — every `at HEAD` measurement in this range is a working-tree measurement.** `your-trainer` carries 591 dirty files under `docs/`. Re-measured against a `git archive HEAD` and a fresh `--shared` clone: tier1 total **496** (not 406), tier2 **85** (not 86), and **zero** command-bearing acceptance checks — so at HEAD that repo emits *no automated section at all* and the 89/9-todo/`evidence: []` population does not exist there. The gate is **68** blocking at HEAD (43 covering a `FEAT`, ten features, 40 out of scope), not 59/39/nine/36. Every figure quoted reproduces exactly against the working tree. No note in this range carries a basis caveat, while `CHG-20260820-The-Suite-Is-The-Verdict` — the note six prior review rounds spent on this exact point — carries 24.

## Independent review — second pass, 2026-08-20

**This supersedes the first-pass verdict above. Current verdict: approved.** Same reviewer, same conditions — fresh context, separate session, `model:claude-opus-5` — re-run against the working tree after the first pass's findings were acted on. Every claim below was re-measured or re-executed rather than read.

Both first-pass findings are closed and re-verified: the desktop `head_counts` mutant now fails its named guard, and the basis blockquote's figures are exact.

Residues: the `Where` list still omits `desktop/src/renderer/renderer.css`, and lines 26 and 52 still say *"at HEAD"* where the blockquote above says the opposite.
