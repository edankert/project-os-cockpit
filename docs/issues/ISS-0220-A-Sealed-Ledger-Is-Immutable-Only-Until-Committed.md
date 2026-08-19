---
type: "[[issue]]"
id: ISS-0220
aliases: ["ISS-0220"]
title: "`LEDGER-SEALED` diffs the working tree against `HEAD`, so editing a sealed ledger and committing it passes forever — *was release R walked?* has an answer that can still change"
status: open
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: medium
component: tooling
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[TASK-0528-The-Validator-Reads-A-Ledger]]", "[[REQ-0052-A-Verdict-Names-Its-Platform-Method-Author-And-Date]]"]
---

# Immutable until committed is not immutable

## Problem

[[ADR-0037]] decision 9: *"A sealed ledger is never edited. The validator enforces it. **Was release R walked?** is answered by reading its ledger, and the answer does not change afterwards."*

`validate_ledgers` enforces it by comparing the file on disk to `git show HEAD:<path>`. So it catches an **uncommitted** edit and passes forever once that edit is committed. The honest scope of the rule is *"you have not edited a sealed ledger since the last commit"* — which is what a pre-commit gate can see, and not what the decision claims.

Found by independent review of [[PHASE-038]] Stage 1, 2026-08-19 (finding 6).

## Why it matters more than it looks

The immutability is not a tidiness rule. It is the entire basis of one of the five queries [[ADR-0037]] promises — *was release R walked?* — and of the release record being a record at all. A sealed ledger that can be rewritten is a mutable log, which is a scalar with extra steps.

It is also the one rule whose violation leaves **no other trace**: a rewritten verdict looks exactly like a verdict that was always there.

## What it would take

The seal has to be checked against **the commit that created it**, not against the previous commit. That means recording the sealing commit — which cannot go in the ledger itself, because the sha does not exist until after the file is written.

Two candidate shapes, neither free:

1. **A second commit** that stamps `sealed_at: <sha>` into the ledger, so the check becomes *"the file matches what `sealed_at` points at"*. Honest, and it makes sealing a two-commit operation.
2. **The release note carries the sha**, and the check reads it from there. Keeps sealing atomic, and puts a fact about a ledger somewhere other than the ledger.

Neither should be picked in a hurry: this is a record-integrity mechanism and getting it half-right is worse than the current honest gap.

## Done when

- [ ] A sealed ledger that is edited **and committed** is an error.
- [ ] The shape is decided in [[ADR-0037]] or an amendment, not in a commit message.
- [ ] `tests/test_ledger_validator.py::test_a_sealed_ledger_edited_in_the_working_tree_is_caught` — whose last assertion currently pins the *gap* — is updated, and its comment says so.

## Until then

The gap is asserted rather than hidden. That test ends with `assert "LEDGER-SEALED" not in out.stdout` and a message saying *"if this now fails, the rule was strengthened — update ISS-0220"*, so the limit cannot quietly stop being true.
