---
type: "[[feature]]"
id: FEAT-0055
aliases: ["FEAT-0055"]
title: "Close-out commits its own work, and being behind a remote is visible"
status: done
phase: "[[PHASE-021-Git-Is-Not-The-Users-Job]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["Edwin 2026-07-30: 'a user of project-os should not necessarily be in charge of the git commits and pushes' — assisted, not automatic"]
goal: "Make the commit a step of close-out rather than a separate skill, and make a repo that is behind its remote say so where repo health is already reported."
requirements: []
tasks:
  - "[[TASK-0264-Commit-At-Close-Out]]"
  - "[[TASK-0265-Unpushed-State-On-The-Fleet-Surface]]"
  - "[[TASK-0266-A-Deliberate-Push-Action]]"
release: ""
related: ["[[FEAT-0028-Fleet-Health-Surface]]"]

---

# Git assist

## Brief plan

1. **[[TASK-0264]]** — `tools/scripts/close-out-commit.sh`: stage the paths the work declares, refuse anything outside them, take the message from the notes, and let the existing pre-commit hook gate it.
2. **[[TASK-0265]]** — the fleet payload carries `ahead` / `remote_kind` per repo; the badge and the roll-up show it.
3. **[[TASK-0266]]** — a push action on the roll-up. Backup remotes only; a deploy remote is refused with the reason.

## Acceptance

- Running the close-out script commits the work and **leaves a dirty file outside its scope untouched**, saying so.
- A repo behind its remote shows the count on the rail tooltip and the roll-up.
- The push action pushes a GitHub-style remote and **refuses** `your-applications.com`, naming the remote as a deploy target.
- Nothing pushes without a person asking.

## The declined option, recorded

**Scheduled unattended push.** Would need: never a deploy remote, never outside declared scope, and a per-repo setting defaulting off. Declined for now because a push is publishing and irreversible; recorded so the decision can be revisited rather than re-derived.


## Done 2026-07-30

All four acceptance criteria verified.

- **The script commits and leaves outside-scope work alone**, saying so — nine tests against real repositories, mutation-verified.
- **A repo behind its remote shows the count** on the tooltip and in its own roll-up group.
- **The push action refuses `your-applications.com`**, naming the remote as a deploy target.
- **Nothing pushes without a person** — asserted by there being exactly one `git.push(` call site.

The demonstration wrote itself: after this morning's push, the *only* fleet repo still behind is the one whose remote is a production server. The surface shows 31 commits and offers no button.
