---
type: "[[feature]]"
id: FEAT-0138
aliases: ["FEAT-0138"]
title: "Coverage is observed, not declared — the test names the check it covers, CI emits the entry, and a deleted test simply stops emitting"
status: backlog
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
goal: "A claim that a machine covers a check is produced by a run rather than asserted in frontmatter, so deleting or disabling the covering test puts the check back on the run list on its own."
requirements: ["[[REQ-0057-Coverage-Is-Observed-From-A-Run]]"]
tasks: ["[[TASK-0541-Seed-The-Mapping-Before-Deleting-The-Field]]", "[[TASK-0542-The-Test-Declares-The-Check]]", "[[TASK-0543-The-CI-Emitter-Writes-Into-The-Working-Ledger]]"]
related: ["[[ADR-0037-A-Verdict-Is-An-Event]]", "[[ISS-0198-Automation-And-Covered-By-Are-Empty-On-All-669-Checks]]", "[[DES-0012-Tests-In-Two-Flows]]"]
tags: [feature]
---

# The dependency inverts

## Goal

`covered_by:` on the check is a **standing claim** and it rots silently: rename, delete or `@Ignore` the covering test and the note keeps asserting coverage while the check drops out of the run list permanently, with no signal. That is worse than a stale verdict, because a stale verdict still asks.

Invert it. **The test declares the check** — `@Covers("TST-0028")`, or a comment-and-grep convention for v1 — and the CI run emits `method: automated` entries into the working ledger. A deleted test stops emitting and the check reappears on its own.

## Why this is the version that works, measured

[[ISS-0198]] tried the standing claim and closed with the field **deliberately empty**: `your-trainer`'s 203 annotated bodies name **54 JVM test classes and not one `TST-*` id**, and `cover_check` correctly refuses a link to something no runner can execute. Filling it would have meant inventing 54 unrunnable notes.

Under observed coverage that population is exactly the one that works. The 54 classes each declare the check they cover in their own source, the gradle run emits, and nothing has to invent a note for a command nobody can execute.

## Scope

- **Seed before deleting.** `covered_by:` holds nothing anywhere, so the real seed is the 203 prose annotations. Extract them before [[FEAT-0134]] removes `automation:`.
- The declaration convention, per language. Comment-and-grep for v1 — this repo is pytest, `your-trainer` is JVM, and a v1 that needs a shared annotation library ships nowhere.
- The emitter: a CI run appends `method: automated` entries for what it observed.

## Out of scope

- **Making CI run in the fleet repos.** [[ISS-0209]]: the acceptance gate runs in no repo holding a check. Until that is resolved, the emitter runs here and nowhere the data lives, and this feature must not claim otherwise.

## Acceptance

- [ ] The 203 annotations are extracted and recorded before `automation:` is removed.
- [ ] A test declares the check it covers, in a form one grep finds.
- [ ] A CI run appends observed-coverage entries to the working ledger for its platform.
- [ ] Deleting a covering test puts its check back on the run list within one CI cycle, proved.
- [ ] Nothing declares coverage in a note.

## Re-homed out of PHASE-038, 2026-08-19

**Stage 2 is a body of work, not a leftover.** [[PHASE-038]] closed on the thing it was opened for — a verdict is an event, and the ledger is the only place one lives — and its nine exit criteria are met. Observed coverage is the *next* argument, and holding a finished phase open for it would make the phase's status say something false about the work that is done.

The seed it depends on is safe: [[TASK-0541]] extracted **278 checks naming 81 JVM classes** before [[TASK-0530]] removed the field they lived in, and that file is committed.

What it still needs before anybody starts it: a declaration convention that works in pytest *and* JVM without a shared library, and [[ISS-0209]] — the acceptance gate runs in no repo that holds a check, so an emitter would run here and nowhere the data lives.

## The tasks came too, 2026-08-20 — they had not

Re-homing this feature into [[PHASE-037]] on 2026-08-20 moved the **feature** and left [[TASK-0542]] and [[TASK-0543]] pointing at [[PHASE-999]]. `PHASE-CHILDREN` gates a phase on notes naming it in `phase:`, so both were invisible to the gate on the phase that owns their work — and invisible to every other gate too, because `PHASE-999` is never closed. A child in a parking lot cannot hold anything open.

Same shape as the miss the phase's own widening note records one level up: *"FEAT-0138 also pointed at PHASE-999 without ever being listed in it, which is why nothing flagged it."*

Both now name `PHASE-037`, in the notes and in `SNAPSHOT.yaml` — `sync-snapshot.py` propagates status but **not** `phase`, so that second edit is by hand. [[TASK-0541]] keeps `PHASE-038`: it is `done`, and a finished task records where the work actually happened.

**The consequence is deliberate and it is not small.** `PHASE-037` cannot close while either is unresolved, and neither can start: this feature's own note says what they wait on — a declaration convention that works in pytest *and* JVM without a shared library, and [[ISS-0209]], which is why an emitter would run here and nowhere the data lives.
