---
type: "[[task]]"
id: TASK-0298
aliases: ["TASK-0298"]
title: "The capture affordance where judgments happen"
status: done
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0066-Visual-Evidence]]"]
parent: "[[FEAT-0066-Visual-Evidence]]"
effort: S
depends: ["[[TASK-0297]]"]
blocks: []
related: []
tests: []
---

# The capture affordance where judgments happen

## Definition of Done

- The runner's 📷, the TST manual runner and the note actuator row can attach a capture to the verdict being written; the evidence line carries the image reference in the same write.

## Done — 2026-08-11

`📷` in the acceptance runner's action row, beside Pass / Fail / Reconcile.

**It attaches to the NEXT verdict rather than writing on its own** — DES-0006's *"attach a capture to whatever the next verdict is"*. So a picture is always evidence **for** something: a pass cites it in the tick's evidence string, a fail carries it into the issue body. A capture that wrote itself immediately would produce loose files nothing points at, which is the failure this feature exists to prevent one level up.

**The button was nearly shipped as a door to nothing.** The first cut set `pendingCapture` and no verdict consumed it — the exact failure [[REL-0001]] recorded against [[FEAT-0088]] (*"a door to nothing teaches the reader the feature works"*), and I had just finished criticising it. Completed instead: the verdict spends the capture through `/api/notes/attach` **before** recording, so a failed attach stops the verdict rather than silently dropping the only proof.

**The staging round-trip is the part with a threat model.** The desktop bridge writes to `inbox/` and hands back a name, but `inbox/` is gitignored staging whose success condition is being *empty* — so the endpoint reads it, files it under `docs/attachments/`, and **removes it from staging**. The name is reduced to a basename and the resolved path checked against `inbox/`, because a name arriving from a renderer must not be able to read an arbitrary file; a `../secret.png` attempt is refused and the file left untouched, with a test that asserts both.
