---
type: "[[phase]]"
id: PHASE-021
aliases: ["PHASE-021"]
title: "Git is not the user's job — close-out commits, and being behind is visible instead of forgotten"
status: done
order: 21
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
goal: "Close-out commits its own work, and a repo that is behind its remote says so on the surface that already reports repo health — so pushing is a decision you can see rather than a chore you forget."
features:
  - "[[FEAT-0055-Git-Assist]]"
requirements: []
issues: []
depends: ["[[PHASE-020-Clipboard-That-Works]]"]
related: ["[[FEAT-0028-Fleet-Health-Surface]]", "[[FEAT-0052-History-Timeline]]"]
tags: [git, lifecycle]
---

# Git is not the user's job

## Where this came from

Edwin, 2026-07-30: *"since a user of project-os should not necessarily be in charge of the git commits and pushes, suggest how to automate this"* — and, having heard the options, **assisted** rather than fully automatic.

## The measurement

On 2026-07-30 this machine was **312 commits and six days behind** across eight repositories. `project-os-cockpit`'s remote sat at 2026-07-24 with 117 commits unpushed. Nobody had been careless: nothing anywhere ever mentioned it.

**The push does not fail because it is hard. It fails because it is invisible.**

## Why assisted rather than automatic

Three hazards, each measured the same day:

1. **`git add -A` would commit other people's work.** `your-trainer` carries 44 uncommitted files and `your-health` 8, from 2026-07-28. Both were deliberately left alone; an automation that adds everything sweeps them in.
2. **One repo's only remote is a production server.** `your-applications.com` has no `origin` — it has `production` → a server path. Pushing there **deploys a website**.
3. **A green validator is not working software.** Three clipboard bugs shipped that day through a clean validator and 642 passing tests. The gate stops documentation drift and says nothing about whether the thing works.

A commit is local and reversible. **A push is publishing, and irreversible once caches and indexes have it.** So the commit is automated and the push is made *visible* — which is the half that actually fails.

## Scope

- **[[FEAT-0055]]** — commit at close-out, unpushed state on the fleet surface, and a deliberate push action that refuses deploy remotes.

## Out of Scope

- **Scheduled or unattended push.** Explicitly declined for now; the guards it would need are recorded in [[FEAT-0055]] so the decision can be revisited rather than re-derived.
- **Anything touching a deploy remote.** Not a setting — a classification.

## Exit Criteria

- [x] Close-out produces a commit scoped to the work — evidence: `close-out-commit.sh`, nine tests, and this phase committed with it
- [x] A repo behind its remote says so where repo health is reported — evidence: *"Not pushed — 31 commits across 1 repo"* on the roll-up, plus the rail tooltip
- [x] Pushing is one deliberate action from that surface — evidence: the row's button
- [x] A deploy remote is never pushed — evidence: `your-applications.com` renders `deploy remote`, disabled, and `git:push` refuses it again in main

## Notes

The connection worth keeping: **"unpushed commits" is the same shape of fact as "validator errors"** — per repo, cheap to compute, currently invisible. [[FEAT-0028]] already built the surface that reports the first. This puts the second beside it rather than inventing somewhere new, which is the mistake [[PHASE-016]] spent itself undoing.


## Closed 2026-07-30

Assisted, as chosen: the commit is automatic, the push is visible and deliberate.

**The demonstration was accidental and perfect.** After this morning's push of 312 commits, the only fleet repo still behind is `your-applications.com` — whose only remote is a production server. So the first thing the new surface ever showed was 31 commits it refuses to push, with the reason.

**Two bugs found by exactly one test each**, both worth keeping:

- `git status --porcelain` collapses untracked content to the directory, so the scope comparison compared directories to filenames.
- Appending code after `if __name__ == "__main__"` binds nothing under `python -m`. Twelve tests passed because importing a module runs all of it; the single subprocess test failed.

Both are cases where the obvious reading of the code was right and the runtime disagreed.
