---
type: "[[task]]"
id: TASK-0294
aliases: ["TASK-0294"]
title: "The debt payload — three queries over the index"
status: done
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0065-Acceptance-Debt-Surface]]"]
parent: "[[FEAT-0065-Acceptance-Debt-Surface]]"
effort: M
depends: []
blocks: []
related: []
tests: []
---

# The debt payload

## Definition of Done

- Unverified requirements (no TST names them in `verifies:`), unresolved criteria on non-terminal notes, ticks carrying no evidence — one endpoint, counts plus rows.
- Numbers reconcile with the validator's own counts on the same corpus, asserted.

## Done — 2026-08-11

`GET /api/cockpit/acceptance-debt`, in `criteria.py` — the module that already owns the parse, so the debt numbers and the runner cannot disagree about what a criterion is.

Measured on this corpus at close: **24 unverified · 4 unresolved · 0 evidence-free.**

Each is a different question about the same gap between what the record *claims* and what it *shows*:

- **unverified** — no `[[test]]` names the requirement in `verifies:`. It may be perfectly implemented; nothing mechanical checks it. 24 of them here.
- **unresolved** — open criteria on notes that are still live. Not an error (REQ-BOXES only fires at terminal), but it is the work in front of a run. The four are REQ-0029/0030/0031 — [[PHASE-027]]'s drafts — and REQ-0032.
- **evidence-free ticks** — the most interesting, and currently zero: a `- [x]` with no evidence and no witness reads exactly like one with proof, which is the failure [[REQ-0028]] was written about.

Two judgments in the query, both about not manufacturing debt: a **terminal** requirement's open boxes are not owed to anybody (cancelled/superseded are excluded), and a requirement that declares criteria with **no boxes at all** counts at its declared size — zero boxes means "no verification record", not "nothing owed".
