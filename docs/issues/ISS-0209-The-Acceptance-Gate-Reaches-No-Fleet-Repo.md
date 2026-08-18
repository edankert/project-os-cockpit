---
type: "[[issue]]"
id: ISS-0209
aliases: ["ISS-0209"]
title: "The acceptance gate runs in no repo that holds acceptance checks — the fleet validators are ~690 lines behind upstream and cannot be synced without a migration"
status: open
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: high
component: tooling
phase: "[[PHASE-999-Future]]"
related: ["[[ADR-0034-Three-Axes-Not-One-Word]]", "[[ISS-0208-Retire-The-Tier-Rule]]", "[[PHASE-036-One-Human-Walk]]"]
---

# The gate is in the wrong repos

`VERIFY-ACCEPTANCE` and `_acceptance_is_settled` exist in `project-os-cockpit`'s validator and — since `project-os@61c5c92` — in upstream's. They occur **zero** times in `your-sudoku`, `your-trainer`, `your-health` and `obsidian-supernote-sync`.

**Those are the repos that hold the 669 acceptance checks.** `your-sudoku` has six true `VERIFY-ACCEPTANCE` findings (FEAT-0025 against TST-0028..0033) that fire in no pre-commit and in no CI. The gate is installed everywhere except where the thing it gates lives.

Raised by all three independent reviews of [[PHASE-036-One-Human-Walk]]; the third called it one of a pattern with the uncommitted upstream validator and the uncommitted `kind:` removals — *"work that exists on the authoring machine and nowhere else"*. Those two are now committed. This one is not, because it is not a commit.

## Why it was not just synced

Measured 2026-08-18, not assumed. The fleet validators diverge from upstream by **690 lines** (`your-sudoku`, `your-trainer`, `obsidian-supernote-sync`) and **725** (`your-health`). Copying upstream's validator into `your-sudoku` — the one repo with a clean tree — and running it produced a **flood** of errors it currently passes: `SNAPSHOT-MEMBERSHIP` on eight features, `PARENT-BACKLINK` on every task in `FEAT-0001`, and more. The repo would have been unable to commit anything.

So the fleet validators are not behind by the acceptance gate. They are behind by **every upstream rule added since they were last synced**, and pulling one pulls all of them. That is a migration per repo — reconcile the notes each new rule reports — and `your-trainer` carries 59 dirty files belonging to another agent's work while it waits.

## Options

1. **Sync and migrate, one repo at a time**, cleanest first (`your-sudoku` is clean today). Honest, and the only route to the fleet actually sharing a gate.
2. **Backport only the acceptance rules** into each fleet validator. Cheap, gets the gate where the checks are, and widens the divergence it is a symptom of.
3. **Run the cockpit's validator over the fleet** from one place (`fleet_validate` already walks every repo) and treat *that* as the fleet gate, leaving each repo's own validator as the local pre-commit. Changes what "the gate" means rather than closing the gap.

Option 1 is right and expensive; option 2 is a patch that makes option 1 harder later.

## Done when

- [ ] `_acceptance_is_settled` runs in every repo holding acceptance checks, by whichever route is chosen.
- [ ] `your-sudoku`'s six FEAT-0025 findings either fire in its own pre-commit or are fixed.
- [ ] The divergence number is measured again and recorded, so the next reviewer sees whether it is closing or growing.
