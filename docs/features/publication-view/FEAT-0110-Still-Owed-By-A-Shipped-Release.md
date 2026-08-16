---
type: "[[feature]]"
id: FEAT-0110
aliases: ["FEAT-0110"]
title: "Still owed by a shipped release — the post-release checklist every release note already carries is read, verified against the record, and offered back"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Independent functionality review of PHASE-034, 2026-08-16 — the one proposal with a consequence outside the documentation system", "Measured against ../your-trainer and ../your-applications.com on 2026-08-16"]
goal: "A release does not end when the tag is written. Eight shipped release notes already carry a post-release checklist with 37 unticked boxes; read them, say which are provably done, which are provably still open and for how long, and which cannot be known."
requirements: []
tasks: ["[[TASK-0452-Read-The-Post-Release-Checklist]]", "[[TASK-0453-Three-Verdicts-And-An-Offered-Tick]]"]
design: ""
release: ""
depends: []
related: ["[[FEAT-0107-Publication-Is-A-List-Of-Releases]]", "[[ADR-0028-Work-Has-Three-Phases]]", "[[ADR-0022]]", "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"]
tests: ["[[TST-0036-FEAT0109]]"]
---

# Still owed by a shipped release

## A fix from May is still showing a warning to real riders

`../your-trainer`'s `REL-0010` (v2.0.5, shipped 2026-05-23) carries this unticked box:

```
- [ ] flip reported_issues.investigation_status to resolved in compatibility.json on your-applications.com
```

Checked on 2026-08-16: `../your-applications.com/public/your-trainer/compatibility.json` still reads `investigation_status: "investigating"`. Every owner of a Tacx Neo Bike and a ThinkRider XXpro is still told the in-app compatibility test may not complete. **The fix shipped 85 days ago**, and the only thing in the world that remembers to retire the warning is a checkbox in a Markdown file that nothing reads.

The cockpit renders both of those repos. It walks past this.

## What is already written down

Eight shipped release notes carry a `## Post-Release Actions` section of real `- [ ]` boxes. **37 are unticked**, and a surprising number are decidable from data the index already holds:

| unticked box | what the record says |
|---|---|
| REL-0010 `Tag repo: git tag v2.0.5` | tag **v2.0.5 exists** — done, box stale |
| REL-0007 `Tag repo: git tag v2.0.0` | tag **v2.0.0 exists** — done, box stale |
| REL-0010 `Set status: fixed on ISS-0268 + ISS-0269` | both are **`fixed`** — done, box stale |
| REL-0011 `Resume PHASE-019 (iOS parity)` | PHASE-019 is **`active`** — done, box stale |
| REL-0010 `Set status: passing on REQ-0183 after the 30-day window` | REQ-0183 is **still `draft`**; the window closed 2026-06-22 |
| REL-0010 `flip investigation_status in compatibility.json` | still **`investigating`** — live, 85 days |
| REL-0010 `Watch Play Console Vitals for 30 days; zero entries is the bar` | nothing recorded, ever — **unknowable** |
| REL-0004/5/8/10 `Update REL-#### status to published` | **`published` is not a release status** — `STATUSES.md` allows `draft`, `released`, `reverted` |

Four are provably done and the box is simply stale. Three are provably open, one of them visible to the public. One cannot be known from anything in the repo. And four ask for a status transition that the schema does not permit — which is its own finding about the release template.

## What the page says

```
Still owed by this release                                shipped 85 days ago
  ✓ verifiable-done   tag v2.0.5 exists                          [ Tick ]
  ✓ verifiable-done   ISS-0268 / ISS-0269 are fixed               [ Tick ]
  ! open              REQ-0183 still draft — window closed 55d ago
  ! open              compatibility.json still "investigating"
  ? unknowable        Play Console Vitals watch — no evidence recorded
```

**Three verdict classes, and only three.** *Verifiable-done* offers the tick. *Verifiably-open* says so with an age. *Unknowable* says that too — an unknowable box is honest, a silently-carried one is not.

This is the same read `_known_issues` already performs for `## Known issues`, against a different heading.

## Acceptance criteria

- [x] A shipped release page reads its `## Post-Release Actions` section and lists the **unticked** boxes.
- [x] Each box carries one of exactly **three verdicts** — verifiable-done, open, unknowable — and the evidence for it.
- [x] An **open** box carries an age in days, measured from the release date.
- [x] A **verifiable-done** box offers a tick and the tick is **never** applied without a click.
- [x] A release note with **no such section** — four of the twelve — renders nothing rather than an empty heading.
- [x] The section heading is matched with the same tolerance as `## Known issues`: `Post-Release Actions`, `Post release actions`, `Follow-up`.
- [x] A box naming a **cross-repo** target resolves through the workspace index where it can, and reports *unknowable* where it cannot — it does not guess.
- [x] Nothing here pushes, deploys, or edits a file in another workspace. Per [[ADR-0022]], the cockpit names publication and does not perform it.

## The rule that governs the tick

**No box is ever ticked automatically.** Offer it, with the evidence beside it.

This project's recorded failure mode is *issues appearing without anyone asking* (Edwin, 2026-07-30). Boxes **disappearing** without anyone asking is the same failure with a worse blast radius: an automatic tick on a wrong inference destroys the only record that the obligation existed. The verdict is computed; the write is a person's.

## How this is verified

A `TST-*` over a fixture carrying one box of each verdict class, plus a live assertion against `../your-trainer` that the four stale-done boxes are found and that the `compatibility.json` box is reported open. Mutations to defeat: report a *verifiable-done* verdict when the evidence lookup fails; tick without a click; count ticked boxes as owed; return the whole section rather than the unticked subset.

## What this opens and does not close

`published` appearing as an instruction in four release notes when it is not a valid status is a **template** defect, not a rendering one. It is recorded here because this feature is what found it, and it belongs upstream in the release template rather than in this page. Filed as a note in the phase, not fixed here.

This feature is also half of ISS-0181's fourth item — *complete a release from the release note*. It supplies the **after**; it does not supply the ship transition itself, which needs [[FEAT-0108]] and [[FEAT-0109]] underneath it and is deliberately left for later.
