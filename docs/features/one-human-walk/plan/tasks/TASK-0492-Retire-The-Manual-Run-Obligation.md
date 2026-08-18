---
type: "[[task]]"
id: TASK-0492
aliases: ["TASK-0492"]
title: "Retire the `Run` obligation's manual clause, and prove the badge does not grow"
status: done
phase: "[[PHASE-036-One-Human-Walk]]"
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
source: ["[[FEAT-0122-One-Human-Walked-Population]]"]
parent: "[[FEAT-0122-One-Human-Walked-Population]]"
effort: S
depends: ["[[TASK-0491-Tier-The-Twenty-Two]]"]
blocks: []
related: []
tests: []
---

# Retire the manual Run obligation

With no manual tests outside the tiers, the `test` obligation's manual clause has no subjects. It goes, and what a person owes becomes what the tiers already say.

**The number is the thing to watch.** Baseline per repo: `project-os-cockpit` 1, `your-sudoku` 0, `your-trainer` 5. Afterwards the Tests badge must be **derived from unsettled Tier 1/2 rows and no larger than the number it replaces** — and [[ADR-0027-The-Registry-Counts-What-Needs-A-Person]] still forbids per-check obligations, so this must not become 60 in `your-trainer`.

That is the sharp edge of this whole phase: retiring `Needs a run` means the manual population stops asking **individually**, not that the acceptance population starts. Get it wrong and the badge goes from 5 to 60 overnight, which is precisely the harm ADR-0027 exists to prevent.

Done when: the clause is gone, the badge is derived, the per-repo numbers are measured before and after, and the ADR-0027 guard is green.

## Done 2026-08-18 — and the badge moved, so it was fixed rather than accepted

The `Run` obligation now calls the reader's predicate, and **that alone took `your-trainer` from 5 to 8**: its three frozen per-release suites sit at `status: ready` and carry no `command:`, so the reader correctly called them human-walked and the registry started asking somebody to walk a shipped release's frozen checklist.

They are now `status: retired` — terminal, and exactly what [[ADR-0030]] decision 5 says they are: *records of what past releases were measured against*, never to be migrated or re-walked. **This is the first thing the merged type's new terminal status has been needed for**, six hours after it became legal.

Badges, measured per repo before and after: `project-os-cockpit` **1 → 1**, `your-sudoku` **0 → 0**, `your-trainer` **5 → 5**, `your-health` **2 → 2**. No acceptance row reaches a badge in any repo.
