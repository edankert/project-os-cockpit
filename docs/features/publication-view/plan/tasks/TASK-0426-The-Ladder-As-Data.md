---
type: "[[task]]"
id: TASK-0426
aliases: ["TASK-0426"]
title: "The ladder as data — one payload saying how far this repo's work has travelled, for every rung it can reach and none it cannot"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[ADR-0028]] decision 1"]
parent: "[[FEAT-0102-Publication-Becomes-A-View]]"
effort: M
depends: ["[[ADR-0028-Work-Has-Three-Phases]]"]
blocks: ["[[TASK-0427-The-Publication-View]]", "[[TASK-0428-The-Release-Rung]]"]
related: ["[[FEAT-0100-Unpushed-Work-Needs-A-Person]]", "[[ISS-0165]]", "[[ISS-0156]]"]
tests: ["[[TST-0027-The-Ladder-Is-Non-Empty-In-Every-Repo]]"]
---

# The ladder as data

## What

One payload answering *how far has this work travelled*: commit, push, deploy, versioned release — the rungs this repo reaches, in order, with what stands at each.

Most of it exists. `history_payload` already returns `remote_kind`, `unpublished_count`, `publication_known` and a per-commit `unpublished` flag. This composes it into a ladder and adds the rung nothing reads.

## First, because the claim is about data

The view's central claim is that it is **never empty in any of the twelve repos**. That is a property of the payload across a real fleet, not of a renderer, and it can be proven before anything is drawn.

## The four shapes it must get right

1. **Reachable but empty** — a backup remote with 0 ahead. The rung is shown, clear.
2. **Unreachable** — a repo with no remote (`articles`, `project-os-bench`). The rung is **absent**, not shown at zero. Absent-at-zero is this project's standing rule.
3. **Reachable, count unknown** — `edankert.com`: a deploy remote with no upstream, so `ahead is None`. One row saying the count cannot be taken, never a zero. [[FEAT-0100]] already refuses this coercion and independent review caught it once when the repair was Python-only.
4. **Refused** — a deploy remote with commits. Counted, named, and no action offered.

## Definition of done

- [ ] One payload, one walk, composed from the existing `git_state`/history reads rather than a new pass — [[ISS-0165]] removed a duplicate git walk and this must not add a fourth
- [ ] Every rung the repo reaches is present with what stands at it; a rung it cannot reach is absent
- [ ] `ahead is None` yields a row that says the count is unknown, and never a zero, on this payload as on every other surface
- [ ] The deploy rung carries its refusal and its reason as data, so no renderer has to compose the sentence
- [ ] Release rung is present in the payload's shape from the start even though [[TASK-0428]] fills it — a rung added later is a rung the renderer learns about twice
- [ ] Walked against all 12 discovered repos and the counts recorded: 12 reach commit, 8 push, 2 deploy, 3 release
- [ ] No new subprocess per repo on a warm path; the cold fleet pass already spawns `git log` per repo and this rides it
