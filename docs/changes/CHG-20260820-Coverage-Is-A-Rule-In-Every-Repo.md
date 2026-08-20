---
type: "[[change]]"
id: CHG-20260820
aliases: ["CHG-20260820"]
title: "`FEATURE-UNCOVERED` and its escape land in the template repo, so acceptance coverage is a lifecycle rule rather than one repo's habit"
status: merged
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[FEAT-0132-Acceptance-Tests-Are-Scaffolded-By-Rule]]", "[[REQ-0051-Coverage-Is-A-Rule-Not-A-Request]]", "[[TASK-0522-Scaffold-Acceptance-Tests-With-The-Feature]]", "[[TASK-0523-The-Validator-Names-An-Uncovered-Feature]]", "[[FEAT-0130-Surfaces-Are-A-First-Class-Type]]", "[[REQ-0049-A-Surface-Exists-Whether-Or-Not-A-Test-Names-It]]", "[[ISS-0250-A-Surface-Rename-Silently-Orphans-Its-Checks]]"]
tags: [change, lifecycle, validator]
---

# Coverage is a rule in every repo, not only in this one

## What changed

**`~/Dev/repos/project-os/tools/scripts/validate-docs.py` gained `FEATURE-UNCOVERED`.** A feature at `done` that no `level: acceptance` check names in `covers:` produces one **warning**, on the feature, in any repo that holds at least one acceptance check. `acceptance_exception:` on the feature silences it permanently.

**`docs/__templates__/SCHEMAS.md` documents `acceptance_exception:`** — in the template repo *and* here. It did not, in either. The rule named a field the schema did not, and an escape a person cannot find is an escape nobody uses.

**Nothing changes in this repo's own validator output.** The rule has been here since `cc90468`; what moved is where it lives.

## Who is affected

`tools/scripts/` is `template`-owned in `tools/sync/MANIFEST.yaml`. On the next `sync-project-os.sh`:

- a fleet repo whose `validate-docs.py` still matches the recorded baseline **receives the rule**;
- a repo with a locally diverged copy — this one, 720 lines ahead — is **skipped and reported for hand-merge**, not clobbered.

Of the twelve `SNAPSHOT.yaml`-bearing repos, **nine hold no acceptance check at all** and the rule is silent in all nine by construction. The three that hold a suite carry **134** terminal-and-uncovered features between them under the rule as it ships.

**It warns and never errors, and that is deliberate.** [[project-os-dev#ADR-0011]] clause 3 forbids promoting a rule over existing debt. `FEATURE-UNCOVERED` is absent from `PROMOTIONS` and a test fails if anybody adds it.

## Why the previous decision was reversed

[[TASK-0522]] recorded that the rule *"stays downstream for now"* because *"pushing one rule up while that gap exists would be a partial sync."* The gap is real — 3213 lines here against upstream's 2500 — but the conclusion is not, and the manifest says so in one line: `template` ownership **skips** a diverged downstream copy. A fair question that already had an answer, in a file nobody opened.

## How it is guarded

**By execution, not by grep.** A substring search for `FEATURE-UNCOVERED` in upstream's source is satisfied by a comment mentioning it — the over-broad text match that has bitten this phase seven times. The four new tests in `tests/test_feature_uncovered.py` drive upstream's validator over a constructed corpus and read what it reports.

Six-case domain, enumerated rather than sampled, behaving upstream exactly as it does here: `done` + suite -> 1; `doing` -> 0; no suite -> 0; exception -> 0; covered by an acceptance check -> 0; covered **only** by a non-acceptance `TST-*` -> 1.

Four mutants executed against upstream with `__pycache__` cleared and `PYTHONDONTWRITEBYTECODE=1`, each failing exactly one test: deleting the rule, replacing the has-a-suite guard with `if True:`, dropping the exception clause, and stripping the field from `SCHEMAS.md`. A fifth, upstream only: dropping the `level == "acceptance"` filter takes the last case from 1 to 0.

## Two defects fixed in this repo's own copies

**The rule's explanatory comment was attached to a different rule.** In both validator copies the `#: **A finished feature that nothing verifies**` block sat above the `RELEASE-PREPARING` loop, with `FEATURE-UNCOVERED`'s code forty lines below carrying no comment at all — and the `# -- counter integrity` marker it displaced was stranded two rules from the counters. Moved onto its own rule.

**`_repo_has_an_acceptance_suite`'s docstring said 89** where the arithmetic gives **86** (220 - 134). It was the gap between the two *wide* figures carried onto the narrow pair — the one place the previous round's correction did not reach.

Both validator copies remain byte-identical.

## Also in this change: the surface mapping is recorded

[[FEAT-0130]] closed, and the last thing it was waiting on was that **the 76-to-15 `area:` consolidation was recorded nowhere.** The table [[TASK-0515]] carried was a superseded proposal — thirteen of its fifteen surface names exist nowhere in `your-trainer` — and the only copy of what was actually applied was an **uncommitted working-tree diff in another repo**.

It is recorded now, against `HEAD` and with the basis stated: 75 of the 76 original values map one-to-one, and the 76th (the `Moved from Tier 1 / Tier 2 — Fully Automated` parking bay) fans out across 13 surfaces and so is recorded **note by note**, all 66. 513 + 66 = 579.

[[REQ-0049]] criterion 4 — *"the original `area:` string is preserved on the note"* — is `[~]` **reconciled, not ticked**: the property (reversible by reading) holds, the instrument (a field on the note) was never built, and the cost is stated. [[ISS-0250]] carries the fragility that survives: the check-to-surface join is a **string comparison**, so an em dash retyped as a hyphen drops a surface from 91 checks to 0 in silence — measured, and the first version of that note named two edits the join actually survives.
