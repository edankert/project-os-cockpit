---
type: "[[task]]"
id: TASK-0547
aliases: ["TASK-0547"]
title: "A release can be sealed from the cockpit — the ledger has no lifecycle until something closes it"
status: done
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
parent: "[[FEAT-0133-The-Ledger-Is-The-Only-Place-A-Verdict-Lives]]"
phase: "[[PHASE-038-A-Verdict-Is-An-Event]]"
tags: [task]
---

# Nothing seals

`ledger.seal()` exists and **nothing calls it but a script**. Found while marking [[PHASE-038]]'s exit criteria against reality: it is not a missing button, it is a missing lifecycle.

Without it, entries accumulate in `WORKING-<platform>.json` forever; `na` and `pass` are never attributed to a release; *was release R walked?* has no R to ask about; and **decision 7's expiry — the sharpest single argument in [[ADR-0037]] — can never fire.** `excused` is proved to expire in tests and cannot expire in the product.

## Definition of Done

- [x] `POST /api/notes/seal-ledger` seals one platform's working ledger against a release, refusing an unknown release id and a platform with no working ledger.
- [x] The release note records each sealed ledger and its blob hash ([[TASK-0548]]) **in the same write**.
- [x] The release page offers it, and only where it means something: a `preparing` release with a working ledger.
- [x] Sealing is refused on a release that is already `released` — [[ADR-0035]] says a release page reports and does not record, and re-sealing a shipped release is the one write that would rewrite history.
- [x] Proved end to end: walk a check, seal, and the check is owed again on the next cycle if it was `excused`.

## Done 2026-08-19

`POST /api/notes/seal-ledger` and a **Seal** action on the release page, offered only on a release that has not shipped and only when a platform is selected — sealing "everything" would have to invent which cycle it was closing, so no platform means no button rather than a guess.

Refused on a `released` release: [[ADR-0035]] says a release page reports and does not record, and re-sealing a shipped release is the one write that rewrites what it was measured against rather than adding to it.

**Proved end to end**: walk two checks, excuse one, seal — the pass persists, the excuse is gone, the working ledger is gone, and the release note carries the sealed file's hash. That is decision 7 firing where a person can see it, which it could not do at all before.
