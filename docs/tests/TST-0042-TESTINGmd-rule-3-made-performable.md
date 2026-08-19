---
type: "[[test]]"
id: TST-0042
aliases: ["TST-0042"]
title: "TESTING.md rule 3 made performable — one Save, N added, M invalidated, one commit"
status: retired
covers: ["[[FEAT-0115-The-Sweep-Is-Continuous]]"]
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
last_verified: 2026-08-17
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
scope: feature
automated: true
command: ""   # the suite it ran is deleted (ADR-0036)
related: ["[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]"]
---

# TESTING.md rule 3 made performable

Was automated. Its suite was deleted with the subject ([[ADR-0036]]); the filename is deliberately not repeated here, because a register that scans these notes for test names cannot tell a historical mention from a live claim.

The benchmark is the corpus's own hand commit, `a4577c01`: six checks added, three invalidated, one commit. The rule's other half is annotated and not performed — 54 rows carry a hand-written `RE-RUN (…)` and all 54 are still ticked.

## What it pins

**That one Save produces that commit's shape**, asserted on the files in `HEAD` rather than on the return value.

**That an invalidated check keeps its record** — unticked AND saying who unticked it and why, with its previous pass date intact.

**That a pass discharges the invalidation it answers.** Added after a mutation deleting the clear left the suite green; without it every migrated check would be permanently stale, because not one of the fleet's 54 annotations carries a date.

**That staleness is arithmetic in BOTH directions** once the dates exist. A one-sided test also passes a rule that always returns `True`, and did.

**That nothing is written when anything is refused**, and that a sweep changing nothing must say why rather than stamping a date.

**That no check is owed, measured on a corpus where every check is unwalked** — the state that would make per-check obligations most tempting.

## Adequacy

Six mutations; all killed. Two survived first (the invalidation clear, and the staleness arithmetic) and are guarded above.

## Retired 2026-08-18 — the subject is withdrawn ([[ADR-0036]])

This verified the acceptance sweep: one Save, N checks added, M invalidated, one commit. The sweep is withdrawn and its suite is deleted, so `command:` is cleared rather than left pointing at a file that is not there — a stale entrypoint is a test that reports nothing while looking like it reports something.

**Retired, not deleted.** It is the record that TESTING.md rule 3 was once made performable and how it was verified — which stays true. If invalidation returns, keyed on the surface rather than the feature ([[DES-0012]]), this is the note that says what the first attempt covered.
