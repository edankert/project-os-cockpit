---
type: "[[task]]"
id: TASK-0266
aliases: ["TASK-0266"]
title: "A push action that a person triggers, and that refuses deploy remotes"
status: done
phase: "[[PHASE-021-Git-Is-Not-The-Users-Job]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["[[FEAT-0055-Git-Assist]]"]
parent: "[[FEAT-0055-Git-Assist]]"
effort: S
depends: ["[[TASK-0265-Unpushed-State-On-The-Fleet-Surface]]"]
blocks: []
related: []
tests: []
---

# A deliberate push

## Definition of Done
- [x] A push action on the roll-up row for a repo that is behind
- [x] It says **what it will publish** before doing it — the count, and the remote
- [x] A `deploy` remote is **refused**, naming the remote and why
- [x] A repo with no remote offers nothing
- [x] Failure is reported with git's own message, not swallowed
- [x] Nothing pushes without this action being used

## Steps
- [x] `git:push` IPC in main, refusing anything not classified `backup`
- [x] The action on the roll-up row
- [x] Test: the refusal path, and that no code path pushes without it

## Notes

**The refusal is the feature.** `your-applications.com`'s only remote is `root@…:/home/…/your-applications.com.git` — pushing there deploys a live website, and on 2026-07-30 that was one ambiguous instruction away from happening. A button that publishes must know the difference between a backup and a deployment.

**Saying what it will publish** matters because the counts are large and surprising: 117 commits and six days for the repo this is written in. "Push" reads like a small action and was not one.

## Done 2026-07-30

`git:push` IPC plus the action on the roll-up row.

**The refusal, verified live:** `your-applications.com` is 31 commits behind and its button reads `deploy remote`, disabled, with the reason in the tooltip. It is the only fleet repo that is behind at all, which makes it the perfect demonstration — the one thing the surface offers to push is the one thing it must not.

**Classified in main as well as in the payload, deliberately.** The renderer's disabled button is a UI state, not a guard; the process that actually runs `git push` re-derives the kind from the URL and refuses there too.

Guarded: the deploy refusal, the unrecognised-is-deploy default, and that the renderer has **exactly one** `git.push(` call site — so "nothing else pushes" is asserted rather than asserted-about.
