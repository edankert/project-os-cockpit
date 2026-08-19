---
type: "[[issue]]"
id: ISS-0220
aliases: ["ISS-0220"]
title: "`LEDGER-SEALED` diffs the working tree against `HEAD`, so editing a sealed ledger and committing it passes forever — *was release R walked?* has an answer that can still change"
status: fixed
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

- [x] A sealed ledger that is edited **and committed** is an error.
- [x] The shape is decided in [[ADR-0037]] decision 9a, not in a commit message.
- [x] The test that pinned the *gap* is replaced by two that pin the fix.

## Fixed 2026-08-19 — [[ADR-0037]] decision 9a

**Neither of the two shapes this issue proposed.** Edwin chose *the sha goes in the release note*, and the mechanics made a third option better than both: **a git blob hash rather than a commit sha.**

A commit sha does not exist until after the commit, so recording one would have made sealing a two-commit operation with an unprotected window between them — exactly the state a reader cannot distinguish from tampering. A blob hash is a hash of the *content*, computable at seal time, so the ledger and the release note that vouches for it land in **one commit**.

It is also strictly stronger than what this issue asked for. The old check compared the working tree to `HEAD`, so it verified *history*; this verifies **bytes**. An edit is caught whether it was committed, rebased, cherry-picked or restored from a backup, because none of those changes what the content hashes to.

`ledger.blob_sha` computes it without a subprocess and matches `git hash-object` exactly — asserted against the real command.

**A second rule fell out of it, and it is the half this issue did not ask for:** a sealed ledger that **no** release note vouches for is now an error of its own. An unvouched seal is precisely the state the old check could not tell from a good one.

## Reopened and re-fixed the same day — four bypasses

The first implementation ticked this issue's criteria and **did not hold**. Independent review reproduced four clean escapes, and the cause was one design error: the check walked `docs/releases/ledgers/*.json` and examined the files whose `sealed` key was set — **gating the check on a field inside the file it protects.**

| bypass | why it worked |
| --- | --- |
| delete `sealed:`, rewrite every entry | the file opted itself out |
| delete the ledger file | nothing walked the vouched list to notice an absence |
| move it out of the directory | same |
| rewrite LF → CRLF | `Path.read_text()` normalises newlines, so the "hash of the bytes" was not |

**The walk starts from the release note now**, because the record that vouches lives outside the file it vouches for — and it reads **bytes**. All four are guarded, each by a test written from the bypass.

The lesson is not about ledgers: *a tamper check keyed on data the tamperer controls is not a tamper check.*
