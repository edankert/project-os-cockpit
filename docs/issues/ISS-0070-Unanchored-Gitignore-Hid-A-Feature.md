---
type: "[[issue]]"
id: ISS-0070
aliases: ["ISS-0070"]
title: "An unanchored `inbox/` in .gitignore hid docs/features/inbox/ — FEAT-0045 and three tasks were never in the repository, and a fresh clone failed validate-docs.py"
status: fixed
phase: "[[PHASE-011-Unproven-Claims]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["independent review of PHASE-011/012, 2026-07-30"]
severity: high
component: repo
related: ["[[FEAT-0045-Project-Inbox]]", "[[CHG-20260730-Two-Features-Closed]]", "[[TASK-0232-Inbox-Convention-And-Triage-Skill]]"]
tests: []
---

# An unanchored gitignore pattern hid a whole feature

## Problem

`.gitignore` carried a bare `inbox/`. A gitignore pattern with no leading slash matches a directory of that name **at any depth**, so it also matched `docs/features/inbox/` — the home of [[FEAT-0045]], its `plan/PLAN.md`, and `TASK-0232` / `TASK-0233` / `TASK-0234`.

```
$ git ls-files docs/features/inbox/ | wc -l
0
$ ls docs/features/inbox/ docs/features/inbox/plan/tasks/ | wc -l
8
$ git check-ignore -v docs/features/inbox/FEAT-0045-Project-Inbox.md
.gitignore:45:inbox/    docs/features/inbox/FEAT-0045-Project-Inbox.md
```

**Eight files existed only on one machine.** Not staged, not committed, not recoverable from the remote.

## Why it went unnoticed

`SNAPSHOT.yaml`'s metrics count the feature and its tasks, because `sync-snapshot.py` reads the filesystem. So locally everything agrees and the validator is green. **A fresh clone fails with 4 `METRICS` errors** — `features_done` 45 vs 44, `features_total` 50 vs 49, `tasks_done` 240 vs 237, `tasks_total` 247 vs 244 — because the snapshot counts notes the clone cannot see. LIFECYCLE step 7 puts that validator in CI, so this was a red build nobody had run.

The regression predates the range that surfaced it (it arrived with `afc4fa7`, and a clone at `74a2187` already failed with 3 errors).

## The part that is mine

[[CHG-20260730]] closed FEAT-0045 under the heading *"checked rather than assumed"*, and one of the things it checked was that **`inbox/` is gitignored and empty** — without noticing that the same pattern was hiding the feature's own record. So the close-out inspected the exact mechanism that invalidated it and read it as evidence in favour.

Worse for the process than for the code: **FEAT-0045 could not be independently reviewed at all**, because its notes were not in the handoff surface. Any verdict recorded on that note was uncommittable. A close-out that cannot be reviewed is not a close-out.

## Fix

`inbox/` → `/inbox/`, anchored to the repository root, with the reasoning inline so it is not "tidied" back. Verified in both directions: `docs/features/inbox/…` is no longer ignored, and `inbox/probe.png` at the root still is.

The eight files are now committed.

## Expected, and what to check next time

A gitignore entry for a *specific* directory is anchored. The other entries in this file are worth a pass for the same shape — an unanchored name is only correct when the intent really is "anywhere".

Worth considering upstream: this pattern block is template-owned prose (`LIFECYCLE.md` describes the inbox), so any fleet repo that adopted the inbox convention has the same unanchored rule.

## Notes

The check that would have caught it is cheap and does not exist: **does a fresh clone of `main` validate?** Everything local was green throughout. Filed as a follow-up in the Next Actions of [[ISS-0071]] rather than bolted on here.
