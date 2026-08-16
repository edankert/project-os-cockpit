---
type: "[[task]]"
id: TASK-0428
aliases: ["TASK-0428"]
title: "The release rung — `REL-*` notes and git tags, which nothing currently reads, and `draft` as the signal that a release is in preparation"
status: done
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin 2026-08-16: 'actual versioned releases … should they all be shown in this release view together with a history?'"]
parent: "[[FEAT-0102-Publication-Becomes-A-View]]"
effort: M
depends: ["[[TASK-0426-The-Ladder-As-Data]]"]
blocks: ["[[TASK-0429-The-Gate-Is-A-Campaign]]"]
related: ["[[ISS-0142-The-Release-Note-Cannot-Be-Found-By-Name]]", "[[ADR-0022]]"]
tests: ["[[TST-0027-The-Ladder-Is-Non-Empty-In-Every-Repo]]"]
---

# The release rung

## What

The fourth rung: `REL-*` notes and git tags. Neither is read anywhere today — `git_state.py` mentions "tag" once, in a comment, and `REL-*` notes reach a surface only via the Library file tree and the quick palette ([[ISS-0142]]).

Fleet-wide: your-trainer 11 notes + 12 tags, this repo 1 + 1, your-applications.com 1 + 0 tags. Nine repos have neither, and for them the rung is **unreached** rather than empty.

## `draft` is the signal

`STATUSES.md` documents a release's `draft` as *"prepared and verified, not yet live"*. That is a release in preparation, it is representable today, and nothing reads it. It is what [[TASK-0429]]'s gate keys on and what [[ADR-0028]]'s in-flight rule reads for a publication-phase test.

Worth stating because it is currently invisible in the one repo that would use it: your-trainer's newest is `REL-0012`, already `released`. So nothing is in preparation there, and the correct behaviour today is that the gate asks for nothing.

## Definition of done

- [ ] `REL-*` notes appear on the rung with their status and version, newest first
- [ ] Git tags appear and are related to their release note where one names the same version; a tag with no note, and a note with no tag, are both shown as themselves rather than hidden
- [ ] A `draft` release is distinguished from a `released` one on sight — it is the state the whole rung is about
- [ ] A repo with no releases and no tags shows the rung as **unreached**, not as an empty list
- [ ] The rung's data comes from the payload in [[TASK-0426]], not from a second read in the renderer
- [ ] Tag reading tolerates a repo with no tags, a detached HEAD and an unreadable git dir without taking the fleet pass down — one bad repo must not kill the batch
- [ ] Walked against all three repos that have releases, and at least two that have none
