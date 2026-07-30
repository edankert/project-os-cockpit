---
type: "[[phase]]"
id: PHASE-013
aliases: ["PHASE-013"]
title: "Fleet surfaces — the cockpit reports on every repo it can see, not just the open one"
status: done
order: 13
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
goal: "Finish the work that treats the fleet as the unit rather than the workspace: roll the design-system convention across the repos that have a UX, and surface per-repo validator health without opening each one. Both already have one leg built."
features:
  - "[[FEAT-0028-Fleet-Health-Surface]]"
  - "[[FEAT-0044-Fleet-Design-Systems]]"
requirements: []
issues:
  - "[[ISS-0055-Deferred-Findings-From-The-Design-Bench-Reviews]]"
depends: ["[[PHASE-009-Design-Surfaces]]"]
related: ["[[DES-0002-Cockpit-Design-System]]", "[[FEAT-0032-Agents-Screen]]", "[[PHASE-011-Unproven-Claims]]"]
tags: [fleet, design]
reviewed_by: "model:claude-opus-5"
review_date: 2026-07-30
review_verdict: "approved"
---

# Fleet surfaces

## Goal

Two features here are half-built, and both were paused rather than abandoned.

[[FEAT-0044]] is `doing` with [[TASK-0230]] `done` and [[TASK-0231]] outstanding: the per-project stylesheet route shipped, the rollout across the fleet did not. [[FEAT-0028]] is `backlog` with no tasks — per-workspace validator badges, which the `~agents` screen already proves is possible because it aggregates per-workspace state across repos.

The reason to do them together is that they need the same thing: a reliable read of *another* repo's docs from this one. `~agents` does it for agent state, `validate-fleet.sh` does it for validation, and neither is wired into a surface.

## Scope

- **[[TASK-0231]]** — roll the design-system convention out across the fleet repos that have a UX, finishing [[FEAT-0044]]. [[DES-0002]] is the template and is `implemented`, so this is application rather than design.
- **[[FEAT-0028]]** — per-workspace validator badges across discovered repos. Needs task breakdown; there are none yet.
- **[[ISS-0055]]** — the deferred design-bench findings (at-rule descent, a dead token, others). Grouped here because they are the residue of the machinery this phase leans on, and fixing them in isolation would mean opening the design bench twice.

## Out of Scope

- **The MCP server** ([[FEAT-0029]]). Also cross-boundary, but a different boundary — exposing this cockpit outward rather than reading other repos inward. Stays in [[PHASE-999-Future]].
- **The downstream pilot** ([[FEAT-0005]] / [[PHASE-003]]). It has its own phase, untouched since PHASE-002. Whether it is still wanted is a decision, not scope to absorb here.
- **Distribution** ([[TASK-0065]] — signing, notarization, auto-update). Deliberately parked until sharing outside this machine matters.
- **Fixing other repos' corpora.** If the rollout finds a fleet repo whose docs do not conform, that is an issue filed against that repo, not work in this phase.

## Exit Criteria

- [x] Every fleet repo with a UX has a design-system note and a living style guide read from its own CSS — evidence: the seven-row table in [[TASK-0231]], with measured token counts and the five skipped repos named with reasons
- [x] The cockpit shows validator health for every discovered workspace without opening it — evidence: ten workspaces, one deliberately drifted, badge and roll-up verified live ([[TASK-0250]], [[TASK-0251]])
- [x] [[FEAT-0028]] has tasks before implementation starts — evidence: TASK-0248..0251, written and committed (`718a3ac`) before any code
- [x] [[ISS-0055]]'s findings are each fixed or explicitly declined with a reason — evidence: the note, item by item; §1 was already fixed and said so, §2–4 fixed, and the closing observation acted on in new code

## Notes

Sequenced last of the three. Nothing here is wrong today — it is unfinished, which is a weaker claim on attention than [[PHASE-011]]'s misleading surfaces or [[PHASE-012]]'s duplicated section.

Worth watching for scope creep: "the fleet" is 11 repos on one machine, and every surface that reads across them is a surface that can be wrong about ten codebases at once. [[FEAT-0028]] in particular should ship read-only and stay that way.

## Independent review — 2026-07-30 (model:claude-opus-5, fresh context, separate session) — approved

Approved as a plan. Scope, sequencing and the exclusions are defensible from the note alone: both features genuinely have one leg built, the shared prerequisite (a reliable read of another repo's docs) is the real reason to group them, and "fixing other repos' corpora" being out of scope is the boundary that keeps this from becoming unbounded. The `FEAT-0028`-needs-tasks criterion is the right gate on a feature with no breakdown, and the read-only caution in Notes is the one warning this phase needed.

No findings. One observation for whoever starts it: the fleet-wide leg of [[ISS-0069]] ("consider upstreaming", still open) and the `.gitignore` defect recorded in [[CHG-20260730-Two-Features-Closed]] are both cross-repo conventions that this phase's tooling will be reading across 11 corpora — worth knowing before the rollout, not after.


## Closed 2026-07-30

Both features done, the issue fixed, and the fleet re-validated: **12 of 12 repos OK**, unchanged from the baseline taken before any of this. Fresh clones of the six repos touched also validate clean — the check [[ISS-0070]] taught, because a machine that validates locally proves nothing about what was committed.

### What landed

- **[[FEAT-0028]]** — per-workspace validator badges and a fleet roll-up, live (SSE, no polling) for open workspaces and cold (bounded subprocess, 10-minute schedule, read-only asserted by test) for the rest. Four tasks, all verified against the real fleet.
- **[[FEAT-0044]]** — [[TASK-0231]]'s rollout finished. All seven surfaces across six projects now have a page that reads that project's own source, including the three native apps that were blocked when the note was written.
- **[[ISS-0055]]** — the four deferred design-bench findings.

### Written to other repositories, with a per-repo record

The user's go-ahead covered this; it is listed so it is auditable rather than implied.

| Repo | Change | Commit |
|---|---|---|
| your-health | DES-0001: family palette de-duplicated, stale "no single source" claim corrected, rollout recorded | `c8aafca` |
| your-sudoku | same | `b594d8f` |
| your-trainer | same | `f0af198` |
| project-os | `.gitignore`: `inbox/` → `/inbox/` | `9c8de68` |
| project-os-dev | ISS-0024/0025/0026 filed + the same `.gitignore` fix | one commit each |
| edankert.com, obsidian-supernote-sync, project-os-bench, your-applications.com, your-health, your-sudoku, yourtrainer-mcp | `.gitignore` anchoring | one commit each |

**Nothing else in those repos was touched.** `your-health` carries unrelated uncommitted work from 2026-07-28 (six PLAN.md edits and a CHG note); it was left alone, and only `.gitignore` was staged there.

`your-trainer` has no `.gitignore` inbox entry at all, so it needed none — noted so the eight-of-nine count reads as deliberate.

### The `.gitignore` fix is fleet-wide because the defect was

[[ISS-0070]] fixed the unanchored `inbox/` here. The pattern is **template-owned**, so eight other repos carried the identical latent defect: any directory named `inbox` at any depth vanishes silently. Swept the fleet for live casualties — one hit, `your-applications.com/public/your-trainer/inbox/`, which turns out to be **deliberately** ignored by its own anchored rule three lines earlier. So this repo was the only victim, and the other eight were fixed before they could become one.

### Owed, and named rather than absorbed

- **The six downstream design notes are still `draft`.** They leave `draft` when Edwin has looked at the pages. A human gate, not outstanding work.
- **Upstream decisions are not made here.** project-os-dev ISS-0024/0025/0026 are filed with recommendations and evidence; deciding them is that repo's work.
- **[[TASK-0251]]'s roll-up has no automated test** — DOM code that cannot be imported outside a browser, covered by the live pass and marked `[~]`.

### [[ISS-0072]] — found here, diagnosed here, fixed here

The live pass turned up that the sidecar's `SNAPSHOT.yaml` observer never fired, so `METRICS` drift — the commonest validator error — could not clear without a restart. The cause was not in the observer: **FSEvents is case-sensitive on a case-insensitive filesystem**, so a watch registered as `/Users/edwin/…` matched no event reported as `/Users/Edwin/…`. The recursive docs watcher matches by prefix and was unaffected; only the exact-match SNAPSHOT watch broke — on **every app-spawned sidecar**, because the shell stores workspace roots as the path was typed.

Fixed by canonicalising the case of `ValidationRunner.project_root`, verified against the exact invocation that failed, and mutation-tested.

### Worth carrying forward

Three of this phase's findings came from **running the thing**, not reading it: [[ISS-0072]], [[ISS-0073]], and `your-trainer`'s zone ramp turning out not to be a designed scale. All three were invisible in the source and unavoidable the moment something rendered. Same lesson [[ISS-0069]] recorded — the surface catching what the validator could not — arriving three more times in one phase.

And a sharper version of it, from ISS-0072: **[[FEAT-0018]]'s acceptance was verified live and still missed this**, because the fault that pass induced took the working code path. A live check is only as good as the fault you induce, and inducing the convenient one is how a broken path stays green.
