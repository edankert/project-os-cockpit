---
type: "[[task]]"
id: TASK-0288
aliases: ["TASK-0288"]
title: "The runner surface — one criterion at a time, four verbs, progress named"
status: done
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0063-The-Acceptance-Runner]]"]
parent: "[[FEAT-0063-The-Acceptance-Runner]]"
effort: M
depends: ["[[TASK-0287]]"]
blocks: []
related: []
tests: []
---

# The runner surface

## Definition of Done

- Centre-pane walk per DES-0006: criterion text large, `Pass / Fail… / Skip-reconcile… / 📷`, progress `3 of 7`.
- Pass ticks through the tick path with the machine-composed witness; Fail opens inline issue capture pre-linked to REQ and feature; the run continues after a fail.
- Keyboard-first: enter passes, f fails, esc leaves the run resumable.

## Done — 2026-08-11

`~accept/<FEAT-id>` — the centre-pane walk from [[DES-0006]]. One criterion at a time, deliberately not a checklist page: *a list invites skimming, and the runner's whole value is that each criterion was actually tried.*

`Pass` ticks through the [[DES-0005]] tick path with the evidence **machine-composed** (`accepted in cockpit run, user:edwin, 2026-08-11` — [[REQ-0028]]'s witness by construction). `Fail…` files a pre-linked issue and **the run continues**, because a fail is a datum, not an abort. `Skip / reconcile…` writes the `[~]` form with its reason. Keyboard-first: enter passes, `f` fails, `s` reconciles, esc pauses.

`Accept…` in the actuator row is the on-demand entry point; the queue entry is [[TASK-0290]].

**Every verdict writes immediately** rather than at the end. An abandoned run therefore keeps the work already done — the record is the ledger, not the in-memory run object — which is what makes esc safe and resume meaningful.

### Two things a real walk found that no unit test would have

**1. The tick path could not tick anything on REQ-0028.** `stamp_tick` rewrites an *existing* checkbox, and a requirement may declare its criteria in frontmatter `acceptance:` with **no boxes at all** — REQ-BOXES' "no verification record", and precisely the state a run exists to move out of. REQ-0028 was in it: four criteria, zero boxes. The runner's first target was a requirement it could not write to.

Fixed by letting a first tick **create** the box, guarded so the criterion must appear verbatim in that note's own `acceptance:` list. Without the guard this verb becomes *"write any line into any note"*; with it, the runner can only record verdicts on criteria the record already declares.

**2. The run stamp refused features that had not opted in.** DES-0006's feature-note entry is *"for accepting anything on demand, opted-in or not"* and only the **stamp** is conditional — but the first cut refused the whole call, which would have made a walk impossible on most features. Now the run is always recorded and `accepted_by` still requires `acceptance: requested`; the log line says *"not accepted (acceptance was not requested)"* so a completed walk cannot read as an acceptance.

### Walked, not just compiled

Against a throwaway copy of the corpus: four criteria on REQ-0028 — three passed, one reconciled — then the run recorded on FEAT-0063. The resulting note carries a proper `## Acceptance Criteria` section, and the validator reports **0 REQ-BOXES errors** on the walked copy, so the boxes the runner writes are exactly the shape the gate parses. The real record was untouched.
