---
type: "[[task]]"
id: TASK-0249
aliases: ["TASK-0249"]
title: "Validate cold workspaces on a bounded schedule, and decide whose validator runs"
status: backlog
phase: "[[PHASE-013-Fleet-Surfaces]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["[[FEAT-0028-Fleet-Health-Surface]]"]
parent: "[[FEAT-0028-Fleet-Health-Surface]]"
effort: M
depends: []
blocks: ["[[TASK-0251-Fleet-Roll-Up]]"]
related: ["[[TASK-0248-Live-Workspace-Validation-Aggregate]]", "[[ISS-0026-Bundled-Validator-Drift]]"]
tests: []
---

# TASK-0249 — Cold-workspace validation

## Definition of Done
- [ ] A decision is **recorded** on whose `validate-docs.py` runs against another repo — per-repo or this repo's — with the reasoning, before any code
- [ ] Discovered workspaces with no live sidecar get a validation state marked `source: 'cold'` and carrying its own `checked_at`
- [ ] The schedule is **bounded and stated**: how often, how many concurrently, and what triggers an off-schedule run
- [ ] A state older than the schedule interval is marked stale rather than presented as current
- [ ] **Nothing writes to a repo this app does not own** — asserted by a test, not by intention
- [ ] A repo with no `SNAPSHOT.yaml`, no validator, or an unreadable one reports `unknown` with a reason, never a false green

## Steps
- [ ] Settle the validator question (below) and write it into this note
- [ ] Reuse `ValidationRunner`'s locate rules for finding a validator; do not invent a second search
- [ ] Run out-of-process with a timeout, serialised or small-N concurrent — ten repos' validators at once is a visible stall
- [ ] Test: a fixture fleet of three repos (one clean, one drifting, one with no snapshot) produces three distinct states; and a read-only assertion over the fixture's mtimes/contents

## The decision this task owns

FEAT-0028's brief plan and an existing script disagree, and the difference is not cosmetic.

- The feature says **"run the repo's `tools/scripts/validate-docs.py`"** — honours a repo that deliberately pinned an older template; each repo is judged by its own rules.
- `tools/scripts/validate-fleet.sh` says **"uses THIS repo's validate-docs.py for uniform semantics"** — makes counts comparable across the fleet, at the cost of reporting drift a repo has not adopted a rule for.

They produce different badges for the same repo. [[ISS-0026]] is the cautionary precedent: this repo's *bundled* validator copy silently drifted from the template, and the fix was byte-identity plus a guard. A fleet surface that mixes semantics per repo would have no such anchor.

Recommendation, to be confirmed: **per-repo**, because a red badge a repo's own CI would not raise is a false positive, and false positives on a ten-repo dashboard are how a dashboard stops being read. With the repo's validator version surfaced in the tooltip so uniformity is visible rather than assumed.

## Notes

The expensive half, and the one with a blast radius: it runs a script in ten repositories the user did not ask this app to touch. Read-only is therefore a **test**, not a promise — the same distinction [[TASK-0231]] is blocked on for the same reason.

Cost is the other real risk. `validate-fleet.sh` runs the fleet synchronously and is a deliberate manual action; doing it on a timer inside a GUI is a different proposition. If a bound cannot be found that keeps the app responsive, the honest outcome is on-focus-only rather than a background poll.
