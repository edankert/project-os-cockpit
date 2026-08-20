---
type: "[[change]]"
id: CHG-20260820
aliases: ["CHG-20260820"]
title: "`FEATURE-UNCOVERED` and its escape land in the template repo, so acceptance coverage is a lifecycle rule rather than one repo's habit"
status: merged
owner: user:edwin
created: 2026-08-20
updated: "2026-08-20"
reviewed_by: model:claude-opus-5
review_date: 2026-08-20
review_verdict: changes-requested
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

Of the twelve `SNAPSHOT.yaml`-bearing repos, **nine hold no acceptance check at all** and the rule is silent in all nine by construction. The three that hold a suite carry **139** terminal-and-uncovered features between them under the rule as it ships (2026-08-20).

**The figure the argument rests on is 86, and it is the only one that holds still.** Fleet and suite totals move under every commit — 220 / 134 when the rule landed, 225 / 139 hours later, the whole delta this repo's own close-outs. The nine no-suite repos do not move, so the number of findings the suite guard suppresses is 86 at either basis.

**It warns and never errors, and that is deliberate.** [[project-os-dev#ADR-0011]] clause 3 forbids promoting a rule over existing debt. `FEATURE-UNCOVERED` is absent from `PROMOTIONS` and a test fails if anybody adds it.

## Why the previous decision was reversed

[[TASK-0522]] recorded that the rule *"stays downstream for now"* because *"pushing one rule up while that gap exists would be a partial sync."* The gap is real — 3213 lines here against upstream's 2500 — but the conclusion is not, and the manifest says so in one line: `template` ownership **skips** a diverged downstream copy. A fair question that already had an answer, in a file nobody opened.

## How it is guarded

**By execution, not by grep.** A substring search for `FEATURE-UNCOVERED` in upstream's source is satisfied by a comment mentioning it — the over-broad text match that has bitten this phase seven times. The four new tests in `tests/test_feature_uncovered.py` drive upstream's validator over a constructed corpus and read what it reports.

Six-case domain, enumerated rather than sampled, behaving upstream exactly as it does here: `done` + suite -> 1; `doing` -> 0; no suite -> 0; exception -> 0; covered by an acceptance check -> 0; covered **only** by a non-acceptance `TST-*` -> 1.

Four mutants executed against upstream with `__pycache__` cleared and `PYTHONDONTWRITEBYTECODE=1`, each failing exactly one test: deleting the rule, replacing the has-a-suite guard with `if True:`, dropping the exception clause, and stripping the field from `SCHEMAS.md`. A fifth, upstream only: dropping the `level == "acceptance"` filter takes the last case from 1 to 0.

## The exposure this note left out

**None of the upstream edits are committed.** In `~/Dev/repos/project-os`, `tools/scripts/validate-docs.py`, `docs/__templates__/SCHEMAS.md`, `feature.md`, `test.md`, `acceptance-tests.md`, `tools/instructions/TAXONOMY.md` and `tools/skills/feature-scaffold/SKILL.md` are **modified and uncommitted**, and `docs/__templates__/surface.md` is **untracked**. `sync-project-os.sh` copies from a checkout, so **no fleet repo receives any of this until somebody commits it there.**

*(Added after independent review. The first version of this note described the work as *"landed upstream"* and then, in the section on `FEAT-0130` below, condemned exactly this failure mode by name — an edit held *"on disk and in no commit"* — without noticing it was describing itself two sections up. [[TASK-0514]] and [[TASK-0522]] had the same gap and now carry the same caveat.)*

## Two defects fixed in this repo's own copies

**The rule's explanatory comment was attached to a different rule.** In both validator copies the `#: **A finished feature that nothing verifies**` block sat above the `RELEASE-PREPARING` loop, with `FEATURE-UNCOVERED`'s code forty lines below carrying no comment at all — and the `# -- counter integrity` marker it displaced was stranded two rules from the counters. Moved onto its own rule.

**`_repo_has_an_acceptance_suite`'s docstring said 89** where the arithmetic gives **86** (225 − 139, and 220 − 134 before that — the gap is basis-independent). It was the difference between the two *wide* figures carried onto the narrow pair — the one place the previous round's correction did not reach.

Both validator copies remain byte-identical.

## And the rule's positive half was guarded by nothing

Found by independent review the same day. Replacing `_features_covered_by_acceptance`'s body so that coverage is **never recognised** passed **all fourteen** tests in `tests/test_feature_uncovered.py`, in both validator copies and upstream, while taking this repo from 94 warnings to **125**.

The case *"a feature covered by an acceptance check is quiet"* was measured when the port was written and asserted nowhere: every fixture built a check whose `covers:` was empty, so coverage was only ever exercised as the empty set. **A rule that reports on everything is as useless as one that reports on nothing**, and a suite made of negative cases cannot tell them apart. Three guards added; the mutant now fails 2 tests downstream and 1 upstream.

The section above says the domain was *"enumerated rather than sampled"*. It was — and enumerating a domain is not the same act as guarding it.

## Also in this change: the surface mapping is recorded

[[FEAT-0130]] closed, and the last thing it was waiting on was that **the 76-to-15 `area:` consolidation was recorded nowhere.** The table [[TASK-0515]] carried was a superseded proposal — thirteen of its fifteen surface names exist nowhere in `your-trainer` — and the only copy of what was actually applied was an **uncommitted working-tree diff in another repo**.

It is recorded now, against **`49cf2ce9`** and with the basis stated: 75 of the 76 original values map one-to-one, and the 76th (the `Moved from Tier 1 / Tier 2 — Fully Automated` parking bay) fans out across 13 surfaces and so is recorded **note by note**, all 66. 513 + 66 = 579.

**Two basis corrections, both from independent review.** The table's basis is `49cf2ce9`, **not** `HEAD` as the note first said: `your-trainer`'s HEAD is `0dad8104`, which committed the migration for six notes, so the same diff run today gives 73 originals over 573 rows. The table itself needed no change — re-derived against `49cf2ce9` it matches cell for cell — and `49cf2ce9` is the right basis because it is the last state in which all 579 originals sit in one place. And **`your-trainer`'s fifteen `SUR-*` notes exist in no commit on any branch**: at that repo's HEAD there are zero surfaces and 579 checks naming none of them. Every count here describes one machine's disk, which is why the record was worth making.

[[REQ-0049]] criterion 4 — *"the original `area:` string is preserved on the note"* — is `[~]` **reconciled, not ticked**: the property (reversible by reading) holds, the instrument (a field on the note) was never built, and the cost is stated. [[ISS-0250]] carries the fragility that survives: the check-to-surface join is a **string comparison**, so an em dash retyped as a hyphen drops a surface from 91 checks to 0 in silence — measured, and the first version of that note named two edits the join actually survives.

## Independent review — fresh-context pass, 2026-08-20 (`b4b9c50` / `4521a7a`)

Separate session, `model:claude-opus-5`, starting from the notes and the diff with no access to the author's reasoning. Same model family as the author, recorded in `reviewed_by`; the independence claimed here is **context**, not weights ([[project-os-dev#ADR-0013]]). Every number below was re-measured, and every mutant re-executed with `__pycache__` cleared and `PYTHONDONTWRITEBYTECODE=1`. Upstream was backed up before mutation and checksum-verified after restore.

**Verdict: changes-requested.** The technical claims hold; the change record omits the one caveat its own subject demands.

### 1. This note is the only place in the change that does not say the upstream edit is uncommitted

*"`~/Dev/repos/project-os/tools/scripts/validate-docs.py` gained `FEATURE-UNCOVERED`"* and *"On the next `sync-project-os.sh`: a fleet repo … **receives the rule**"* are stated without qualification. Measured: `FEATURE-UNCOVERED` appears **0** times in upstream at `HEAD` and once in its working tree; `docs/__templates__/feature.md` carries `acceptance_exception` only in the working tree; `docs/__templates__/surface.md` is **untracked** there. [[REQ-0051]] and [[TASK-0523]] both disclose this prominently. This note does not — two sections above its own paragraph condemning *"an **uncommitted working-tree diff in another repo**"*.

A change note is what a reader opens first and the durable record of what landed. As written it says a rule landed in the template repo, and a fresh clone of `project-os` does not have it.

### 2. `134` and `220` are correct against a stale basis

Re-measured across the twelve repos: **225** fleet-wide, **139** in the three suite-bearing ones. The stated pair reconstructs exactly with this repo at **88** and `your-trainer` at **33**, both already superseded when this was written. **The `86` derivation is sound and basis-independent** — it is the nine no-suite repos summed, and 225-139 gives 86 as surely as 220-134 does. *Nine hold no acceptance check* and *three hold a suite* both reproduce.

### 3. One unguarded case behind *"enumerated rather than sampled"*

`_features_covered_by_acceptance` can be made to return the empty set and all 14 tests pass in both repos; this repo goes 94 -> 125 findings in silence. Case 5 of the six listed — *covered by an acceptance check -> 0* — is asserted by no test. Recorded in full on [[TASK-0523]] and [[REQ-0051]].

### Verified rather than accepted

- *"Nothing changes in this repo's own validator output"* — **true, byte-for-byte.** Ran the pre-commit and post-commit validators against the same materialised corpus; the outputs are identical.
- The `MANIFEST.yaml` quotation is verbatim and the reversal of [[TASK-0522]] is sound (`--force` overrides, which the task records and this note omits).
- The `86` correction, the comment relocation, and byte-identity of the two copies all check out.
- Line counts are approximate: measured at this commit, **3267** here against upstream's **2493** at `HEAD` (774 ahead) or **2581** with the port applied (686), not *"3213 against 2500"* / *"720 ahead"*. It does not affect the argument.
- The [[ISS-0250]] summary in the last paragraph is exact — see that note.
