---
type: "[[feature]]"
id: FEAT-0122
aliases: ["FEAT-0122"]
title: "One human-walked population — the 22 manual tests become tiered acceptance tests, and one predicate answers who runs a test"
status: backlog
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
goal: "Make `kind: manual` outside `level: acceptance` impossible: migrate the 22 notes that hold it onto a tier, retire the `Run` obligation's manual clause, collapse the two who-runs-this predicates into one, and replace time-based staleness with the invalidation the corpus already records."
requirements: ["[[REQ-0041-One-Answer-To-Who-Runs-This]]"]
tasks: ["[[TASK-0491-Tier-The-Twenty-Two]]", "[[TASK-0492-Retire-The-Manual-Run-Obligation]]", "[[TASK-0493-One-Who-Runs-This-Predicate]]", "[[TASK-0494-Change-Replaces-Time-As-Staleness]]"]
release: ""
acceptance: ""
design: ""
related: ["[[ADR-0033-A-Manual-Test-Is-An-Acceptance-Test]]", "[[ISS-0202-Needs-A-Run-Versus-The-Tiers]]", "[[ISS-0195-Two-Types-Carry-One-Act]]"]
---

# One human-walked population

**The residue is small and the simplification is not.** 22 notes fleet-wide — 5 here, 15 in `your-trainer`, 2 in `your-health` — against a surface that currently carries two verdict fields, two re-arming models, two gates and two verbs for one act.

**The tiering is a judgement per note, not a bulk rewrite.** Tier 1 for a capability, Tier 2 for a regression guard that names its `ISS-*`, Tier 3 for a one-build verification — and Tier 3 is the real find here, because it is where the genuinely transient cases go and it retires them after a verified release exactly as TESTING.md already describes.

**The one thing this feature must not do** is move acceptance rows onto a badge. Retiring `Needs a run` means the manual population stops asking *individually*; it does not mean 669 rows start.
