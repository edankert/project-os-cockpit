---
type: "[[task]]"
id: TASK-0522
aliases: ["TASK-0522"]
title: "The feature scaffold emits a Tier 1 acceptance test beside PLAN.md"
status: done
owner: user:edwin
created: 2026-08-18
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: approved
parent: "[[FEAT-0132-Acceptance-Tests-Are-Scaffolded-By-Rule]]"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
tags: [task]
---

# The feature scaffold emits a Tier 1 acceptance test beside PLAN.md

Template-owned: lands in `~/Dev/repos/project-os` first (`tools/skills/feature-scaffold/SKILL.md` and the templates) and syncs down. REQ-0051 criterion 5 — the sweep governed one repo and eleven carried on uncovered.

The emitted note is Tier 1 by TESTING.md's own definition: *created when a feature is first implemented*.

## Done 2026-08-20 — upstream first, then synced

`tools/skills/feature-scaffold/SKILL.md` step 9, edited in `~/Dev/repos/project-os` and copied down byte-identical. `acceptance_exception: ""` added to `docs/__templates__/feature.md` in both.

### What changed, and why it is a rule now

Step 9 read *"if the feature requires verification, create `TST-*` notes"*. That is a judgement made per feature, at the end, by whoever was tired — and the corpus says how it went. Measured across the twelve project-os repos, 2026-08-20:

| | features reaching a terminal status with no acceptance check |
|---|---|
| all twelve repos | **236** |
| the three holding a suite | **147** |

**A rule applied when somebody remembers is not a rule.** The scaffold now emits `plan/tests/TST-####-*.md` — `level: acceptance`, `covers: ["[[FEAT-####]]"]`, no `command:` — as an Output rather than a conditional step.

### The escape, at the end where the reason is known

`acceptance_exception:` is in the feature template, empty. Some features never can have a check: an engine with no user-facing surface, a phase of work, a repo that ships prose. Said **once, at scaffold time**, when whoever is creating the feature actually knows why — rather than at close-out, which is where [[TASK-0524]] found 33 features nobody could write a true exception for.

**The two ends now ask one question.** The scaffold emits or excepts; `FEATURE-UNCOVERED` ([[TASK-0523]]) warns at close-out for anything that is neither. A test asserts both name the same field, because a skill and a validator disagreeing about it is [[REQ-0059]]'s shape across two artefacts.

### `FEATURE-UNCOVERED` stayed downstream for a day, and the reason given was wrong

**What this section used to say:** *"Pushing one rule up while that gap exists would be a partial sync, which is how the `kind:` removal took three passes. The rule is cockpit-local until the validators are reconciled."*

The gap is real — the cockpit's validator is **3213 lines against upstream's 2500**, 720 **ahead** rather than behind. What is wrong is the conclusion, and `tools/sync/MANIFEST.yaml` answers it in one line:

> `template` — *overwritten when the downstream copy matches the recorded baseline; **locally diverged copies are skipped and reported for hand-merge** (`--force` overrides)*

So a rule added upstream reaches every fleet repo whose validator still matches the baseline, and this repo's diverged copy is **skipped**, not clobbered. The hazard the section named does not exist. It was a fair question that already had an answer, in a file nobody opened.

**Landed upstream 2026-08-20**, which is [[REQ-0051]] criterion 5 — see [[TASK-0523]] for the port, its six-case domain and its four mutants.

### Two errors of mine, both from moving between repos

The template edit ran **twice against upstream** — the second block inherited the shell's `cd` — so `acceptance_exception:` appeared there twice and downstream not at all. And the guard for the old wording matched **my own quotation of it** inside the new step: the over-broad text match that has now bitten four guards in this phase. It asserts the wording is absent as a live *instruction*, not as a quotation.

### The upstream edit is uncommitted, and this note did not say so

Added 2026-08-20 after independent review, which found [[TASK-0523]] and [[REQ-0051]] citing this note as already carrying that caveat when it carried nothing of the kind — no *uncommitted*, no *working tree*, no *no commit* anywhere in it.

`tools/skills/feature-scaffold/SKILL.md` and `docs/__templates__/feature.md` are **modified and uncommitted** in `~/Dev/repos/project-os`, alongside `SCHEMAS.md`, `TAXONOMY.md`, `test.md`, `acceptance-tests.md` and `validate-docs.py`, plus an **untracked** `surface.md`. *"Upstream first"* is true of the edit and not yet of the record.

This is the `kind:` failure mode this task's own opening line invokes — *"three passes because six repos held the edit on disk and in no commit"* — and it needs a commit in `project-os` that nothing in this repo can make.

## Independent review — fifth pass, 2026-08-20

Fresh context, separate session, `model:claude-opus-5`. Verdict: **approved**. Re-measured or re-executed, not read.

Upstream-first is real, not asserted. `diff -q` reports the scaffold skill **byte-identical** between `~/Dev/repos/project-os/tools/skills/feature-scaffold/SKILL.md` and this repo's copy.

**No duplication upstream, and the field is empty in both templates.** `acceptance_exception:` appears exactly **once** in each of the two feature templates, as `acceptance_exception: ""`, and a corpus-wide sweep of both `docs/__templates__` directories finds it in those two files and nowhere else — so the duplication you caught once has not recurred.

**The scaffold and `FEATURE-UNCOVERED` name the same field**, verified by grep on both sides. That is what makes the escape usable: the rule tells you the field, the scaffold ships it empty, and nothing has to be remembered.

Pre-filling the escape would defeat it — an exception that arrives already written is one nobody chose — and shipping it empty rather than omitting it is the difference between an escape a person finds and one they have to be told about.

## Independent review — fresh-context pass, 2026-08-20 (`b4b9c50` / `4521a7a`)

Separate session, `model:claude-opus-5`, starting from the notes and the diff with no access to the author's reasoning. Same model family as the author, recorded in `reviewed_by`; the independence claimed here is **context**, not weights ([[project-os-dev#ADR-0013]]).

**Verdict: approved.** The reversal is sound and the manifest quotation is verbatim.

`tools/sync/MANIFEST.yaml` line 5 reads exactly as quoted: *"`template` — template-owned: overwritten when the downstream copy matches the recorded baseline; locally diverged copies are skipped and reported for hand-merge (`--force` overrides)"*, and `"tools/scripts/": template` is line 18. So the hazard the superseded section named genuinely does not exist, and this note is right to keep the `--force` clause that [[CHG-20260820]] drops.

Two things to note without blocking:

- The line counts are stale: measured at this commit, this repo's validator is **3267** lines and upstream's is **2493** at `HEAD` (**774** ahead) or **2581** with the port applied (**686** ahead), not *"3213 against 2500"* / *"720 ahead"*. The argument does not depend on the figure.
- *"**Landed upstream 2026-08-20**"* is true of the working tree and of no commit — `FEATURE-UNCOVERED` appears **0** times in upstream at `HEAD`. [[TASK-0523]] and [[REQ-0051]] disclose that; this note does not, and [[REQ-0051]] cites this note as one of two that *"already carry it"*. It does not — recorded as a finding on [[REQ-0051]].
