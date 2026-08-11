---
type: "[[change]]"
id: CHG-20260811-P024
title: "PHASE-024 closes — acceptance is a recorded act: criteria walked one at a time, a witness by construction, evidence that is a file in the record"
status: merged
date: 2026-08-11
owner: user:edwin
related: ["[[PHASE-024-Acceptance-Witnessed]]", "[[FEAT-0063-The-Acceptance-Runner]]", "[[FEAT-0064-The-Acceptance-Gate]]", "[[FEAT-0065-Acceptance-Debt]]", "[[FEAT-0066-Visual-Evidence]]", "[[ISS-0096]]", "[[REQ-0028]]", "[[REL-0001-The-Human-Has-Levers]]"]
tags: [change]
---

# PHASE-024 closes

Third of [[REL-0001]]'s five. *"PHASE-022 ran twelve acceptance rounds whose only witness record is a chat transcript"* — [[REQ-0028]]'s opening line, and the thing this phase exists to make impossible.

## What shipped

**[[FEAT-0063]] — the runner.** `~accept/<FEAT-id>`, one criterion at a time. Pass ticks with a machine-composed witness; fail files a pre-linked issue and **the run continues**; reconcile writes the `[~]` form. Every verdict writes immediately, so an abandoned run keeps the work already done.

**[[FEAT-0064]] — the gate.** `acceptance:` documented with three states, opt-in and never blocking. `ACCEPT-STALE` warns — never errors — because a gate that blocks on the one unautomatable judgment becomes a rubber stamp.

**[[FEAT-0065]] — the debt.** Three numbers that existed nowhere: **24 unverified · 4 unresolved · 0 evidence-free**. A record card, not a badge: the gap was invisible, which is the problem; it is not a deadline.

**[[FEAT-0066]] — visual evidence.** Captures land at `docs/attachments/<NOTE-ID>/…` and are committed. No new read path was needed — `/docs/<path>` already serves the tree and the renderer already rewrites image sources.

**[[ISS-0096]] — the shape of a change.** `ISS-0135 touched 14 files — 6 notes, 4 source, 3 tests`. That sentence did not exist anywhere; `commits_payload` discards non-`.md` paths on purpose, for its own question.

## Four things a real walk found that no unit test would have

1. **The runner could not write to the requirement that specifies it.** `stamp_tick` rewrites an *existing* checkbox, and [[REQ-0028]] declared four criteria with **no boxes** — REQ-BOXES' "no verification record", the exact state a run exists to move out of. A first tick may now create the box, guarded so the criterion must appear verbatim in that note's own `acceptance:` list; without the guard the verb becomes "write any line into any note".

2. **The run stamp refused features that had not opted in.** [[DES-0006]]'s entry point is *"for accepting anything on demand, opted-in or not"* and only the **stamp** is conditional. The run now always records, and the log says *"not accepted (acceptance was not requested)"* so a completed walk cannot read as an acceptance.

3. **The 📷 was nearly shipped as a door to nothing** — the exact failure this release recorded against [[FEAT-0088]], while I was in the middle of citing it. The capture is now spent on the verdict it was taken for, *before* the verdict is recorded, so a failed attach stops the verdict rather than silently dropping the only proof.

4. **A verification that proved nothing.** `validate-docs.py` takes `--repo-root`, not a positional path. An earlier check passed a positional path, the script exited on a usage error, and `grep -c ERROR` returned zero — which reads exactly like a clean run. The claim happened to be true; the evidence was not. Re-run correctly, and recorded in [[TASK-0288]] and [[TASK-0293]] because the same shape would silently pass any future check written that way.

## Also caught

Adding `ACCEPT-STALE` to `validate-docs.py` drifted it from `validate_docs_bundled.py`, which is a **verbatim** copy. `test_bundled_validator_matches_the_canonical_one` caught it — the guard that exists because the bundle once fell behind ADR-0007 and would have accepted a retired status.

## Verification

New: `tests/test_criteria.py` (13), `tests/test_acceptance_run.py` (8), `tests/test_attachments.py` (11), `tests/test_change_shape.py` (6).

The parse the runner uses is proven **identical to REQ-BOXES requirement-by-requirement over the whole corpus**, against the real `validate-docs.py`, rather than against fixtures — because if they diverge, a person can finish a run and still be refused at close-out.
