---
type: "[[task]]"
id: TASK-0453
aliases: ["TASK-0453"]
title: "Three verdicts and an offered tick — verifiable-done, open with an age, unknowable; and nothing ticks itself"
status: backlog
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["[[FEAT-0110-Still-Owed-By-A-Shipped-Release]]", "Edwin 2026-07-30: issues appearing without anyone asking is a worse failure than one occasionally missed"]
parent: "[[FEAT-0110-Still-Owed-By-A-Shipped-Release]]"
effort: M
depends: ["[[TASK-0452-Read-The-Post-Release-Checklist]]"]
blocks: []
related: ["[[ADR-0022]]"]
tests: []
---

# Three verdicts and an offered tick

## Why

Of the 37 unticked boxes, four are provably **done** and the box is simply stale, three are provably **open**, and one cannot be known from anything in the repo. Rendering them as one undifferentiated list would repeat the mistake [[FEAT-0108]] is fixing on the other page.

The sharpest one, checked 2026-08-16: `REL-0010` says to flip `investigation_status` in `compatibility.json` on `your-applications.com`. It still reads `investigating`. The fix shipped **85 days ago** and riders still see the warning.

## What

Each unticked box gets exactly one of three verdicts, with its evidence:

| verdict | means | rendering |
|---|---|---|
| verifiable-done | the record proves it happened | offer a tick |
| open | the record proves it has not | say so, with an age in days |
| unknowable | nothing in the record can decide | say that |

## The verdict sources

Only lookups the index and `publication._tags` already perform:

- `git tag vX.Y.Z` → does the tag exist
- `ISS-####` / `REQ-####` / `PHASE-####` reaching a named status → the index
- a path in a sibling workspace → the workspace index, where the file is reachable
- anything else → **unknowable**

## The rule, and it is the point of the task

**Nothing is ever ticked automatically.** The verdict is computed; the write is a click.

This project's recorded failure mode is *issues appearing without anyone asking*. A box **disappearing** without anyone asking is the same failure with a worse blast radius — an automatic tick on a wrong inference destroys the only record that the obligation ever existed.

And per [[ADR-0022]]: nothing here pushes, deploys, or writes into another workspace. It can *read* `compatibility.json` in a sibling repo and report that the box is open. It cannot edit it.

## Deliberately out of scope

Four release notes carry `Update REL-#### status to published`, and **`published` is not a valid release status** — `STATUSES.md` allows `draft`, `released`, `reverted`. Those boxes are `unknowable` here. The defect is in the release **template** and belongs upstream; it is recorded in the phase note, not fixed by a rendering task.

## Done when

- [ ] every unticked box carries exactly one verdict and the evidence for it
- [ ] an open box carries an age in days from the release date
- [ ] a tick is offered only for verifiable-done, and requires a click — the mutation that must fail is the automatic write
- [ ] a failed evidence lookup yields **unknowable**, never verifiable-done — tested directly
- [ ] a cross-repo target that cannot be reached yields unknowable rather than a guess
- [ ] no path from this surface writes into another workspace
- [ ] asserted live: the four stale-done boxes found, and the `compatibility.json` box reported open
