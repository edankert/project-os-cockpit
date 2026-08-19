---
type: "[[task]]"
id: TASK-0548
aliases: ["TASK-0548"]
title: "A sealed ledger names its own content hash and the release note holds it, so an edit is caught whether or not it was committed"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0133-The-Ledger-Is-The-Only-Place-A-Verdict-Lives]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# [[ISS-0220]], closed by [[ADR-0037]] decision 9a

`LEDGER-SEALED` compared the working tree to `HEAD`, so an edit that was **committed** passed forever.

## Definition of Done

- [x] `ledger.blob_sha(path)` computes git's blob hash — `sha1("blob <len>\0" + content)` — with no subprocess.
- [x] `seal()` returns it; the release note's `ledgers:` records `{file, sha}` per sealed ledger.
- [x] `LEDGER-SEALED` compares the **computed** hash to the recorded one, so an edit is caught committed, uncommitted, rebased or restored from a backup.
- [x] A sealed ledger that **no** release note vouches for is an error of its own — an unvouched seal is exactly the state the old check could not tell from a good one.
- [x] `tests/test_ledger_validator.py`'s assertion that currently pins the *gap* is replaced by one that pins the fix, and [[ISS-0220]] closes.

## Notes

**A blob hash, not a commit sha**, and the difference is not cosmetic: a commit sha does not exist until after the commit, so recording one would make sealing two commits with an unprotected window between them. A blob hash is computable at seal time, so the ledger and the note that vouches for it land together — and it verifies the **bytes** rather than the history.

## Done 2026-08-19 — [[ISS-0220]] closed

`ledger.blob_sha` computes git's blob hash without a subprocess and **matches `git hash-object` exactly**, asserted against the real command. `seal_record` returns `{file, sha}`; `note_writes.seal_ledger` writes it into the release note's `ledgers:` **in the same write** as the seal.

`LEDGER-SEALED` now compares the **computed** hash to the recorded one. An edit is caught committed, uncommitted, rebased or restored from a backup — the old rule compared the working tree to `HEAD` and so verified *history*, which is why a committed edit passed forever.

**A second rule fell out that this task did not ask for:** a sealed ledger no release note vouches for is its own error. An unvouched seal is exactly the state the old check could not tell from a good one.
