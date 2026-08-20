---
type: "[[feature]]"
id: FEAT-0141
aliases: ["FEAT-0141"]
title: "The contract says it upstream — `TESTING.md` and `STATUSES.md` carry the rules, and the fleet is synced"
status: done
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
source: ["Edwin 2026-08-19: 'make sure this is covered eveywhere (project-os) to this extent'"]
goal: "The tier vocabulary, the invalidation rule and the no-verdict rule are stated once in the template-owned instructions and reach every repo by sync."
requirements: []
tasks: ["[[TASK-0573-Testing-Md-Five-Edits-Upstream]]", "[[TASK-0574-Statuses-Md-Line-One-Four-Four]]", "[[TASK-0575-Sync-The-Fleet]]"]
release: ""
acceptance: ""
design: ""
related: ["[[ADR-0038-The-Suite-Is-The-Verdict]]", "[[ADR-0039-Three-Sections-Derived-Not-Filed]]", "[[ISS-0238-There-Is-Nowhere-To-Put-An-Automated-Check]]"]
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
tags: [feature, documentation]
---

# The contract says it upstream

## Goal

`TESTING.md` is template-owned and canonical at `~/Dev/repos/project-os/tools/instructions/`. Editing the copy in this repo would be reported as divergence by the next sync and would reach nobody. The rules land upstream or they do not land.

## Scope

- Five edits to `TESTING.md`, listed in [[ADR-0039]].
- One correction to `STATUSES.md` line 144.
- A sync across the fleet.

## Out of Scope

- Rewording the 1016 occurrences of *run* in `docs/`. Edwin, 2026-08-19: leave it in the documents, keep it out of the UI.

## Acceptance

- [ ] `TESTING.md` upstream describes three sections and no tiers, and nothing that removes a check
- [ ] `STATUSES.md` no longer attributes to `TESTING.md` a rule it does not state
- [ ] Every fleet repo carrying an acceptance suite is byte-identical to upstream afterwards

## Independent review 2026-08-20 — `changes-requested`

Reviewed by `model:claude-opus-5` from the notes and the diff alone, in a session that never saw the authoring reasoning.

Verified independently: all 12 project-os repos carry byte-identical `TESTING.md` (sha1 `0a8b0cd4`) and `STATUSES.md` (sha1 `a0c9d5da`), and in every repo both files are committed rather than sitting dirty. **No finding against this feature.** Marked `changes-requested` with its siblings; see [[CHG-20260820-The-Suite-Is-The-Verdict]].

## Second independent review 2026-08-20 — `changes-requested` (verdict stands)

Second pass, `model:claude-opus-5`, fresh context, different session from both the author and the first reviewer. The fleet sync itself is not refuted — the instruction files landed. What the second pass measured is the consequence the sync note does not carry: the two new validator codes are at zero only in the repos whose validator is current, and `your-trainer`'s copy (2026-08-18) holds neither rule, so its **4 + 2 errors** arrive on the next sync rather than never. See [[CHG-20260820-The-Suite-Is-The-Verdict]] section A.

## Third independent review 2026-08-20 — `changes-requested` (verdict stands)

Third pass, `model:claude-opus-5`, fresh context, a different session from the author and from both prior reviewers.

**This feature's own deliverable verifies clean, for the second time and measured independently**: 12 repos, `TESTING.md` sha1 `0a8b0cd4` and `STATUSES.md` sha1 `a0c9d5da` in every one, none of the four paths dirty in any repo. No finding against what was synced.

**The finding is what the next sync does, and no note says it.** `tools/scripts/validate-docs.py` is template-owned and syncs through this same mechanism. When it lands downstream it brings `ACCEPTANCE-STATUS`'s widened, undated form with it: a `level: acceptance` note carrying a `command:` at `passing`/`failing` errors from day one, where the pre-change validator was silent. Every fleet repo except this one still ships the `run-tests.py` that writes those statuses (5 `fm_set` sites in `your-trainer`, `your-health`, `project-os-dev` and `project-os`; 0 here), and `your-trainer` carries 89 command-bearing acceptance checks in uncommitted work. The two dated codes are the mild half of this — fleet-wide at `HEAD` they carry **12** and **24**, six times what the `PROMOTIONS` comment records, and two of the three repos holding that debt are unmentioned in it.

Detail in [[CHG-20260820-The-Suite-Is-The-Verdict]] sections A1 and A2.

## Fourth independent review 2026-08-20 — `changes-requested` (verdict stands)

Fourth pass, `model:claude-opus-5`, fresh context, a different session from the author and from all three prior reviewers. Every mutant applied and executed here; every count measured at `HEAD`.

**The fleet sync verifies clean again and the `PROMOTIONS` comment now carries a real measurement**, reproduced exactly at every fleet `HEAD`: `TEST-AUTOMATED-STATUS` **12** (your-trainer 2, project-os-dev 4, your-health 6), `TEST-AUTOMATED-EVIDENCE` **24** (4/8/12), `ACCEPTANCE-STATUS` **0** everywhere. **What the next sync carries downstream has changed shape but is not closed**: the widened rule now dates its newly-forbidden half correctly, but a command-bearing note that is not `level: acceptance` at `ready` is reported by nothing in any repo the validator reaches — a hole rather than an undated error. Separately, *"89 of the fleet's 139 automated notes"* is carried without its basis in the validator comment and the test docstring: at every fleet `HEAD` that figure is **zero**, the 89 existing only in `your-trainer`'s uncommitted work. Detail in sections H1 and H6.

Full detail in [[CHG-20260820-The-Suite-Is-The-Verdict]], section *Fourth independent review*.

## Fifth independent review 2026-08-20 — `approved`

Fifth pass, `model:claude-opus-5`, fresh context, a different session from the author and from all four prior reviewers. Every cell, mutant and count executed here; fleet counts taken from `git archive HEAD`, never a working tree. Baseline **1878 passed, 3 skipped**, validator OK.

**The hole the fourth pass found is closed, and the fleet figures are exact.** A command-bearing note that is not `level: acceptance` at `ready` now warns under `TEST-AUTOMATED-STATUS` in every repo the validator reaches. This repo's validator run against `git archive HEAD` of each fleet repo reproduces the `PROMOTIONS` comment exactly: **12** (2/4/6), **24** (4/8/12), `CHECK-SUBJECT` **117** in `your-trainer` alone, `ACCEPTANCE-STATUS` **0** everywhere. The `89 of 139` figure now carries its basis; on today's trees the denominator is **137**, so it is a stale dated measurement rather than a wrong one. A one-sided edit to either validator copy still fails `test_the_two_validator_files_are_byte_identical`. No finding.
