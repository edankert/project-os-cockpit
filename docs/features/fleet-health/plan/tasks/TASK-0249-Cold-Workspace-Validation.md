---
type: "[[task]]"
id: TASK-0249
aliases: ["TASK-0249"]
title: "Validate cold workspaces on a bounded schedule, and decide whose validator runs"
status: done
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
- [x] A decision is **recorded** on whose `validate-docs.py` runs against another repo — per-repo or this repo's — with the reasoning, before any code
- [x] Discovered workspaces with no live sidecar get a validation state marked `source: 'cold'` and carrying its own `checked_at`
- [x] The schedule is **bounded and stated**: how often, how many concurrently, and what triggers an off-schedule run
- [x] A state older than the schedule interval is marked stale rather than presented as current
- [x] **Nothing writes to a repo this app does not own** — asserted by a test, not by intention
- [x] A repo with no `SNAPSHOT.yaml`, no validator, or an unreadable one reports `unknown` with a reason, never a false green

## Steps
- [x] Settle the validator question (below) and write it into this note
- [x] Reuse `ValidationRunner`'s locate rules for finding a validator; do not invent a second search
- [x] Run out-of-process with a timeout, serialised or small-N concurrent — ten repos' validators at once is a visible stall
- [x] Test: a fixture fleet of three repos (one clean, one drifting, one with no snapshot) produces three distinct states; and a read-only assertion over the fixture's mtimes/contents

## The decision this task owns

FEAT-0028's brief plan and an existing script disagree, and the difference is not cosmetic.

- The feature says **"run the repo's `tools/scripts/validate-docs.py`"** — honours a repo that deliberately pinned an older template; each repo is judged by its own rules.
- `tools/scripts/validate-fleet.sh` says **"uses THIS repo's validate-docs.py for uniform semantics"** — makes counts comparable across the fleet, at the cost of reporting drift a repo has not adopted a rule for.

They produce different badges for the same repo. [[ISS-0026]] is the cautionary precedent: this repo's *bundled* validator copy silently drifted from the template, and the fix was byte-identity plus a guard. A fleet surface that mixes semantics per repo would have no such anchor.

Recommendation, to be confirmed: **per-repo**, because a red badge a repo's own CI would not raise is a false positive, and false positives on a ten-repo dashboard are how a dashboard stops being read. With the repo's validator version surfaced in the tooltip so uniformity is visible rather than assumed.

## Notes

The expensive half, and the one with a blast radius: it runs a script in ten repositories the user did not ask this app to touch. Read-only is therefore a **test**, not a promise — the same distinction [[TASK-0231]] is blocked on for the same reason.

Cost is the other real risk. `validate-fleet.sh` runs the fleet synchronously and is a deliberate manual action; doing it on a timer inside a GUI is a different proposition. If a bound cannot be found that keeps the app responsive, the honest outcome is on-focus-only rather than a background poll.

## Decision 2026-07-30 — the repo's own validator

**The evidence settled this, not a preference.** `ValidationRunner`'s locate order already chose per-repo in FEAT-0018 and stated why: a repo's own copy *"honours that repo's `STATUSES.md`"*. FEAT-0028's own plan says to reuse "the same locate rules as `ValidationRunner`". So `validate-fleet.sh` is the outlier, and it is right to be: comparability is the point of a manual diagnostic, and a false positive is the cost of a badge. A red mark a repo's own CI would not raise trains people to stop reading the surface.

Recorded before implementing, as this note required. Pinned by `test_the_repos_own_validator_is_preferred_over_the_bundled_copy`.

**The counter-argument, kept rather than dropped:** running each repo's own script means executing N different scripts. These are all the user's own repos on their own machine and `validate-fleet.sh` already does something similar, so the marginal exposure is small — but it is not zero, and "uniform" would have avoided it. Uniform loses on false positives, which is the failure that kills a dashboard.

## Done 2026-07-30

- `src/project_os_cockpit/fleet_validate.py` — `python -m project_os_cockpit.fleet_validate <repo> [...]`, one JSON line per repo, **counts not lists** (ten repos' full violation lists across a pipe is a lot of bytes for a badge showing a number; opening a workspace gets the full report from its own sidecar).
- `validation.validate_repo()` — public, so the locate order stays the single place that decides whose validator runs. The desktop shell spawns this rather than re-deriving those rules in TypeScript.
- `refreshColdWorkspaces()` in `fleet-health.ts`, skipping any workspace that has a live subscription, and skipping again on completion for one whose sidecar came up mid-batch.

### The bounds, stated

- **One subprocess for the whole batch**, serial inside Python. Ten validators at once is a visible stall on the machine the user is working on, and nobody is waiting on a repo nobody has open.
- **10 minutes**, plus once at startup after the live pass. A repo nobody is editing does not drift.
- **`fleet:health` (opening a surface) does NOT trigger it** — only the slow timer and an explicit `fleet:health-recheck`. A surface opening must not fork ten subprocesses.
- **Older than 20 minutes → `stale`.** The row keeps its state and count and says how old it is; presenting a two-hour-old reading as current is the failure this exists to avoid.

### Read-only, asserted

`test_validating_a_repo_does_not_modify_it` clones this repo's real corpus, fingerprints every file's mtime **and** content hash, validates, and compares. `test_the_cold_pass_command_never_carries_fix_metrics` captures the argv at the `subprocess.run` boundary — the validator's one write path (`fix_metrics`, which rewrites `SNAPSHOT.yaml`) is behind that flag. `coldArgv` is pinned on the TypeScript side too.

**The first cut of that guard had the defect it was guarding.** It grepped the source for `--fix-metrics` and failed on the docstring explaining that the flag is not passed — a string-shaped guard producing a false positive. Rewritten to capture the real argv.

### No false greens

A repo with no `SNAPSHOT.yaml`, no validator, or an unreadable one reports `unavailable` **with a reason**, never `ok`. One bad repo does not kill the batch.
