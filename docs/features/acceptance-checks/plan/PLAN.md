---
type: "[[plan]]"
title: "Plan — PHASE-035 acceptance-checks features"
status: draft
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
source: []
implements: ["[[FEAT-0113-The-Check-Type-And-The-Migration]]", "[[FEAT-0114-The-Suite-Is-A-View]]", "[[FEAT-0115-The-Sweep-Is-Continuous]]", "[[FEAT-0116-A-Release-Can-Be-Finished]]", "[[FEAT-0117-One-View-Per-Item]]"]
related: ["[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]", "[[PHASE-035-Acceptance-Checks-Are-Notes]]"]
---

# Plan — PHASE-035, five features, one order

## The two gates before anything

1. **[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]] is `proposed`.** Nothing migrates, scaffolds or writes a `CHK-*` until Edwin accepts it. The phase is documented in full precisely so the acceptance is about something concrete.
2. **Upstream first.** [[TASK-0459-The-Check-Type-Lands-Upstream]] lands in `~/Dev/repos/project-os` and syncs down before any note exists in any repo — nothing carries permanent template divergence.

## Delivery sequence

1. **[[TASK-0459]]** upstream type → **[[TASK-0460]]** migration script → **[[TASK-0461]]** pilot on this repo (34 rows). Record-level parity proven before any UI changes.
2. **[[TASK-0462]]** the two-shape delta — the gate must not lose a single historical tag, and this is provable the moment the pilot lands.
3. **[[TASK-0464]]** the generated view (retiring the document plumbing), then **[[TASK-0466]]** verdict writes on notes. The view and the writes together replace everything the document path did.
4. **[[TASK-0467]]** the sweep, then **[[TASK-0468]]** the considered obligation — the continuous model becomes real here, and the pilot repo runs a genuine close-out sweep.
5. **[[TASK-0469]]** Mark released, behind both refusals. **[[TASK-0470]]** and **[[TASK-0471]]** are independent and slot anywhere.
6. **[[TASK-0463]]** fleet migration — `your-sudoku`, then `your-trainer` last, only after step 4 has happened for real in the pilot.
7. **[[TASK-0472]]** the per-item view, last by design: until the sweep exists it has nothing honest to say about a feature with no checks, and until Mark released freezes `features:` the item list it slices is wrong.
8. **[[TASK-0465]]** one walk layer rides beside step 3 or after it.

## Measured price, accepted up front

~9.5 days across the sequence, against ~1 day for the projection alternative recorded in [[FEAT-0112-The-Acceptance-Suite-Gets-A-Machine-Readable-Projection]] — the premium buys per-check evidence, index-resolvable coverage, burden as a field, and the native shape. On the record here so it is a decision, not a week-two discovery.
